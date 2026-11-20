window.DOCS_DATA = window.DOCS_DATA || {};
window.DOCS_DATA["architecture"] = `# Pipeline Architecture

## Entry Point

The pipeline entry point is the \`phoenix\` script (no file extension). It is
executed via:

\`\`\`
plk.bat phoenix [extOut] [pair] [--qa-only]
\`\`\`

Which runs \`python\\python.exe phoenix\` from the distribution folder with
\`Tools/\` prepended to PATH.

\`phoenix\` sets \`DEEPBLUE_PAIR\` from the pair argument **before** importing
any \`Customlib\` module, so \`config.py\` resolves the correct language
configuration for the process.

---

## Module Map

\`\`\`
phoenix
 ├── sgna_log            print patching (timestamps) + crash handler (crash.log)
 ├── sgna_listing        ListadorPaquetesAndroid — adb package listing + filters
 ├── sgna_crawler        Crawler — uiautomator2 UI exploration
 │    └── sgna_crawler_config   all crawler tunables (depth, thresholds, sleeps)
 ├── sgna_qa             QA — OCR + BlueCode analysis
 │    └── DeepBlue/
 │         ├── config.py         language pair resolution, BC/OCR params
 │         ├── core_ocr.py       DeepBlueOCR (PaddleOCR wrapper)
 │         ├── core_bluecode.py  BlueCodeACP (HTTP client) + _QA_PROMPT
 │         └── utilities.py      format_ocr (unused)
 └── sgna_graph          generate_graph — maps.json + qa_report.json → graph.html
\`\`\`

---

## Data Flow

\`\`\`
adb pm list packages ──► flist [(pkg, apk_path)]
                              │
                              ▼
                     Crawler (u2.connect)
                       │  screenshots/*.png
                       │  screenshots.index   (per pkg, atomic, regenerated)
                       │  nodes/*.json
                       │  maps.json           (per pkg, atomic, schema v2)
                       │  .status             (crawl checkpoint)
                       ▼
                     QA (PaddleOCR + BlueCode)
                       │  qa_report.json      (per pkg, atomic, per-image saves)
                       │  actividad_qa.log
                       ▼
                     generate_graph (per pkg)
                       └─► graph.html + vis-network.min.js
\`\`\`

---

## Legacy Modules (not imported by the pipeline)

| Module | Purpose | Status |
|--------|---------|--------|
| \`sgna_extractor.py\` | APK pull + apktool decompile + \`values-*\` copy + \`reporte.json\` | Legacy. Not imported by \`phoenix\`. |
| \`DeepBlue/core_ui.py\` | Flask GUI | Legacy. Not imported by \`phoenix\`. |

---

## Dead Code in Active Modules

| Item | Location | Notes |
|------|----------|-------|
| \`QA.index_path\` | sgna_qa.py:333 | Set to \`index.txt\`, never read. QA reads per-package \`screenshots.index\`. |
| \`_OCR_SCALE\` / \`_BBOX_SCALE\` | sgna_qa.py:14-15 | Computed from \`config.OCR_SCALE\`, never used. |
| \`compute_coverage()\` | sgna_qa.py:170 | Never called. Dead duplicate of the graph's coverage logic. |
| \`generate_graph(self.salida)\` | sgna_qa.py:554 | Missing \`pkg\` argument → \`TypeError\` swallowed by \`except: pass\`. Graph never refreshes during QA. |
| \`format_ocr()\` | utilities.py:9 | Never called. Only consumer of \`CF_LEVEL\`. |
| \`SCREENSHOTS_FOLDER\` | sgna_crawler_config.py:48 | Never referenced. |
| \`config.OCR_SCALE\` | config.py:173 | Shadowed by \`core_ocr.py:20\` local copy. |
| \`FLASK_*\` (4 vars) | config.py:176-179 | No active consumer. |
`;
