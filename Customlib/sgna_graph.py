
import json
import os
import re
import unicodedata
import xml.etree.ElementTree as ET
import html as html_mod
import shutil
import time
import base64


def _esc(val):
    return html_mod.escape(str(val), quote=True)


def _img_to_data_uri(abs_path, max_width=400):
    try:
        from PIL import Image
        import io
        img = Image.open(abs_path)
        if img.width > max_width:
            ratio = max_width / img.width
            img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
        buf = io.BytesIO()
        fmt = "JPEG"
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        img.save(buf, format=fmt, quality=85)
        data = base64.b64encode(buf.getvalue()).decode('ascii')
        return 'data:image/jpeg;base64,' + data
    except Exception:
        try:
            with open(abs_path, 'rb') as f:
                data = base64.b64encode(f.read()).decode('ascii')
            return 'data:image/png;base64,' + data
        except Exception:
            return None


def _load_json(path):
    if not os.path.isfile(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


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


def _load_strings_from_folder(pkg_path, folder):
    strings_file = os.path.join(pkg_path, folder, "strings.xml")
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


def _match_one(obs, meaningful_static, static_norm_map, template_strings):
    if obs in meaningful_static:
        return obs, "exact"
    obs_norm = _normalize_text(obs)
    if obs_norm in static_norm_map:
        return static_norm_map[obs_norm], "normalized"
    for tmpl in template_strings:
        if _is_template_match(obs, tmpl):
            return tmpl, "template"
    return None, None


def _compute_pkg_coverage(salida, pkg, ocr_by_screen):
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

    all_observed = set()
    all_matched_statics = set()
    all_observed_matched = set()
    matched_records = []
    per_screen = {}
    per_source = {"ocr": {"observed": 0, "matched": 0}}

    for screen_id, texts in ocr_by_screen.items():
        screen_observed = set()
        screen_matched = 0
        for t in texts:
            if not t or not isinstance(t, str):
                continue
            all_observed.add(t)
            screen_observed.add(t)
            per_source["ocr"]["observed"] += 1
            matched_static, method = _match_one(t, meaningful_static, static_norm_map, template_strings)
            if matched_static:
                all_matched_statics.add(matched_static)
                all_observed_matched.add(t)
                screen_matched += 1
                per_source["ocr"]["matched"] += 1
                matched_records.append({"static": matched_static, "observed": t, "method": method})

        screen_expected = len(meaningful_static)
        screen_cov = round(100 * screen_matched / len(screen_observed)) if screen_observed else 0
        status = "TEXT_COVERED" if screen_matched == len(screen_observed) and screen_matched > 0 else ("PARTIALLY_COVERED" if screen_matched > 0 else "UNCOVERED")
        per_screen[screen_id] = {
            "expected": screen_expected,
            "observed": len(screen_observed),
            "matched": screen_matched,
            "coverage": screen_cov,
            "status": status,
        }

    per_variant = {}
    for variant, vals in variant_labels.items():
        variant_set = {v for v in vals if _is_meaningful_label(v)}
        v_matched = variant_set & all_matched_statics
        v_cov = round(100 * len(v_matched) / len(variant_set)) if variant_set else None
        per_variant[variant] = {
            "static": len(variant_set),
            "matched": len(v_matched),
            "coverage": v_cov,
        }

    total_static = len(meaningful_static)
    metric_a = round(100 * len(all_matched_statics) / total_static) if total_static else None
    metric_b = round(100 * len(all_observed_matched) / len(all_observed)) if all_observed else None

    screen_covs = [ps["coverage"] for ps in per_screen.values() if ps["observed"] > 0]
    metric_c = round(sum(screen_covs) / len(screen_covs)) if screen_covs else None

    matched_list = sorted(all_matched_statics)
    not_observed_list = sorted(meaningful_static - all_matched_statics)
    observed_only_list = sorted(all_observed - all_observed_matched)

    for src in per_source:
        s = per_source[src]
        s["resolution"] = round(100 * s["matched"] / s["observed"]) if s["observed"] else None

    return {
        "static_inventory": total_static,
        "expected": total_static,
        "observed_total": len(all_observed),
        "matched": matched_list,
        "matched_records": matched_records,
        "static_not_observed": not_observed_list,
        "observed_only": observed_only_list,
        "per_variant": per_variant,
        "per_source": per_source,
        "per_screen": per_screen,
        "metrics": {"A": metric_a, "B": metric_b, "C": metric_c},
    }


def _compute_coverage(salida, qa):
    ocr_by_pkg_screen = {}
    for pkg_entry in qa.get("paquetes", []):
        pkg = pkg_entry.get("paquete", "")
        screen_map = {}
        for r in pkg_entry.get("resultados", []):
            img = r.get("imagen", "")
            screen_id = img.rsplit("/", 1)[-1].replace(".png", "") if img else "unknown"
            texts = [t for t in r.get("ocr_texts", []) if t]
            if texts:
                screen_map[screen_id] = texts
        ocr_by_pkg_screen[pkg] = screen_map

    results = {}
    for pkg, screen_map in ocr_by_pkg_screen.items():
        cov = _compute_pkg_coverage(salida, pkg, screen_map)
        if cov:
            results[pkg] = cov
    return results
def generate_graph(salida, pkg):
    salida = os.path.abspath(salida)
    pkg_dir = os.path.join(salida, pkg)
    if not os.path.isdir(pkg_dir):
        return None
    mapa = _load_json(os.path.join(salida, pkg, "maps.json")) or {"paquetes": [], "nodes": {}}
    qa = _load_json(os.path.join(salida, pkg, "qa_report.json")) or {"paquetes": []}

    nodes_data = mapa.get("nodes", {})
    paquetes = mapa.get("paquetes", [])

    vis_nodes = []
    vis_edges = []
    edge_meta = {}
    screen_data = {}
    edge_idx = 0
    actions_log = []
    errors = []

    for pkg_entry in paquetes:
        pkg = pkg_entry.get("paquete", "")
        pkg_nodes = nodes_data.get(pkg, {})
        for node_id, node_info in pkg_nodes.items():
            screenshots = node_info.get("screenshots", [])
            actions = node_info.get("actions", {})

            is_root = node_id == "0"
            depth = node_id.count(".") if not is_root else 0
            label = node_id if len(node_id) <= 20 else "..." + node_id[-17:]

            ss_rel = ""
            if screenshots:
                first = screenshots[0]
                ss_abs = os.path.join(salida, first)
                if os.path.isfile(ss_abs):
                    ss_rel = _img_to_data_uri(ss_abs) or first.replace("\\", "/")

            n = {
                "id": node_id,
                "label": label,
                "level": depth,
                "title": "pkg={} d={} actions={}".format(pkg, depth, len(actions)),
                "color": {
                    "background": "#fff9c4" if is_root else "#e3f2fd",
                    "border": "#f9a825" if is_root else "#1976d2",
                },
                "font": {"size": 13, "bold": is_root, "multi": False},
                "margin": 14,
                "shape": "box",
            }
            vis_nodes.append(n)

            screen_data[node_id] = {
                "depth": depth,
                "node_id": node_id,
                "pkg": pkg,
                "screenshot": ss_rel,
                "screenshots": [],
                "_screenshot_paths": [os.path.join(salida, s) for s in screenshots if os.path.isfile(os.path.join(salida, s))],
                "actions": [
                    {"index": k, "label": a.get("label", ""), "target": a.get("target")}
                    for k, a in actions.items()
                ],
                "qa_results": [],
            }

            for k, a in actions.items():
                target = a.get("target")
                act_label = (a.get("label", "") or "")[:25]
                if target and target in pkg_nodes:
                    eid = "e{}".format(edge_idx)
                    vis_edges.append({
                        "id": eid, "from": node_id, "to": target, "label": act_label,
                        "font": {"size": 11, "color": "#333", "align": "middle", "vadjust": -14, "background": "rgba(255,255,255,0.85)"},
                        "color": {"color": "#4caf50", "opacity": 0.8}, "arrows": "to",
                        "smooth": {"type": "cubicBezier", "roundness": 0.4},
                    })
                    edge_meta[eid] = {"from_id": node_id, "to_id": target, "label": a.get("label", ""), "nav_type": "push", "is_phantom": False}
                    actions_log.append({"iter": k, "action": "tap", "screen": node_id, "target_index": k, "reason": act_label})
                    edge_idx += 1
                elif not target:
                    eid = "e{}".format(edge_idx)
                    phantom_to = "phantom_{}_{}".format(pkg[:10], k)
                    vis_edges.append({
                        "id": eid, "from": node_id, "to": phantom_to, "label": act_label,
                        "font": {"size": 11, "color": "#e91e63", "align": "middle", "vadjust": 14, "background": "rgba(255,255,255,0.85)"},
                        "color": {"color": "#e91e63", "opacity": 0.8}, "arrows": "to",
                        "smooth": {"type": "cubicBezier", "roundness": 0.4}, "dashes": True,
                    })
                    edge_meta[eid] = {"from_id": node_id, "to_id": None, "label": a.get("label", ""), "nav_type": "exit", "is_phantom": True}
                    actions_log.append({"iter": k, "action": "exit", "screen": node_id, "target_index": k, "reason": act_label})
                    edge_idx += 1

    # --- Unexplored children (from nodes/{id}.json clickables) ---
    node_json_dir = os.path.join(salida, pkg, "nodes")
    node_jsons = {}
    if os.path.isdir(node_json_dir):
        for fname in os.listdir(node_json_dir):
            if fname.endswith(".json"):
                nid = fname[:-5]
                nj = _load_json(os.path.join(node_json_dir, fname))
                if nj:
                    node_jsons[nid] = nj

    unexplored_count = 0
    for pkg_entry in paquetes:
        pkg = pkg_entry.get("paquete", "")
        pkg_nodes = nodes_data.get(pkg, {})
        for node_id, node_info in pkg_nodes.items():
            nj = node_jsons.get(node_id, {})
            clickables = nj.get("clickables", [])
            if not clickables:
                continue
            for i, c in enumerate(clickables, 1):
                child_id = "{}.{}".format(node_id, i)
                if child_id in pkg_nodes:
                    continue
                info = c if isinstance(c, dict) else {}
                clabel = (info.get("text") or info.get("contentDescription") or info.get("resourceName") or "")[:30]
                if not clabel:
                    clabel = child_id
                eid = "e{}".format(edge_idx)
                vis_nodes.append({
                    "id": child_id,
                    "label": clabel,
                    "level": node_id.count(".") + 1,
                    "title": "UNEXPLORED: {} (child of {})".format(clabel, node_id),
                    "color": {"background": "#f5f5f5", "border": "#9e9e9e"},
                    "font": {"size": 10, "color": "#757575", "multi": False},
                    "margin": 8,
                    "shape": "box",
                    "borderWidth": 1,
                })
                vis_edges.append({
                    "id": eid,
                    "from": node_id,
                    "to": child_id,
                    "label": clabel[:20],
                    "font": {"size": 9, "color": "#9e9e9e", "align": "middle", "vadjust": 14, "background": "rgba(255,255,255,0.85)"},
                    "color": {"color": "#9e9e9e", "opacity": 0.5},
                    "arrows": "to",
                    "smooth": {"type": "cubicBezier", "roundness": 0.4},
                    "dashes": True,
                    "width": 1,
                })
                edge_meta[eid] = {"from_id": node_id, "to_id": child_id, "label": clabel, "nav_type": "unexplored", "is_phantom": False}
                screen_data[child_id] = {
                    "depth": node_id.count(".") + 1,
                    "node_id": child_id,
                    "pkg": pkg,
                    "screenshot": "",
                    "screenshots": [],
                    "actions": [],
                    "qa_results": [],
                    "unexplored": True,
                    "parent_id": node_id,
                    "class_name": info.get("className", ""),
                    "resource_name": info.get("resourceName", ""),
                }
                edge_idx += 1
                unexplored_count += 1

    known_node_ids = set(sd["node_id"] for sd in screen_data.values())
    for pkg_entry in paquetes:
        pkg = pkg_entry.get("paquete", "")
        ss_dir = os.path.join(salida, pkg, "screenshots")
        if not os.path.isdir(ss_dir):
            continue
        discovered = {}
        for fname in sorted(os.listdir(ss_dir)):
            if not fname.endswith(".png"):
                continue
            m = re.match(r"^([\d.]+?)(?:_\d+)?\.png$", fname)
            if not m:
                continue
            node_id = m.group(1)
            rel = "{}/screenshots/{}".format(pkg, fname)
            discovered.setdefault(node_id, []).append(rel)
        for node_id, shots in discovered.items():
            if node_id in known_node_ids:
                continue
            known_node_ids.add(node_id)
            depth = node_id.count(".") if node_id != "0" else 0
            label = node_id if len(node_id) <= 20 else "..." + node_id[-17:]
            first_abs = os.path.join(salida, shots[0])
            ss_rel = ""
            if os.path.isfile(first_abs):
                ss_rel = _img_to_data_uri(first_abs) or shots[0].replace("\\", "/")
            vis_nodes.append({
                "id": node_id, "label": label, "level": depth,
                "title": "pkg={} d={} (discovered)".format(pkg, depth),
                "color": {"background": "#e8f5e9", "border": "#43a047"},
                "font": {"size": 11, "bold": False, "multi": False},
                "margin": 10,
                "shape": "box",
            })
            screen_data[node_id] = {
                "depth": depth,
                "node_id": node_id,
                "pkg": pkg,
                "screenshot": ss_rel,
                "screenshots": [],
                "_screenshot_paths": [os.path.join(salida, s) for s in shots if os.path.isfile(os.path.join(salida, s))],
                "actions": [],
                "qa_results": [],
            }

    phantom_ids = set()
    for e in vis_edges:
        if "phantom_" in e["to"]:
            phantom_ids.add(e["to"])
    for ph in sorted(phantom_ids):
        vis_nodes.append({
            "id": ph, "label": ph.replace("phantom_", "")[:20], "shape": "box",
            "color": {"background": "#fce4ec", "border": "#e91e63"},
            "font": {"size": 10, "color": "#c62828"}, "margin": 6, "title": "PHANTOM / UNRESOLVED",
        })

    qa_by_image = {}
    for pkg_entry in qa.get("paquetes", []):
        for r in pkg_entry.get("resultados", []):
            img = r.get("imagen", "")
            qa_by_image[img] = r

    screenshot_map = {}
    for node_id, sd in screen_data.items():
        rel_paths = sd.pop("_screenshot_paths", [])
        sd["screenshots"] = []
        for abs_path in rel_paths:
            uri = _img_to_data_uri(abs_path)
            if uri:
                sd["screenshots"].append(uri)
            rel = abs_path.replace("\\", "/")
            if rel.startswith(salida.replace("\\", "/")):
                rel = rel[len(salida.replace("\\", "/")) + 1:]
            screenshot_map[rel] = uri or ""
        for abs_path in rel_paths:
            rel = abs_path.replace("\\", "/")
            if rel.startswith(salida.replace("\\", "/")):
                rel = rel[len(salida.replace("\\", "/")) + 1:]
            r = qa_by_image.get(rel)
            if r:
                sd["qa_results"].append(r)

    total_issues = 0
    total_images_qa = 0
    quality_counts = {"excellent": 0, "good": 0, "acceptable": 0, "poor": 0, "critical": 0}
    total_ocr_regions = 0
    total_ocr_text_extracted = 0
    total_ocr_warnings = 0
    for r in qa_by_image.values():
        total_images_qa += 1
        issues = r.get("issues", []) or []
        total_issues += len(issues)
        q = (r.get("quality") or "").lower()
        if q in quality_counts:
            quality_counts[q] += 1
        total_ocr_regions += r.get("regiones", 0) or 0
        total_ocr_text_extracted += len(r.get("ocr_texts", []) or [])
        total_ocr_warnings += len(r.get("ocr_warnings", []) or [])

    unexplored_node_ids = set(k for k, v in screen_data.items() if v.get("unexplored"))
    total_screens = len([n for n in vis_nodes if "phantom_" not in n.get("id", "") and n.get("id") not in unexplored_node_ids])
    total_screenshots_on_disk = 0
    for pkg_entry in paquetes:
        pkg = pkg_entry.get("paquete", "")
        ss_dir = os.path.join(salida, pkg, "screenshots")
        if os.path.isdir(ss_dir):
            total_screenshots_on_disk += len([f for f in os.listdir(ss_dir) if f.endswith(".png")])
    total_qa_ok = sum(1 for r in qa_by_image.values() if r.get("ok", True))
    capture_rate = round(100 * total_qa_ok / max(1, total_screenshots_on_disk)) if total_screenshots_on_disk > 0 else None
    text_conversion_rate = round(100 * (total_ocr_regions - total_ocr_warnings) / max(1, total_ocr_regions)) if total_ocr_regions > 0 else None

    max_depth = max((n.get("level", 0) for n in vis_nodes if n.get("id") not in unexplored_node_ids), default=0)
    unexplored_edge_ids = set(e["id"] for e in vis_edges if edge_meta.get(e["id"], {}).get("nav_type") == "unexplored")
    real_edges = [e for e in vis_edges if e["id"] not in unexplored_edge_ids]
    n_resolved = sum(1 for e in real_edges if not edge_meta.get(e["id"], {}).get("is_phantom", False))
    n_unresolved = len(real_edges) - n_resolved

    coverage = _compute_coverage(salida, qa)

    coverage_inline = ""
    cap_str = "{}%".format(capture_rate) if capture_rate is not None else "N/A"
    tcr_str = "{}%".format(text_conversion_rate) if text_conversion_rate is not None else "N/A"
    coverage_inline += '<span class="cov-tag"><span class="cov-name">Capture Rate</span> <span class="cov-val">{}</span></span>'.format(cap_str)
    coverage_inline += '<span class="cov-tag"><span class="cov-name">Text Conv.</span> <span class="cov-val">{}</span></span>'.format(tcr_str)

    screens_info = []
    first_pkg_cov = list(coverage.values())[0] if coverage else {}
    per_screen_cov = first_pkg_cov.get("per_screen", {})
    for n in vis_nodes:
        if "phantom_" in n.get("id", ""):
            continue
        if n.get("id") in unexplored_node_ids:
            continue
        sd = screen_data.get(n["id"], {})
        sc = per_screen_cov.get(n["id"], {})
        if not sc:
            for ss in sd.get("screenshots", []):
                screen_key = ss.rsplit("/", 1)[-1].replace(".png", "")
                sc = per_screen_cov.get(screen_key, {})
                if sc:
                    break
        screens_info.append({
            "hash": n["id"][:8], "full_hash": n["id"], "activity": n.get("label", ""),
            "depth": n.get("level", 0),
            "expected": sc.get("expected", 0),
            "matched": sc.get("matched", 0),
            "coverage": sc.get("coverage"),
            "status": sc.get("status", ""),
        })

    actions_rows = ""
    for a in actions_log:
        actions_rows += "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
            a.get("iter", ""), _esc(a.get("action", ""))[:12],
            _esc(a.get("screen", ""))[:8], a.get("target_index", ""),
            _esc(a.get("reason", ""))[:55])

    errors_html = '<div style="color:#999;font-size:12px;padding:20px;text-align:center">No errors recorded.</div>' if not errors else ""
    for err in errors:
        errors_html += '<div class="err-item">{}</div>'.format(_esc(err))

    screen_texts = {}
    for node_id, sd in screen_data.items():
        texts = []
        for qr in sd.get("qa_results", []):
            for t in qr.get("ocr_texts", []):
                if t and t not in texts:
                    texts.append(t)
        if texts:
            screen_texts[node_id] = {"texts": texts, "by_source": {"ocr": len(texts)}}

    ts = time.strftime("%Y-%m-%d %H:%M:%S")

    placeholders = {
        "NODES_JSON": json.dumps(vis_nodes, ensure_ascii=False),
        "EDGES_JSON": json.dumps(vis_edges, ensure_ascii=False),
        "EDGE_META_JSON": json.dumps(edge_meta, ensure_ascii=False),
        "SCREEN_DATA_JSON": json.dumps(screen_data, ensure_ascii=False),
        "QA_JSON": json.dumps(qa, ensure_ascii=False),
        "COVERAGE_JSON": json.dumps(coverage, ensure_ascii=False),
        "SCREEN_TEXTS_JSON": json.dumps(screen_texts, ensure_ascii=False),
        "SCREENS_INFO_JSON": json.dumps(screens_info, ensure_ascii=False),
        "NS": str(total_screens),
        "NE": str(len(vis_edges)),
        "NR": str(n_resolved),
        "NU": str(n_unresolved),
        "NPH": str(len(phantom_ids)),
        "NUNEXP": str(unexplored_count),
        "MAXD": str(max_depth),
        "NQA": str(total_images_qa),
        "NISS": str(total_issues),
        "QEXCELLENT": str(quality_counts["excellent"]),
        "QGOOD": str(quality_counts["good"]),
        "QACCEPTABLE": str(quality_counts["acceptable"]),
        "QPOOR": str(quality_counts["poor"]),
        "QCRITICAL": str(quality_counts["critical"]),
        "NACT": str(len(actions_log)),
        "NEC": str(len(errors)),
        "CAPRATE": str(capture_rate) if capture_rate is not None else "null",
        "TCRRATE": str(text_conversion_rate) if text_conversion_rate is not None else "null",
        "OCREG": str(total_ocr_regions),
        "OCGOOD": str(total_ocr_text_extracted),
        "ACTIONS_ROWS": actions_rows,
        "ERRORS_HTML": errors_html,
        "COVERAGE_INLINE": coverage_inline,
        "SCREENSHOT_MAP_JSON": json.dumps(screenshot_map, ensure_ascii=False),
        "TIMESTAMP": ts,
        "PACKAGE": paquetes[0].get("paquete", "unknown") if paquetes else "unknown",
    }

    html = _build_template(ts)
    for key, val in placeholders.items():
        html = html.replace("__" + key + "__", val)

    html_path = os.path.join(salida, pkg, "graph.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    vis_src = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Tools", "vis-network.min.js")
    if os.path.isfile(vis_src):
        try:
            shutil.copy2(vis_src, os.path.join(salida, pkg, "vis-network.min.js"))
        except Exception:
            pass

    return html_path


