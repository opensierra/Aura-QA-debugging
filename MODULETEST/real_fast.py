# -*- coding: utf-8 -*-
"""Real tests against the DUT using a temp catalog (does not touch the real psdns.json)."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from Customlib import psdns2 as p

TMP = Path(__file__).resolve().parent / "tmp"
TMP.mkdir(exist_ok=True)
DNS = TMP / "psdns.json"

# Seed catalog simulating multi-device history:
# "Reloj"/"Clock" known from a Samsung device (not installed on this Vivo DUT)
# and from the stock deskclock (installed on this DUT).
seed = {
    "com.android.deskclock": {"es": ["Reloj"], "en": ["Clock"]},
    "com.samsung.clock":     {"es": ["Reloj"], "en": ["Clock"]},
}
with open(DNS, "w", encoding="utf-8") as f:
    json.dump(seed, f, ensure_ascii=False, indent=4)

def run(title, **kw):
    print(f"\n{'='*60}\n### {title}\n{'='*60}", flush=True)
    before = json.loads(DNS.read_text(encoding="utf-8"))
    result = p.update_catalog(output_dir=TMP, languages=["es", "en", "default"], **kw)
    after = json.loads(DNS.read_text(encoding="utf-8"))
    added = sorted(set(after) - set(before))
    print(f"### RESULT: catalog {len(before)} -> {len(after)}; added: {added}")
    return result

# --- Case 1: empty list -> no work, no ADB, catalog untouched
run("1. Empty list (no work)", entries=[])

# --- Case 2: name whose original package is NOT on the DUT,
#     but another catalogued package IS -> present, no extraction
run("2. Name 'Reloj' (absent original, installed sibling)", entries=["Reloj"])

# --- Case 3: absent catalogued package -> validated through its labels
run("3. Absent package 'com.samsung.clock'", entries=["com.samsung.clock"])

# --- Case 4: installed package unknown to catalog -> extract
run("4. Installed unknown 'com.vivo.appstore' (extract)", entries=["com.vivo.appstore"])

# --- Case 5: refresh=True re-extracts installed catalogued package
run("5. refresh=True on 'com.android.deskclock'", entries=["com.android.deskclock"], refresh=True)

# --- Case 6: error handling
try:
    p.update_catalog(packages=["x"], entries=["y"], output_dir=TMP)
    print("\n### FAIL: should have raised ValueError")
except ValueError as e:
    print(f"\n### 6a. OK ValueError: {e}")

try:
    p.update_catalog(entries="Reloj", output_dir=TMP)
    print("### FAIL: should have raised TypeError")
except TypeError as e:
    print(f"### 6b. OK TypeError: {e}")

print("\n=== FAST CASES DONE ===")
