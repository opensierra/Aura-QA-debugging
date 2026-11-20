window.DOCS_DATA = window.DOCS_DATA || {};
window.DOCS_DATA["configuration"] = `# Configuration Reference

Configuration is done by editing source files directly, plus two CLI
arguments to \`phoenix\` (output dir and language pair). There is no
configuration file.

---

## Execution Parameters (\`phoenix\`)

| Variable | Default | Purpose | Effective? |
|----------|---------|---------|------------|
| \`filter_o\` | \`["/system", "/system_ext", "/product", "/vendor"]\` | Origin filter (APK path prefixes). **Currently unused** — listing uses \`filtrar_por_paquete\`, not \`filtrar_por_origen\`. | NO (dead in current flow) |
| \`filter_t\` | \`["com.android.settings"]\` | Package name filter (substring match). Also the package list in \`--qa-only\` mode. | YES |
| \`filter_e\` | \`["com.android.bbk.lockscreen3"]\` | Packages to exclude (blocks the screen). | YES |
| \`extOut\` | \`"Test/settings/Vietnamese-Spanish"\` | Output directory for all artifacts. Set via \`argv[1]\`. | YES |
| \`pair\` | basename of \`extOut\` | Language pair (e.g. \`id-en\`). Set via \`argv[2]\`, exported as \`DEEPBLUE_PAIR\` before imports. | YES |

---

## Language Pair (\`DEEPBLUE_PAIR\`)

Format: \`{source}-{target}\`, e.g. \`vi-es\`, \`id-en\`, \`ur-pt\`.

- **Source** selects the OCR model, the audited-UI language tag, and the
  localization rules. Valid sources: \`es\`, \`id\`, \`ur\`, \`pt\`, \`th\`, \`vi\`.
  An unsupported source raises \`ValueError\` at import time.
- **Target** selects the report language. Valid targets: the 6 sources plus
  \`en\` (→ \`En-US\`). Unknown targets fall back to \`Es-CO\`.

| Pair source | OCR lang | UI tag (audited) | Rules |
|-------------|----------|------------------|-------|
| \`es\` | \`es\` | \`Es-CO\` | \`RULES_ES_CO\` |
| \`id\` | \`id\` | \`Id-ID\` | \`RULES_ID_ID\` |
| \`ur\` | \`ur\` | \`Ur-PK\` | \`RULES_UR_PK\` |
| \`pt\` | \`pt\` | \`Pt-BR\` | \`RULES_PT_BR\` |
| \`th\` | \`th\` | \`Th-TH\` | \`RULES_TH_TH\` |
| \`vi\` | \`vi\` | \`Vi-VN\` | \`RULES_VI_VN\` |

Default pair when \`DEEPBLUE_PAIR\` is unset: \`Vi-VN\`.

---

## OCR and QA Configuration (\`Customlib/DeepBlue/config.py\`)

| Parameter | Default | Purpose | Effective? |
|-----------|---------|---------|------------|
| \`LANGUAGE\` | per pair | PaddleOCR language model | YES |
| \`LANGUAGE_TAG\` | per pair | UI language tag injected into the QA prompt | YES (core_bluecode) |
| \`LANGUAGE_REPORT\` | per pair | Report language injected into the QA prompt | YES (core_bluecode) |
| \`LANGUAGE_RULES\` | per pair | Localization rules injected into the QA prompt | YES (core_bluecode) |
| \`DOC_ORIENTATION\` | \`False\` | PaddleOCR document orientation classification | YES |
| \`DOC_UNWARPING\` | \`False\` | PaddleOCR document unwarping | YES |
| \`TEXTLINE_ORIENTATION\` | \`False\` | PaddleOCR text line orientation | YES |
| \`CF_LEVEL\` | \`0.15\` | Confidence level for OCR noise flagging | NO (only used by \`format_ocr()\` in utilities.py, which is never called) |
| \`BC_HOST\` | \`"127.0.0.1"\` | BlueCode server hostname | YES |
| \`BC_PORT\` | \`0\` | BlueCode server port. \`0\` = auto-select a free port at startup. | YES |
| \`BC_TIMEOUT\` | \`120\` | HTTP timeout for BlueCode API (seconds) | YES |
| \`QA_PASSES\` | \`1\` | Number of QA analysis passes per screenshot (results are unioned) | YES |
| \`OCR_SCALE\` | \`0.5\` | Preprocessing scale factor | NO — shadowed by \`core_ocr.py:20\` |
| \`FLASK_HOST\` / \`FLASK_PORT\` / \`FLASK_DEBUG\` / \`FLASK_URL_DEF\` | — | Flask GUI server | NO (legacy, no active consumer) |

---

## OCR Scale — Dual Definition

\`OCR_SCALE\` is defined in two places:

1. \`config.py:173\` — value \`0.5\`. Imported by \`sgna_qa.py:14\` into
   \`_OCR_SCALE\` but **never used** (only feeds the dead \`_BBOX_SCALE\`).
2. \`core_ocr.py:20\` — local value \`0.5\`. This is the value the OCR
   engine actually uses.

**To change OCR scale, edit \`core_ocr.py:20\`.** Changing \`config.py\`
has no effect.

---

## Crawler Parameters (\`Customlib/sgna_crawler_config.py\`)

| Parameter | Default | Purpose |
|-----------|---------|---------|
| \`MAX_DEPTH\` | \`2\` | Maximum navigation depth (0 = root only) |
| \`SPEED_FACTOR\` | \`1\` | Latency multiplier for all sleeps |
| \`SIMILARITY_THRESHOLD\` | \`0.85\` | Jaccard similarity: scroll stop + back verification |
| \`GHOST_SIMILARITY_THRESHOLD\` | \`0.95\` | Jaccard similarity for ghost-tap detection (stricter) |
| \`MAX_BACK\` | \`2\` | Back-press retries to return to parent |
| \`MAX_RELAUNCH\` | \`2\` | App relaunches allowed during back recovery |
| \`MAX_SCROLL\` | \`15\` | Max swipes per node |
| \`MARGIN_TOP\` / \`MARGIN_BOTTOM\` | \`0.30\` / \`0.10\` | Tap exclusion margins (fractions of screen) |
| \`MARGIN_LEFT\` / \`MARGIN_RIGHT\` | \`0.20\` / \`0.20\` | Tap exclusion margins |
| \`DURATION\` | \`0.3 * SPEED_FACTOR\` | Swipe duration |
| \`SLEEP_STABLE\` | \`0.7\` | Wait after swipe |
| \`SLEEP_BACK\` | \`0.3\` | Wait after back |
| \`SLEEP_EXIT\` | \`0.1\` | Wait after app_stop |
| \`SLEEP_START\` | \`1.0\` | Wait after app launch |
| \`ROOT_NAME\` | \`"0"\` | Root node id |
| \`ENABLE_CAPTURE\` | \`True\` | Screenshot capture enabled |
| \`SCREENSHOTS_FOLDER\` | \`"Screenshots"\` | **DEAD** — never referenced; actual folder is \`screenshots\` |

The crawler is instantiated as \`Crawler(extOut)\` — \`speed\` defaults to
\`SPEED_FACTOR\`. There is no \`Speedfactor\` variable in \`phoenix\`.

---

## QA Prompt (\`Customlib/DeepBlue/core_bluecode.py\`)

The QA system prompt is the hardcoded string \`_QA_PROMPT\` (line 17). It
instructs the AI to act as a strict, zero-tolerance localization QA auditor.
Placeholders \`{LANGUAGE_TAG}\` (audited UI language) and \`{LANGUAGE_REPORT}\`
(report language) are substituted from the active pair at prompt-build time.
The per-language rule blocks (\`RULES_*\`) are appended under
"MANDATORY localization rules".

---

## Summary of Dead Configuration

| Variable | Why Dead |
|----------|----------|
| \`filter_o\` (phoenix) | Listing uses \`filtrar_por_paquete\`; \`filtrar_por_origen\` is commented out |
| \`config.OCR_SCALE\` | Shadowed by \`core_ocr.py:20\` local copy |
| \`CF_LEVEL\` | Only consumer is \`format_ocr()\` (utilities.py), never called |
| \`_OCR_SCALE\` (sgna_qa) | Read but never used |
| \`_BBOX_SCALE\` (sgna_qa) | Derived from dead \`_OCR_SCALE\`, never used |
| \`SCREENSHOTS_FOLDER\` (crawler_config) | Never referenced; hardcoded \`"screenshots"\` used instead |
| \`FLASK_*\` (4 vars) | No active consumer (legacy GUI) |
| \`QA.index_path\` (sgna_qa:333) | Set to \`index.txt\` but never read; QA reads per-package \`screenshots.index\` |
`;
