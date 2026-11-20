window.DOCS_DATA = window.DOCS_DATA || {};
window.DOCS_DATA["troubleshooting"] = `# Troubleshooting

---

## "Error: 'adb' is not installed or not in PATH."

**Cause:** ADB not available. \`plk.bat\` prepends \`Tools/\` to PATH, so this
should not happen when using \`plk.bat\`.

**Check:** Run \`adb devices\` from a plain command prompt.

**Fix:** Reinstall the distribution or add ADB to PATH manually.

---

## Crawler logs "SKIP {pkg}" and skips the package

**Cause:** \`monkey -p {pkg} -c android.intent.category.LAUNCHER 1\` returned
a non-zero exit code. The app may crash on launch, require permissions, or
have no launcher activity.

**Check:** Crawler console output shows the reason (the \`**\` line from
monkey output). Try launching the app manually on the device.

**Fix:** Ensure the target app is installed, doesn't require initial setup
permissions, and has a launcher activity. Some system apps may not be
startable via monkey.

---

## "FileNotFoundError: bluecode is not found in PATH."

**Cause:** BlueCode CLI not installed or not in system PATH. \`plk.bat\` only
adds \`Tools/\` to PATH — it does not include BlueCode's install location.

**Check:** Open a command prompt and run \`bluecode --version\`.

**Fix:** Install BlueCode and ensure it's in the system PATH (not just user
PATH — \`plk.bat\` inherits the system PATH).

---

## QA stage starts but produces "error": "QA pass 1 failed: ..."

**Cause:** BlueCode server started but API call failed. Common causes: server
not ready, timeout (default 120s), or AI model returned unparseable output.

**Check:** Open \`actividad_qa.log\`. Look for the error after
\`"QA: {image}"\`. Check if the BlueCode server process is still running.

**Fix:** Increase \`BC_TIMEOUT\` in \`config.py\` if the model is slow.
Re-run \`plk.bat phoenix\` — the checkpoint system will skip completed
packages.

---

## OCR returns 0 regions for a screenshot

**Cause:** Screenshot is blank, too dark, or OCR model failed to detect text.
Normal for loading/transition screens.

**Check:** Open the screenshot image file and verify it contains visible text.
Check \`qa_report.json\` for the entry with \`"regiones": 0\`.

**Fix:** No fix needed. Entry saved with \`"ok": true\` and
\`"summary": "Sin texto detectado"\`.

---

## Crawler gets stuck in an infinite loop

**Cause:** A clickable element opens a screen that looks different (e.g.,
keyboard appears) but isn't a new navigable screen. Ghost detection may fail
if the keyboard introduces new clickable elements.

**Check:** Crawler console output shows repeated node IDs (e.g.,
\`4.1.0.0\`, \`4.1.0.0.0\`, ...).

**Fix:** Add the problematic element's class or resource-id to the
blacklist rules in \`sgna_crawler_config.py\`. The existing rules for
\`EditText\`, \`search\`, and \`spinner\` were added to address observed cases.

---

## "No device detected" / uiautomator2 connection error

**Cause:** No device connected, or uiautomator2's ATX agent not installed on
the device.

**Check:** Run \`adb devices\`. Ensure the device shows as \`device\`
(not \`unauthorized\` or \`offline\`).

**Fix:** Reconnect the device, re-authorize the RSA key, and run
\`plk.bat -m uiautomator2 init\` (first time only).

---

## qa_report.json is corrupt after interruption

**Cause:** Although \`qa_report.json\` uses atomic writes (tmp +
\`os.replace\`), the checkpoint reader in \`sgna_qa.py:_load_report()\`
(line 348-353) has no try/except. If the file was corrupted by a different
mechanism (e.g., disk error), the pipeline will crash.

**Fix:** Delete the package's \`qa_report.json\` and re-run. QA will
reprocess all images for that package.

---

## graph.html not updating during QA

**Cause:** **Known bug.** \`sgna_qa.py:554\` calls
\`generate_graph(self.salida)\` without the required \`pkg\` argument. The
\`TypeError\` is swallowed by \`try/except Exception: pass\`, so the graph
never refreshes while QA runs.

**Check:** \`graph.html\` timestamp is older than \`qa_report.json\`.

**Fix:** No fix needed for final results — phoenix's final loop
(\`phoenix:77-78\`) regenerates every \`graph.html\` after QA completes.
If you need the graph mid-run, run \`generate_graph\` manually from a
separate script.

---

## A/B/C coverage shows N/A in graph.html

**Cause:** The A/B/C metrics compare OCR text against the APK's static
\`values-*\` string folders. The extractor that produced those folders
(\`sgna_extractor.py\`) is legacy and no longer runs in the pipeline.

**Check:** Look for \`{extOut}/{pkg}/values*/\` folders.

**Fix:** Run the extractor manually if you need A/B/C, or ignore the metric
— it is not a primary output.
`;