def _build_template(ts):
    return r'''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>SNGA - Navigation Graph + QA</title>
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family:'Segoe UI',Roboto,-apple-system,sans-serif; background:#fafafa; color:#333; font-size:13px; }
.header { background:#1a237e; color:#fff; padding:10px 20px; display:flex; align-items:center; justify-content:space-between; }
.header h1 { font-size:16px; font-weight:600; letter-spacing:0.5px; }
.header .meta { font-size:11px; opacity:0.75; margin-top:2px; }
.header .actions { display:flex; gap:6px; align-items:center; }
.header .actions button { background:rgba(255,255,255,0.15); border:1px solid rgba(255,255,255,0.2); color:#fff; padding:5px 12px; border-radius:4px; cursor:pointer; font-size:11px; }
.header .actions button:hover { background:rgba(255,255,255,0.25); }
.toolbar { background:#fff; border-bottom:1px solid #e0e0e0; padding:6px 20px; display:flex; align-items:center; justify-content:space-between; gap:12px; flex-wrap:wrap; }
.toolbar .views { display:flex; gap:4px; }
.toolbar .views button { background:#f5f5f5; border:1px solid #ddd; padding:4px 12px; border-radius:4px; cursor:pointer; font-size:11px; }
.toolbar .views button.active { background:#1a237e; color:#fff; border-color:#1a237e; }
.toolbar .legend-inline { display:flex; gap:8px; font-size:10px; align-items:center; }
.toolbar .legend-inline .dot { width:7px; height:7px; border-radius:50%; display:inline-block; margin-right:2px; }
.toolbar .coverage-inline { display:flex; gap:8px; font-size:10px; align-items:center; flex-wrap:wrap; }
.toolbar .cov-tag { display:inline-flex; align-items:baseline; gap:2px; padding:2px 6px; border-radius:3px; background:#f5f5f7; border:1px solid #e0e0e0; }
.toolbar .cov-tag .cov-name { color:#1a237e; font-weight:600; }
.toolbar .cov-tag .cov-val { color:#333; font-weight:600; }
.toolbar .cov-total { font-size:11px; padding:2px 8px; border-radius:3px; background:#e8eaf6; border:1px solid #c5cae9; }
.toolbar .cov-total .val { font-weight:700; color:#1a237e; }
.footbar { background:#fff; border-top:1px solid #e0e0e0; }
.footbar-stats { display:flex; gap:16px; font-size:11px; align-items:center; padding:8px 20px; flex-wrap:wrap; }
.footbar-stats span b { color:#1a237e; }
.main { display:flex; height:calc(100vh - 120px); }
.graph-area { flex:1; position:relative; border-right:1px solid #e0e0e0; }
#graph { width:100%; height:100%; background:#fff; }
.inspector { width:380px; min-width:320px; background:#fff; overflow-y:auto; padding:14px; border-left:1px solid #e0e0e0; }
.inspector h2 { font-size:13px; color:#1a237e; margin:10px 0 6px; text-transform:uppercase; letter-spacing:0.5px; }
.inspector h2:first-child { margin-top:0; }
.inspector .field { display:flex; justify-content:space-between; padding:3px 0; border-bottom:1px solid #f0f0f0; font-size:12px; }
.inspector .field .key { color:#888; }
.inspector .field .val { font-weight:600; }
.inspector img.screenshot { max-width:100%; border-radius:6px; border:1px solid #ddd; margin:6px 0; display:block; }
.inspector .no-screenshot { font-size:11px; color:#aaa; padding:12px; border:1px dashed #ccc; border-radius:6px; text-align:center; margin:6px 0; }
.inspector .section-title { font-size:11px; font-weight:700; color:#666; text-transform:uppercase; margin:8px 0 4px; }
.inspector .relation-block { background:#f8f9fa; border:1px solid #e0e0e0; border-radius:6px; padding:10px; margin:6px 0; }
.inspector .clickable-table { width:100%; border-collapse:collapse; font-size:11px; }
.inspector .clickable-table th { text-align:left; background:#f5f5f5; padding:4px 6px; border-bottom:1px solid #e0e0e0; }
.inspector .clickable-table td { padding:3px 6px; border-bottom:1px solid #f0f0f0; }
.inspector .clickable-table tr:hover { background:#f9f9f9; }
.inspector .err-item { font-size:11px; color:#c62828; padding:4px 0; border-bottom:1px solid #fce4ec; }
.semantic-tree { font-family:'Consolas','Courier New',monospace; font-size:12px; line-height:1.6; }
.semantic-tree .root-node { font-weight:700; color:#1a237e; }
.semantic-tree .action-node { color:#1976d2; }
.bottom-table { width:100%; border-collapse:collapse; font-size:11px; }
.bottom-table th { text-align:left; background:#f5f5f5; padding:4px 8px; border-bottom:2px solid #ddd; }
.bottom-table td { padding:3px 8px; border-bottom:1px solid #eee; }
.bottom-table tr:hover { background:#f9f9f9; }
.graph-legend { position:absolute; bottom:12px; left:12px; background:rgba(255,255,255,0.95); padding:8px 12px; border-radius:6px; font-size:11px; border:1px solid #ddd; box-shadow:0 1px 4px rgba(0,0,0,0.1); z-index:10; }
.graph-legend .item { display:flex; align-items:center; gap:5px; margin:2px 0; }
.graph-legend .box { width:10px; height:10px; border-radius:2px; border:2px solid; }
.graph-legend .line { width:18px; height:2px; border-radius:2px; }
.tabs { display:flex; gap:0; margin-bottom:8px; border-bottom:2px solid #e0e0e0; flex-wrap:wrap; }
.tabs .tab { padding:6px 14px; cursor:pointer; font-size:12px; border-bottom:2px solid transparent; margin-bottom:-2px; }
.tabs .tab.active { border-bottom-color:#1a237e; color:#1a237e; font-weight:600; }
.tab-content { display:none; }
.tab-content.active { display:block; }
.stats-section { margin:8px 0 14px; }
.stats-section h3 { font-size:12px; color:#1a237e; margin:0 0 6px; text-transform:uppercase; letter-spacing:0.4px; border-bottom:1px solid #e0e0e0; padding-bottom:3px; }
.stats-section h3 .sub { font-size:10px; color:#888; font-weight:400; text-transform:none; float:right; }
.stats-metric { display:flex; justify-content:space-between; padding:4px 0; font-size:12px; border-bottom:1px solid #f5f5f5; }
.stats-metric .key { color:#888; }
.stats-metric .val { font-weight:700; }
.stats-metric .val.good { color:#2e7d32; }
.stats-metric .val.low { color:#c62828; }
.stats-metric .val.mid { color:#f57f17; }
.stats-table { width:100%; border-collapse:collapse; font-size:11px; margin-top:4px; }
.stats-table th { text-align:left; background:#f5f5f5; padding:4px 6px; border-bottom:1px solid #e0e0e0; font-weight:600; color:#555; }
.stats-table td { padding:3px 6px; border-bottom:1px solid #f0f0f0; }
.stats-table tr:hover { background:#f9f9f9; }
.stats-table .num { text-align:right; font-family:monospace; }
.stats-bar { height:6px; border-radius:3px; background:#e0e0e0; overflow:hidden; margin-top:2px; }
.stats-bar .fill { height:100%; border-radius:3px; transition:width 0.3s; }
.stats-bar .fill.green { background:#4caf50; }
.stats-bar .fill.orange { background:#ff9800; }
.stats-bar .fill.red { background:#f44336; }
.variant-row { display:flex; align-items:center; gap:6px; padding:3px 0; border-bottom:1px solid #f5f5f5; font-size:11px; }
.variant-row .vname { min-width:90px; color:#1a237e; font-weight:600; }
.variant-row .vbar { flex:1; height:8px; border-radius:4px; background:#e0e0e0; overflow:hidden; }
.variant-row .vbar .vfill { height:100%; border-radius:4px; background:#1976d2; }
.variant-row .vnum { min-width:60px; text-align:right; font-family:monospace; color:#333; }
/* QA full-screen view */
.view { display:none; }
.view.active { display:block; }
#view-qa { padding:20px; overflow-y:auto; height:calc(100vh - 120px); }
.qa-pkg { margin-bottom:8px; }
.qa-pkg h2 { font-size:16px; color:#1a237e; margin:0 0 6px 0; }
.qa-pkg .qa-pkg-meta { display:flex; gap:12px; font-size:11px; color:#888; margin-bottom:12px; padding-bottom:8px; border-bottom:1px solid #e0e0e0; }
.qa-pkg .qa-pkg-meta span { display:inline-flex; align-items:center; gap:4px; }
.qa-img-card { background:#fff; border:1px solid #e0e0e0; border-radius:10px; margin-bottom:16px; overflow:visible; transition:box-shadow .2s; }
.qa-img-card:hover { box-shadow:0 2px 12px rgba(0,0,0,0.08); }
.qa-img-header { display:flex; align-items:center; justify-content:space-between; padding:10px 16px; background:#f8f9fa; border-bottom:1px solid #e0e0e0; flex-wrap:wrap; gap:8px; }
.qa-img-header .img-name { font-size:12px; font-weight:600; color:#1a237e; word-break:break-all; }
.qa-img-header .img-badges { display:flex; gap:6px; align-items:center; }
.qa-badge { display:inline-block; padding:2px 8px; border-radius:12px; font-size:10px; font-weight:600; text-transform:uppercase; letter-spacing:0.5px; }
.qa-badge.good { background:#e8f5e9; color:#2e7d32; }
.qa-badge.mid { background:#fff8e1; color:#f57f17; }
.qa-badge.low { background:#ffebee; color:#c62828; }
.qa-badge.neutral { background:#e3f2fd; color:#1565c0; }
.qa-img-body { display:flex; gap:0; width:100%; align-items:flex-start; }
.qa-img-screenshot { flex:0 0 200px; padding:12px; }
.qa-img-screenshot img { width:100%; border-radius:6px; border:1px solid #e0e0e0; display:block; }
.qa-img-content { flex:1; padding:12px 16px 12px 0; min-width:0; }
.qa-metrics { display:flex; flex-wrap:wrap; gap:8px; margin-bottom:10px; }
.qa-metric { background:#f5f5f5; border-radius:6px; padding:4px 10px; font-size:11px; display:flex; align-items:center; gap:6px; }
.qa-metric .m-key { color:#888; }
.qa-metric .m-val { font-weight:700; color:#333; }
.qa-metric .m-val.good { color:#2e7d32; }
.qa-metric .m-val.low { color:#c62828; }
.qa-metric .m-val.mid { color:#f57f17; }
.qa-summary-box { font-size:12px; color:#455; margin:8px 0; padding:10px 12px; background:#f8f9fa; border-radius:6px; border-left:3px solid #1976d2; line-height:1.5; }
.qa-section-label { font-size:11px; font-weight:700; color:#555; text-transform:uppercase; letter-spacing:0.5px; margin:12px 0 6px 0; }
.qa-issue-card { background:#fff8e1; border:1px solid #ffe0b2; border-radius:8px; padding:10px 12px; margin:4px 0; }
.qa-issue-card.sev-high { background:#ffebee; border-color:#ffcdd2; }
.qa-issue-card.sev-medium { background:#fff3e0; border-color:#ffe0b2; }
.qa-issue-card.sev-low { background:#e3f2fd; border-color:#bbdefb; }
.qa-issue-card .iss-header { display:flex; align-items:center; gap:8px; margin-bottom:4px; }
.qa-issue-card .iss-sev { font-size:9px; font-weight:700; padding:2px 6px; border-radius:10px; text-transform:uppercase; }
.qa-issue-card .iss-sev.high { background:#c62828; color:#fff; }
.qa-issue-card .iss-sev.medium { background:#f57f17; color:#fff; }
.qa-issue-card .iss-sev.low { background:#1976d2; color:#fff; }
.qa-issue-card .iss-cat { font-size:11px; font-weight:600; color:#333; }
.qa-issue-card .iss-pair { display:flex; gap:12px; margin:4px 0; font-size:11px; }
.qa-issue-card .iss-pair .iss-old { color:#c62828; text-decoration:line-through; }
.qa-issue-card .iss-pair .iss-arrow { color:#999; }
.qa-issue-card .iss-pair .iss-new { color:#2e7d32; font-weight:600; }
.qa-issue-card .iss-explain { font-size:10px; color:#777; line-height:1.4; margin:4px 0; }
.qa-issue-card .iss-meta { display:flex; gap:10px; font-size:9px; color:#aaa; margin-top:4px; }
.qa-ocr-warn-box { background:#fff3e0; border:1px solid #ffe0b2; border-radius:6px; padding:6px 10px; margin:2px 0; font-size:10px; color:#e65100; }
.qa-ocr-texts-box { margin-top:8px; }
.qa-ocr-texts-box summary { cursor:pointer; font-size:10px; color:#1976d2; font-weight:600; }
.qa-ocr-texts-box ul { margin:4px 0 0 16px; font-size:10px; color:#888; }
.qa-ocr-texts-box li { padding:1px 0; }
.qa-err { font-size:12px; color:#c62828; padding:8px; background:#ffebee; border-radius:6px; }
.qa-empty { text-align:center; padding:60px 20px; color:#aaa; }
.qa-empty .qa-empty-icon { font-size:48px; margin-bottom:12px; opacity:0.3; }
.nav-btns { display:flex; gap:4px; }
.nav-btns button { background:#f5f5f5; border:1px solid #ddd; padding:4px 12px; border-radius:4px; cursor:pointer; font-size:11px; }
.nav-btns button.active { background:#1a237e; color:#fff; border-color:#1a237e; }
</style>
<script src="vis-network.min.js"></script>
</head>
<body>
<div class="header">
  <div>
    <h1>SNGA - Navigation Graph + QA</h1>
    <div class="meta">Package: __PACKAGE__ | Generated: __TIMESTAMP__</div>
  </div>
  <div class="actions">
    <button onclick="exportJSON()">Export JSON</button>
  </div>
</div>
<div class="toolbar">
  <div class="views">
    <button class="active" onclick="showView('view-graph',this)">Graph</button>
    <button onclick="showView('view-qa',this)">QA (__NQA__)</button>
  </div>
  <div class="legend-inline">
    <span><span class="dot" style="background:#f9a825"></span>ROOT</span>
    <span><span class="dot" style="background:#1976d2"></span>SCREEN</span>
    <span><span class="dot" style="background:#e91e63"></span>PHANTOM</span>
    <span style="color:#4caf50">PUSH</span>
    <span style="color:#e91e63">EXIT</span>
  </div>
  <div class="coverage-inline">__COVERAGE_INLINE__</div>
</div>

<!-- ===================== GRAPH VIEW ===================== -->
<div class="view active" id="view-graph">
<div class="main">
  <div class="graph-area">
    <div id="graph"></div>
    <div class="graph-legend">
      <div class="item"><div class="box" style="background:#fff9c4;border-color:#f9a825"></div> root</div>
      <div class="item"><div class="box" style="background:#e3f2fd;border-color:#1976d2"></div> screen</div>
      <div class="item"><div class="box" style="background:#fce4ec;border-color:#e91e63"></div> phantom</div>
      <div class="item"><div class="box" style="background:#f5f5f5;border-color:#9e9e9e"></div> unexplored</div>
      <div class="item"><div class="line" style="background:#4caf50"></div> push</div>
      <div class="item"><div class="line" style="background:#e91e63;border-top:2px dashed #e91e63"></div> exit</div>
    </div>
  </div>
  <div class="inspector">
    <div class="tabs">
      <div class="tab active" onclick="switchTab(this,'stats-tab')">Stats</div>
      <div class="tab" onclick="switchTab(this,'screen-tab')">Screen</div>
      <div class="tab" onclick="switchTab(this,'relation-tab')">Relation</div>
      <div class="tab" onclick="switchTab(this,'actions-tab')">Actions (__NACT__)</div>
      <div class="tab" onclick="switchTab(this,'errors-tab')">Errors (__NEC__)</div>
    </div>
    <div class="tab-content active" id="stats-tab">
      <div id="statsInspector"></div>
    </div>
    <div class="tab-content" id="screen-tab">
      <div id="screenInspector"><div style="color:#999;font-size:12px;padding:20px;text-align:center">Click a screen node to inspect.</div></div>
    </div>
    <div class="tab-content" id="relation-tab">
      <div id="relationInspector"><div style="color:#999;font-size:12px;padding:20px;text-align:center">Click an edge to inspect the navigation relation.</div></div>
    </div>
    <div class="tab-content" id="actions-tab">
      <table class="bottom-table" style="margin-top:4px">
        <tr><th>Iter</th><th>Action</th><th>Screen</th><th>Target</th><th>Reason</th></tr>
        __ACTIONS_ROWS__
      </table>
    </div>
    <div class="tab-content" id="errors-tab">
      <div id="errorsInspector">__ERRORS_HTML__</div>
    </div>
  </div>
</div>
</div>

<!-- ===================== QA FULL-SCREEN VIEW ===================== -->
<div class="view" id="view-qa">
  <div id="qaContainer"></div>
</div>

<div class="footbar" id="footbar">
  <div class="footbar-stats">
    <span>Screens: <b>__NS__</b></span>
    <span>Edges: <b>__NE__</b></span>
    <span>Resolved: <b>__NR__</b></span>
    <span>Unresolved: <b>__NU__</b></span>
    <span>Phantoms: <b>__NPH__</b></span>
    <span>Unexplored: <b>__NUNEXP__</b></span>
    <span>Max depth: <b>__MAXD__</b></span>
    <span>QA Images: <b>__NQA__</b></span>
    <span>QA Issues: <b>__NISS__</b></span>
  </div>
</div>
<script>
var nodesData = __NODES_JSON__;
var edgesData = __EDGES_JSON__;
var edgeMeta = __EDGE_META_JSON__;
var screenData = __SCREEN_DATA_JSON__;
var qaReport = __QA_JSON__;
var coverageData = __COVERAGE_JSON__;
var screenTextsData = __SCREEN_TEXTS_JSON__;
var screenshotMap = __SCREENSHOT_MAP_JSON__;
var screensInfoData = __SCREENS_INFO_JSON__;

var nodes = new vis.DataSet(nodesData);
var edges = new vis.DataSet(edgesData);
var network = new vis.Network(document.getElementById('graph'), {nodes:nodes, edges:edges}, {
  layout: { hierarchical: { enabled:false } },
  physics: { enabled:true, barnesHut: { gravitationalConstant: -8000, springConstant: 0.04, springLength: 180, damping: 0.4, avoidOverlap: true } },
  interaction: { hover:true, tooltipDelay:200, zoomView:true, dragNodes:true, dragView:true },
  nodes: { borderWidth:2, shadow:true, shapeProperties:{ useBorderWithImage:true } },
  edges: { width:1.5 }
});

network.on('click', function(params) {
  if (params.nodes.length > 0) {
    showScreenInspector(params.nodes[0]);
    selectTab('screen-tab');
  } else if (params.edges.length > 0) {
    showRelationInspector(params.edges[0]);
    selectTab('relation-tab');
  }
});

network.on('doubleClick', function(params) {
  if (params.nodes.length > 0) {
    var n = nodes.get(params.nodes[0]);
    if (n.image) window.open(n.image, '_blank');
  }
});

function showView(viewId, btn) {
  document.querySelectorAll('.view').forEach(function(v){v.classList.remove('active');});
  document.getElementById(viewId).classList.add('active');
  document.querySelectorAll('.views button').forEach(function(b){b.classList.remove('active');});
  btn.classList.add('active');
  if (viewId === 'view-graph') {
    setTimeout(function(){ network.redraw(); network.fit(); }, 50);
  }
}

function showScreenInspector(nodeId) {
  var s = screenData[nodeId];
  if (!s) {
    document.getElementById('screenInspector').innerHTML = '<div style="color:#999;padding:20px">PHANTOM / UNRESOLVED</div>';
    return;
  }
  if (s.unexplored) {
    var html = '<h2>Unexplored Child</h2>';
    html += '<div class="field"><span class="key">Node</span><span class="val">'+esc(s.node_id)+'</span></div>';
    html += '<div class="field"><span class="key">Parent</span><span class="val">'+esc(s.parent_id)+'</span></div>';
    html += '<div class="field"><span class="key">Depth</span><span class="val">'+s.depth+'</span></div>';
    html += '<div class="field"><span class="key">Package</span><span class="val">'+esc(s.pkg)+'</span></div>';
    if (s.class_name) html += '<div class="field"><span class="key">Class</span><span class="val">'+esc(s.class_name)+'</span></div>';
    if (s.resource_name) html += '<div class="field"><span class="key">Resource</span><span class="val">'+esc(s.resource_name)+'</span></div>';
    html += '<div class="no-screenshot" style="margin-top:10px">Not explored (depth limit reached).<br>No screenshot, no QA data.</div>';
    document.getElementById('screenInspector').innerHTML = html;
    return;
  }
  var ssHtml = s.screenshot ? '<img class="screenshot" src="'+s.screenshot+'">' : '<div class="no-screenshot">No screenshot</div>';
  var clickRows = '';
  s.actions.forEach(function(c) {
    clickRows += '<tr><td>'+c.index+'</td><td>'+esc(c.label).substring(0,30)+'</td><td>'+(c.target||'&#x2014;')+'</td></tr>';
  });
  var treeHtml = '<div class="semantic-tree"><div class="root-node">'+esc(s.node_id)+'</div>';
  if (s.actions.length > 0) {
    treeHtml += '<div style="padding-left:16px">';
    s.actions.forEach(function(c) {
      treeHtml += '<div class="action-node">ACTION: "'+esc(c.label).substring(0,30)+'"</div>';
    });
    treeHtml += '</div>';
  }
  treeHtml += '</div>';
  var html = '<h2>Screen</h2>';
  html += '<div class="field"><span class="key">Node</span><span class="val">'+esc(s.node_id)+'</span></div>';
  html += '<div class="field"><span class="key">Depth</span><span class="val">'+s.depth+'</span></div>';
  html += '<div class="field"><span class="key">Package</span><span class="val">'+esc(s.pkg)+'</span></div>';
  html += '<div class="field"><span class="key">Actions</span><span class="val">'+s.actions.length+'</span></div>';
  html += ssHtml;
  if (s.screenshots.length > 1) {
    html += '<div class="section-title">All Screenshots ('+s.screenshots.length+')</div>';
    s.screenshots.forEach(function(ss) {
      html += '<img class="screenshot" src="'+ss+'">';
    });
  }
  html += '<div class="section-title">Semantic Structure</div>';
  html += treeHtml;
  html += '<div class="section-title">Clickable Elements</div>';
  html += '<table class="clickable-table"><tr><th>#</th><th>Label</th><th>Target</th></tr>'+clickRows+'</table>';
  if (s.qa_results && s.qa_results.length > 0) {
    html += '<div class="section-title">QA Results ('+s.qa_results.length+')</div>';
    s.qa_results.forEach(function(r) {
      html += '<div class="field"><span class="key">'+esc(r.imagen||'')+'</span><span class="val '+(r.quality||'').toLowerCase()+'">'+esc(r.quality||'N/A')+'</span></div>';
    });
  }
  document.getElementById('screenInspector').innerHTML = html;
}

function showRelationInspector(edgeId) {
  var d = edgeMeta[edgeId];
  if (!d) return;
  var html = '<h2>Navigation Relation</h2><div class="relation-block">';
  html += '<div class="field"><span class="key">From</span><span class="val">'+esc(d.from_id)+'</span></div>';
  html += '<div class="field"><span class="key">To</span><span class="val">'+esc(d.to_id||'UNRESOLVED')+'</span></div>';
  html += '<div class="field"><span class="key">Action</span><span class="val">'+esc(d.nav_type).toUpperCase()+'</span></div>';
  html += '<div class="field"><span class="key">Label</span><span class="val">"'+esc(d.label)+'"</span></div>';
  html += '<div class="field"><span class="key">Status</span><span class="val">'+(d.is_phantom?'UNRESOLVED':'OBSERVED')+'</span></div>';
  html += '</div>';
  document.getElementById('relationInspector').innerHTML = html;
}

function selectTab(tabId) {
  document.querySelectorAll('.tab-content').forEach(function(t){t.classList.remove('active');});
  document.querySelectorAll('.tabs .tab').forEach(function(t){t.classList.remove('active');});
  var el = document.getElementById(tabId);
  if (el) el.classList.add('active');
}
function switchTab(btn, tabId) {
  selectTab(tabId);
  document.querySelectorAll('.tabs .tab').forEach(function(t){t.classList.remove('active');});
  btn.classList.add('active');
}

function pctColor(pct) {
  if (pct === null || pct === undefined) return '';
  if (pct >= 50) return 'good';
  if (pct >= 20) return 'mid';
  return 'low';
}
function barColor(pct) {
  if (pct === null || pct === undefined) return 'red';
  if (pct >= 50) return 'green';
  if (pct >= 20) return 'orange';
  return 'red';
}
function fmtPct(v) {
  if (v === null || v === undefined) return 'N/A';
  return v + '%';
}

function buildStatsInspector() {
  var html = '';
  html += '<div class="stats-section">';
  html += '<h3>Tool Metrics <span class="sub">Capture / Text Conversion</span></h3>';
  var capVal = __CAPRATE__;
  var tcrVal = __TCRRATE__;
  html += '<div class="stats-metric"><span class="key">Capture Rate</span><span class="val '+pctColor(capVal)+'">'+fmtPct(capVal)+'</span></div>';
  html += '<div class="stats-bar"><div class="fill '+barColor(capVal)+'" style="width:'+(capVal||0)+'%"></div></div>';
  html += '<div style="font-size:10px;color:#888;margin-bottom:8px">Screenshots successfully analyzed vs total on disk</div>';
  html += '<div class="stats-metric"><span class="key">Text Conversion Rate</span><span class="val '+pctColor(tcrVal)+'">'+fmtPct(tcrVal)+'</span></div>';
  html += '<div class="stats-bar"><div class="fill '+barColor(tcrVal)+'" style="width:'+(tcrVal||0)+'%"></div></div>';
  html += '<div style="font-size:10px;color:#888;margin-bottom:8px">Regions with successful text extraction vs total OCR regions</div>';
  html += '<div class="stats-metric"><span class="key">OCR Regions</span><span class="val">'+__OCREG__+'</span></div>';
  html += '<div class="stats-metric"><span class="key">Texts Extracted</span><span class="val good">'+__OCGOOD__+'</span></div>';
  html += '</div>';
  html += '<div class="stats-section">';
  html += '<h3>Navigation Summary</h3>';
    html += '<div class="stats-metric"><span class="key">Screens</span><span class="val">'+__NS__+'</span></div>';
    html += '<div class="stats-metric"><span class="key">Edges</span><span class="val">'+__NE__+'</span></div>';
    html += '<div class="stats-metric"><span class="key">Resolved</span><span class="val good">'+__NR__+'</span></div>';
    html += '<div class="stats-metric"><span class="key">Unresolved</span><span class="val low">'+__NU__+'</span></div>';
    html += '<div class="stats-metric"><span class="key">Phantoms</span><span class="val low">'+__NPH__+'</span></div>';
    html += '<div class="stats-metric"><span class="key">Max depth</span><span class="val">'+__MAXD__+'</span></div>';
    html += '</div>';
    html += '<div class="stats-section">';
    html += '<h3>QA Summary</h3>';
    html += '<div class="stats-metric"><span class="key">Images analyzed</span><span class="val">'+__NQA__+'</span></div>';
    html += '<div class="stats-metric"><span class="key">Total issues</span><span class="val low">'+__NISS__+'</span></div>';
    html += '<div class="stats-metric"><span class="key">Excellent</span><span class="val good">'+__QEXCELLENT__+'</span></div>';
    html += '<div class="stats-metric"><span class="key">Good</span><span class="val good">'+__QGOOD__+'</span></div>';
    html += '<div class="stats-metric"><span class="key">Acceptable</span><span class="val mid">'+__QACCEPTABLE__+'</span></div>';
    html += '<div class="stats-metric"><span class="key">Poor</span><span class="val low">'+__QPOOR__+'</span></div>';
    html += '<div class="stats-metric"><span class="key">Critical</span><span class="val low">'+__QCRITICAL__+'</span></div>';
    html += '</div>';
    html += '<div class="stats-section">';
    html += '<h3>Screen Summary</h3>';
    html += '<table class="stats-table">';
    html += '<tr><th>Node</th><th>Activity</th><th>D</th></tr>';
    screensInfoData.forEach(function(s) {
      html += '<tr><td style="font-family:monospace">'+esc(s.hash)+'</td><td>'+esc(s.activity.substring(0,18))+'</td><td>'+s.depth+'</td></tr>';
    });
    html += '</table></div>';
    html += '<div class="stats-section">';
    html += '<h3>Screen Texts <span class="sub">from OCR</span></h3>';
    var st = screenTextsData || {};
    var hashes = Object.keys(st).sort();
    if (hashes.length === 0) {
      html += '<div style="color:#999;font-size:11px;padding:8px">No screen_texts data.</div>';
    }
    hashes.forEach(function(h) {
      var d = st[h] || {};
      var texts = d.texts || [];
      html += '<div style="margin:6px 0;padding:6px;border:1px solid #eee;border-radius:4px">';
      html += '<div style="font-family:monospace;font-size:10px;color:#1a237e;margin-bottom:3px">'+esc(h.substring(0,16))+'</div>';
      html += '<div style="font-size:10px;color:#555">Total: '+texts.length+' texts</div>';
      if (texts.length > 0) {
        html += '<details style="margin-top:3px"><summary style="cursor:pointer;font-size:10px;color:#1976d2">Show texts</summary>';
        html += '<ul style="margin:4px 0 0 16px;font-size:10px;color:#666">';
        texts.forEach(function(t) { html += '<li>'+esc(t.substring(0,60))+'</li>'; });
        html += '</ul></details>';
      }
      html += '</div>';
    });
    html += '</div>';
  document.getElementById('statsInspector').innerHTML = html;
}

function buildQAView() {
  var html = '';
  var pkgs = qaReport.paquetes || [];
  if (pkgs.length === 0) {
    html += '<div class="qa-empty"><div class="qa-empty-icon">&#x1F50D;</div>No QA results yet.<br><span style="font-size:11px">Run phoenix to analyze captures.</span></div>';
  }
  pkgs.forEach(function(p) {
    var resultados = p.resultados || [];
    var pkgIssues = 0;
    resultados.forEach(function(r) { pkgIssues += (r.issues||[]).length; });
    html += '<div class="qa-pkg">';
    html += '<h2>'+esc(p.paquete)+'</h2>';
    html += '<div class="qa-pkg-meta">';
    html += '<span>&#x1F4F7; '+(p.total_imagenes||resultados.length)+' images</span>';
    html += '<span class="qa-badge '+(p.qa_ok?'good':'low')+'">QA '+(p.qa_ok?'PASS':'FAIL')+'</span>';
    html += '<span>&#x26A0; '+pkgIssues+' issues</span>';
    html += '</div>';
    resultados.forEach(function(r) {
      var q = (r.quality||'').toLowerCase();
      var qBadge = q==='excellent'?'good':(q==='good'?'good':(q==='critical'?'low':(q==='poor'?'low':'neutral')));
      var issues = r.issues || [];
      var ocrWarns = r.ocr_warnings || [];
      var ocrTexts = r.ocr_texts || [];
      html += '<div class="qa-img-card">';
      html += '<div class="qa-img-header">';
      var shortName = (r.imagen||'').split('/').pop() || '';
      html += '<span class="img-name">'+esc(shortName)+'</span>';
      html += '<div class="img-badges">';
      if (r.quality && r.quality !== 'N/A') html += '<span class="qa-badge '+qBadge+'">'+esc(r.quality)+'</span>';
      html += '<span class="qa-badge neutral">'+(r.regiones||0)+' regions</span>';
      if (issues.length > 0) html += '<span class="qa-badge low">'+issues.length+' issues</span>';
      if (r.qa_passes) html += '<span class="qa-badge neutral">'+r.qa_passes+' passes</span>';
      html += '</div>';
      html += '</div>';
      if (r.ok === false) {
        html += '<div class="qa-err">Error: '+esc(r.error||'')+'</div>';
        html += '</div>';
        return;
      }
      html += '<div class="qa-img-body">';
      var ssUri = screenDataShort(r.imagen);
      if (ssUri) {
        html += '<div class="qa-img-screenshot"><img src="'+ssUri+'" onerror="this.parentElement.style.display=\'none\'"></div>';
      }
      html += '<div class="qa-img-content">';
      html += '<div class="qa-metrics">';
      if (r.tiempo_ocr) html += '<div class="qa-metric"><span class="m-key">OCR</span><span class="m-val">'+r.tiempo_ocr+'s</span></div>';
      if (r.tiempo_qa) html += '<div class="qa-metric"><span class="m-key">QA</span><span class="m-val">'+r.tiempo_qa+'s</span></div>';
      if (r.qa_pass_counts && r.qa_pass_counts.length) html += '<div class="qa-metric"><span class="m-key">Pass counts</span><span class="m-val">['+r.qa_pass_counts.join(', ')+']</span></div>';
      html += '</div>';
      if (r.summary && r.summary !== 'N/A') {
        html += '<div class="qa-summary-box">'+esc(r.summary)+'</div>';
      }
      if (ocrWarns.length > 0) {
        html += '<div class="qa-section-label">OCR Warnings ('+ocrWarns.length+')</div>';
        ocrWarns.forEach(function(w) {
          html += '<div class="qa-ocr-warn-box">';
          if (typeof w === 'object') {
            if (w.region_id !== undefined) html += '<strong>R'+w.region_id+'</strong>: ';
            html += esc(w.text||'')+' &mdash; '+esc(w.note||'');
          } else {
            html += esc(w);
          }
          html += '</div>';
        });
      }
      if (issues.length > 0) {
        html += '<div class="qa-section-label">Defects ('+issues.length+')</div>';
        issues.forEach(function(iss) {
          var sev = (iss.severity||'').toLowerCase();
          html += '<div class="qa-issue-card sev-'+sev+'">';
          html += '<div class="iss-header">';
          html += '<span class="iss-sev '+sev+'">'+esc(iss.severity||'')+'</span>';
          html += '<span class="iss-cat">'+esc(iss.category||'')+'</span>';
          html += '</div>';
          if (iss.text_excerpt || iss.suggestion) {
            html += '<div class="iss-pair">';
            if (iss.text_excerpt) html += '<span class="iss-old">'+esc(iss.text_excerpt)+'</span>';
            if (iss.text_excerpt && iss.suggestion) html += '<span class="iss-arrow">&rarr;</span>';
            if (iss.suggestion) html += '<span class="iss-new">'+esc(iss.suggestion)+'</span>';
            html += '</div>';
          }
          if (iss.explanation_en) html += '<div class="iss-explain">'+esc(iss.explanation_en)+'</div>';
          if (iss.explanation) html += '<details style="margin:2px 0"><summary style="cursor:pointer;font-size:9px;color:#aaa">ES explanation</summary><div class="iss-explain">'+esc(iss.explanation)+'</div></details>';
          html += '<div class="iss-meta">';
          if (iss.confidence) html += '<span>conf: '+esc(iss.confidence)+'</span>';
          if (iss.region_ids) html += '<span>regions: ['+iss.region_ids.join(', ')+']</span>';
          if (iss.bbox) html += '<span>bbox: '+iss.bbox.x+','+iss.bbox.y+' '+iss.bbox.width+'x'+iss.bbox.height+'</span>';
          html += '</div>';
          html += '</div>';
        });
      }
      if (ocrTexts.length > 0) {
        html += '<details class="qa-ocr-texts-box"><summary>OCR Texts ('+ocrTexts.length+')</summary><ul>';
        ocrTexts.forEach(function(t) { html += '<li>'+esc(t)+'</li>'; });
        html += '</ul></details>';
      }
      html += '</div>';
      html += '</div>';
      html += '</div>';
    });
    html += '</div>';
  });
  document.getElementById('qaContainer').innerHTML = html;
}

function screenDataShort(relPath) {
  if (!relPath) return '';
  var p = relPath.replace(/\\\\/g,'/');
  return screenshotMap[p] || '';
}

buildStatsInspector();
buildQAView();

function exportJSON(){var d={timestamp:"__TIMESTAMP__",package:"__PACKAGE__",screens:nodesData,edges:edgesData,qa:qaReport,coverage:coverageData};var b=new Blob([JSON.stringify(d,null,2)],{type:'application/json'});var u=URL.createObjectURL(b);var a=document.createElement('a');a.href=u;a.download='export.json';a.click();URL.revokeObjectURL(u);}
function esc(s){var d=document.createElement('div');d.textContent=s||'';return d.innerHTML;}
</script>
</body>
</html>'''
