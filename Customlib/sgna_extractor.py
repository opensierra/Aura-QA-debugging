import subprocess
import sys
import os
import shutil
import argparse
import json
import time
import threading
from concurrent.futures import ThreadPoolExecutor

BASE = os.path.dirname(os.path.abspath(__file__))
ADB = "adb"
APKTOOL = os.path.join(BASE, "..", "Tools", "apktool.bat")


def run(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"{' '.join(cmd)}\n{result.stderr.strip()}")
    return result.stdout


def install_frameworks(frame_dir=None):
    if frame_dir is None:
        frame_dir = os.path.join(
            os.environ.get("LOCALAPPDATA", os.path.expanduser("~")),
            "apktool", "framework"
        )
    os.makedirs(frame_dir, exist_ok=True)
    listing = run([ADB, "shell", "ls", "/system/framework/*.apk"]).splitlines()
    for line in listing:
        apk = line.strip()
        if not apk:
            continue
        local = os.path.join(frame_dir, os.path.basename(apk))
        run([ADB, "pull", apk, local])
        subprocess.run(
            [APKTOOL, "if", local, "-p", frame_dir],
            capture_output=True, text=True
        )


def list_packages_with_paths():
    out = run([ADB, "shell", "pm", "list", "packages", "-f"])
    grupos = {}
    for line in out.splitlines():
        line = line.strip()
        if not line.startswith("package:"):
            continue
        body = line[len("package:"):].strip()
        ruta, _, pkg = body.rpartition("=")
        if pkg and ruta:
            grupos.setdefault(pkg, []).append(ruta)
    return grupos


def decode_apk(apk_local, dest):
    result = subprocess.run(
        [APKTOOL, "d", "-s", "-f", "-q", apk_local, "-o", dest],
        capture_output=True, text=True,
    )
    if result.returncode != 0 and not os.path.isdir(os.path.join(dest, "res")):
        raise RuntimeError(f"apktool d {apk_local}\n{result.stderr.strip()}")


def copiar_locale(decoded, dest_pkg, locale):
    res = os.path.join(decoded, "res")
    if not os.path.isdir(res):
        return 0
    n = 0
    for nombre in os.listdir(res):
        if nombre == "values" or nombre.startswith(f"values-{locale}"):
            src = os.path.join(res, nombre)
            if os.path.isdir(src):
                shutil.copytree(
                    src, os.path.join(dest_pkg, nombre), dirs_exist_ok=True
                )
                n += 1
    return n


def extraer(pkg, rutas, salida, locale, temp):
    dest_pkg = os.path.join(salida, pkg)
    os.makedirs(dest_pkg, exist_ok=True)
    copiadas = 0
    ok = True
    for j, ruta in enumerate(rutas):
        try:
            apk_local = os.path.join(
                temp, f"{pkg}__{j}__{os.path.basename(ruta)}"
            )
            run([ADB, "pull", ruta, apk_local])
            decoded = os.path.join(temp, f"dec_{pkg}_{j}")
            decode_apk(apk_local, decoded)
            copiadas += copiar_locale(decoded, dest_pkg, locale)
        except RuntimeError:
            ok = False
        finally:
            shutil.rmtree(
                os.path.join(temp, f"dec_{pkg}_{j}"), ignore_errors=True
            )
            try:
                os.remove(
                    os.path.join(
                        temp, f"{pkg}__{j}__{os.path.basename(ruta)}"
                    )
                )
            except OSError:
                pass
    if copiadas == 0:
        shutil.rmtree(dest_pkg, ignore_errors=True)
    return copiadas, ok


def log_text(ts, pkg, n, ok, locale):
    if ok:
        if n > 0:
            msg = f"done  {pkg}  ->  {n} values-{locale} folders"
        else:
            msg = f"done  {pkg}  (no values-{locale})"
    else:
        msg = f"fail  {pkg}"
    return f"[{ts}] {msg}"


