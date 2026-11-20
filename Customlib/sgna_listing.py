import subprocess
import sys


class ListadorPaquetesAndroid:
    PARTICIONES = (
        ("system",     "/system/"),
        ("system_ext", "/system_ext/"),
        ("product",    "/product/"),
        ("vendor",     "/vendor/"),
        ("odm",        "/odm/"),
        ("data",       "/data/"),
    )

    def __init__(self):
        self.paquetes = []
        self.obtener_paquetes()

    def obtener_paquetes(self):
        try:
            resultado = subprocess.run(
                ["adb", "shell", "pm", "list", "packages", "-f"],
                capture_output=True,
                text=True
            )
        except FileNotFoundError:
            print("Error: 'adb' is not installed or not in PATH.")
            sys.exit(1)

        if resultado.returncode != 0:
            print("Error running adb:", resultado.stderr)
            sys.exit(1)

        self.paquetes = []
        for linea in resultado.stdout.strip().splitlines():
            if not linea.startswith("package:"):
                continue
            contenido = linea[len("package:"):].strip()
            if "=" in contenido:
                ruta, nombre = contenido.rsplit("=", 1)
            else:
                ruta, nombre = "", contenido
            self.paquetes.append((nombre, ruta))

    def filtrar_por_origen(self, origen, lista=None):
        origen = [origen] if isinstance(origen, str) else origen
        datos = lista if lista is not None else self.paquetes
        return [(n, r) for n, r in datos if any(r.startswith(o) for o in origen)]

    def filtrar_por_paquete(self, busqueda, lista=None):
        busqueda = [busqueda] if isinstance(busqueda, str) else busqueda
        datos = lista if lista is not None else self.paquetes
        return [(n, r) for n, r in datos
                if any(b.lower() in n.lower() for b in busqueda)]

    def excluir_por_paquete(self, busqueda, lista=None):
        busqueda = [busqueda] if isinstance(busqueda, str) else busqueda
        datos = lista if lista is not None else self.paquetes
        return [(n, r) for n, r in datos
                if not any(b.lower() in n.lower() for b in busqueda)]

    def obtener_particion(self, ruta):
        if not ruta:
            return None
        for nombre, prefijo in self.PARTICIONES:
            if ruta.startswith(prefijo):
                return nombre
        return "other"

    def infodump(self):
        total = len(self.paquetes)
        particiones = {}
        sin_ruta = 0

        for _, ruta in self.paquetes:
            if not ruta:
                sin_ruta += 1
                continue
            particion = self.obtener_particion(ruta)
            particiones[particion] = particiones.get(particion, 0) + 1

        print("\nANDROID PACKAGE SUMMARY")
        print(f"Total packages : {total}")
        for p in (*dict(self.PARTICIONES), "other"):
            cantidad = particiones.get(p, 0)
            if cantidad:
                print(f"{p:<15}: {cantidad}")
        print(f"\nMissing paths : {sin_ruta}")


if __name__ == "__main__":
    listador = ListadorPaquetesAndroid()
    listador.obtener_paquetes()

    while True:
        print("\n=== Android Package Lister ===")
        print("1. Filter by source")
        print("2. Filter by package name")
        print("3. Summary")
        print("4. Exit")
        opcion = input("Select an option: ").strip()

        if opcion == "1":
            origen = input("Source to search: ").strip()
            resultados = listador.filtrar_por_origen(origen)
            print(f"\nPackages with source '{origen}' ({len(resultados)}):\n")
            for nombre, ruta in resultados:
                print(f"  {nombre:<50} {ruta}")
        elif opcion == "2":
            nombre = input("Package name to search: ").strip()
            resultados = listador.filtrar_por_paquete(nombre)
            print(f"\nPackages matching '{nombre}' ({len(resultados)}):\n")
            for n, r in resultados:
                print(f"  {n:<50} {r}")
        elif opcion == "3":
            listador.infodump()
        elif opcion == "4":
            break
        else:
            print("Invalid option.")
