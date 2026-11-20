# -*- coding: utf-8 -*-
"""
Test: consume run_pipeline.py tal como lo hace la UI (subproceso + JSON events).
Config tomada de UI/settings.json (la misma fuente que usa la UI).
Verifica que el package Customlib.sgna_crawler resuelve y produce salida.

Se lanza con el Python embebido (igual que plk.bat).
Deja crawlear ~30s, mata el proceso y evalua los resultados en disco.
"""
import json
import os
import subprocess
import sys
import tempfile
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PYTHON = os.path.join(BASE, "python", "python.exe")
PIPELINE = os.path.join(BASE, "run_pipeline.py")
SETTINGS = os.path.join(BASE, "UI", "settings.json")

CRAWL_SECONDS = 30


def build_cfg():
    with open(SETTINGS, "r", encoding="utf-8") as f:
        s = json.load(f)
    p = s.get("pipeline", {})
    return {
        "extOut": os.path.join(tempfile.gettempdir(), "sgna_pkg_test2"),
        "pair": "{}-{}".format(p.get("pairSource", "es"), p.get("pairTarget", "es")),
        "fromScreenshot": False,
        "filterT": p.get("filterT") or [],
        "filterE": p.get("filterE") or [],
        "filterO": [],
        "stages": ["config", "crawl"],
        "exportLang": "es",
        "pipeline": {
            "maxDepth": p.get("maxDepth"),
            "maxScroll": p.get("maxScroll"),
            "speedFactor": p.get("speedFactor"),
            "similarityThreshold": p.get("similarityThreshold"),
            "ghostThreshold": p.get("ghostThreshold"),
            "maxBack": p.get("maxBack"),
            "maxRelaunch": p.get("maxRelaunch"),
            "marginTop": p.get("marginTop"),
            "marginBottom": p.get("marginBottom"),
            "marginLeft": p.get("marginLeft"),
            "marginRight": p.get("marginRight"),
            "duration": p.get("duration"),
            "sleepStable": p.get("sleepStable"),
            "sleepBack": p.get("sleepBack"),
            "sleepExit": p.get("sleepExit"),
            "sleepStart": p.get("sleepStart"),
            "enableCapture": p.get("enableCapture"),
            "rootName": p.get("rootName"),
            "docOrientation": p.get("docOrientation"),
            "docUnwarping": p.get("docUnwarping"),
            "textlineOrientation": p.get("textlineOrientation"),
            "bcHost": p.get("bcHost"),
            "bcPort": p.get("bcPort"),
            "bcTimeout": p.get("bcTimeout"),
            "qaPasses": p.get("qaPasses"),
        },
    }


def main():
    cfg = build_cfg()
    # solo 1 paquete para no crawlear los 19 de settings
    cfg["filterT"] = cfg["filterT"][:1]
    extOut = cfg["extOut"]
    if os.path.exists(extOut):
        import shutil
        shutil.rmtree(extOut)
    os.makedirs(extOut, exist_ok=True)

    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0

    print(f"[TEST] python:   {PYTHON}")
    print(f"[TEST] settings: {SETTINGS}")
    print(f"[TEST] paquete:  {cfg['filterT']}")
    print(f"[TEST] extOut:   {extOut}")
    print()

    proc = subprocess.Popen(
        [PYTHON, PIPELINE, json.dumps(cfg, ensure_ascii=True)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd=BASE,
        creationflags=flags,
        encoding="utf-8",
        errors="replace",
        env=env,
    )

    import_ok = False
    import_error = None
    errors = []
    nodes_logged = 0
    t0 = time.time()

    try:
        for line in proc.stdout:
            line = line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            etype = ev.get("event", "?")

            if etype == "log":
                msg = ev.get("msg", "")
                if "Node:" in msg:
                    nodes_logged += 1
                    print(f"  [NODE] {msg}")
                elif "ERROR" in ev.get("level", ""):
                    print(f"  [LOG-ERR] {msg}")
            elif etype == "step":
                print(f"  [STEP] {ev.get('step')} -> {ev.get('state')}")
                if ev.get("step") == "crawl" and ev.get("state") == "active":
                    import_ok = True
            elif etype == "error":
                msg = ev.get("msg", "")
                print(f"  [ERROR] {msg}")
                errors.append(msg)
                if "ImportError" in msg or "ModuleNotFoundError" in msg:
                    import_error = msg
                    break
            elif etype == "exit":
                print(f"  [EXIT] code={ev.get('code')}")
                break
            if time.time() - t0 > CRAWL_SECONDS + 15:
                print("  [TIMEOUT] limite de tiempo alcanzado")
                break
    finally:
        proc.kill()
        proc.wait()

    # ---- evaluacion de resultados en disco ----
    print()
    print("=" * 60)
    print("[EVAL] Contenido de extOut:")

    n_nodes = 0
    n_shots = 0
    n_manifest = 0
    for root, dirs, files in os.walk(extOut):
        for f in files:
            if f.endswith(".json") and "manifest" in f:
                n_manifest += 1
            elif f.endswith(".png"):
                n_shots += 1
            elif f.endswith(".txt") and "nodes" in root:
                n_nodes += 1

    print(f"  nodos (.txt):    {n_nodes}")
    print(f"  capturas (.png): {n_shots}")
    print(f"  manifests:       {n_manifest}")
    print(f"  nodos en log:    {nodes_logged}")
    print(f"  errores:         {len(errors)}")

    print()
    print("=" * 60)

    if import_error:
        print(f"[FAIL] Error de import: {import_error}")
        sys.exit(1)
    if not import_ok:
        print("[FAIL] No se confirmo el import del package.")
        for e in errors:
            print(f"  {e}")
        sys.exit(1)
    if n_nodes == 0 and n_shots == 0:
        print("[FAIL] El crawler no produjo salida en disco.")
        sys.exit(1)

    print("[PASS] Import del package OK.")
    print(f"[PASS] Crawler producio {n_nodes} nodos y {n_shots} capturas en {CRAWL_SECONDS}s.")
    sys.exit(0)


if __name__ == "__main__":
    main()
