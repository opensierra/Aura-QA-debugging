"""AURA QA - exportacion del reporte QA a Excel.

Genera un libro con 3 hojas (4 si se incluyen capturas):

  Resumen   KPIs + desgloses por severidad / paquete / categoria (todo con formulas)
  Imagenes  una fila por imagen analizada
  Hallazgos una fila por hallazgo (filtrable por severidad, categoria, paquete...)
  Capturas  miniaturas con los hallazgos marcados (opcional)

Las hojas "Imagenes" y "Hallazgos" se enlazan con un ID (IMG-001...), de modo que
los conteos del resumen se recalculan solos si alguien edita la hoja de hallazgos.
"""
import datetime
import io
import json
import os
import re

SEVERITIES = ("high", "medium", "low")

# ---------------------------------------------------------------- textos (i18n)
from .i18n import _lang  # noqa: E402


class _Formula(str):
    """Marca una cadena como formula de Excel (el resto de textos se guardan siempre como texto)."""


def fx(text):
    return _Formula(text)


# ------------------------------------------------------------ lectura de datos
def _iter_reports(project):
    """Rinde (nombre_carpeta, paquete_dict) por cada paquete de cada qa_report.json."""
    for name in sorted(os.listdir(project)):
        pkg_dir = os.path.join(project, name)
        if not os.path.isdir(pkg_dir):
            continue
        report_path = os.path.join(pkg_dir, "qa_report.json")
        if not os.path.isfile(report_path):
            continue
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            continue
        for p in data.get("paquetes", []) or []:
            yield name, p


def _norm_list(v, lower=True):
    if not isinstance(v, (list, tuple)) or not v:
        return None
    return {str(x).lower() if lower else str(x) for x in v}


def normalize_opts(opts):
    o = opts or {}
    return {
        "packages": _norm_list(o.get("packages"), lower=False),
        "severities": _norm_list(o.get("severities")),
        "qualities": _norm_list(o.get("qualities")),
        "only_issues": bool(o.get("onlyWithIssues", False)),
        "include_warns": bool(o.get("includeWarnings", False)),
        "include_shots": bool(o.get("includeScreenshots", False)),
        "thumb": o.get("thumbSize") if o.get("thumbSize") in ("s", "m", "l") else "m",
        "lang": o.get("lang") or "en",
    }


def collect(project, opts):
    """Devuelve la lista de imagenes ya filtradas (misma logica para preview y export)."""
    o = normalize_opts(opts)
    rows = []
    for folder, p in _iter_reports(project):
        pkg_name = p.get("paquete", folder)
        if o["packages"] and pkg_name not in o["packages"]:
            continue
        for r in p.get("resultados", []) or []:
            quality = str(r.get("quality", "N/A") or "N/A")
            if o["qualities"] and quality.lower() not in o["qualities"]:
                continue
            issues = [i for i in (r.get("issues") or []) if isinstance(i, dict)]
            if o["severities"]:
                issues = [i for i in issues if str(i.get("severity", "")).lower() in o["severities"]]
                if not issues:
                    continue
            if o["only_issues"] and not issues:
                continue
            img_rel = r.get("imagen", "") or ""
            rows.append({
                "pkg": pkg_name,
                "img_rel": img_rel,
                "img_name": os.path.basename(img_rel.replace("\\", "/")),
                "ok": bool(r.get("ok", False)),
                "quality": quality,
                "issues": issues,
                "warns": [str(w) for w in (r.get("ocr_warnings") or [])],
                "passes": r.get("qa_passes", 0) or 0,
                "ocr_s": float(r.get("tiempo_ocr", 0) or 0),
                "qa_s": float(r.get("tiempo_qa", 0) or 0),
                "summary": r.get("summary", "") or "",
            })
    return rows


def preview(project, opts):
    rows = collect(project, opts)
    return {
        "ok": True,
        "images": len(rows),
        "issues": sum(len(r["issues"]) for r in rows),
        "warnings": sum(len(r["warns"]) for r in rows),
    }