class Extractor:
    def __init__(self, salida, locale, temp=None, workers=None):
        self.salida = os.path.abspath(salida)
        self.locale = locale
        self.temp = os.path.abspath(
            temp or os.path.join(salida, "..", "temp")
        )
        self.workers = workers or min(8, os.cpu_count() or 4)

    def _normalizar(self, flist):
        if isinstance(flist, dict):
            return flist
        grupos = {}
        for pkg, ruta in flist:
            grupos.setdefault(pkg, []).append(ruta)
        return grupos

    def extraer_lista(self, flist):
        grupos = self._normalizar(flist)
        total = len(grupos)

        salida = self.salida
        temp = self.temp
        locale = self.locale

        devices = run([ADB, "devices"]).splitlines()[1:]
        devices = [d.strip() for d in devices if d.strip()]
        if not devices:
            print("No device detected. Connect the DUT via USB.")
            sys.exit(1)
        device = devices[0].split("\t")[0]

        os.makedirs(salida, exist_ok=True)
        os.makedirs(temp, exist_ok=True)

        print(f"Device: {device}")
        print(f"Output: {salida}")
        print(f"Locale: values-{locale}")
        print(f"Packages: {total}")
        print()

        install_frameworks()

        lock = threading.Lock()
        state = {
            "done": 0,
            "with_locale": 0,
            "no_locale": 0,
            "fail": 0,
            "folders": 0,
            "active": 0,
            "start": time.time(),
        }
        reporte = {"paquetes": [], "resumen": {}}

        log_path = os.path.join(salida, "actividad.log")
        logf = open(log_path, "w", encoding="utf-8")

        def procesar(pkg, rutas):
            with lock:
                state["active"] += 1
            dest_pkg = os.path.join(salida, pkg)
            os.makedirs(dest_pkg, exist_ok=True)
            copiadas = 0
            ok = True
            omitido = ""
            for j, ruta in enumerate(rutas):
                try:
                    apk_local = os.path.join(
                        temp, f"{pkg}__{j}__{os.path.basename(ruta)}"
                    )
                    run([ADB, "pull", ruta, apk_local])
                    decoded = os.path.join(temp, f"dec_{pkg}_{j}")
                    decode_apk(apk_local, decoded)
                    copiadas += copiar_locale(decoded, dest_pkg, locale)
                except RuntimeError as e:
                    ok = False
                    omitido = str(e).splitlines()[0]
                finally:
                    shutil.rmtree(
                        os.path.join(temp, f"dec_{pkg}_{j}"),
                        ignore_errors=True
                    )
                    try:
                        os.remove(
                            os.path.join(
                                temp,
                                f"{pkg}__{j}__{os.path.basename(ruta)}"
                            )
                        )
                    except OSError:
                        pass
            if copiadas == 0:
                shutil.rmtree(dest_pkg, ignore_errors=True)
            ts = time.strftime("%H:%M:%S")
            with lock:
                state["active"] -= 1
                if ok:
                    if copiadas > 0:
                        state["with_locale"] += 1
                    else:
                        state["no_locale"] += 1
                else:
                    state["fail"] += 1
                state["folders"] += copiadas
                state["done"] += 1
                reporte["paquetes"].append({
                    "paquete": pkg,
                    "carpetas_es": copiadas,
                    "ok": ok,
                    "error": omitido if not ok else "",
                })
                line = log_text(ts, pkg, copiadas, ok, locale)
                print(line)
                logf.write(line + "\n")
                logf.flush()
            return pkg

        try:
            with ThreadPoolExecutor(max_workers=self.workers) as ex:
                pkgs_sorted = sorted(grupos.keys())
                list(ex.map(
                    procesar,
                    pkgs_sorted,
                    [grupos[p] for p in pkgs_sorted]
                ))
        finally:
            logf.close()

        reporte["resumen"] = {
            "total_paquetes": total,
            "ok": total - state["fail"],
            "con_fallos": state["fail"],
            "sin_es": state["no_locale"],
            "con_es": state["with_locale"],
            "carpetas_es": state["folders"],
            "salida": salida,
        }
        with open(
            os.path.join(salida, "reporte.json"), "w", encoding="utf-8"
        ) as f:
            json.dump(reporte, f, ensure_ascii=False, indent=2)

        elapsed = time.time() - state["start"]
        print()
        print(
            f"Done in {elapsed:.1f}s — "
            f"{state['with_locale']} with values-{locale}, "
            f"{state['no_locale']} without, "
            f"{state['fail']} failed, "
            f"{state['folders']} folders"
        )
        print(f"JSON report: {os.path.join(salida, 'reporte.json')}")
        print(f"Activity log: {log_path}")

        shutil.rmtree(temp, ignore_errors=True)
        print(f"temp cleaned: {temp}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("salida", help="output folder for all extracted resources")
    parser.add_argument("--temp", default=os.path.join(BASE, "..", "temp"))
    parser.add_argument("--locale", default="es", help="locale to extract (e.g. es, fr, de)")
    parser.add_argument("--filtro", default=None, help="process only packages containing this text")
    parser.add_argument("--packages", default=None, help="comma-separated list of package names to process")
    parser.add_argument("--non-interactive", action="store_true", help="run without user prompts")
    args = parser.parse_args()

    salida = os.path.abspath(args.salida)
    temp = os.path.abspath(args.temp)
    os.makedirs(salida, exist_ok=True)
    os.makedirs(temp, exist_ok=True)

    devices = run([ADB, "devices"]).splitlines()[1:]
    devices = [d.strip() for d in devices if d.strip()]
    if not devices:
        print("No device detected. Connect the DUT via USB.")
        sys.exit(1)

    grupos = list_packages_with_paths()
    if args.filtro:
        grupos = {k: v for k, v in grupos.items() if args.filtro in k}
    if args.packages:
        wanted = set(p.strip() for p in args.packages.split(","))
        grupos = {k: v for k, v in grupos.items() if k in wanted}

    ext = Extractor(salida, args.locale, temp)
    ext.extraer_lista(grupos)


if __name__ == "__main__":
    main()