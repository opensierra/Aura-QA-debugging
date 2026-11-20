# -*- coding: utf-8 -*-
"""
DeepBlue.config

This module contains global configuration for the DeepBlue project.
"""

from os import path
import os

# Project general information
PROJECT_NAME         = "DeepBlue"
PROJECT_VERSION      = "0.1.0"
PROJECT_AUTHOR       = "Luis Retamozo"
PROJECT_DESCRIPTION  = "Processing OCR system + BlueCode ACP"
BASE_DIR = path.dirname(path.abspath(__file__))
LAST_UPDATED         = "2026-07-03"

# Reglas de localizacion por idioma de ENTRADA.
# Cada idioma tiene su variable; LANGUAGE_RULES es el enlazador global que
# elige la regla activa (la que recibe el modulo consumidor).
# _RULES_LOGIC es la logica de aplicacion vinculante compartida por todos los
# idiomas; se antepone a las reglas del idioma activo y tiene prioridad sobre
# cualquier regla individual en caso de conflicto.
_RULES_LOGIC = (
    "RULE APPLICATION LOGIC (binding; overrides any individual rule below in case of conflict):\n"
    "0. INPUT MODEL: you receive OCR-extracted text regions only (text, bbox, confidence score, ctx flag) - NOT the image. Every judgment must be grounded in the text content of the regions. A defect is reportable only if it is inferable from the text; do not assert visual or layout defects you cannot infer from the text.\n"
    "1. DETERMINISTIC TEST: a rule is violated ONLY if the text objectively deviates from the specified form. Text that matches the specified form is compliant - never flag it. When a rule allows several acceptable forms, text matching ANY one of them is compliant.\n"
    "2. PRIORITY (when one string could violate several rules, report the highest-priority deviation as the primary category):\n"
    "   P1 Script/orthography (wrong script, missing/wrong diacritics, wrong spelling)\n"
    "   P2 Format (currency, numbers, dates, units)\n"
    "   P3 Vocabulary/terminology (wrong word, untranslated text, language mixture)\n"
    "   P4 Register/tone (pronoun choice, formality)\n"
    "3. AMBIGUITY (two distinct cases - do not conflate):\n"
    "   a. Text-level ambiguity (the text itself could be a defect or not): assume the worst case and flag it (zero tolerance).\n"
    "   b. Context-level ambiguity (the judgment needs brand intent, product tone, or information outside the visible text): do NOT flag it. Brand intent is unknowable; treat such strings as intentional.\n"
    "4. NEVER FLAG (carve-outs; they override every rule):\n"
    "   a. Product, feature, brand, or mode names: standalone labels, all-caps tokens, or proper nouns. Even if they look like source-language words, they are intentional names - keep them as-is.\n"
    "   b. OCR noise: regions with ctx=true or a low score. A recognition error is NOT a localization defect - report it in ocr_warnings only, never in issues.\n"
    "   c. Text that already complies with the rules. Do not \"improve\" compliant text.\n"
    "5. SEVERITY BY RULE TYPE:\n"
    "   - P1: high if meaning is altered; medium for spelling only; low for casing/punctuation.\n"
    "   - P2: high if the value becomes ambiguous or wrong; medium if the format deviates but the value is still clear.\n"
    "   - P3: high for untranslated/mistranslated; medium for non-standard term; low for improvement.\n"
    "   - P4: low, unless it badly clashes with the UI context (then medium).\n"
    "6. CONSISTENCY: the same concept must be rendered consistently across all regions. Flag the same concept rendered differently (different word, format, or casing for the same thing) as an Inconsistency.\n"
    "7. ONE DEFECT PER DEVIATION: report each distinct deviation exactly once. Do not split one deviation into several issues, and do not merge distinct deviations into one.\n"
    "8. SUGGESTION: the minimal drop-in correction that makes the text compliant - same scope as the excerpt, in the target language, a real existing form. Never a rewrite.\n\n"
)
RULES_ES_CO = (
    "- Currency: Colombian peso uses \"$\" BEFORE the amount, thousands separated by DOTS, NO decimals for whole pesos (e.g. \"$1.234.567\" or \"$12.900\"). Never US-style \"$1,234.56\". Use \"COP\" only if ambiguity is real.\n"
    "- Numbers/decimals: decimal separator is COMMA, thousands separator is DOT (e.g. \"1.234,56\"). Never \"1,234.56\".\n"
    "- Dates: DD/MM/AAAA or \"d de mes de aaaa\" (e.g. \"12/03/2026\", \"3 de marzo de 2026\"). NEVER MM/DD/YYYY.\n"
    "- Vocabulary (prefer Latin America over other regions): \"celular\" (not \"móvil\"), \"computador\"/\"computadora\" (not \"ordenador\"), \"carro\"/\"automóvil\" (not \"coche\"), \"correo electrónico\"/\"correo\" (not \"e-mail\"), \"aplicación\"/\"app\", \"cédula\" for national ID, \"listo\"/\"bueno\" (not \"vale\"), \"ustedes\" (never \"vosotros\").\n"
    "- Register: Latin American customer-facing UI typically uses formal \"usted\" and polite, clear copy. Flag informal \"tú\" only where it clashes with the product's established tone.\n"
    "- Orthography: strict RAE accentuation and spelling; flag missing accents, wrong casing, double spaces, missing/extra punctuation.\n"
    "- Units: metric system (km, cm, kg, °C); screen specs use \"pulgadas\" or \"GB/MB\".\n"
    "- Untranslated or source-language leakage in UI copy is a defect (see carve-out 4a for intentional names)."
)
RULES_ID_ID = (
    "- Currency: Indonesian rupiah uses \"Rp\" BEFORE the amount, thousands separated by DOTS, NO decimals (e.g. \"Rp1.234.567\"). Never US-style \"Rp1,234,567\". Use \"IDR\" only if ambiguity is real.\n"
    "- Numbers/decimals: decimal separator is COMMA, thousands separator is DOT (e.g. \"1.234,56\"). Never \"1,234.56\".\n"
    "- Dates: DD/MM/YYYY or \"d bulan aaaa\" (e.g. \"12/03/2026\", \"3 Maret 2026\"). NEVER MM/DD/YYYY.\n"
    "- Vocabulary: prefer standard Indonesian (Bahasa Indonesia) over regional or Dutch-derived variants; \"HP\" for phone, \"komputer\" for computer, \"aplikasi\" for app, \"email\" for e-mail.\n"
    "- Register: customer-facing UI uses polite \"Anda\" (formal you); flag informal \"kamu\"/\"lu\" unless the product's tone is casual.\n"
    "- Orthography: strict EYD/PUEBI spelling; flag missing/wrong diacritics, wrong casing, double spaces, missing/extra punctuation.\n"
    "- Units: metric system (km, cm, kg, °C); screen specs use \"inci\" or \"GB/MB\".\n"
    "- Untranslated or source-language leakage in UI copy is a defect (see carve-out 4a for intentional names)."
)
RULES_UR_PK = (
    "- Script: Urdu is written in the Perso-Arabic script, right-to-left (RTL). Flag LTR rendering, broken word order, or missing RTL punctuation.\n"
    "- Currency: Pakistani rupee uses \"Rs\" or \"₨\" BEFORE the amount, thousands separated by COMMAS (e.g. \"Rs 1,234,567\"). Never dot-separated \"Rs 1.234.567\". Use \"PKR\" only if ambiguity is real.\n"
    "- Numbers/decimals: decimal separator is PERIOD, thousands separator is COMMA (e.g. \"1,234,567.89\").\n"
    "- Dates: DD/MM/YYYY or \"d mes aaaa\" (e.g. \"12/03/2026\", \"3 مارچ 2026\"). NEVER MM/DD/YYYY.\n"
    "- Vocabulary: standard Urdu; flag Hindi/Devanagari leakage or English loanwords where a native term exists.\n"
    "- Register: formal \"آپ\" (aap) for customer-facing; flag informal \"تو\" (tu) unless the product's tone is casual.\n"
    "- Orthography: strict Urdu spelling; flag missing/wrong diacritics, double spaces, missing/extra punctuation (Urdu has no letter case).\n"
    "- Units: metric system; screen specs use \"انچ\" (inch) or \"GB/MB\".\n"
    "- Untranslated or source-language leakage in UI copy is a defect (see carve-out 4a for intentional names)."
)
RULES_PT_BR = (
    "- Currency: Brazilian real uses \"R$\" BEFORE the amount, thousands separated by DOTS, decimals by COMMA (e.g. \"R$ 1.234,56\"). Never US-style \"R$1,234.56\". Use \"BRL\" only if ambiguity is real.\n"
    "- Numbers/decimals: decimal separator is COMMA, thousands separator is DOT (e.g. \"1.234,56\"). Never \"1,234.56\".\n"
    "- Dates: DD/MM/YYYY or \"d de mês de aaaa\" (e.g. \"12/03/2026\", \"3 de março de 2026\"). NEVER MM/DD/YYYY.\n"
    "- Vocabulary: prefer Brazilian Portuguese over European Portuguese: \"celular\" (not \"telemóvel\"), \"aplicativo\"/\"app\", \"você\" (not \"tu\") for customer-facing, \"e-mail\".\n"
    "- Register: Brazilian customer-facing UI uses \"você\" (polite) or \"senhor/senhora\" (formal); flag European \"tu\" or register clashes.\n"
    "- Orthography: strict post-1990 orthographic-agreement spelling; flag missing/wrong accents, wrong casing, double spaces, missing/extra punctuation.\n"
    "- Units: metric system (km, cm, kg, °C); screen specs use \"polegadas\" or \"GB/MB\".\n"
    "- Untranslated or source-language leakage in UI copy is a defect (see carve-out 4a for intentional names)."
)
RULES_TH_TH = (
    "- Script: Thai uses the Thai script; words are NOT separated by spaces. Flag inserted spaces, missing tone marks, or wrong vowel placement.\n"
    "- Currency: Thai baht uses \"฿\" or \"บาท\" AFTER the amount, thousands separated by COMMAS (e.g. \"1,234,567 บาท\" or \"฿1,234,567\"). Use \"THB\" only if ambiguity is real.\n"
    "- Numbers/decimals: decimal separator is PERIOD, thousands separator is COMMA (e.g. \"1,234,567.89\").\n"
    "- Dates: DD/MM/YYYY or \"d เดุน aaaa\" (e.g. \"12/03/2026\", \"3 มีนาคม 2026\"). NEVER MM/DD/YYYY.\n"
    "- Vocabulary: standard Central Thai; flag regional dialects or English loanwords where a native term exists.\n"
    "- Register: Thai uses politeness particles (ครับ/ค่ะ) and pronouns that encode relationship; flag missing/wrong particles or register clashes.\n"
    "- Orthography: strict Thai spelling; flag missing/wrong tone marks, wrong vowel placement, double spaces, missing/extra punctuation.\n"
    "- Units: metric system; screen specs use \"นิ้ว\" (inch) or \"GB/MB\".\n"
    "- Untranslated or source-language leakage in UI copy is a defect (see carve-out 4a for intentional names)."
)
RULES_VI_VN = (
    "- Script: Vietnamese uses the Latin alphabet with diacritics (quốc ngữ). Flag missing/wrong diacritics (tone marks, vowel marks).\n"
    "- Currency: Vietnamese dong uses \"₫\" or \"đ\" AFTER the amount, thousands separated by DOTS or SPACES (e.g. \"1.234.567 ₫\" or \"1 234 567 ₫\"). Use \"VND\" only if ambiguity is real.\n"
    "- Numbers/decimals: decimal separator is COMMA, thousands separator is DOT or SPACE (e.g. \"1.234,56\" or \"1 234,56\").\n"
    "- Dates: DD/MM/YYYY or \"d tháng m aaaa\" (e.g. \"12/03/2026\", \"3 tháng 3 năm 2026\"). NEVER MM/DD/YYYY.\n"
    "- Vocabulary: standard Vietnamese; flag English loanwords where a native term exists.\n"
    "- Register: Vietnamese pronouns encode relationship and politeness (bạn, anh, chị, em, quý khách); flag wrong pronoun choice or register clashes.\n"
    "- Orthography: strict quốc ngữ spelling with correct diacritics; flag missing/wrong tone marks, wrong casing, double spaces, missing/extra punctuation.\n"
    "- Units: metric system; screen specs use \"inch\" or \"GB/MB\".\n"
    "- Untranslated or source-language leakage in UI copy is a defect (see carve-out 4a for intentional names)."
)
RULES_EN_US = (
    "- Currency: US dollar uses \"$\" BEFORE the amount, thousands separated by COMMAS, 2 decimals (e.g. \"$1,234.56\" or \"$12,900\"). Never dot-thousands \"1.234,56\" style.\n"
    "- Numbers/decimals: decimal separator is PERIOD, thousands separator is COMMA (e.g. \"1,234.56\"). Never \"1.234,56\".\n"
    "- Dates: MM/DD/YYYY or \"Month d, yyyy\" (e.g. \"03/12/2026\", \"March 12, 2026\"). NEVER DD/MM/YYYY.\n"
    "- Vocabulary: standard American English; flag British spellings/terms where the US form is standard (\"color\" not \"colour\", \"license\" not \"licence\" as noun, \"gray\" not \"grey\").\n"
    "- Register: customer-facing UI uses clear, direct, neutral copy; flag jargon, slang, or register clashes.\n"
    "- Orthography: strict American spelling; flag wrong casing, double spaces, missing/extra punctuation.\n"
    "- Units: US customary system (mi, °F, in, lb); screen specs use \"inch\" or \"GB/MB\".\n"
    "- Untranslated or source-language leakage in UI copy is a defect (see carve-out 4a for intentional names)."
)

