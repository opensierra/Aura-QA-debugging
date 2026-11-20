window.DOCS_DATA = window.DOCS_DATA || {};
window.DOCS_DATA["quickstart"] = `# Quick Start

## What is FENNIX 2

FENNIX 2 is an automated pipeline that navigates an Android device's UI,
captures screenshots, extracts text via OCR, and performs AI-powered
localization QA on the captured text. It produces a per-package
\`graph.html\` with the navigation tree, QA findings, and tool metrics.

---

## 1. Installation

### Requirements

| Requirement | Details |
|-------------|---------|
| OS | Windows (batch scripts) |
| Internet | Required during setup only (3 downloads) |
| Android device | USB-connected, USB debugging enabled |
| BlueCode | Installed separately, in system PATH |

See the Installation Guide for full setup steps.

---

## 2. Run the Pipeline

\`\`\`
plk.bat phoenix [extOut] [pair] [--qa-only]
\`\`\`

| Argument | Default | Example |
|----------|---------|---------|
| \`extOut\` | \`Test/settings/Vietnamese-Spanish\` | \`Test/settings/Indonesian-English\` |
| \`pair\` | basename of \`extOut\` | \`id-en\` |
| \`--qa-only\` | (flag) | Re-run QA + graphs on existing screenshots, no device needed |

Examples:

\`\`\`
:: Full run (device connected), Indonesian UI → English report
plk.bat phoenix Test/settings/Indonesian-English id-en

:: QA + graphs only, on screenshots already captured
plk.bat phoenix Test/settings/Vietnamese-Spanish vi-es --qa-only
\`\`\`

The pair format is \`{source}-{target}\`:
- **source** = language of the UI being audited (\`es\`, \`id\`, \`ur\`, \`pt\`, \`th\`, \`vi\`)
- **target** = language of the report (same 6 + \`en\`)

---

## 3. What Happens

1. **Listing** — \`adb\` lists installed packages; filters select the target
   package(s) (\`filter_t\` in \`phoenix\`).
2. **Crawl** — uiautomator2 explores the app UI (depth 2), capturing
   screenshots per node/scroll position. Writes \`screenshots.index\`,
   \`maps.json\`, and an initial \`graph.html\` per package.
3. **QA** — PaddleOCR extracts text regions; BlueCode (AI) audits each
   screenshot for localization defects. Writes \`qa_report.json\` per package.
4. **Graphs** — final \`graph.html\` per package with tree + findings + metrics.

---

## 4. Read the Results

Open \`{extOut}/{pkg}/graph.html\` in a browser. It shows:

- **Navigation tree** — every explored screen and transition.
- **QA findings** — per-screen localization defects with suggested fixes.
- **Metrics** — Capture Rate and Text Conversion Rate (tool performance).

The raw data is in \`{extOut}/{pkg}/qa_report.json\`.

---

## 5. Metrics at a Glance

| Metric | Measures |
|--------|----------|
| **Capture Rate** | % of screenshots on disk that have QA results (tool completeness) |
| **Text Conv.** | % of OCR regions without AI-flagged warnings |

- **Note:** \`ocr_warnings\` are AI-generated warnings about potential OCR
  noise, not OCR engine errors. The metric name may be misleading — it does
  not directly measure OCR text extraction success.
- **Does NOT measure:** Localization quality.

Both metrics are displayed in \`graph.html\` after a successful run.
`;
