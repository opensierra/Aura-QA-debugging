window.DOCS_DATA = window.DOCS_DATA || {};
window.DOCS_DATA["pipeline"] = `# Pipeline Execution Flow

## Invocation

\`\`\`
plk.bat phoenix [extOut] [pair] [--qa-only]
\`\`\`

| Argument | Default | Purpose |
|----------|---------|---------|
| \`extOut\` | \`Test/settings/Vietnamese-Spanish\` | Output directory for all artifacts |
| \`pair\` | basename of \`extOut\` | Language pair, e.g. \`id-en\`, \`vi-es\`. Sets \`DEEPBLUE_PAIR\` before any \`Customlib\` import. |
| \`--qa-only\` | (flag) | Skip listing + crawl. Run QA + graphs on screenshots already on disk. |

\`plk.bat\` runs \`python\\python.exe phoenix\` with \`Tools/\` prepended to PATH.

---

## Causal Chain (full run)

### Step 0: Initialization

\`\`\`
phoenix
  → sets DEEPBLUE_PAIR env var from argv[2] (or basename of extOut)
  → imports sgna_log (patches print with timestamps, installs crash handler → crash.log)
  → imports sgna_listing, sgna_crawler, sgna_graph, sgna_qa
\`\`\`

No graph is generated at startup. No browser is opened.

### Step 1: Package Listing and Filtering

\`\`\`
phoenix
  → creates ListadorPaquetesAndroid (Plis)
    → runs: adb shell pm list packages -f
    → parses output into [(package_name, apk_path), ...]
  → filtrar_por_paquete(filter_t)   # filter_t = ["com.android.settings"]
  → excluir_por_paquete(filter_e, flist)   # filter_e = ["com.android.bbk.lockscreen3"]
  → infodump() + beforefilt() (console summary)
\`\`\`

**Input:** Device connected via ADB.
**Output:** \`flist\` — list of \`(package_name, apk_path)\` tuples.

**Failure path:** If \`adb\` not in PATH → \`sys.exit(1)\`.

### Step 2: UI Crawling

\`\`\`
phoenix
  → creates Crawler(extOut)          # speed=SPEED_FACTOR (default 1)
  → calls crawlear(flist)
    → u2.connect()                   # first available device
    → _preparar_salida()
    → _preparar_entorno():
        - marker: .env_done_{serial} (skips if already done for this device)
        - 8 settings commands: rotation off, animations off,
          stay-on-while-plugged-in, screen timeout max, KEYCODE_WAKEUP
    → _cargar_status()               # reads .status checkpoint file
    → for each (pkg, path) in flist:
        → if pkg in status: skip
        → app_stop(pkg), wait SLEEP_EXIT (0.1s)
        → monkey -p {pkg} -c android.intent.category.LAUNCHER 1
        → if exit_code == 0:
            → _preparar_salida_pkg(pkg)   # creates {pkg}/nodes/ + {pkg}/screenshots/
            → wait SLEEP_START (1.0s)
            → _explorar_nodo(pkg, "0", depth=0)
            → _volcar_index(pkg)          # regenerates {pkg}/screenshots.index (atomic)
            → _volcar_maps(pkg)           # writes {pkg}/maps.json (atomic, schema v2)
            → generate_graph(extOut, pkg) # writes {pkg}/graph.html
        → else: log SKIP with reason
        → _marcar_status(pkg)             # appends pkg to .status
\`\`\`

**Exploration (\`_explorar_nodo\`):**
- Recursive, depth-limited (\`MAX_DEPTH=2\`).
- \`_descubrir_nodo\`: scroll loop (max \`MAX_SCROLL=15\` swipes), deduplicates
  clickables, applies \`filter_blocked\` rules.
- Screenshots named \`{node_id}.png\` or \`{node_id}_{swipe}.png\`.
- For each clickable: \`_intentar_click\` → status:
  \`not_found\` / \`left_package\` / \`broken_state\` / \`ghost\` / \`ok\`.
- Ghost detection: Jaccard similarity ≥ \`GHOST_SIMILARITY_THRESHOLD\` (0.95).
- Back navigation: \`_asegurar_back\` (max \`MAX_BACK=2\` retries,
  \`MAX_RELAUNCH=2\` app relaunches). A relaunch breaks the sibling loop
  but the parent continues.

**Input:** Device via USB, package list.
**Output:** \`{pkg}/screenshots/*.png\`, \`{pkg}/screenshots.index\`,
\`{pkg}/maps.json\`, \`{pkg}/nodes/*.json\`, \`{pkg}/graph.html\`, \`.status\`.

**Failure paths:**
- App won't start (monkey exit_code ≠ 0) → package skipped, marked in \`.status\`.
- \`app_stop\` exception → package marked in \`.status\` (no infinite retry).
- Branch exception → logged, node closed as \`broken_state\`, parent continues.

**Side effects on device (persist after run):**
- Rotation disabled, animation scales set to 0.
- Screen timeout set to 2147483647 ms.
- Stay-on-while-plugged-in set to 3.

**Logging:** Module logger (console only). No \`actividad_crawler.log\` file.

### Step 3: Linguistic QA

\`\`\`
phoenix
  → creates QA(extOut)
  → calls analizar(pkgs)
    → opens actividad_qa.log (truncated each run)
    → _load_index(): reads {pkg}/screenshots.index for every pkg dir
    → _group_by_package()
    → filters to pkgs passed in lista_paquetes (if provided)
    → done = packages with qa_ok=True in their {pkg}/qa_report.json
    → pending = groups - done
    → if no pending: log "Todos los paquetes ya tienen QA" and return
    → DeepBlueOCR() → _build()          # PaddleOCR(lang=LANGUAGE)
    → BlueCodeACP() → start()           # port auto (BC_PORT=0)
    → session_create()
    → for each pending pkg:
        → for each image in index:
            → OCR predict → regions
            → if no regions: entry ok=True, "Sin texto detectado"
            → analyze_multi_pass(session, regions, passes=QA_PASSES)
            → entry with issues, ocr_warnings, summary, timings
            → _save_report()             # atomic write to {pkg}/qa_report.json
            → generate_graph(self.salida)  # BUG: missing pkg arg (see below)
    → finally: release OCR, stop BlueCode, close log
\`\`\`

**Input:** Screenshots on disk + \`screenshots.index\` per package.
**Output:** \`{pkg}/qa_report.json\`, \`actividad_qa.log\`.

**Failure paths:**
- Image file missing → logged \`[SKIP]\`, no entry saved.
- OCR exception → entry \`ok=False\`, \`pkg_ok=False\`, continue.
- QA exception → entry \`ok=False\`, \`pkg_ok=False\`, continue.
- \`qa_report.json\` corrupt → \`_load_report()\` will crash (no try/except).

### Step 4: Final Graphs

\`\`\`
phoenix
  → for pkg in pkgs:
      → generate_graph(extOut, pkg)
        → reads {pkg}/maps.json + {pkg}/qa_report.json
        → computes metrics (capture rate, text conversion rate, A/B/C coverage)
        → writes {pkg}/graph.html + copies vis-network.min.js
\`\`\`

No browser is opened. Open \`graph.html\` manually.

---

## --qa-only Mode

\`\`\`
plk.bat phoenix Test/settings/Vietnamese-Spanish vi-es --qa-only
\`\`\`

Skips Steps 1 and 2 entirely. Uses \`filter_t\` as the package list.
Runs Step 3 (QA) + Step 4 (final graphs) on screenshots already on disk.

---

## Known Bug: Graph Not Regenerated During QA

\`sgna_qa.py:554\` calls \`generate_graph(self.salida)\` with only one argument.
The function signature is \`generate_graph(salida, pkg)\` (two required args).
The resulting \`TypeError\` is swallowed by the surrounding
\`try/except Exception: pass\`.

**Effect:** \`graph.html\` is NOT updated after each QA image. It is only
updated by the crawler (after crawl) and by phoenix (final loop, Step 4).
The per-image graph refresh during QA is silently broken.

---

## Checkpoint / Resume Behavior

| Stage | Checkpoint | Resume logic |
|-------|-----------|--------------|
| Crawl | \`.status\` (one pkg per line) | Packages in \`.status\` are skipped. |
| QA | \`{pkg}/qa_report.json\` (\`qa_ok=True\`) | Packages with \`qa_ok=True\` are skipped. |

To force a full re-run, delete \`.status\` and all \`qa_report.json\` files.
`;