# PaddleOCR language setting.
# Check PaddleOCR documentation on https://github.com/PADDLEPADDLE/PADDLEOCR
# Espanol (Latam/Colombia)| es  | Es-CO | RULES_ES_CO
# Indonesio               | id  | Id-ID | RULES_ID_ID
# Urdu (Pakistan)         | ur  | Ur-PK | RULES_UR_PK
# Portugues (Brasil)      | pt  | Pt-BR | RULES_PT_BR
# Tailandes               | th  | Th-TH | RULES_TH_TH
# Vietnamita              | vi  | Vi-VN | RULES_VI_VN
# Ingles (EE.UU.)         | en  | En-US | RULES_EN_US
# NOTA: NO soportado: Bn-BD (Bengali) - PaddleOCR no tiene modelo para ese alfabeto.

# Cada language pair (Source-Target) resuelve su configuracion de idioma.
# SOURCE: modelo OCR + tag de entrada + reglas de localizacion.
# TARGET: idioma del reporte generado.
# Se selecciona por proceso mediante la variable de entorno DEEPBLUE_PAIR
# (la fija phoenix antes de importar este modulo).
_LANGUAGE_MAP = {
    "es": {"lang": "es", "tag": "Es-CO", "rules": RULES_ES_CO},
    "id": {"lang": "id", "tag": "Id-ID", "rules": RULES_ID_ID},
    "ur": {"lang": "ur", "tag": "Ur-PK", "rules": RULES_UR_PK},
    "pt": {"lang": "pt", "tag": "Pt-BR", "rules": RULES_PT_BR},
    "th": {"lang": "th", "tag": "Th-TH", "rules": RULES_TH_TH},
    "vi": {"lang": "vi", "tag": "Vi-VN", "rules": RULES_VI_VN},
    "en": {"lang": "en", "tag": "En-US", "rules": RULES_EN_US},
}
_REPORT_LANG = {
    "es": "Es-CO",
    "id": "Id-ID",
    "ur": "Ur-PK",
    "pt": "Pt-BR",
    "th": "Th-TH",
    "vi": "Vi-VN",
    "en": "En-US",
}

