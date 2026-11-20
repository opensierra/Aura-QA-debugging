import os
import json
import time
import contextlib
import logging
import re
import unicodedata
import xml.etree.ElementTree as ET

from Customlib.DeepBlue.core_ocr import DeepBlueOCR
from Customlib.DeepBlue.core_bluecode import BlueCodeACP
from Customlib.DeepBlue import config as _cfg

_OCR_SCALE = float(getattr(_cfg, "OCR_SCALE", 1.0) or 1.0)
_BBOX_SCALE = 1.0 / _OCR_SCALE if 0 < _OCR_SCALE < 1 else 1.0

import warnings


# ---------------------------------------------------------------------------
# Coverage metrics (adapted from exttex static.py compute_runtime_coverage)
# ---------------------------------------------------------------------------

_NOISE_PATTERNS = [
    re.compile(r'^[a-z_\d]+/[a-z_\d]+$', re.IGNORECASE),
    re.compile(r'^id/', re.IGNORECASE),
    re.compile(r'^android\.', re.IGNORECASE),
    re.compile(r'^[\w]+Activity$', re.IGNORECASE),
    re.compile(r'^[\w]+Fragment$', re.IGNORECASE),
    re.compile(r'^[\w]+Provider$', re.IGNORECASE),
    re.compile(r'^[\w]+Service$', re.IGNORECASE),
    re.compile(r'^action_bar', re.IGNORECASE),
    re.compile(r'^button\d*$', re.IGNORECASE),
    re.compile(r'^text\d*$', re.IGNORECASE),
    re.compile(r'^image\d*$', re.IGNORECASE),
    re.compile(r'^progress\d*$', re.IGNORECASE),
    re.compile(r'^scroll\d*$', re.IGNORECASE),
    re.compile(r'^container\d*$', re.IGNORECASE),
    re.compile(r'^layout\d*$', re.IGNORECASE),
    re.compile(r'^view\d*$', re.IGNORECASE),
    re.compile(r'^frame\d*$', re.IGNORECASE),
    re.compile(r'^linear\d*$', re.IGNORECASE),
    re.compile(r'^relative\d*$', re.IGNORECASE),
    re.compile(r'^recycler\d*$', re.IGNORECASE),
    re.compile(r'^toolbar\d*$', re.IGNORECASE),
    re.compile(r'^card\d*$', re.IGNORECASE),
    re.compile(r'^chip\d*$', re.IGNORECASE),
    re.compile(r'^tab\d*$', re.IGNORECASE),
    re.compile(r'^menu\d*$', re.IGNORECASE),
    re.compile(r'^nav\d*$', re.IGNORECASE),
    re.compile(r'^content_', re.IGNORECASE),
    re.compile(r'^xmlns', re.IGNORECASE),
    re.compile(r'^http', re.IGNORECASE),
    re.compile(r'^false$|^true$', re.IGNORECASE),
    re.compile(r'^\d+$'),
    re.compile(r'^[\d:.\-/\s]+$'),
    re.compile(r'^-?\d+\.?\d*\s*[a-zA-Z\u00b0\u00b2\u00b3]+$'),
    re.compile(r'^[a-f0-9]{8,}$', re.IGNORECASE),
    re.compile(r'^[\w]+\.[\w]+\.[\w]+'),
    re.compile(r'\\'),
]

_SYSTEM_STRINGS = frozenset({
    'OK', 'ok', 'Cancel', 'Cancelar', 'Aceptar', 'Accept',
    'Yes', 'No', 'Si', 'Sí', 'Close', 'Cerrar',
    'Loading', 'Cargando', 'Save', 'Guardar',
    'Back', 'Atrás', 'Next', 'Siguiente', 'Previous', 'Anterior',
    'Done', 'Hecho', 'Finish', 'Finalizar',
    'Settings', 'Configuración', 'Ajustes',
    'Search', 'Buscar', 'Buscando',
    'More', 'Más', 'Options', 'Opciones',
    'Select', 'Seleccionar', 'Selected', 'Seleccionado',
    'Apply', 'Aplicar', 'Reset', 'Restablecer',
    'Enable', 'Habilitar', 'Disable', 'Deshabilitar',
    'On', 'Off', 'Activado', 'Desactivado',
    'Error', 'Warning', 'Advertencia', 'Aviso',
    'Loading...', 'Cargando...', 'Please wait', 'Espere',
    'null', 'none', 'None', 'Ninguno',
    'empty', 'Empty', 'Vacío',
    'default', 'Default', 'Por defecto',
})

