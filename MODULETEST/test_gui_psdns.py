# -*- coding: utf-8 -*-
"""Test GUI psdns methods against the real DUT (read-only: refreshPsdns)."""
import importlib.machinery
import importlib.util
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

loader = importlib.machinery.SourceFileLoader("GUI", str(BASE / "GUI"))
spec = importlib.util.spec_from_loader("GUI", loader)
gui_mod = importlib.util.module_from_spec(spec)
loader.exec_module(gui_mod)

api = gui_mod.Api()

# 1. refreshPsdns: catalog + installed list
res = api.refreshPsdns()
print("ok:", res["ok"])
print("serial:", res["serial"])
print("catalogPackages:", res["catalogPackages"])
print("installed count:", len(res["installed"]))
assert res["ok"] is True
assert res["catalogPackages"] == 18
assert "com.android.deskclock" in res["installed"]

# 2. _psdns_pick_label: uiLang fallback chain
label, all_names = api._psdns_pick_label(res["catalog"]["com.android.deskclock"], "es")
print("label(es):", label, "| all:", all_names)
assert label == "Reloj"

label_en, _ = api._psdns_pick_label(res["catalog"]["com.android.deskclock"], "en")
print("label(en):", label_en)
assert label_en == "Clock"

# region -> base -> default -> package
label_pt, _ = api._psdns_pick_label(res["catalog"]["com.android.camera"], "pt")
print("label(pt) camera:", label_pt)
assert label_pt in ("Câmara", "Câmera")

# 3. updatePsdns lock: second call while running must return already_running
r1 = api.updatePsdns(entries=["com.vivo.appstore"], refresh=False)
print("task1:", r1)
assert r1["ok"] is True and r1["taskId"]
r2 = api.updatePsdns(entries=["com.vivo.appstore"], refresh=False)
print("task2 (must be already_running):", r2)
assert r2["ok"] is False and r2["error"] == "already_running"
assert r2["taskId"] == r1["taskId"]

# wait for the worker to finish (single small package)
import time
for _ in range(60):
    if api._psdns_task is None:
        break
    time.sleep(1)
print("worker finished, task slot free:", api._psdns_task is None)
assert api._psdns_task is None

# 4. catalog after update: com.vivo.appstore merged in
res2 = api.refreshPsdns()
print("catalogPackages after update:", res2["catalogPackages"])
assert "com.vivo.appstore" in res2["catalog"]

print("\n=== GUI PSDNS METHODS OK ===")
