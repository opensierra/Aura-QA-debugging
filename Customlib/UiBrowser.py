# -*- coding: utf-8 -*-
import os
import string

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class UiBrowser(object):

    _SKIP_DIRS = {
        "$recycle.bin", "system volume information", "$sysreset", "$winreagent",
        "config.msi", "perflogs", "found.000", "documents and settings",
        "recovery", "boot",
    }

    @staticmethod
    def _drives():
        if os.name != "nt":
            return ["/"]
        found = []
        for letter in string.ascii_uppercase:
            root = letter + ":\\"
            try:
                if os.path.exists(root):
                    found.append(root)
            except OSError:
                continue
        return found or ["C:\\"]

    @staticmethod
    def _norm_dir(path):
        p = str(path if path is not None else "").strip().strip('"').strip("'")
        if not p:
            return ""
        try:
            p = os.path.expandvars(os.path.expanduser(p))
        except Exception:
            pass
        return os.path.abspath(p)

    def _current_project(self):
        return getattr(self, "_project", None)

    def browseStart(self, kind="generic"):
        proj = self._current_project()
        test_dir = os.path.join(BASE, "Test")
        if kind in ("project", "output", "export"):
            candidates = [proj, test_dir, BASE]
        else:
            candidates = [test_dir, proj, BASE]
        for c in candidates:
            try:
                if c and os.path.isdir(c):
                    return {"ok": True, "path": os.path.abspath(c)}
            except OSError:
                continue
        try:
            return {"ok": True, "path": os.path.abspath(os.path.expanduser("~"))}
        except Exception:
            return {"ok": True, "path": BASE}

    def browseRoots(self):
        roots, seen = [], set()

        def add(label, path, kind="place"):
            try:
                if not label or not path or not os.path.isdir(path):
                    return
                p = os.path.abspath(path)
                key = os.path.normcase(p)
                if key in seen:
                    return
                seen.add(key)
                roots.append({"label": label, "path": p, "kind": kind})
            except OSError:
                pass

        proj = self._current_project()
        if proj:
            try:
                add(os.path.basename(os.path.normpath(proj)) or "Project", proj, "project")
            except Exception:
                pass
        add("Test", os.path.join(BASE, "Test"), "project")
        try:
            home = os.path.expanduser("~")
        except Exception:
            home = None
        if home:
            add("Desktop", os.path.join(home, "Desktop"))
            add("Documents", os.path.join(home, "Documents"))
            add("Downloads", os.path.join(home, "Downloads"))
        for d in self._drives():
            add(d.rstrip("\\/") or d, d, "drive")
        return {"ok": True, "roots": roots}

    def listDir(self, path=None):
        try:
            norm = self._norm_dir(path)
            if not norm:
                norm = self.browseStart("generic")["path"]
            if not os.path.isdir(norm):
                alt = os.path.dirname(norm)
                if alt and os.path.isdir(alt):
                    norm = alt
                else:
                    return {"ok": False, "error": "not_a_folder", "detail": norm, "path": norm}
            dirs = []
            try:
                with os.scandir(norm) as it:
                    for entry in it:
                        try:
                            name = entry.name
                            if name.startswith(".") or name.lower() in self._SKIP_DIRS:
                                continue
                            if entry.is_symlink() or not entry.is_dir(follow_symlinks=False):
                                continue
                            dirs.append({"name": name, "path": os.path.join(norm, name)})
                        except OSError:
                            continue
            except PermissionError:
                return {"ok": False, "error": "denied", "detail": norm, "path": norm}
            except OSError as e:
                return {"ok": False, "error": "io", "detail": str(e), "path": norm}
            dirs.sort(key=lambda d: d["name"].lower())
            parent = os.path.dirname(norm)
            if parent == norm:
                parent = None
            return {"ok": True, "path": norm, "parent": parent, "dirs": dirs, "count": len(dirs)}
        except Exception as e:
            return {"ok": False, "error": "unexpected", "detail": str(e), "path": str(path or "")}