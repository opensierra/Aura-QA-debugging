# -*- coding: utf-8 -*-
import os
import json
import time
import datetime

VERSION = 1
STAGES = ("listing", "crawl", "qa", "autoexport")
SCREENSHOTS_PER_PACKAGE = 20   # estimación inicial para el ETA del crawl


def _now():
    return datetime.datetime.now().isoformat(timespec="seconds")


class RunStateWriter(object):

    def __init__(self, out_dir, cfg=None):
        self.out_dir = out_dir
        self.cfg = dict(cfg or {})
        self.started = time.time()
        self._stages = {}
        self._order = []
        self._current_stage = None
        self._progress = {"stage": None, "current": 0, "total": None,
                          "package": None, "item": None}
        self._packages = []
        self._done = False
        self._load_previous()

    def _load_previous(self):
        """Hereda etapas ya completadas de un run_state.json previo (flujo por pasos)."""
        try:
            if not self.out_dir or not os.path.isfile(self.path):
                return
            with open(self.path, "r", encoding="utf-8") as f:
                prev = json.load(f)
        except Exception:
            return
        if not isinstance(prev, dict):
            return
        prev_started = prev.get("started")
        if prev_started:
            try:
                self.started = datetime.datetime.fromisoformat(prev_started).timestamp()
            except Exception:
                pass
        prev_stages = prev.get("stages") or {}
        for name, st in prev_stages.items():
            if not isinstance(st, dict):
                continue
            if st.get("state") in ("done", "skipped", "error"):
                self._stages[name] = dict(st)
                if name not in self._order:
                    self._order.append(name)
        prev_pkgs = prev.get("packages") or []
        for p in prev_pkgs:
            if p not in self._packages:
                self._packages.append(p)

    # ---------------------------------------------------------------- etapas
    def stage_start(self, name):
        name = str(name)
        if name not in self._order:
            self._order.append(name)
        self._stages[name] = {"state": "active", "started": time.time(),
                              "duration_s": 0}
        self._current_stage = name
        self.write()

    def stage_end(self, name, state="done", **extra):
        name = str(name)
        st = self._stages.get(name)
        if st is None:
            st = {"started": time.time()}
            self._stages[name] = st
            if name not in self._order:
                self._order.append(name)
        st["state"] = state
        st["duration_s"] = round(time.time() - st.get("started", time.time()), 2)
        st.pop("started", None)
        st.update(extra)
        if self._current_stage == name:
            self._current_stage = None
        self.write()

    def stage_skip(self, name):
        self.stage_end(name, "skipped", duration_s=0)

    # -------------------------------------------------------------- progreso
    def progress(self, stage, current, total=None, package=None, item=None):
        self._progress["stage"] = stage
        self._progress["current"] = int(current or 0)
        if total is not None:
            self._progress["total"] = int(total)
        if package:
            self._progress["package"] = package
            if package not in self._packages:
                self._packages.append(package)
        if item:
            self._progress["item"] = item
        self.write()

    def set_crawl_estimate(self, n_packages, per_package=SCREENSHOTS_PER_PACKAGE):
        """Tarea 5: total aproximado para que el ETA funcione en el crawl."""
        try:
            n = int(n_packages or 0)
        except (TypeError, ValueError):
            n = 0
        if n > 0 and not self._progress.get("total"):
            self._progress["total"] = n * max(1, int(per_package))
            self.write()
        return self._progress.get("total")

    # ---------------------------------------------------------------- cierre
    def finish(self, exit_code=0, error=None):
        if self._done:
            return self.snapshot()
        self._done = True
        for name in self._order:
            st = self._stages.get(name)
            if st and st.get("state") == "active":
                st["state"] = "error" if exit_code != 0 else "done"
                st["duration_s"] = round(time.time() - st.get("started", time.time()), 2)
                st.pop("started", None)
        snap = self.snapshot()
        snap["exit_code"] = int(exit_code or 0)
        snap["error"] = error
        self.write(snap)
        return snap

    def snapshot(self):
        finished = time.time()
        stages = {}
        for name in self._order:
            st = dict(self._stages.get(name, {}))
            if "started" in st:
                st["duration_s"] = round(finished - st["started"], 2)
                st.pop("started", None)
            stages[name] = st
        return {
            "version": VERSION,
            "started": datetime.datetime.fromtimestamp(self.started).isoformat(timespec="seconds"),
            "finished": _now(),
            "duration_s": int(finished - self.started),
            "stages": stages,
            "stage_order": list(self._order),
            "progress": dict(self._progress),
            "packages": list(self._packages),
            "pair": self.cfg.get("pair"),
            "config": {k: v for k, v in self.cfg.items() if k != "pipeline"},
            "exit_code": None,
            "error": None,
        }

    # ---------------------------------------------------------------- disco
    @property
    def path(self):
        return os.path.join(self.out_dir, "run_state.json")

    def write(self, data=None):
        """Escritura atómica: nunca deja un run_state.json a medias."""
        if not self.out_dir:
            return False
        payload = data if data is not None else self.snapshot()
        try:
            os.makedirs(self.out_dir, exist_ok=True)
            tmp = self.path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
            os.replace(tmp, self.path)
            return True
        except Exception:
            return False