_LIBRARY_PATTERNS = [
    re.compile(r'^(Alt|Ctrl|Mayús|Mayúscula|Meta|Menú|Función|Sym|Shift)\s*\+', re.IGNORECASE),
    re.compile(r'^\d+\s*[ap]\.?m\.?$', re.IGNORECASE),
    re.compile(r'^(AM|PM|A\.M\.|P\.M\.)$', re.IGNORECASE),
    re.compile(r'^(Selecciona|Seleccionar)\s+(AM|PM|a\.m\.|p\.m\.|la hora|una fecha|un período|un periodo|minutos|horas)', re.IGNORECASE),
    re.compile(r'^(Cambiar al (mes|modo|año)\s+(anterior|siguiente|de entrada|de introducción|de calendario|de texto))', re.IGNORECASE),
    re.compile(r'^(Ir (al año|a inicio|a la página principal))', re.IGNORECASE),
    re.compile(r'^(Columna de días|Navegar (hacia arriba|al año))', re.IGNORECASE),
    re.compile(r'^(Caracteres (ingresados|introducidos))', re.IGNORECASE),
    re.compile(r'^\d+\s*(notificaciones? nuevas?)', re.IGNORECASE),
    re.compile(r'^(Barra deslizante|Control deslizante|Pestaña|Botón|Espacio|Intro|Borrar (texto|consulta))$', re.IGNORECASE),
    re.compile(r'^(Mostrar (contraseña|menú desplegable))', re.IGNORECASE),
    re.compile(r'^(Suprimir|Contraer|Desplegar|Expandir|Ocultar)', re.IGNORECASE),
    re.compile(r'^(Capturar|Pausar|Continuar|Reanudar)$', re.IGNORECASE),
    re.compile(r'^(Ver todas?|Ver todo)$', re.IGNORECASE),
]

_FORMAT_STRING_RE = re.compile(r'%[0-9]*\$?[sdif]')
_TEMPLATE_RE = re.compile(r'%[0-9]*\$?[sdf]')


def _is_meaningful_label(label):
    if not label:
        return False
    t = label.strip()
    if not t:
        return False
    if len(t) > 80:
        return False
    for pat in _NOISE_PATTERNS:
        if pat.match(t):
            return False
    if t in _SYSTEM_STRINGS:
        return False
    for pat in _LIBRARY_PATTERNS:
        if pat.match(t):
            return False
    if _FORMAT_STRING_RE.search(t):
        return False
    if '/' in t and len(t) < 40:
        return False
    if re.match(r'^[a-z][a-z_\d]*$', t) and '_' in t and len(t) < 30:
        return False
    return True


def _normalize_text(t):
    if not t:
        return ""
    t = unicodedata.normalize('NFD', t)
    t = ''.join(c for c in t if unicodedata.category(c) != 'Mn')
    t = t.lower().strip()
    t = re.sub(r'\s+', ' ', t)
    return t


def _is_template_match(observed, static_str):
    if not _TEMPLATE_RE.search(static_str):
        return False
    pattern = re.escape(static_str)
    pattern = _TEMPLATE_RE.sub(r'.+', pattern)
    return bool(re.match('^' + pattern + '$', observed))


def _load_strings_from_folder(pkg_path, values_dir_name):
    values_path = os.path.join(pkg_path, values_dir_name)
    if not os.path.isdir(values_path):
        return {}
    strings_file = os.path.join(values_path, "strings.xml")
    if not os.path.isfile(strings_file):
        return {}
    result = {}
    try:
        tree = ET.parse(strings_file)
        root = tree.getroot()
        for s in root:
            tag = s.tag.split("}")[-1] if "}" in s.tag else s.tag
            if tag == "string":
                name = s.attrib.get("name", "")
                val = (s.text or "").strip()
                if val:
                    result[name] = val
    except Exception:
        pass
    return result


