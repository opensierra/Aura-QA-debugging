#!/usr/bin/env python3
"""
Runner del pipeline de QA (mismo flujo que phoenix) para ejecutarlo desde la GUI.

Se lanza como subproceso:  python run_pipeline.py <JSON_CONFIG>

Emite eventos JSON por stdout (una linea por evento) que la GUI lee y muestra:
    {"event": "log",       "msg": "...", "level": "INFO"}
    {"event": "step",      "step": "listing|crawl|qa|autoexport", "state": "active|done|skipped|error"}
    {"event": "progress",  "stage": "crawl", "package": "...", "current": 5, "total": null, "item": "0.5_1.png"}
    {"event": "done",      "ok": true, "extOut": "...", "pkgs": [...]}
    {"event": "error",     "msg": "..."}
    {"event": "exit",      "code": 0}

La config (JSON) tiene la forma de collectSettings().pipeline de la UI mas los
campos de ejecucion:
    {
      "extOut": "Test/Spanish-English",
      "pair":   "vi-es",
      "filterT": ["com.android.settings"],
      "filterE": ["com.android.bbk.lockscreen3"],
      "filterO": ["/system", "/system_ext", "/product", "/vendor"],
      "stages":  ["listing", "crawl", "qa", "autoexport"],
      "pipeline": { ...parametros de crawler/ocr/bc... }
    }

"stages" es 100% configurable: cualquier subconjunto de las 4 etapas.
- crawl sin listing requiere paquetes en filterT.
- qa/autoexport asumen screenshots ya en disco (como phoenix --qa-only).

Tarea 3 backend: escribe run_state.json mediante Customlib.run_state.RunStateWriter.
Tarea 5 backend: set_crawl_estimate publica total aproximado para el ETA en crawl.
"""
import os
import sys
import json
import time
import logging
import threading
import traceback

BASE = os.path.dirname(os.path.abspath(__file__))
if BASE not in sys.path:
    sys.path.insert(0, BASE)

_REAL_STDOUT = sys.stdout
_emit_lock = threading.Lock()
_log_fp = None


def emit(event, **kw):
    try:
        line = json.dumps({"event": event, **kw}, ensure_ascii=False) + "\n"
        with _emit_lock:
            _REAL_STDOUT.write(line)
            _REAL_STDOUT.flush()
    except Exception:
        pass
    if event == "log" and _log_fp:
        try:
            ts = time.strftime("%H:%M:%S")
            _log_fp.write("{}\t{}\t{}\n".format(ts, kw.get("level", "INFO"), kw.get("msg", "")))
            _log_fp.flush()
        except Exception:
            pass


