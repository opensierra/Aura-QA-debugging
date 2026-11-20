# -*- coding: utf-8 -*-
"""Slow real tests: discovery scan against the DUT (temp catalog)."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from Customlib import psdns2 as p

TMP = Path(__file__).resolve().parent / "tmp"
TMP.mkdir(exist_ok=True)
DNS = TMP / "psdns.json"

# Seed: only the Samsung clock is known for "Reloj"/"Clock".
# The Vivo DUT has com.android.deskclock (installed, NOT catalogued here),
# so "Reloj" must be resolved through a discovery scan.
seed = {
    "com.samsung.clock": {"es": ["Reloj"], "en": ["Clock"]},
}
with open(DNS, "w", encoding="utf-8") as f:
    json.dump(seed, f, ensure_ascii=False, indent=4)

print("### SLOW 1: name 'Reloj' with no installed catalogued package -> discovery scan", flush=True)
result = p.update_catalog(
    output_dir=TMP,
    languages=["es", "en", "default"],
    entries=["Reloj"],
)
after = json.loads(DNS.read_text(encoding="utf-8"))
print(f"### RESULT: catalog now has {len(after)} packages")
print("### com.android.deskclock in catalog:", "com.android.deskclock" in after)
if "com.android.deskclock" in after:
    print("### its labels:", json.dumps(after["com.android.deskclock"], ensure_ascii=False))

print("\n### SLOW 2: name group ['Calculadora','Calculator'] -> discovery scan", flush=True)
result2 = p.update_catalog(
    output_dir=TMP,
    languages=["es", "en", "default"],
    entries=[["Calculadora", "Calculator"]],
)
after2 = json.loads(DNS.read_text(encoding="utf-8"))
print(f"### RESULT: catalog now has {len(after2)} packages")
print("### com.vivo.calculator in catalog:", "com.vivo.calculator" in after2)
if "com.vivo.calculator" in after2:
    print("### its labels:", json.dumps(after2["com.vivo.calculator"], ensure_ascii=False))

print("\n=== SLOW CASES DONE ===")