_pair = os.environ.get("DEEPBLUE_PAIR", "Vi-VN").strip()
_src, _sep, _tgt = _pair.partition("-")
_src = _src.lower()
_tgt = _tgt.lower()
if _src not in _LANGUAGE_MAP:
    raise ValueError(f"DEEPBLUE_PAIR source '{_src}' no soportado. Validos: {sorted(_LANGUAGE_MAP)}")
_src_cfg = _LANGUAGE_MAP[_src]

LANGUAGE              = _src_cfg["lang"]   # idioma del modelo de reconocimiento
LANGUAGE_TAG          = _src_cfg["tag"]    # ENTRADA: idioma del texto de UI auditado
LANGUAGE_REPORT       = _REPORT_LANG.get(_tgt, "Es-CO")  # SALIDA: idioma del reporte
LANGUAGE_RULES        = _RULES_LOGIC + _src_cfg["rules"]
DOC_ORIENTATION       = False
DOC_UNWARPING         = False
TEXTLINE_ORIENTATION  = False
CF_LEVEL              = 0.15       # level of confidence for format_ocr funtion (calculated for each text box), see it on ./utilities.py
                                   # if confidence level is less than (1 - CF_LEVEL) it will be dismissed as “orc noise”.

# BlueCode ACP server configuration
BC_HOST         = "127.0.0.1"
BC_PORT         = 0     # 0 means auto-select an available port
BC_TIMEOUT      = 120   # seconds
QA_PASSES       = 1     # number of QA analysis passes; each enriches the previous

# Preprocessing scale factor for OCR: 0.5 == 50% of original size. Lower
# values shrink the image before OCR for speed. Set to 1.0 to disable.
OCR_SCALE       = 0.5

# Falsk GUI server configuracion
FLASK_HOST        = "127.0.0.1"
FLASK_PORT        = 5000
FLASK_DEBUG       = True
FLASK_URL_DEF     = f"http://{FLASK_HOST}:{FLASK_PORT}"


