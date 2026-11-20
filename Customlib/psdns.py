# -*- coding: utf-8 -*-
import json
import shutil
import subprocess
import tempfile
import time
from datetime import datetime
from pathlib import Path

from androguard.core.apk import APK
from loguru import logger

logger.disable("androguard")


def _log(mensaje):
    hora = datetime.now().strftime("%H:%M:%S")
    print(f"[{hora}] {mensaje}", flush=True)


def _ejecutar(argumentos):
    resultado = subprocess.run(
        argumentos,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    if resultado.returncode != 0:
        detalle = resultado.stderr.strip() or resultado.stdout.strip()
        raise RuntimeError(detalle or "El comando fallo.")

    return resultado.stdout.strip()


def _seleccionar_dispositivo(adb):
    _log("Comprobando dispositivos Android...")

    salida = _ejecutar([adb, "devices"])
    dispositivos = []

    for linea in salida.splitlines():
        partes = linea.split()

        if not partes or partes[0] == "List":
            continue

        if len(partes) >= 2:
            dispositivos.append((partes[0], partes[1]))

    disponibles = [
        serial
        for serial, estado in dispositivos
        if estado == "device"
    ]

    if len(disponibles) > 1:
        raise RuntimeError(
            "Hay varios dispositivos disponibles. Conecta solo uno."
        )

    if not disponibles:
        estados = ", ".join(
            f"{serial}: {estado}"
            for serial, estado in dispositivos
        )

        raise RuntimeError(
            "No hay un dispositivo Android disponible."
            + (f" Estados: {estados}" if estados else "")
        )

    serial = disponibles[0]
    _log(f"Dispositivo seleccionado: {serial}")

    return [adb, "-s", serial]


def _guardar_json(datos, archivo):
    temporal = archivo.with_suffix(".json.tmp")

    with temporal.open("w", encoding="utf-8") as salida:
        json.dump(
            datos,
            salida,
            ensure_ascii=False,
            indent=4,
        )

    temporal.replace(archivo)


def _normalizar_idioma(valor):
    valor = valor.replace("\x00", "").strip()

    if not valor:
        return "default"

    valor = valor.lower().replace("_", "-")

    if valor.startswith("b+"):
        valor = valor[2:].replace("+", "-")

    partes = valor.split("-")

    # Android: es-rES -> es-es.
    if len(partes) > 1 and partes[1].startswith("r"):
        region = partes[1][1:]

        if len(region) == 2 or region.isdigit():
            partes[1] = region

    partes[0] = {
        "in": "id",
        "iw": "he",
        "ji": "yi",
    }.get(partes[0], partes[0])

    return "-".join(partes)


def _obtener_etiqueta(apk):
    etiqueta = apk.get_attribute_value("application", "label")

    if etiqueta:
        return etiqueta

    principales = {
        apk.format_value(nombre)
        for nombre in apk.get_main_activities()
    }

    for tipo in ("activity", "activity-alias"):
        for elemento in apk.find_tags(tipo):
            nombre = apk.get_value_from_tag(elemento, "name")

            if nombre and apk.format_value(nombre) in principales:
                etiqueta = apk.get_value_from_tag(elemento, "label")

                if etiqueta:
                    return etiqueta

    raise RuntimeError("No se encontro una etiqueta utilizable.")


def _extraer_variantes(apk):
    etiqueta = _obtener_etiqueta(apk)

    # Una etiqueta literal no tiene idioma identificado.
    if not etiqueta.startswith("@"):
        return [("default", etiqueta)]

    recursos = apk.get_android_resources()

    if recursos is None:
        raise RuntimeError("El APK no contiene recursos legibles.")

    recurso_id, paquete_recurso = recursos.parse_id(etiqueta)

    if paquete_recurso and paquete_recurso != apk.get_package():
        raise RuntimeError(
            f"La etiqueta depende de recursos externos: {paquete_recurso}"
        )

    variantes = []

    for configuracion, texto in recursos.get_resolved_res_configs(
        recurso_id
    ):
        if not isinstance(texto, str):
            continue

        texto = texto.strip()

        if not texto or texto.startswith("@"):
            continue

        idioma = _normalizar_idioma(
            configuracion.get_language_and_region()
        )

        variante = (idioma, texto)

        if variante not in variantes:
            variantes.append(variante)

    if not variantes:
        raise RuntimeError(
            f"No se pudo resolver ninguna variante de {etiqueta}."
        )

    return variantes


def _agrupar_nombres(variantes, idiomas):
    resultado = {}

    for solicitado in idiomas:
        nombres = []

        for variante, nombre in variantes:
            coincide = variante == solicitado

            # Un idioma general incluye sus variantes regionales.
            if solicitado != "default" and "-" not in solicitado:
                coincide = (
                    coincide
                    or variante.startswith(solicitado + "-")
                )

            if coincide and nombre not in nombres:
                nombres.append(nombre)

        if nombres:
            resultado[solicitado] = sorted(
                nombres,
                key=lambda nombre: (nombre.casefold(), nombre),
            )

    return resultado


def _obtener_nombres(comando_adb, paquete, carpeta, idiomas):
    archivo_apk = carpeta / "app.apk"

    try:
        _log("  Consultando ruta APK...")

        salida = _ejecutar(
            comando_adb + ["shell", "pm", "path", paquete]
        )

        rutas = [
            linea.strip().removeprefix("package:")
            for linea in salida.splitlines()
            if linea.strip().startswith("package:")
        ]

        if not rutas:
            raise RuntimeError("Android no devolvio una ruta APK.")

        ruta = next(
            (ruta for ruta in rutas if ruta.endswith("/base.apk")),
            rutas[0],
        )

        _log(f"  Descargando APK: {ruta}")

        _ejecutar(
            comando_adb + ["pull", ruta, str(archivo_apk)]
        )

        if not archivo_apk.is_file() or archivo_apk.stat().st_size == 0:
            raise RuntimeError("No se descargo un APK valido.")

        megabytes = archivo_apk.stat().st_size / (1024 * 1024)
        _log(f"  APK descargado: {megabytes:.1f} MB")
        _log("  Analizando manifiesto y recursos...")

        apk = APK(archivo_apk.read_bytes(), raw=True)
        variantes = _extraer_variantes(apk)
        resultado = _agrupar_nombres(variantes, idiomas)

        for idioma in idiomas:
            nombres = resultado.get(idioma)

            if nombres:
                _log(
                    f"  [{idioma}] "
                    + json.dumps(nombres, ensure_ascii=False)
                )
            else:
                _log(
                    f"  [{idioma}] Sin variantes coincidentes; "
                    "se omite del JSON."
                )

        return resultado

    except Exception as error:
        _log(f"  ERROR: {error}")
        return {}

    finally:
        try:
            archivo_apk.unlink(missing_ok=True)
        except OSError as error:
            _log(f"  AVISO al borrar APK temporal: {error}")


def _imprimir_tabla(datos, idiomas):
    encabezados = ["Paquete"] + idiomas
    filas = []

    for paquete, traducciones in datos.items():
        fila = [paquete]

        for idioma in idiomas:
            nombres = traducciones.get(idioma, [])
            celda = " / ".join(
                " ".join(nombre.split())
                for nombre in nombres
            )
            fila.append(celda or "-")

        filas.append(fila)

    anchos = [
        max(
            len(encabezados[columna]),
            max(
                (len(fila[columna]) for fila in filas),
                default=0,
            ),
        )
        for columna in range(len(encabezados))
    ]

    separador = "+-" + "-+-".join(
        "-" * ancho for ancho in anchos
    ) + "-+"

    def imprimir_fila(fila):
        print(
            "| "
            + " | ".join(
                valor.ljust(ancho)
                for valor, ancho in zip(fila, anchos)
            )
            + " |",
            flush=True,
        )

    print("", flush=True)
    print(separador, flush=True)
    imprimir_fila(encabezados)
    print(separador, flush=True)

    for fila in filas:
        imprimir_fila(fila)

    print(separador, flush=True)


def main(paquetes, directorio_salida, idiomas=("es", "default")):
    """
    Genera psdns.json con la estructura:
        paquete -> idioma solicitado -> lista de nombres unicos.

    Un idioma general, como "es", agrupa sus variantes regionales.
    Un idioma regional, como "es-rES", requiere coincidencia exacta.
    Las llaves de idioma se normalizan, por ejemplo: "es-rES" -> "es-es".

    Los idiomas sin nombres y los paquetes vacios se omiten.
    Los errores solo se imprimen en consola.

    Devuelve el diccionario guardado.
    Cada llamada reemplaza el archivo anterior.
    """
    inicio = time.monotonic()
    _log("Iniciando generacion del catalogo...")

    if isinstance(paquetes, str):
        raise TypeError("paquetes debe ser una lista, no un texto.")

    if isinstance(idiomas, str):
        idiomas = [idiomas]

    paquetes = list(dict.fromkeys(
        paquete.strip()
        for paquete in paquetes
        if paquete.strip()
    ))

    idiomas = list(dict.fromkeys(
        _normalizar_idioma(idioma)
        for idioma in idiomas
        if idioma.strip()
    ))

    if not paquetes:
        raise ValueError("Debes indicar al menos un paquete.")

    if not idiomas:
        raise ValueError("Debes indicar al menos un idioma.")

    adb_local = Path(__file__).resolve().parent / "adb.exe"
    adb = str(adb_local) if adb_local.is_file() else shutil.which("adb")

    if not adb:
        raise FileNotFoundError(
            "No se encontro ADB junto al modulo ni en el PATH."
        )

    # No modificar el JSON si no hay un dispositivo disponible.
    try:
        comando_adb = _seleccionar_dispositivo(adb)
    except RuntimeError as error:
        _log(f"ERROR: {error}")
        _log("Proceso cancelado. No se modifico psdns.json.")
        raise

    carpeta_salida = Path(directorio_salida).expanduser().resolve()
    carpeta_salida.mkdir(parents=True, exist_ok=True)
    archivo_json = carpeta_salida / "psdns.json"

    datos = {}
    omitidos = []

    _log(f"Paquetes: {len(paquetes)}")
    _log(f"Idiomas: {', '.join(idiomas)}")
    _log(f"Salida: {archivo_json}")

    with tempfile.TemporaryDirectory(prefix="psdns_") as temporal:
        carpeta_temporal = Path(temporal)

        for indice, paquete in enumerate(paquetes, start=1):
            inicio_paquete = time.monotonic()

            _log(
                f"[{indice}/{len(paquetes)}] Procesando {paquete}"
            )

            nombres = _obtener_nombres(
                comando_adb,
                paquete,
                carpeta_temporal,
                idiomas,
            )

            if nombres:
                datos[paquete] = nombres
                _guardar_json(datos, archivo_json)
            else:
                omitidos.append(paquete)

            segundos = time.monotonic() - inicio_paquete
            _log(
                f"[{indice}/{len(paquetes)}] "
                f"Terminado en {segundos:.1f}s."
            )

    _imprimir_tabla(datos, idiomas)

    if omitidos:
        _log("Paquetes omitidos por no tener nombres coincidentes:")

        for paquete in omitidos:
            _log(f"  {paquete}")

    if datos:
        _log(f"JSON guardado en: {archivo_json}")
    else:
        _log(
            "No se obtuvieron nombres. "
            "No se creo ni reemplazo psdns.json."
        )

    _log(f"Finalizado en {time.monotonic() - inicio:.1f}s.")

    return datos