def compute_coverage(salida, pkg, ocr_texts):
    """Compute A/B/C coverage metrics for a package.

    Baseline = union of all values-es* folders (excludes plain 'values').
    Observed = set of OCR texts from qa_report entries.

    A = static coverage: % of baseline strings observed at runtime
    B = observation resolution: % of observed texts that match a baseline string
    C = avg per-screen coverage: mean of per-screen match rates
    """
    pkg_path = os.path.join(salida, pkg)
    if not os.path.isdir(pkg_path):
        return None

    all_folders = [d for d in os.listdir(pkg_path)
                   if os.path.isdir(os.path.join(pkg_path, d))]

    variant_labels = {}
    all_values = set()
    for folder in all_folders:
        if folder == "values":
            continue
        if not folder.startswith("values"):
            continue
        strings = _load_strings_from_folder(pkg_path, folder)
        if strings:
            vals = set(strings.values())
            variant_labels[folder] = vals
            all_values.update(vals)

    meaningful_static = {s for s in all_values if _is_meaningful_label(s)}
    static_norm_map = {}
    for s in meaningful_static:
        sn = _normalize_text(s)
        if sn and sn not in static_norm_map:
            static_norm_map[sn] = s

    template_strings = [s for s in meaningful_static if _TEMPLATE_RE.search(s)]

    observed_set = set()
    for t in ocr_texts:
        if t and isinstance(t, str):
            observed_set.add(t)

    matched_records = []
    matched_statics = set()
    observed_matched = set()

    for obs in observed_set:
        if not obs:
            continue
        method = None
        matched_static = None
        if obs in meaningful_static:
            method = "EXACT"
            matched_static = obs
        else:
            obs_norm = _normalize_text(obs)
            if obs_norm in static_norm_map:
                matched_static = static_norm_map[obs_norm]
                method = "NORMALIZED"
            else:
                for tmpl in template_strings:
                    if _is_template_match(obs, tmpl):
                        method = "TEMPLATE"
                        matched_static = tmpl
                        break
        if matched_static:
            matched_records.append({"static": matched_static, "observed": obs, "method": method})
            matched_statics.add(matched_static)
            observed_matched.add(obs)

    static_not_observed = sorted(meaningful_static - matched_statics)
    observed_only = sorted(observed_set - observed_matched)

    per_variant = {}
    for variant, vals in variant_labels.items():
        variant_set = {v for v in vals if _is_meaningful_label(v)}
        v_matched = variant_set & matched_statics
        v_cov = round(100 * len(v_matched) / len(variant_set)) if variant_set else None
        per_variant[variant] = {
            "static": len(variant_set),
            "matched": len(v_matched),
            "coverage": v_cov,
        }

    total_static = len(meaningful_static)
    metric_a = round(100 * len(matched_statics) / total_static) if total_static else None
    metric_b = round(100 * len(observed_matched) / len(observed_set)) if observed_set else None

    return {
        "static_inventory": total_static,
        "observed_total": len(observed_set),
        "matched": len(matched_statics),
        "static_not_observed": static_not_observed,
        "observed_only": observed_only[:200],
        "per_variant": per_variant,
        "metrics": {"A": metric_a, "B": metric_b},
    }


@contextlib.contextmanager
def _silent_ocr():
    devnull = os.open(os.devnull, os.O_WRONLY)
    so, se = os.dup(1), os.dup(2)
    os.dup2(devnull, 1)
    os.dup2(devnull, 2)

    old_stdout, old_stderr = __import__("sys").stdout, __import__("sys").stderr
    import sys as _sys
    _sys.stdout = _sys.stderr = open(os.devnull, "w", encoding="utf-8", errors="ignore")

    ocr_logger = logging.getLogger("ppocr")
    old_level = ocr_logger.level
    ocr_logger.setLevel(logging.CRITICAL + 1)
    pad_logger = logging.getLogger("paddlex")
    old_pad_level = pad_logger.level
    pad_logger.setLevel(logging.CRITICAL + 1)
    root_logger = logging.getLogger()
    old_root_level = root_logger.level
    root_logger.setLevel(logging.CRITICAL + 1)
    old_warn = warnings.showwarning
    warnings.showwarning = lambda *a, **k: None

    try:
        yield
    finally:
        _sys.stdout, _sys.stderr = old_stdout, old_stderr
        ocr_logger.setLevel(old_level)
        pad_logger.setLevel(old_pad_level)
        root_logger.setLevel(old_root_level)
        warnings.showwarning = old_warn
        try:
            old_stdout.flush()
            old_stderr.flush()
        except Exception:
            pass
        os.dup2(so, 1)
        os.dup2(se, 2)
        for f in (devnull, so, se):
            os.close(f)