# --------------------------------------------------------------------- helpers
def safe_filename(name, fallback):
    name = os.path.basename(str(name or "").replace("\\", "/")).strip().strip(".")
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", name)
    if not name:
        name = fallback
    if not name.lower().endswith(".xlsx"):
        name += ".xlsx"
    return name


def _describe_filters(o, L):
    parts = []
    if o["packages"]:
        parts.append("{}: {}".format(L["f_pkg"], ", ".join(sorted(o["packages"]))))
    if o["severities"]:
        parts.append("{}: {}".format(L["f_sev"], ", ".join(s for s in SEVERITIES if s in o["severities"])))
    if o["qualities"]:
        parts.append("{}: {}".format(L["f_q"], ", ".join(sorted(o["qualities"]))))
    if o["only_issues"]:
        parts.append(L["f_only"])
    return "; ".join(parts) if parts else L["n_none"]


# ------------------------------------------------------------------- exportador
def export_xlsx(project, opts, dest, fname):
    """Genera el .xlsx. Devuelve dict {ok, path, images, issues, size} o {ok: False, error, detail}."""
    try:
        from openpyxl import Workbook
        from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE
        from openpyxl.drawing.image import Image as XLImage
        from openpyxl.formatting.rule import CellIsRule, DataBarRule
        from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
        from openpyxl.utils import get_column_letter
        from openpyxl.worksheet.hyperlink import Hyperlink
        from openpyxl.worksheet.properties import PageSetupProperties
        from PIL import Image as PILImage, ImageDraw
    except Exception as e:  # dependencia ausente
        return {"ok": False, "error": "deps", "detail": str(e)}

    o = normalize_opts(opts)
    L = _lang(o["lang"])
    rows = collect(project, opts)
    if not rows:
        return {"ok": False, "error": "no_rows"}

    # ------------------------------------------------------------- estilos
    F = "Arial"
    INK, MUTED, LINE = "1F2933", "6B7785", "D5DBE3"
    BAND, ACCENT, HDR_FILL, TILE = "202020", "4A90E2", "EAF0F8", "F5F7FA"
    soft = {  # (fondo, texto)
        "green": ("DDF3E4", "1E6B34"), "red": ("FBE0E0", "9B2C2C"),
        "amber": ("FCEFD3", "8A5A00"), "blue": ("DCEAFB", "1F4E8C"),
        "gray": ("ECEFF3", "4A5560"),
    }
    f_body = Font(name=F, size=10, color=INK)
    f_bold = Font(name=F, size=10, bold=True, color=INK)
    f_muted = Font(name=F, size=9, color=MUTED)
    f_link = Font(name=F, size=10, color=ACCENT, underline="single")
    f_hdr = Font(name=F, size=10, bold=True, color=INK)
    fill_band = PatternFill("solid", fgColor=BAND)
    fill_hdr = PatternFill("solid", fgColor=HDR_FILL)
    fill_tile = PatternFill("solid", fgColor=TILE)
    thin = Side(style="thin", color=LINE)
    b_all = Border(left=thin, right=thin, top=thin, bottom=thin)
    b_hdr = Border(left=thin, right=thin, top=thin, bottom=Side(style="medium", color=ACCENT))
    a_center = Alignment(horizontal="center", vertical="top")
    a_left = Alignment(horizontal="left", vertical="top")
    a_wrap = Alignment(horizontal="left", vertical="top", wrap_text=True)
    a_mid_center = Alignment(horizontal="center", vertical="center")

    def cf_fill(key):
        bg, fg = soft[key]
        return PatternFill(start_color=bg, end_color=bg, fill_type="solid"), Font(name=F, bold=True, color=fg)

    def put(ws, row, col, value, font=f_body, align=a_left, border=b_all, fmt=None):
        """Escribe un valor de forma segura: sin caracteres ilegales y sin que
        un texto que empiece por '=' (frecuente en OCR) se interprete como formula."""
        cell = ws.cell(row=row, column=col)
        if isinstance(value, _Formula):
            cell.value = str(value)
        elif isinstance(value, str):
            value = ILLEGAL_CHARACTERS_RE.sub("", value)[:32000]
            cell.value = value
            if value.startswith("="):
                cell.data_type = "s"
        else:
            cell.value = value
        cell.font = font
        cell.alignment = align
        if border is not None:
            cell.border = border
        if fmt:
            cell.number_format = fmt
        return cell

    def title_band(ws, last_col, subtitle):
        ws.sheet_view.showGridLines = False
        ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=last_col)
        ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=last_col)
        for r in (1, 2):
            for c in range(1, last_col + 1):
                ws.cell(row=r, column=c).fill = fill_band
        t = ws.cell(row=1, column=1, value=L["title"])
        t.font = Font(name=F, size=14, bold=True, color="FFFFFF")
        t.alignment = Alignment(horizontal="left", vertical="center", indent=1)
        s = ws.cell(row=2, column=1, value=subtitle)
        s.font = Font(name=F, size=9, color="C4CAD3")
        s.alignment = Alignment(horizontal="left", vertical="center", indent=1)
        ws.row_dimensions[1].height = 28
        ws.row_dimensions[2].height = 18
        ws.row_dimensions[3].height = 8

    def header_row(ws, row, labels, widths):
        for c, (lab, w) in enumerate(zip(labels, widths), 1):
            put(ws, row, c, lab, f_hdr, a_mid_center, b_hdr).fill = fill_hdr
            ws.column_dimensions[get_column_letter(c)].width = w
        ws.row_dimensions[row].height = 22

    def page_setup(ws, title_rows="4:4"):
        ws.page_setup.orientation = "landscape"
        ws.page_setup.fitToWidth = 1
        ws.page_setup.fitToHeight = 0
        ws.sheet_properties.pageSetUpPr = PageSetupProperties(fitToPage=True)
        if title_rows:
            ws.print_title_rows = title_rows

    HDR = 4
    FIRST = HDR + 1
    n_img = len(rows)
    all_issues = []  # (idx_img, id, row_dict, issue)
    for i, r in enumerate(rows, 1):
        r["id"] = "IMG-{:03d}".format(i)
        for k, iss in enumerate(r["issues"], 1):
            all_issues.append((i, r, k, iss))
    n_iss = len(all_issues)

    project_name = os.path.basename(os.path.normpath(project))
    subtitle = "{}   |   {}".format(project_name, datetime.date.today().isoformat())

    # ------------------------------------------------ miniaturas embebidas
    THUMB_W, THUMB_MAX_H = 100, 130
    _thumb_cache = {}

    def thumb_bytes(img_rel):
        """Miniatura JPEG (con caché) como (bytes, ancho, alto); None si no se puede generar."""
        if img_rel in _thumb_cache:
            return _thumb_cache[img_rel]
        res = None
        abs_path = os.path.join(project, img_rel.replace("/", os.sep))
        if os.path.isfile(abs_path):
            try:
                with PILImage.open(abs_path) as im:
                    im = im.convert("RGB")
                    scale = min(THUMB_W / float(im.width), THUMB_MAX_H / float(im.height), 1.0)
                    tw, th = max(1, int(im.width * scale)), max(1, int(im.height * scale))
                    im = im.resize((tw, th), PILImage.LANCZOS)
                    buf = io.BytesIO()
                    im.save(buf, format="JPEG", quality=80, optimize=True)
                    res = (buf.getvalue(), tw, th)
            except Exception:
                res = None
        _thumb_cache[img_rel] = res
        return res

    def embed_thumb(ws, row, col, img_rel):
        """Inserta la miniatura en la celda indicada y devuelve la altura de fila sugerida."""
        t = thumb_bytes(img_rel)
        if not t:
            return None
        data, tw, th = t
        xl = XLImage(io.BytesIO(data))
        xl.width, xl.height = tw, th
        ws.add_image(xl, "{}{}".format(get_column_letter(col), row))
        return th * 0.75 + 6

    wb = Workbook()
    ws_sum = wb.active
    ws_sum.title = L["sheet_summary"]
    ws_img = wb.create_sheet(L["sheet_images"])
    ws_iss = wb.create_sheet(L["sheet_issues"])
    ws_shot = wb.create_sheet(L["sheet_shots"]) if o["include_shots"] else None
    q = lambda ws: "'{}'".format(ws.title.replace("'", "''"))

    # ----------------------------------------------------------- hoja Hallazgos
    iss_cols = [("h_id", 10), ("h_pkg", 26), ("h_img", 18), ("h_thumb", 18), ("h_n", 5), ("h_sev", 12),
                ("h_cat", 20), ("h_conf", 12), ("h_det", 38), ("h_sug", 38), ("h_exp", 64),
                ("h_bbox", 20)]
    IC = {k: i for i, (k, _) in enumerate(iss_cols, 1)}
    title_band(ws_iss, len(iss_cols), subtitle)
    header_row(ws_iss, HDR, [L[k] for k, _ in iss_cols], [w for _, w in iss_cols])
    last_iss = max(FIRST, FIRST + n_iss - 1)
    shot_row = {}  # id -> fila en Capturas
    if ws_shot is not None:
        for i, r in enumerate(rows, 1):
            shot_row[r["id"]] = FIRST + i - 1

    def link_to_shot(ws, cell, img_id):
        if ws_shot is None or img_id not in shot_row:
            return
        ref = "{}!A{}".format(q(ws_shot), shot_row[img_id])
        cell.hyperlink = Hyperlink(ref=cell.coordinate, location=ref, display=str(cell.value))
        cell.font = f_link

    for n, (_, r, k, iss) in enumerate(all_issues):
        row = FIRST + n
        b = iss.get("bbox") or {}
        bbox_txt = ""
        if b.get("width") is not None and b.get("height") is not None:
            bbox_txt = "{}, {}, {}×{}".format(b.get("x", 0), b.get("y", 0), b.get("width"), b.get("height"))
        vals = {
            "h_id": r["id"], "h_pkg": r["pkg"], "h_img": r["img_name"], "h_thumb": "", "h_n": k,
            "h_sev": str(iss.get("severity", "") or "").capitalize(),
            "h_cat": iss.get("category", "") or "",
            "h_conf": str(iss.get("confidence", "") or "").capitalize(),
            "h_det": iss.get("text_excerpt", "") or "",
            "h_sug": iss.get("suggestion", "") or "",
            "h_exp": iss.get("explanation", "") or "",
            "h_bbox": bbox_txt,
        }
        for key, _w in iss_cols:
            align = a_center if key in ("h_id", "h_n", "h_sev", "h_conf") else (
                a_wrap if key in ("h_det", "h_sug", "h_exp", "h_cat") else a_left)
            c = put(ws_iss, row, IC[key], vals[key], f_body, align)
            if key == "h_img":
                link_to_shot(ws_iss, c, r["id"])
        h = embed_thumb(ws_iss, row, IC["h_thumb"], r["img_rel"])
        if h:
            ws_iss.row_dimensions[row].height = max(20, h)
    if n_iss:
        ws_iss.auto_filter.ref = "A{}:{}{}".format(HDR, get_column_letter(len(iss_cols)), last_iss)
    ws_iss.freeze_panes = "D{}".format(FIRST)
    sev_rng = "{0}{1}:{0}{2}".format(get_column_letter(IC["h_sev"]), FIRST, last_iss)
    for word, key in (("High", "red"), ("Medium", "amber"), ("Low", "blue")):
        fl, fo = cf_fill(key)
        ws_iss.conditional_formatting.add(sev_rng, CellIsRule(operator="equal", formula=['"{}"'.format(word)], fill=fl, font=fo))
    page_setup(ws_iss)
    ws_iss.sheet_properties.tabColor = "9AA5B1"

    # ------------------------------------------------------------ hoja Imagenes
    img_cols = [("h_id", 10), ("h_pkg", 26), ("h_img", 18), ("h_thumb", 18), ("h_ok", 10), ("h_q", 12),
                ("h_issues", 11), ("h_high", 8), ("h_med", 9), ("h_low", 8)]
    if o["include_warns"]:
        img_cols.append(("h_warn", 10))
    img_cols += [("h_passes", 11), ("h_ocr", 9), ("h_qa", 9), ("h_summary", 72)]
    MC = {k: i for i, (k, _) in enumerate(img_cols, 1)}
    title_band(ws_img, len(img_cols), subtitle)
    header_row(ws_img, HDR, [L[k] for k, _ in img_cols], [w for _, w in img_cols])
    iss_id_rng = "{}!${}${}:${}${}".format(q(ws_iss), get_column_letter(IC["h_id"]), FIRST, get_column_letter(IC["h_id"]), last_iss)
    iss_sev_rng = "{}!${}${}:${}${}".format(q(ws_iss), get_column_letter(IC["h_sev"]), FIRST, get_column_letter(IC["h_sev"]), last_iss)
    id_col = get_column_letter(MC["h_id"])
    for i, r in enumerate(rows):
        row = FIRST + i
        put(ws_img, row, MC["h_id"], r["id"], f_body, a_center)
        put(ws_img, row, MC["h_pkg"], r["pkg"], f_body, a_left)
        c = put(ws_img, row, MC["h_img"], r["img_name"], f_body, a_left)
        link_to_shot(ws_img, c, r["id"])
        put(ws_img, row, MC["h_ok"], L["ok"] if r["ok"] else L["fail"], f_bold, a_center)
        put(ws_img, row, MC["h_q"], r["quality"].capitalize() if r["quality"].upper() != "N/A" else "N/A", f_body, a_center)
        put(ws_img, row, MC["h_issues"], fx("=COUNTIF({},${}{})".format(iss_id_rng, id_col, row)), f_bold, a_center, fmt="0")
        for key, word in (("h_high", "High"), ("h_med", "Medium"), ("h_low", "Low")):
            put(ws_img, row, MC[key], fx('=COUNTIFS({},${}{},{},"{}")'.format(iss_id_rng, id_col, row, iss_sev_rng, word)), f_body, a_center, fmt="0")
        if o["include_warns"]:
            put(ws_img, row, MC["h_warn"], len(r["warns"]), f_body, a_center, fmt="0")
        put(ws_img, row, MC["h_passes"], r["passes"], f_body, a_center, fmt="0")
        put(ws_img, row, MC["h_ocr"], r["ocr_s"], f_body, a_center, fmt="0.0")
        put(ws_img, row, MC["h_qa"], r["qa_s"], f_body, a_center, fmt="0.0")
        put(ws_img, row, MC["h_summary"], r["summary"], f_body, a_wrap)
        h = embed_thumb(ws_img, row, MC["h_thumb"], r["img_rel"])
        if h:
            ws_img.row_dimensions[row].height = max(20, h)
    last_img = FIRST + n_img - 1
    ws_img.auto_filter.ref = "A{}:{}{}".format(HDR, get_column_letter(len(img_cols)), last_img)
    ws_img.freeze_panes = "D{}".format(FIRST)

    def col_rng(key):
        col = get_column_letter(MC[key])
        return "{}{}:{}{}".format(col, FIRST, col, last_img)

    for word, key in ((L["ok"], "green"), (L["fail"], "red")):
        fl, fo = cf_fill(key)
        ws_img.conditional_formatting.add(col_rng("h_ok"), CellIsRule(operator="equal", formula=['"{}"'.format(word)], fill=fl, font=fo))
    for word, key in (("Excellent", "green"), ("Good", "blue"), ("Poor", "red"), ("N/A", "gray")):
        fl, fo = cf_fill(key)
        ws_img.conditional_formatting.add(col_rng("h_q"), CellIsRule(operator="equal", formula=['"{}"'.format(word)], fill=fl, font=fo))
    fl, fo = cf_fill("green")
    ws_img.conditional_formatting.add(col_rng("h_issues"), CellIsRule(operator="equal", formula=["0"], fill=fl, font=fo))
    fl, fo = cf_fill("amber")
    ws_img.conditional_formatting.add(col_rng("h_issues"), CellIsRule(operator="between", formula=["1", "2"], fill=fl, font=fo))
    fl, fo = cf_fill("red")
    ws_img.conditional_formatting.add(col_rng("h_issues"), CellIsRule(operator="greaterThan", formula=["2"], fill=fl, font=fo))
    zero_font = Font(name=F, color="B0B8C4")
    for key in ("h_high", "h_med", "h_low"):
        ws_img.conditional_formatting.add(col_rng(key), CellIsRule(operator="equal", formula=["0"], font=zero_font))
    ws_img.conditional_formatting.add(col_rng("h_high"), CellIsRule(operator="greaterThan", formula=["0"], font=Font(name=F, bold=True, color=soft["red"][1])))
    page_setup(ws_img)
    ws_img.sheet_properties.tabColor = "9AA5B1"

    # ---------------------------------------------------------- hoja Capturas
    if ws_shot is not None:
        thumb_w = {"s": 110, "m": 160, "l": 240}[o["thumb"]]
        max_h = 540
        shot_cols = [("h_id", 10), ("h_shot", thumb_w / 7.0 + 3), ("h_pkg", 26), ("h_img", 18),
                     ("h_issues", 11), ("h_q", 12)]
        title_band(ws_shot, len(shot_cols), subtitle)
        header_row(ws_shot, HDR, [L[k] for k, _ in shot_cols], [w for _, w in shot_cols])
        sev_color = {"high": "#E05252", "medium": "#E2A04A", "low": "#4A90E2"}
        for i, r in enumerate(rows):
            row = FIRST + i
            put(ws_shot, row, 1, r["id"], f_body, a_center)
            put(ws_shot, row, 2, None, f_body, a_center)
            put(ws_shot, row, 3, r["pkg"], f_body, a_left)
            put(ws_shot, row, 4, r["img_name"], f_body, a_left)
            put(ws_shot, row, 5, fx("=COUNTIF({},$A{})".format(iss_id_rng, row)), f_bold, a_center, fmt="0")
            put(ws_shot, row, 6, r["quality"].capitalize() if r["quality"].upper() != "N/A" else "N/A", f_body, a_center)
            ws_shot.row_dimensions[row].height = 40
            img_abs = os.path.join(project, r["img_rel"].replace("/", os.sep))
            if not os.path.isfile(img_abs):
                continue
            try:
                with PILImage.open(img_abs) as im:
                    im = im.convert("RGB")
                    scale = min(thumb_w / float(im.width), max_h / float(im.height), 1.0)
                    tw, th = max(1, int(im.width * scale)), max(1, int(im.height * scale))
                    im = im.resize((tw, th), PILImage.LANCZOS)
                    draw = ImageDraw.Draw(im)
                    lw = max(1, int(round(tw / 110.0)))
                    for iss in r["issues"]:
                        b = iss.get("bbox") or {}
                        if b.get("width") is None or b.get("height") is None:
                            continue
                        x0, y0 = (b.get("x", 0) or 0) * scale, (b.get("y", 0) or 0) * scale
                        x1, y1 = x0 + b["width"] * scale, y0 + b["height"] * scale
                        col = sev_color.get(str(iss.get("severity", "")).lower(), "#4A90E2")
                        draw.rectangle([x0, y0, x1, y1], outline=col, width=lw)
                    buf = io.BytesIO()
                    im.save(buf, format="JPEG", quality=82, optimize=True)
                    buf.seek(0)
                xl = XLImage(buf)
                xl.width, xl.height = tw, th
                ws_shot.add_image(xl, "B{}".format(row))
                ws_shot.row_dimensions[row].height = max(40, th * 0.75 + 6)
            except Exception:
                continue  # una captura corrupta no debe tumbar todo el export
        ws_shot.freeze_panes = "A{}".format(FIRST)
        page_setup(ws_shot)
        ws_shot.sheet_properties.tabColor = "9AA5B1"

    # ------------------------------------------------------------ hoja Resumen
    widths = [3, 30, 16, 16, 20, 20, 20, 20]
    for i, w in enumerate(widths, 1):
        ws_sum.column_dimensions[get_column_letter(i)].width = w
    title_band(ws_sum, len(widths), subtitle)

    IMG = q(ws_img)
    ISS = q(ws_iss)

    def irng(key):
        col = get_column_letter(MC[key])
        return "{}!${}${}:${}${}".format(IMG, col, FIRST, col, last_img)

    def srng(key):
        col = get_column_letter(IC[key])
        return "{}!${}${}:${}${}".format(ISS, col, FIRST, col, last_iss)

    tiles = [
        (L["k_images"], "=COUNTA({})".format(irng("h_id")), "0"),
        (L["k_issues"], "=COUNTA({})".format(srng("h_id")), "0"),
        (L["k_per_img"], "=IF($B$6=0,0,$C$6/$B$6)", "0.0"),
        (L["k_clean"], '=COUNTIF({},0)'.format(irng("h_issues")), "0"),
    ]
    if o["include_warns"]:
        tiles.append((L["k_warns"], "=SUM({})".format(irng("h_warn")), "0"))
    tiles.append((L["k_time"], "=(SUM({})+SUM({}))/60".format(irng("h_ocr"), irng("h_qa")), "0.0"))
    for i, (lab, formula, fmt) in enumerate(tiles):
        col = 2 + i
        c = ws_sum.cell(row=5, column=col, value=lab)
        c.font = f_muted
        c.fill = fill_tile
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = Border(left=thin, right=thin, top=thin)
        v = ws_sum.cell(row=6, column=col, value=formula)
        v.font = Font(name=F, size=20, bold=True, color=INK)
        v.fill = fill_tile
        v.alignment = a_mid_center
        v.border = Border(left=thin, right=thin, bottom=thin)
        v.number_format = fmt
    ws_sum.row_dimensions[5].height = 30
    ws_sum.row_dimensions[6].height = 38

    def section(ws, row, label):
        c = ws.cell(row=row, column=2, value=label)
        c.font = Font(name=F, size=11, bold=True, color=INK)
        ws.row_dimensions[row].height = 22
        return row + 1

    def table_header(ws, row, labels):
        for i, lab in enumerate(labels):
            put(ws, row, 2 + i, lab, f_hdr, a_left if i == 0 else a_mid_center, b_hdr).fill = fill_hdr
        return row + 1

    databar = lambda: DataBarRule(start_type="num", start_value=0, end_type="max", color="9CC3F0", showValue=True)

    # severidad
    r0 = section(ws_sum, 8, L["by_sev"])
    r0 = table_header(ws_sum, r0, [L["sev"], L["count"], L["share"]])
    sev_first = r0
    for word in ("High", "Medium", "Low"):
        put(ws_sum, r0, 2, word, f_body, a_left)
        put(ws_sum, r0, 3, fx('=COUNTIF({},B{})'.format(srng("h_sev"), r0)), f_body, a_mid_center, fmt="0")
        put(ws_sum, r0, 4, fx("=IF($C$6=0,0,C{}/$C$6)".format(r0)), f_body, a_mid_center, fmt="0.0%")
        r0 += 1
    ws_sum.conditional_formatting.add("C{}:C{}".format(sev_first, r0 - 1), databar())
    for offset, key in enumerate(("red", "amber", "blue")):
        fl, fo = cf_fill(key)
        ws_sum.cell(row=sev_first + offset, column=2).fill = fl
        ws_sum.cell(row=sev_first + offset, column=2).font = fo

    # paquete
    r0 = section(ws_sum, r0 + 1, L["by_pkg"])
    r0 = table_header(ws_sum, r0, [L["pkg"], L["imgs"], L["count"], L["k_per_img"], L["clean"]])
    pkgs = []
    for r in rows:
        if r["pkg"] not in pkgs:
            pkgs.append(r["pkg"])
    pkg_first = r0
    for pkg in pkgs:
        put(ws_sum, r0, 2, pkg, f_body, a_left)
        put(ws_sum, r0, 3, fx("=COUNTIF({},B{})".format(irng("h_pkg"), r0)), f_body, a_mid_center, fmt="0")
        put(ws_sum, r0, 4, fx("=SUMIF({},B{},{})".format(irng("h_pkg"), r0, irng("h_issues"))), f_body, a_mid_center, fmt="0")
        put(ws_sum, r0, 5, fx("=IF(C{0}=0,0,D{0}/C{0})".format(r0)), f_body, a_mid_center, fmt="0.0")
        put(ws_sum, r0, 6, fx("=COUNTIFS({},B{},{},0)".format(irng("h_pkg"), r0, irng("h_issues"))), f_body, a_mid_center, fmt="0")
        r0 += 1
    ws_sum.conditional_formatting.add("D{}:D{}".format(pkg_first, r0 - 1), databar())

    # categoria
    cats = {}
    for _, _r, _k, iss in all_issues:
        cats[iss.get("category", "") or "—"] = cats.get(iss.get("category", "") or "—", 0) + 1
    if cats:
        r0 = section(ws_sum, r0 + 1, L["by_cat"])
        r0 = table_header(ws_sum, r0, [L["cat"], L["count"], L["share"]])
        cat_first = r0
        for cat, _n in sorted(cats.items(), key=lambda kv: (-kv[1], kv[0])):
            put(ws_sum, r0, 2, cat, f_body, a_left)
            put(ws_sum, r0, 3, fx("=COUNTIF({},B{})".format(srng("h_cat"), r0)), f_body, a_mid_center, fmt="0")
            put(ws_sum, r0, 4, fx("=IF($C$6=0,0,C{}/$C$6)".format(r0)), f_body, a_mid_center, fmt="0.0%")
            r0 += 1
        ws_sum.conditional_formatting.add("C{}:C{}".format(cat_first, r0 - 1), databar())

    # notas
    r0 = section(ws_sum, r0 + 1, L["notes"])
    for line in (
        "{}: {}".format(L["n_filters"], _describe_filters(o, L)),
        L["n_live"],
        L["n_ai"],
    ):
        c = ws_sum.cell(row=r0, column=2, value=line)
        c.font = f_muted
        r0 += 1
    ws_sum.sheet_properties.tabColor = ACCENT
    page_setup(ws_sum, title_rows=None)

    # ------------------------------------------------------ metadatos y guardado
    wb.properties.title = L["title"]
    wb.properties.creator = "AURA QA"
    wb.calculation.fullCalcOnLoad = True

    try:
        os.makedirs(dest, exist_ok=True)
    except Exception as e:
        return {"ok": False, "error": "bad_destination", "detail": str(e)}
    out_path = os.path.join(dest, fname)
    tmp_path = out_path + ".tmp"
    try:
        wb.save(tmp_path)
        os.replace(tmp_path, out_path)  # falla limpio si el destino esta abierto en Excel
    except PermissionError as e:
        _silent_remove(tmp_path)
        return {"ok": False, "error": "locked", "detail": str(e), "path": out_path}
    except Exception as e:
        _silent_remove(tmp_path)
        return {"ok": False, "error": "save_failed", "detail": str(e)}
    return {"ok": True, "path": out_path, "images": n_img, "issues": n_iss,
            "size": os.path.getsize(out_path)}


def _silent_remove(path):
    try:
        os.remove(path)
    except OSError:
        pass
