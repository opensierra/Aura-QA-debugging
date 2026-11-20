# -*- coding: utf-8 -*-
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from Customlib import psdns2 as p

# --- Caso 1: nombre cuyo paquete original NO esta en el DUT,
#     pero otro paquete SI lo tiene. Debe validar como "present".
data = {
    "com.android.deskclock": {"es": ["Reloj"], "en": ["Clock"]},
    "com.samsung.clock":     {"es": ["Reloj"], "en": ["Clock"]},
}
installed = {"com.samsung.clock", "com.other.app"}
by_name, by_package = p._build_indexes(data)

reqs = p._make_requests(["Reloj"], data, installed)
assert reqs[0]["kind"] == "name"
status, present = p._request_status(reqs[0], by_name, by_package, installed)
print("[1] 'Reloj' ->", status, sorted(present))
assert status == "present" and present == {"com.samsung.clock"}

# --- Caso 2: paquete instalado pero desconocido en el catalogo -> "extract".
reqs2 = p._make_requests(["com.other.app"], data, installed)
assert reqs2[0]["kind"] == "package"
status2, present2 = p._request_status(reqs2[0], by_name, by_package, installed)
print("[2] 'com.other.app' ->", status2, sorted(present2))
assert status2 == "extract" and present2 == {"com.other.app"}

# --- Caso 3: nombre que NINGUN paquete instalado tiene -> "discover".
reqs3 = p._make_requests(["NombreInexistente"], data, installed)
status3, present3 = p._request_status(reqs3[0], by_name, by_package, installed)
print("[3] 'NombreInexistente' ->", status3, sorted(present3))
assert status3 == "discover" and present3 == set()

# --- Caso 4 (bug anterior): paquete instalado solo se llama "Clock",
#     no "Reloj". El request de "Reloj" NO debe validarlo.
data4 = {
    "com.android.deskclock": {"es": ["Reloj"], "en": ["Clock"]},
    "com.google.clock":      {"en": ["Clock"]},
}
installed4 = {"com.google.clock"}
bn4, bp4 = p._build_indexes(data4)
reqs4 = p._make_requests(["Reloj"], data4, installed4)
print("[4] labels del request:", reqs4[0]["labels"])
status4, present4 = p._request_status(reqs4[0], bn4, bp4, installed4)
print("    'Reloj' ->", status4, sorted(present4))
assert status4 == "discover" and present4 == set()

# --- Caso 5: paquete ausente del DUT pero catalogado -> valida
#     con sus propios labels registrados contra el dispositivo.
reqs5 = p._make_requests(["com.android.deskclock"], data4, installed4)
assert reqs5[0]["kind"] == "package"
status5, present5 = p._request_status(reqs5[0], bn4, bp4, installed4)
print("[5] 'com.android.deskclock' (ausente) ->", status5, sorted(present5))
assert status5 == "present" and present5 == {"com.google.clock"}

# --- Caso 6: grupo de nombres alternativos.
reqs6 = p._make_requests([["Reloj", "Clock"]], data4, installed4)
assert reqs6[0]["kind"] == "name_group"
status6, present6 = p._request_status(reqs6[0], bn4, bp4, installed4)
print("[6] ['Reloj','Clock'] ->", status6, sorted(present6))
assert status6 == "present" and present6 == {"com.google.clock"}

# --- Caso 7: paquete instalado y catalogado -> "present" directo.
reqs7 = p._make_requests(["com.samsung.clock"], data, installed)
status7, present7 = p._request_status(reqs7[0], by_name, by_package, installed)
print("[7] 'com.samsung.clock' (instalado+catalogado) ->", status7, sorted(present7))
assert status7 == "present" and present7 == {"com.samsung.clock"}

print("\n=== TODOS LOS CASOS PASARON ===")