def _extract_json(text):
    start = text.find("{")
    end = text.rfind("}") + 1
    if start != -1 and end > start:
        try:
            return json.loads(text[start:end])
        except json.JSONDecodeError:
            pass
    return {"error": "Could not parse response", "raw": text[:500]}


class QA:
    """
    Pipeline de QA de localizacion es-CO.
    Lee index.txt, extrae texto con OCR, analiza con BlueCode y guarda
    un reporte JSON por paquete.
    """

    def __init__(self, salida):
        self.salida = os.path.abspath(salida)
        self.index_path = os.path.join(self.salida, "index.txt")
        self.report_path = os.path.join(self.salida, "qa_report.json")
        self._log_fp = None
        self._ocr = None
        self._acp = None
        self._session = None

    def _log(self, msg):
        ts = time.strftime("%H:%M:%S")
        line = f"[{ts}] {msg}"
        print(line)
        if self._log_fp:
            self._log_fp.write(line + "\n")
            self._log_fp.flush()

    def _load_report(self, pkg):
        path = os.path.join(self.salida, pkg, "qa_report.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"paquetes": []}

    def _done_packages(self, report):
        return {p["paquete"] for p in report.get("paquetes", []) if p.get("qa_ok")}

    def _load_index(self):
        entries = []
        for pkg in sorted(os.listdir(self.salida)):
            idx = os.path.join(self.salida, pkg, "screenshots.index")
            if not os.path.isfile(idx):
                continue
            with open(idx, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        entries.append(f"{pkg}/{line}")
        return entries

    def _group_by_package(self, entries):
        groups = {}
        for rel_path in entries:
            parts = rel_path.replace("\\", "/").split("/")
            pkg = parts[0] if parts else "unknown"
            groups.setdefault(pkg, []).append(rel_path)
        return groups

    def _regions_from_ocr(self, ocr_result):
        if not ocr_result or len(ocr_result) == 0 or "rec_texts" not in ocr_result[0]:
            return []
        boxes = ocr_result[0]["rec_boxes"]
        texts = ocr_result[0]["rec_texts"]
        scores = ocr_result[0]["rec_scores"]
        regions = []
        for i, (text, score) in enumerate(zip(texts, scores)):
            x1, y1, x2, y2 = (int(v) for v in boxes[i])
            sx1 = int(round(x1 * _BBOX_SCALE))
            sy1 = int(round(y1 * _BBOX_SCALE))
            sx2 = int(round(x2 * _BBOX_SCALE))
            sy2 = int(round(y2 * _BBOX_SCALE))
            regions.append({
                "id": i,
                "text": text,
                "bbox": {"x": sx1, "y": sy1, "width": sx2 - sx1, "height": sy2 - sy1},
                "score": round(float(score), 3),
                "ctx": score < 0.85,
            })
        return regions

    def _save_report(self, report, pkg, pkg_results, pkg_ok):
        report["paquetes"] = [p for p in report.get("paquetes", []) if p["paquete"] != pkg]
        report["paquetes"].append({
            "paquete": pkg,
            "qa_ok": pkg_ok,
            "total_imagenes": len(pkg_results),
            "resultados": pkg_results,
        })
        path = os.path.join(self.salida, pkg, "qa_report.json")
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        os.replace(tmp, path)

    def analizar(self, lista_paquetes=None):
        if not os.path.isdir(self.salida):
            print(f"[QA] Salida no existe: {self.salida}")
            return

        log_path = os.path.join(self.salida, "actividad_qa.log")
        self._log_fp = open(log_path, "w", encoding="utf-8")

        entries = self._load_index()
        if not entries:
            self._log("No hay entradas en index.txt")
            self._log_fp.close()
            self._log_fp = None
            return

        groups = self._group_by_package(entries)

        if lista_paquetes:
            groups = {p: groups.get(p, []) for p in lista_paquetes if p in groups}

        done = {p for p in groups if p in self._done_packages(self._load_report(p))}
        pending = {p: imgs for p, imgs in groups.items() if p not in done}
        if not pending:
            self._log("Todos los paquetes ya tienen QA. Nada que hacer.")
            self._log_fp.close()
            self._log_fp = None
            return

        self._log(f"Paquetes pendientes: {list(pending.keys())}")

        # Inicializar motores
        self._log("Cargando motor OCR (PaddleOCR)...")
        t0 = time.time()
        self._ocr = DeepBlueOCR()
        self._ocr._build()
        self._log(f"OCR listo ({time.time() - t0:.1f}s)")

        self._log("Iniciando servidor BlueCode...")
        t0 = time.time()
        self._acp = BlueCodeACP()
        self._acp.start()
        self._session = self._acp.session_create()
        self._log(f"BlueCode listo, sesion {self._session[:8]}... ({time.time() - t0:.1f}s)")

        try:
            for pkg, imgs in pending.items():
                self._log(f"--- {pkg} ({len(imgs)} imagenes) ---")
                report = self._load_report(pkg)
                pkg_results = []
                pkg_ok = True

                for rel_path in imgs:
                    abs_path = os.path.join(self.salida, rel_path)
                    if not os.path.exists(abs_path):
                        self._log(f"  [SKIP] {rel_path} (no existe)")
                        continue

                    entry = None

                    self._log(f"  OCR: {rel_path}")
                    t_ext = time.time()
                    try:
                        with _silent_ocr():
                            ocr_result = self._ocr.predict(abs_path)
                    except Exception as e:
                        self._log(f"  [ERROR OCR] {rel_path}: {e}")
                        pkg_ok = False
                        entry = {
                            "imagen": rel_path,
                            "error": f"OCR: {e}",
                            "ok": False,
                        }
                        pkg_results.append(entry)
                        self._save_report(report, pkg, pkg_results, pkg_ok)
                        continue
                    dt_ext = time.time() - t_ext
                    regions = self._regions_from_ocr(ocr_result)
                    self._log(f"  OCR OK ({len(regions)} regiones, {dt_ext:.1f}s)")

                    if not regions:
                        entry = {
                            "imagen": rel_path,
                            "ok": True,
                            "regiones": 0,
                            "quality": "N/A",
                            "issues": [],
                            "summary": "Sin texto detectado",
                        }
                        pkg_results.append(entry)
                        self._save_report(report, pkg, pkg_results, pkg_ok)
                        continue

                    self._log(f"  QA: {rel_path}")
                    t_an = time.time()
                    try:
                        result = self._acp.analyze_multi_pass(
                            self._session, regions, passes=_cfg.QA_PASSES)
                    except Exception as e:
                        self._log(f"  [ERROR QA] {rel_path}: {e}")
                        pkg_ok = False
                        entry = {
                            "imagen": rel_path,
                            "ok": False,
                            "error": f"QA: {e}",
                        }
                        pkg_results.append(entry)
                        self._save_report(report, pkg, pkg_results, pkg_ok)
                        continue
                    dt_an = time.time() - t_an
                    if "error" in result:
                        self._log(f"  [ERROR QA] {rel_path}: {result['error']}")
                        pkg_ok = False
                        entry = {
                            "imagen": rel_path,
                            "ok": False,
                            "error": result["error"],
                        }
                        pkg_results.append(entry)
                        self._save_report(report, pkg, pkg_results, pkg_ok)
                        continue
                    self._log(f"  QA OK ({len(result.get('issues', []))} defectos, {dt_an:.1f}s)")

                    ocr_texts = [r["text"] for r in regions if r.get("text")]

                    entry = {
                        "imagen": rel_path,
                        "ok": True,
                        "regiones": len(regions),
                        "quality": result.get("overall_quality", "N/A"),
                        "issues": result.get("issues", []),
                        "ocr_warnings": result.get("ocr_warnings", []),
                        "qa_passes": result.get("qa_passes", 1),
                        "qa_pass_counts": result.get("qa_pass_counts", []),
                        "summary": result.get("summary", "N/A"),
                        "tiempo_ocr": round(dt_ext, 2),
                        "tiempo_qa": round(dt_an, 2),
                        "ocr_texts": ocr_texts,
                    }
                    pkg_results.append(entry)
                    self._save_report(report, pkg, pkg_results, pkg_ok)

                    try:
                        from Customlib.sgna_graph import generate_graph
                        generate_graph(self.salida)
                    except Exception:
                        pass

                self._log(f"  Paquete {pkg} completado ({len(pkg_results)} imagenes)")

        finally:
            self._log("Liberando motores...")
            try:
                self._ocr.release()
            except Exception:
                pass
            try:
                self._acp.stop()
            except Exception:
                pass
            self._log_fp.close()
            self._log_fp = None