def _load_qa_report_cached(path):
    """Carga qa_report.json desde disco en cada consulta."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


class _JsonStream:
    """Stream que convierte cada linea escrita en un evento 'log' JSON."""

    def __init__(self):
        self._buf = ""

    def write(self, s):
        if not s:
            return 0
        self._buf += s
        while "\n" in self._buf:
            line, self._buf = self._buf.split("\n", 1)
            if line.strip():
                emit("log", msg=line.rstrip(), level="INFO")

        # Bug #23 corregido: flush preventivo para evitar buffer gigante.
        if len(self._buf) > 65536:
            self.flush()

        return len(s)

    def flush(self):
        if self._buf.strip():
            emit("log", msg=self._buf.rstrip(), level="INFO")
            self._buf = ""


class _JsonLogHandler(logging.Handler):
    def emit(self, record):
        try:
            emit("log", msg=self.format(record), level=record.levelname)
        except Exception:
            pass


def _setup_logging():
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    handler = _JsonLogHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    root.addHandler(handler)


def _as_bool(v):
    """Convierte a bool de forma segura: acepta bool, int, y strings ('true'/'false'/'1'/'0').
    Evita el bug de bool('false') == True cuando el frontend envía strings."""
    if isinstance(v, bool):
        return v
    if isinstance(v, (int, float)):
        return v != 0
    if isinstance(v, str):
        return v.strip().lower() in ("1", "true", "yes", "on")
    return bool(v)


def _patch_config(pipe):
    """Parchea Customlib.DeepBlue.config ANTES de importar los consumidores."""
    from Customlib.DeepBlue import config as cfg
    if pipe.get("docOrientation") is not None:
        cfg.DOC_ORIENTATION = _as_bool(pipe["docOrientation"])
    if pipe.get("docUnwarping") is not None:
        cfg.DOC_UNWARPING = _as_bool(pipe["docUnwarping"])
    if pipe.get("textlineOrientation") is not None:
        cfg.TEXTLINE_ORIENTATION = _as_bool(pipe["textlineOrientation"])
    if pipe.get("bcHost"):
        cfg.BC_HOST = str(pipe["bcHost"])
    if pipe.get("bcPort") is not None:
        cfg.BC_PORT = int(pipe["bcPort"])
    if pipe.get("bcTimeout") is not None:
        cfg.BC_TIMEOUT = int(pipe["bcTimeout"])
    if pipe.get("qaPasses") is not None:
        cfg.QA_PASSES = int(pipe["qaPasses"])
    return cfg


def _patch_crawler(pipe):
    """Parchea las constantes del crawler en el namespace de sgna_crawler."""
    import Customlib.sgna_crawler as crw
    int_map = {
        "maxDepth": "MAX_DEPTH",
        "maxScroll": "MAX_SCROLL",
        "maxBack": "MAX_BACK",
        "maxRelaunch": "MAX_RELAUNCH",
    }
    float_map = {
        "similarityThreshold": "SIMILARITY_THRESHOLD",
        "ghostThreshold": "GHOST_SIMILARITY_THRESHOLD",
        "marginTop": "MARGIN_TOP",
        "marginBottom": "MARGIN_BOTTOM",
        "marginLeft": "MARGIN_LEFT",
        "marginRight": "MARGIN_RIGHT",
        "duration": "DURATION",
        "sleepStable": "SLEEP_STABLE",
        "sleepBack": "SLEEP_BACK",
        "sleepExit": "SLEEP_EXIT",
        "sleepStart": "SLEEP_START",
        "speedFactor": "SPEED_FACTOR",
    }
    for key, attr in int_map.items():
        if pipe.get(key) is not None:
            setattr(crw, attr, int(pipe[key]))
    for key, attr in float_map.items():
        if pipe.get(key) is not None:
            setattr(crw, attr, float(pipe[key]))
    if pipe.get("enableCapture") is not None:
        crw.ENABLE_CAPTURE = _as_bool(pipe["enableCapture"])
    if pipe.get("rootName") is not None:
        crw.ROOT_NAME = str(pipe["rootName"])
    return crw


def _step(name, state):
    emit("step", step=name, state=state)


def _count_screenshots(extOut, pkgs):
    total = 0
    for pkg in pkgs:
        d = os.path.join(extOut, pkg, "screenshots")
        if os.path.isdir(d):
            total += len([f for f in os.listdir(d) if f.lower().endswith((".png", ".jpg", ".jpeg"))])
    return total


def _count_index(extOut, pkgs):
    total = 0
    for pkg in pkgs:
        idx = os.path.join(extOut, pkg, "screenshots.index")
        if os.path.isfile(idx):
            with open(idx, "r", encoding="utf-8") as f:
                total += sum(1 for line in f if line.strip())
    return total


def _qa_progress(extOut, pkgs):
    cur = 0
    issues = warnings = 0
    last_pkg = last_item = None
    for pkg in pkgs:
        rp = os.path.join(extOut, pkg, "qa_report.json")
        if not os.path.isfile(rp):
            continue

        data = _load_qa_report_cached(rp)
        if not data:
            continue

        for p in data.get("paquetes", []):
            for r in p.get("resultados", []):
                cur += 1
                issues += len(r.get("issues", []) or [])
                warnings += len(r.get("ocr_warnings", []) or [])
                last_pkg = p.get("paquete", pkg)
                last_item = r.get("imagen")
    total = _count_index(extOut, pkgs)
    return cur, total, last_pkg, last_item, issues, warnings


def _count_exports(extOut, pkgs):
    n = 0
    for pkg in pkgs:
        d = os.path.join(extOut, pkg)
        if os.path.isdir(d):
            for f in os.listdir(d):
                if f.lower().endswith(".xlsx"):
                    n += 1
                    break
    return n


class _ProgressMonitor:
    """Hilo que emite eventos 'progress' cada 2s leyendo el estado real en disco.
    Tambien escribe en el RunStateWriter para que la UI persista el progreso."""

    def __init__(self, extOut, pkgs, stage, writer=None):
        self.extOut = extOut
        self.pkgs = pkgs
        self.stage = stage
        self.writer = writer
        self._stop = threading.Event()
        self._thread = None
        self._last = -1

    def start(self):
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=3)

    def _run(self):
        while not self._stop.is_set():
            try:
                if self.stage == "crawl":
                    cur = _count_screenshots(self.extOut, self.pkgs)
                    total = None
                    pkg = item = None
                    issues = warnings = None
                elif self.stage == "qa":
                    cur, total, pkg, item, issues, warnings = _qa_progress(self.extOut, self.pkgs)
                elif self.stage == "autoexport":
                    cur = _count_exports(self.extOut, self.pkgs)
                    total = len(self.pkgs)
                    pkg = item = None
                    issues = warnings = None
                else:
                    cur, total, pkg, item, issues, warnings = 0, None, None, None, None, None
                emit("progress", stage=self.stage, current=cur, total=total,
                     package=pkg, item=item, issues=issues, warnings=warnings)
                if self.writer is not None:
                    self.writer.progress(self.stage, cur, total=total,
                                         package=pkg, item=item)
            except Exception:
                pass
            self._stop.wait(0.1)


def _beforefilt(flist, n=3):
    emit("log", msg="Filter by package ...", level="INFO")
    for i, (pack, path) in enumerate(flist[:n], 1):
        emit("log", msg="{:<5} {:<55} {}".format(i, pack, path), level="INFO")
    if len(flist) > n:
        emit("log", msg="...   {} more".format(len(flist) - n), level="INFO")


def main():
    if len(sys.argv) < 2:
        emit("error", msg="Falta la config JSON (argv[1])")
        emit("exit", code=2)
        return

    cfg = json.loads(sys.argv[1])
    extOut = cfg.get("extOut") or ""
    if not extOut:
        emit("error", msg="extOut es obligatorio.")
        emit("exit", code=1)
        return
    pair = (cfg.get("pair") or "").strip() or os.path.basename(extOut.replace("\\", "/"))
    filterT = cfg.get("filterT") or []
    filterE = cfg.get("filterE") or []
    filterO = cfg.get("filterO") or []
    pipe = cfg.get("pipeline") or {}
    export_lang = (cfg.get("exportLang") or "en").strip() or "en"

    all_stages = ["config", "listing", "crawl", "qa", "autoexport"]
    stages = cfg.get("stages")
    if not isinstance(stages, list) or not stages:
        stages = list(all_stages)
    stages = [s for s in all_stages if s in stages]
    if "crawl" in stages and "listing" not in stages and not filterT:
        emit("error", msg="Crawleo sin listing requiere paquetes en 'Filtrar por paquete'.")
        emit("exit", code=1)
        return

    os.environ["DEEPBLUE_PAIR"] = pair

    sys.stdout = _JsonStream()
    sys.stderr = _JsonStream()
    _setup_logging()

    global _log_fp
    try:
        _log_fp = open(os.path.join(extOut, ".log"), "a", encoding="utf-8")
    except Exception:
        _log_fp = None

    try:
        from Customlib.run_state import RunStateWriter
        writer = RunStateWriter(extOut, cfg)
        writer.write()
    except Exception as e:
        emit("log", msg="run_state writer disabled: {}".format(e), level="WARNING")
        writer = None

    emit("log", msg="Test iniciado | salida={} | par={} | etapas={}".format(extOut, pair, stages), level="INFO")

    monitor = None
    exit_code = 0
    last_error = None
    export_info = None
    try:
        _patch_config(pipe)

        flist = None
        pkgs = list(filterT)

        if "config" in stages:
            _step("config", "active")
            if writer:
                writer.stage_start("config")
            emit("log", msg="Configurando DUT...", level="INFO")
            try:
                from Customlib.sgna_dut import configure as _dut_configure
                dut_result = _dut_configure()
                if dut_result.get("ok"):
                    emit("log", msg="DUT configurado: {}".format(dut_result["msg"]), level="INFO")
                else:
                    failed = dut_result.get("failed", [])
                    emit("log", msg="DUT config incompleta: {}".format(", ".join(failed) or dut_result.get("msg", "")), level="WARNING")
                _step("config", "done")
                if writer:
                    writer.stage_end("config", "done")
            except Exception as e:
                emit("log", msg="DUT config error: {}: {}".format(type(e).__name__, e), level="WARNING")
                _step("config", "error")
                if writer:
                    writer.stage_end("config", "error", error=str(e))
        else:
            _step("config", "skipped")
            if writer:
                writer.stage_skip("config")

        if "listing" in stages:
            _step("listing", "active")
            if writer:
                writer.stage_start("listing")
            emit("log", msg="Cargando lista de paquetes (Plis)...", level="INFO")
            from Customlib.sgna_listing import ListadorPaquetesAndroid
            dut = ListadorPaquetesAndroid()
            flist = dut.filtrar_por_paquete(filterT) if filterT else list(dut.paquetes)
            if filterE:
                flist = dut.excluir_por_paquete(filterE, flist)
            if filterO:
                flist = dut.filtrar_por_origen(filterO, flist)
            pkgs = [p for p, _ in flist]
            dut.infodump()
            _beforefilt(flist)
            emit("log", msg="Paquetes objetivo ({}): {}".format(len(pkgs), pkgs), level="INFO")
            emit("packages", packages=pkgs)
            if not pkgs:
                emit("error", msg="No hay paquetes que cumplir los filtros.")
                _step("listing", "error")
                if writer:
                    writer.stage_end("listing", "error", error="No packages after filters")
                emit("exit", code=1)
                return
            if writer and "crawl" in stages:
                writer.set_crawl_estimate(len(pkgs))
            _step("listing", "done")
            if writer:
                writer.stage_end("listing", "done", count=len(pkgs))
        else:
            _step("listing", "skipped")
            if writer:
                writer.stage_skip("listing")
            if "crawl" in stages:
                flist = [(p, "") for p in filterT]

        if "crawl" in stages:
            _step("crawl", "active")
            if writer:
                writer.stage_start("crawl")
            emit("log", msg="Iniciando crawleo (Crw)...", level="INFO")
            from Customlib.sgna_crawler import Crawler
            _patch_crawler(pipe)
            speed = float(pipe.get("speedFactor", 1) or 1)
            monitor = _ProgressMonitor(extOut, pkgs, "crawl", writer=writer)
            monitor.start()
            Crawler(extOut, speed=speed).crawlear(flist)
            monitor.stop()
            monitor = None
            total_shots = _count_screenshots(extOut, pkgs)
            emit("progress", stage="crawl", current=total_shots, total=total_shots, package=None, item=None)
            if writer:
                writer.progress("crawl", total_shots, total=total_shots)
                writer.stage_end("crawl", "done", screenshots=total_shots)
            _step("crawl", "done")
        else:
            _step("crawl", "skipped")
            if writer:
                writer.stage_skip("crawl")

        if "qa" in stages:
            _step("qa", "active")
            if writer:
                writer.stage_start("qa")
            emit("log", msg="Iniciando analisis QA (Qal)...", level="INFO")
            from Customlib.sgna_qa import QA
            # Modo desestructurado: el paquete "unstructure" no esta en el
            # filtro de paquetes; el QA debe procesar TODO lo que el indice
            # encuentre (sin filtro). Sin el flag, el flujo normal no cambia.
            if cfg.get("fromScreenshot"):
                qa_pkgs = [d for d in sorted(os.listdir(extOut))
                           if os.path.isfile(os.path.join(extOut, d, "screenshots.index"))]
                emit("log", msg="QA desestructurado: paquetes del indice = {}".format(qa_pkgs), level="INFO")
            else:
                qa_pkgs = pkgs
            monitor = _ProgressMonitor(extOut, qa_pkgs, "qa", writer=writer)
            monitor.start()
            QA(extOut).analizar(qa_pkgs)
            monitor.stop()
            monitor = None
            cur, total, pkg, item, issues, warnings = _qa_progress(extOut, qa_pkgs)
            emit("progress", stage="qa", current=cur, total=total, package=pkg, item=item,
                 issues=issues, warnings=warnings)
            if writer:
                writer.progress("qa", cur, total=total, package=pkg, item=item)
                writer.stage_end("qa", "done", issues=issues, warnings=warnings)
            _step("qa", "done")
        else:
            _step("qa", "skipped")
            if writer:
                writer.stage_skip("qa")

        emit("log", msg="Pipeline finalizado correctamente.", level="SUCCESS")
        emit("done", ok=True, extOut=extOut, pkgs=pkgs)
        if writer:
            writer.finish(exit_code=0)
        emit("exit", code=0)

    except SystemExit as e:
        exit_code = int(e.code or 1)
        last_error = "SystemExit: {}".format(e.code)
        if monitor:
            monitor.stop()
        emit("error", msg=last_error)
        if writer:
            writer.finish(exit_code=exit_code, error=last_error)
        emit("exit", code=exit_code)
    except ValueError as e:
        exit_code = 1
        last_error = str(e)
        if monitor:
            monitor.stop()
        emit("error", msg=last_error)
        if writer:
            writer.finish(exit_code=exit_code, error=last_error)
        emit("exit", code=exit_code)
    except Exception as e:
        exit_code = 1
        last_error = "{}: {}".format(type(e).__name__, e)
        if monitor:
            monitor.stop()
        emit("error", msg=last_error)
        emit("log", msg=traceback.format_exc(), level="ERROR")
        if writer:
            writer.finish(exit_code=exit_code, error=last_error)
        emit("exit", code=exit_code)
    finally:
        if _log_fp:
            try:
                _log_fp.close()
            except Exception:
                pass
            _log_fp = None


if __name__ == "__main__":
    main()