window.DOCS_DATA = window.DOCS_DATA || {};
window.DOCS_DATA["metrics"] = `# Metrics Reference

## Primary Metrics

The system produces two tool-performance metrics, computed in
\`sgna_graph.py:595-602\`:

### Capture Rate

| Aspect | Value |
|--------|-------|
| **Definition** | Percentage of screenshots on disk that have QA results |
| **Formula** | \`round(100 * total_qa_ok / max(1, total_screenshots_on_disk))\` |
| **Code** | \`sgna_graph.py:601\` |
| **Numerator** | Count of \`qa_by_image\` entries where \`r.get("ok", True)\` — note default is \`True\` |
| **Denominator** | Count of \`.png\` files in \`{pkg}/screenshots/\` directories |
| **Measures** | Tool execution completeness — did the pipeline process everything it captured? |
| **Does NOT measure** | Localization quality |

### Text Conversion Rate

| Aspect | Value |
|--------|-------|
| **Definition** | Percentage of OCR regions that are not flagged as warnings |
| **Formula** | \`round(100 * (total_ocr_regions - total_ocr_warnings) / max(1, total_ocr_regions))\` |
| **Code** | \`sgna_graph.py:602\` |
| **\`total_ocr_regions\`** | Sum of \`r.get("regiones", 0)\` across all QA entries (sgna_graph.py:588) |
| **\`total_ocr_warnings\`** | Sum of \`len(r.get("ocr_warnings", []) or [])\` across all QA entries (sgna_graph.py:590) |
| **Measures** | Percentage of OCR regions without AI-flagged warnings |
| **Note** | \`ocr_warnings\` are AI-generated warnings about potential OCR noise, not OCR engine errors. The metric name may be misleading — it does not directly measure OCR text extraction success. |
| **Does NOT measure** | Localization quality |

---

## Legacy Metrics (A/B/C)

The static coverage metrics (A/B/C) compare OCR-extracted text against the
static string inventory from the APK's \`values-*\` folders.

| Metric | Definition | Code |
|--------|-----------|------|
| A | Static coverage: % of meaningful baseline strings observed at runtime | \`sgna_graph.py:283\` |
| B | Observation resolution: % of observed texts that match a baseline string | \`sgna_graph.py:284\` |
| C | Average per-screen coverage: mean of per-screen match rates | \`sgna_graph.py:287\` |

### Status

- \`sgna_graph.py:_compute_coverage()\` (line 312) /
  \`_compute_pkg_coverage()\` (line 206) — **CALLED** by
  \`generate_graph()\` at line 610. Results embedded in \`graph.html\`.
- \`sgna_qa.py:compute_coverage()\` (line 170) — **NEVER CALLED** by any
  module. Dead duplicate implementation.

### Important caveat

The baseline comes from \`{pkg}/values*/strings.xml\` folders. The APK
string-extraction stage (\`sgna_extractor.py\`) is **legacy and no longer
part of the pipeline**, so these folders only exist if you ran the extractor
manually. Without them, A/B/C are all \`N/A\` in \`graph.html\`.

**These are not the primary metrics.** They are computed and displayed but
should not be presented as the system's main output.
`;
