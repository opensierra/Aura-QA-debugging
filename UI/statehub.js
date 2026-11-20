(function () {
  'use strict';

  if (window.__auraStateHub) return;
  window.__auraStateHub = true;

  // ------------------------------------------------------------
  // I18N_DATA corregido (base en/es + fallback seguro para otros)
  // ------------------------------------------------------------
  (function (D) {
    const add = (l, o) => {
      D[l] = Object.assign(D[l] || {}, o);
    };

    const B = (
      idle,
      running,
      done,
      error,
      cancelled,
      noDev,
      unknown,
      errDev,
      connected,
      android,
      toggle
    ) => ({
      'run.status.idle': idle,
      'run.status.running': running,
      'run.status.done': done,
      'run.status.error': error,
      'run.status.cancelled': cancelled,
      'dev.none': noDev,
      'dev.unknown': unknown,
      'dev.error': errDev,
      'dev.connected': connected,
      'dev.android': android,
      'device.os': android,
      'sidebar.toggle': toggle
    });

    const P = (
      folder,
      open,
      output,
      exportDest,
      newProj,
      roots,
      up,
      refresh,
      editPath,
      loading,
      empty,
      denied,
      err,
      noBridge,
      cancel,
      select,
      openBtn,
      create,
      name,
      namePh,
      nameBad,
      willCreate,
      willCreateIn
    ) => ({
      'pk.title.folder': folder,
      'pk.title.open': open,
      'pk.title.output': output,
      'pk.title.export': exportDest,
      'pk.title.new': newProj,
      'pk.roots': roots,
      'pk.up': up,
      'pk.refresh': refresh,
      'pk.editPath': editPath,
      'pk.loading': loading,
      'pk.empty': empty,
      'pk.denied': denied,
      'pk.err': err,
      'pk.noBridge': noBridge,
      'pk.cancel': cancel,
      'pk.select': select,
      'pk.open': openBtn,
      'pk.create': create,
      'pk.name': name,
      'pk.namePh': namePh,
      'pk.nameBad': nameBad,
      'pk.willCreate': willCreate,
      'pk.willCreateIn': willCreateIn
    });

    const J = (
      opened,
      invalid,
      denied,
      empty,
      created,
      verifyFailed,
      createFailed,
      stateQa,
      stateRun,
      needFolder,
      newErr,
      newExists
    ) => ({
      'proj.opened': opened,
      'proj.invalid': invalid,
      'proj.denied': denied,
      'proj.empty': empty,
      'proj.created': created,
      'proj.verifyFailed': verifyFailed,
      'proj.createFailed': createFailed,
      'proj.stateFromQa': stateQa,
      'proj.stateFromRun': stateRun,
      'proj.needFolder': needFolder,
      'new.err': newErr,
      'new.exists': newExists
    });

    add(
      'en',
      Object.assign(
        B(
          'Idle',
          'Running',
          'Done',
          'Error',
          'Cancelled',
          'No device',
          'Unknown',
          'Error',
          'Connected',
          'Android {0}',
          'Toggle sidebar'
        ),
        P(
          'Choose folder',
          'Open project',
          'Output folder',
          'Export destination',
          'New project',
          'Places',
          'Up one level',
          'Refresh',
          'Click to type a path',
          'Loading…',
          'No subfolders here.',
          'You do not have permission to open this folder.',
          'Could not open: {0}',
          'The folder browser only works inside the AURA QA window.',
          'Cancel',
          'Select folder',
          'Open',
          'Create project',
          'Project name',
          'my-project',
          'Enter a valid name (without \\ / : * ? " < > |).',
          'It will be created in: {0}',
          'Type a name to create the project.'
        ),
        J(
          'Project "{0}" is ready.',
          'Not a valid project: {0}',
          'That folder cannot be read. Check permissions.',
          'This project has no packages yet.',
          'Project created in {0}',
          'The folder was created but could not be verified: {0}',
          'The new project folder could not be verified.',
          'Summary rebuilt from the last QA report.',
          'Last run restored from run_state.json.',
          'Select a folder first.',
          "Couldn't create the new project.",
          'A project with that name already exists there.'
        )
      )
    );

    add(
      'es',
      Object.assign(
        B(
          'En reposo',
          'Ejecutando',
          'Completado',
          'Error',
          'Cancelado',
          'Sin dispositivo',
          'Desconocido',
          'Error',
          'Conectado',
          'Android {0}',
          'Alternar menú'
        ),
        P(
          'Elegir carpeta',
          'Abrir proyecto',
          'Carpeta de salida',
          'Destino de la exportación',
          'Nuevo proyecto',
          'Ubicaciones',
          'Subir un nivel',
          'Actualizar',
          'Haz clic para escribir una ruta',
          'Cargando…',
          'No hay subcarpetas aquí.',
          'No tienes permiso para abrir esta carpeta.',
          'No se pudo abrir: {0}',
          'El explorador de carpetas solo funciona dentro de la ventana de AURA QA.',
          'Cancelar',
          'Elegir carpeta',
          'Abrir',
          'Crear proyecto',
          'Nombre del proyecto',
          'mi-proyecto',
          'Introduce un nombre válido (sin \\ / : * ? " < > |).',
          'Se creará en: {0}',
          'Escribe un nombre para crear el proyecto.'
        ),
        J(
          'Proyecto "{0}" listo.',
          'No es un proyecto válido: {0}',
          'Esa carpeta no se puede leer. Revisa los permisos.',
          'Este proyecto todavía no tiene paquetes.',
          'Proyecto creado en {0}',
          'La carpeta se creó pero no se pudo verificar: {0}',
          'No se pudo verificar la carpeta del proyecto nuevo.',
          'Resumen reconstruido desde el último reporte de QA.',
          'Última ejecución restaurada desde run_state.json.',
          'Selecciona una carpeta primero.',
          'No se pudo crear el nuevo proyecto.',
          'Ya existe un proyecto con ese nombre en esa carpeta.'
        )
      )
    );

    // Idiomas restantes: inglés como fallback, traducción nativa encima.
    ['id', 'pt', 'th', 'ur', 'vi', 'zh'].forEach(lang => {
      D[lang] = Object.assign({}, D.en, D[lang] || {});
    });
  })(window.I18N_DATA = window.I18N_DATA || {});

  const T = (k, ...a) => (typeof xt === 'function' ? xt(k, ...a) : k);
  const I = k => {
    try {
      return window.I18N ? I18N.t(k) : k;
    } catch (e) {
      return k;
    }
  };

  const style = document.createElement('style');
  style.textContent = `
    #right-col[data-ctx="test"] { display: flex !important; }
    #right-col[data-ctx="device"] { display: flex !important; }
    #right-col[data-ctx="reports"] { display: flex !important; }
    #right-col[data-ctx="none"] { display: none !important; }
    .right-ctx { display: flex; flex-direction: column; flex: 1 1 auto; min-height: 0; }
    #right-col[data-ctx="test"] #right-export, #right-col[data-ctx="test"] #right-device { display: none !important; }
    #right-col[data-ctx="reports"] #right-run, #right-col[data-ctx="reports"] #right-device { display: none !important; }
    #right-col[data-ctx="device"] #right-export, #right-col[data-ctx="device"] #right-run { display: none !important; }
    #right-run .tel-header { display: none; }

    .run-step-sub { display: none; }
    .run-config .settings-section-title,
    .run-config .settings-group-label,
    .run-config .run-chips-label { text-align: left; }
    .run-stages { justify-content: flex-start; }

    .device-issues.has-issues { color: var(--accent-warn); }

    .badge-status.badge-connected {
      color: var(--accent-green);
      border-color: var(--accent-green);
      background-color: color-mix(in srgb, var(--accent-green) 15%, var(--bg-terminal));
    }

    .device-widget.dw-lost { border-color: var(--accent-danger); }
    .device-widget.dw-lost .device-model,
    .device-widget.dw-lost .device-status-text { color: var(--accent-danger); }

    .device-widget.dw-adberr { border-color: var(--accent-warn); }
    .device-widget.dw-adberr .device-model { color: var(--accent-warn); }

    .device-progress-fill.is-warn { background-color: var(--accent-warn); }
    .device-progress-fill.is-err { background-color: var(--accent-danger); }

    #right-device.is-offline .device-compact { opacity: 0.55; }

    .right-run { text-align: left; }
    #right-device { text-align: left; }

    .tel-header {
      display: flex; align-items: center; justify-content: space-between;
      gap: var(--s2); padding: var(--s3) var(--s3) var(--s2);
      border-bottom: 1px solid var(--border-color); flex-shrink: 0;
    }
    .tel-title {
      font-size: var(--fs-sm); font-weight: 600;
      letter-spacing: var(--letter-spacing-wide);
      color: var(--text-muted); text-transform: uppercase;
    }
    .tel-stage-badge {
      font-size: var(--fs-xs); font-family: var(--font-mono);
      color: var(--text-muted); background: var(--bg-terminal);
      border: 1px solid var(--border-soft); border-radius: var(--radius-compact);
      padding: 2px 8px;
    }
    .tel-stage-badge.is-running { color: var(--accent-blue); border-color: var(--accent-blue); }
    .tel-stage-badge.is-done { color: var(--accent-green); border-color: var(--accent-green); }
    .tel-stage-badge.is-error { color: var(--accent-danger); border-color: var(--accent-danger); }
    .tel-stage-badge.is-off { color: var(--accent-warn); border-color: var(--accent-warn); }

    .tel-scroll {
      flex: 1 1 auto; min-height: 0; overflow-y: auto;
      padding: var(--s3); display: flex; flex-direction: column; gap: var(--s2);
      scrollbar-width: thin; scrollbar-color: var(--border-soft) transparent;
    }

    .tel-card {
       background: var(--bg-input); border: 1px solid var(--border-soft);
       border-radius: var(--radius-standard); padding: var(--s3); flex-shrink: 0;
    }
    .tel-card.is-dim { opacity: 0.6; }
    .tel-card-title {
      font-size: var(--fs-xs); font-weight: 600; text-transform: uppercase;
      letter-spacing: var(--letter-spacing-wide); color: var(--text-muted);
      margin-bottom: var(--s2);
    }

    .tel-ringcard { display: flex; align-items: center; gap: var(--s3); }
    .tel-ring {
      width: 96px; height: 96px; border-radius: 50%; flex-shrink: 0;
      display: grid; place-items: center;
      background: var(--bg-terminal);
      position: relative;
    }
    .tel-ring::after {
      content: '';
      position: absolute; inset: 0;
      border-radius: 50%;
      background: conic-gradient(var(--accent-blue) 0 var(--pct, 0%), transparent var(--pct, 0%) 100%);
      -webkit-mask: radial-gradient(farthest-side, transparent 81%, #000 82%, #000 91%, transparent 92%);
      mask: radial-gradient(farthest-side, transparent 81%, #000 82%, #000 91%, transparent 92%);
      filter: drop-shadow(0 0 3px color-mix(in srgb, var(--accent-blue) 60%, transparent));
    }
    .tel-ring-in {
      width: 74px; height: 74px; border-radius: 50%;
      background: var(--bg-input); display: grid; place-items: center;
      font-size: var(--fs-md); font-weight: 700; font-variant-numeric: tabular-nums;
      position: relative; z-index: 1;
    }
    .tel-ring.tel-indet::before {
      content: '';
      position: absolute; inset: 0;
      border-radius: 50%;
      border: 3px solid color-mix(in srgb, var(--accent-blue) 30%, transparent);
      border-top-color: var(--accent-blue);
      animation: spin 0.9s linear infinite;
    }
    .tel-ring-full .tel-ring-in {
      width: 78px; height: 78px;
    }
    .tel-ring-full .tel-ring-in svg {
      width: 56px; height: 56px;
      overflow: visible; display: block;
    }
    .tel-ringmeta { display: flex; flex-direction: column; gap: var(--s1); min-width: 0; overflow: hidden; }
    .tel-ringmeta b { font-size: var(--fs-md); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .tel-ringmeta span { font-size: var(--fs-xs); color: var(--text-muted); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

    .tel-tiles { display: grid; grid-template-columns: 1fr 1fr; gap: var(--s2); flex-shrink: 0; }
    .tel-tile {
       background: var(--bg-input); border: 1px solid var(--border-soft);
       border-radius: var(--radius-standard); padding: var(--s2) var(--s3);
       display: flex; flex-direction: column; gap: 2px;
    }
    .tel-tile small {
      display: block; font-size: var(--fs-xs);
      text-transform: uppercase; letter-spacing: var(--letter-spacing-wide);
      color: var(--text-muted);
    }
    .tel-tile b { font-size: var(--fs-md); font-weight: 700; font-variant-numeric: tabular-nums; }
    .tel-tile b.mono { font-family: var(--font-mono); font-size: var(--fs-md); }
    .tel-tile.tel-warn b { color: var(--accent-warn); }
    .tel-tile.tel-warn b.is-zero { color: var(--text-primary); }

    .tel-bar-row {
      display: flex; align-items: center;
      gap: var(--s2);
      font-size: var(--fs-xs); color: var(--text-muted);
      margin-bottom: var(--s2);
    }
    .tel-bar-row:last-child { margin-bottom: 0; }
    .tel-bar-row > span:first-child { flex-shrink: 0; }
    .tel-bar { flex: 1 1 auto; height: 6px; background: var(--bg-terminal); border-radius: 3px; overflow: hidden; }
    .tel-bar i {
      display: block; height: 100%; width: 0; border-radius: 3px;
      background: var(--border-soft); transition: width var(--transition-med);
    }
    .tel-bar i.is-done { background: var(--accent-green); }
    .tel-bar i.is-active { background: var(--accent-blue); animation: tel-pulse 1.2s ease-in-out infinite; }
    .tel-bar i.is-error { background: var(--accent-danger); }
    .tel-bar-v { flex-shrink: 0; width: 52px; text-align: right; }

    @keyframes tel-pulse { 50% { opacity: 0.55; } }
    .mono { font-family: var(--font-mono); }

  `;
  document.head.appendChild(style);

  const STAGES = ['config', 'listing', 'crawl', 'qa', 'autoexport'];

  const hub = {
    device: {
      status: 'unknown',
      info: null,
      miss: 0,
      wasConnected: false,
      lost: false,
      aborting: false
    },
    project: {
      status: 'none',
      origin: null,
      path: null,
      name: null,
      fresh: false
    },
    run: {
      times: {},
      qaPollAt: 0,
      cur: 0,
      total: null,
      issues: 0,
      warnings: 0
    },
    deviceCacheAt: 0
  };

  window.auraHub = hub;

  const el = id => document.getElementById(id);

  const setText = (id, v) => {
    const node = el(id);
    if (node) node.textContent = v == null ? '--' : v;
  };

  const api = () =>
    window.pywebview && window.pywebview.api ? window.pywebview.api : null;

  const runSt = () => (typeof runState !== 'undefined' ? runState : null);
  const qa = () => (typeof qaData !== 'undefined' ? qaData : null);

  const curProj = () => {
    try {
      return typeof currentProject !== 'undefined' && currentProject ? currentProject : null;
    } catch (e) {
      return null;
    }
  };

  const fmt = s => (typeof runFmtElapsed === 'function' ? runFmtElapsed(s) : '--:--');

  const qaEmpty = () => {
    const q = qa();
    return !q || !(q.paquetes || []).length;
  };

  const eta = { stage: null, samples: [], rate: 0, total: null, running: false };

  function etaFeed(s) {
    if (!s || s.status !== 'running') {
      if (!s || s.status === 'idle') {
        eta.stage = null;
        eta.samples = [];
        eta.rate = 0;
        eta.total = null;
      }
      eta.running = false;
      return;
    }

    if (!eta.running) {
      eta.running = true;
      eta.samples = [];
      eta.rate = 0;
      eta.total = null;
    }

    if (s.stage !== eta.stage) {
      eta.stage = s.stage || null;
      eta.samples = [];
      eta.rate = 0;
      eta.total = null;
    }

    if (s.total_items != null && s.total_items > 0) eta.total = s.total_items;

    const cur = Number(s.current) || 0;
    const now = Date.now();
    const last = eta.samples[eta.samples.length - 1];

    if (!last || last.c !== cur || now - last.t > 1500) {
      eta.samples.push({ c: cur, t: now });
    }

    const cutoff = now - 120000;
    while (eta.samples.length > 2 && eta.samples[0].t < cutoff) {
      eta.samples.shift();
    }

    if (eta.samples.length > 80) {
      eta.samples.splice(0, eta.samples.length - 80);
    }
  }

  function etaValue() {
    if (eta.total == null || eta.samples.length < 2) return null;

    const a = eta.samples[0];
    const b = eta.samples[eta.samples.length - 1];

    const dt = (b.t - a.t) / 1000;
    const dc = b.c - a.c;

    if (dt <= 0.5 || dc <= 0) return null;

    const inst = dc / dt;
    eta.rate = eta.rate > 0 ? eta.rate * 0.6 + inst * 0.4 : inst;

    if (eta.rate <= 0) return null;

    const rem = (eta.total - b.c) / eta.rate;
    return isFinite(rem) && rem >= 0 ? rem : null;
  }

  // Bug #6 también cubierto aquí.
  const TS_EMBED = /^\s*(?:\d{2}:\d{2}:\d{2}\s*)+/;

  (function () {
    const orig = window.onPipelineLog;
    window.onPipelineLog = function (ev) {
      if (ev && typeof ev.msg === 'string') {
        ev = Object.assign({}, ev, { msg: ev.msg.replace(TS_EMBED, '') });
      }
      if (orig) orig(ev);
    };
  })();

  window.qaSortOptions = function () {
    return [
      { v: 'issues_desc', label: I('qa.sort.issuesDesc') },
      { v: 'qa_desc', label: I('qa.sort.qaDesc') },
      { v: 'qa_asc', label: I('qa.sort.qaAsc') },
      { v: 'ocr_desc', label: I('qa.sort.ocrDesc') },
      { v: 'ocr_asc', label: I('qa.sort.ocrAsc') },
      { v: 'file_asc', label: I('qa.sort.fileAsc') }
    ];
  };

  // Bug #8 mitigado: no sobrescribir si app.js ya definió runRenderSummaryPane.
  if (typeof window.runRenderSummaryPane !== 'function') {
    window.runRenderSummaryPane = function () {
      const pane = el('run-pane-summary');
      if (!pane) return;

      const s = runSt();

      if (!s || s.status === 'idle') {
        pane.innerHTML = '<div class="run-console-empty">' + I('run.waiting') + '</div>';
        return;
      }

      const esc = typeof qaEsc === 'function' ? qaEsc : x => String(x == null ? '' : x);
      const prog = s.total_items ? s.current + ' / ' + s.total_items : s.current || 0;

      const rows = [
        [I('run.sum.status'), I('run.status.' + s.status)],
        [I('run.sum.stage'), s.stage || '--'],
        [I('run.sum.progress'), prog],
        [I('run.sum.elapsed'), fmt(s.elapsed)],
        [I('run.sum.issues'), String(s.issues || 0)],
        [I('run.sum.warnings'), String(s.warnings || 0)]
      ];

      if (s.error) rows.push([I('run.sum.error'), s.error]);

      pane.innerHTML =
        '<table class="run-live-table">' +
        rows
          .map(
            r =>
              '<tr><td class="run-live-k">' +
              esc(r[0]) +
              '</td><td class="run-live-v">' +
              esc(r[1]) +
              '</td></tr>'
          )
          .join('') +
        '</table>';
    };
  }

  function buildTelemetry() {
    const rc = el('right-col');
    if (!rc) return;

    const tc = rc.querySelector('.tab-content');
    if (!tc) return;

    let exp = el('right-export');
    if (!exp) {
      exp = document.createElement('div');
      exp.id = 'right-export';
      exp.className = 'right-ctx';

      while (tc.firstChild) exp.appendChild(tc.firstChild);
      tc.appendChild(exp);
    } else {
      exp.classList.add('right-ctx');
    }

    let run = el('right-run');
    if (!run) {
      run = document.createElement('div');
      run.id = 'right-run';
      tc.appendChild(run);
    }

    run.className = 'right-ctx right-run';

    if (run.dataset.built) return;
    run.dataset.built = '1';

    run.innerHTML =
      '<div class="tel-header"><span class="tel-title" data-xt="tel.title">Run telemetry</span>' +
      '<span class="tel-stage-badge" id="tel-badge">--</span></div>' +
      '<div class="tel-scroll">' +
      '<div class="tel-card tel-ringcard"><div class="tel-ring" id="tel-ring"><div class="tel-ring-in" id="tel-pct">0%</div></div>' +
      '<div class="tel-ringmeta"><b id="tel-stage-label">--</b><span class="mono" id="tel-count">--</span><span class="mono" id="tel-pkg">--</span></div></div>' +
       '<div class="tel-tiles">' +
       '<div class="tel-tile"><b id="tel-images">--</b><small data-xt="tel.images">Images</small></div>' +
       '<div class="tel-tile tel-warn"><b id="tel-issues" class="is-zero">0</b><small data-xt="tel.issues">Issues</small></div>' +
       '<div class="tel-tile tel-warn"><b id="tel-warnings" class="is-zero">0</b><small data-xt="tel.warnings">Warnings</small></div>' +
       '<div class="tel-tile"><b class="mono" id="tel-elapsed">00:00</b><small data-xt="tel.elapsed">Elapsed</small></div></div>' +
      '<div class="tel-card" id="tel-barscard"><div class="tel-card-title" data-xt="tel.stages">Stage durations</div>' +
      STAGES.map(
        s =>
          '<div class="tel-bar-row"><span data-i18n="run.step.' + s + '">' + s + '</span>' +
          '<span class="tel-bar"><i id="tel-bar-' + s + '"></i></span>' +
          '<span class="tel-bar-v mono" id="tel-dur-' + s + '">—</span></div>'
      ).join('') +
      '</div></div>';

    if (typeof applyExtraI18n === 'function') applyExtraI18n();

    try {
      if (window.I18N) I18N.apply(I18N.current);
    } catch (e) {}
  }

  function setCtx() {
    const rc = el('right-col');
    if (!rc) return;

    rc.dataset.ctx = document.querySelector('#pane-test.active')
      ? 'test'
      : document.querySelector('#pane-reports.active')
        ? 'reports'
        : document.querySelector('#pane-device.active')
          ? 'device'
          : 'none';
  }

  function detectProject() {
    const locked = !!document.querySelector('.app-root[data-locked="true"]');
    const cp = curProj();

    const p = hub.project;
    p.path = cp;
    p.name = cp ? String(cp).split(/[\/\\]/).filter(Boolean).pop() : null;

    if (!cp || locked) {
      p.status = 'none';
      p.origin = null;
      p.fresh = false;
    } else {
      p.status = p.origin || 'opened';
      const s = runSt();
      p.fresh = qaEmpty() && (!s || s.status === 'idle' || s.status === 'running');
    }
  }

  function projectLabel() {
    const p = hub.project;

    if (p.status === 'none') return T('hub.noProject');
    if (p.fresh) return T('hub.newProject');

    return p.name || '--';
  }

  async function refreshDevice(force) {
    const a = api();
    const now = Date.now();

    if (!force && now - hub.deviceCacheAt < 2000) return;
    hub.deviceCacheAt = now;

    if (!a) {
      hub.device.info = null;
      hub.device.miss++;
    } else {
      try {
        const info = await a.getDeviceInfo();
        hub.device.miss = 0;
        hub.device.info = info || { connected: false };
      } catch (e) {
        hub.device.info = null;
        hub.device.miss++;
      }
    }

    const d = hub.device;
    const connected = !!(d.info && d.info.connected);

    if (connected) {
      d.wasConnected = true;
      d.status = 'connected';
    } else if (d.info === null && d.miss >= 2) {
      d.status = 'adb-error';
    } else {
      d.status = d.lost ? 'lost' : 'disconnected';
    }
  }

  async function watchdog() {
    const d = hub.device;
    const s = runSt();

    const connected = d.status === 'connected';

    if (connected && d.lost) {
      d.lost = false;
      d.aborting = false;
      if (typeof showToast === 'function') showToast(T('hub.reconnected'), 'success', 3000);
    }

    const gone = !connected && d.wasConnected;

    // Solo listing y crawl necesitan el DUT (adb/uiautomator2).
    // qa y autoexport solo leen archivos en disco: no abortar por desconexión.
    const needsDevice = s && (s.stage === 'listing' || s.stage === 'crawl');

    if (gone && s && s.status === 'running' && needsDevice && !d.aborting) {
      d.aborting = true;
      d.lost = true;
      d.status = 'lost';

      if (typeof runLog === 'function') runLog(T('hub.aborted'), 'ERROR');

      const a = api();
      if (a) {
        try {
          await a.stopPipeline();
        } catch (e) {}
      }

      s.status = 'error';
      s.error = 'device disconnected';

      if (typeof runSetBadge === 'function') runSetBadge('error');
      if (typeof runSetRunning === 'function') runSetRunning(false);
      if (typeof runRenderSummaryPane === 'function') runRenderSummaryPane();
      if (typeof showToast === 'function') showToast(T('hub.aborted'), 'danger', 5000);
    }
  }

  function renderSidebar() {
    const w = el('device-widget');
    if (!w) return;

    const d = hub.device;
    const s = runSt();
    const status = s ? s.status : 'idle';
    const running = status === 'running';

    w.classList.toggle('dw-lost', d.status === 'lost');
    w.classList.toggle('dw-adberr', d.status === 'adb-error');

    setText(
      'device-model',
      d.status === 'lost'
        ? T('hub.lost')
        : d.status === 'connected'
          ? (d.info && d.info.model) || '--'
          : d.status === 'adb-error'
            ? T('hub.adbError')
            : T('hub.noDevice')
    );

    setText(
      'device-os',
      d.status === 'connected' && d.info && d.info.release
        ? T('device.os', d.info.release)
        : '--'
    );

    setText('device-status', d.status === 'lost' ? T('hub.lost') : T('run.status.' + status));

    setText('device-step', running ? s.stage || '--' : projectLabel());

    const bar = el('device-progress');
    if (bar) {
      const rem = running ? etaValue() : null;

    bar.title =
      (running || status === 'done'
        ? T('hub.elapsed') + ' ' + fmt(window.__counters.elapsed || 0)
        : '') +
      (rem != null
        ? ' · ' + T('hub.eta') + ' ~' + fmt(rem)
        : running
          ? ' · ' + T('hub.eta') + ' --:--'
          : '');
  }
  }

  function renderDevicePanel() {
    const d = hub.device;
    const connected = d.status === 'connected';
    const info = d.info || {};

    const model = connected
      ? info.model || '--'
      : d.status === 'lost'
        ? T('hub.lost')
        : T('hub.noDevice');

    const os = connected && info.release ? T('device.os', info.release) : '--';

    setText('hero-model', model);
    setText('hero-os', os);

    setText('spec-model', model);
    setText('spec-release', connected ? info.release || '--' : '--');
    setText('spec-build', connected ? info.build_id : '');
    setText('spec-language', connected ? info.language : '');
    setText('spec-resolution', connected ? info.resolution : '');
    setText('spec-density', connected ? info.density : '');
    setText('spec-serial', connected ? info.serial : '');

    const dev = el('right-device');
    if (dev) dev.classList.toggle('is-offline', !connected);

    const label =
      d.status === 'lost'
        ? T('hub.lost')
        : d.status === 'adb-error'
          ? T('hub.adbError')
          : connected
            ? I('dev.connected')
            : I('dev.none');

    document.querySelectorAll('.badge-dut').forEach(b => {
      b.textContent = label;
      b.classList.toggle('badge-connected', connected);
    });
  }

  function renderRunBadge(status) {
    const badge = el('run-badge');
    if (!badge) return;

    badge.classList.remove('badge-running', 'badge-done', 'badge-error', 'badge-cancelled');

    const cls = {
      running: 'badge-running',
      done: 'badge-done',
      error: 'badge-error',
      cancelled: 'badge-cancelled'
    }[status];

    if (cls) badge.classList.add(cls);
    badge.textContent = T('run.status.' + status);
  }

  function stageDur(s) {
    const frozen = { listing: _durListing, crawl: _durCrawl, qa: _durQa, autoexport: _durAutoexport }[s];
    if (frozen != null) return frozen;
    const t = hub.run.times[s];
    if (!t || !t.start) return null;
    return (Date.now() - t.start) / 1000;
  }

  function qaImages() {
    const q = qa();
    if (!q || !q.paquetes) return null;
    return q.paquetes.reduce((a, p) => a + (p.total_imagenes || 0), 0);
  }

  let _animRaf = null;
  let _animReal = -1;
  let _animFrom = 0;
  let _animT0 = 0;
  let _animDur = 0;
  let _realChangedAt = 0;
  let _elapsedTimer = null;
  let _curDp = 0;
  let _elBase = -1;
  let _elBaseAt = 0;
  let _durListing = null, _durCrawl = null, _durQa = null, _durAutoexport = null;
  let _ringFull = false;
  let _ringAnimRaf = null;

  function _ringStartAnim() {
    if (_ringAnimRaf) return;
    const pctEl = el('tel-pct');
    if (!pctEl) return;
    pctEl.textContent = '';
    const svgNS = 'http://www.w3.org/2000/svg';
    const svg = document.createElementNS(svgNS, 'svg');
    svg.setAttribute('viewBox', '-40 -40 80 80');
    const edgeGroup = document.createElementNS(svgNS, 'g');
    edgeGroup.setAttribute('class', 'psdns-l-edge');
    const activeEdgeGroup = document.createElementNS(svgNS, 'g');
    activeEdgeGroup.setAttribute('class', 'psdns-l-edge-active');
    const vertexGroup = document.createElementNS(svgNS, 'g');
    vertexGroup.setAttribute('class', 'psdns-l-vertex');
    const vertexActiveGroup = document.createElementNS(svgNS, 'g');
    vertexActiveGroup.setAttribute('class', 'psdns-l-vertex-active');
    svg.append(edgeGroup, activeEdgeGroup, vertexGroup, vertexActiveGroup);
    pctEl.appendChild(svg);

    const s = 0.62;
    const cubeVerts = [[-s,-s,-s],[s,-s,-s],[s,s,-s],[-s,s,-s],[-s,-s,s],[s,-s,s],[s,s,s],[-s,s,s]];
    const cubeEdges = [[0,1],[1,2],[2,3],[3,0],[4,5],[5,6],[6,7],[7,4],[0,4],[1,5],[2,6],[3,7]];
    const octVerts = [[0,1,0],[0,-1,0],[1,0,0],[-1,0,0],[0,0,1],[0,0,-1]];
    const octEdges = [[0,2],[0,3],[0,4],[0,5],[1,2],[1,3],[1,4],[1,5],[2,4],[4,3],[3,5],[5,2]];

    function rotate3D(v, ax, ay, az) {
      let x = v[0], y = v[1], z = v[2];
      let y1 = y * Math.cos(ax) - z * Math.sin(ax), z1 = y * Math.sin(ax) + z * Math.cos(ax);
      y = y1; z = z1;
      let x2 = x * Math.cos(ay) + z * Math.sin(ay), z2 = -x * Math.sin(ay) + z * Math.cos(ay);
      x = x2; z = z2;
      return [x * Math.cos(az) - y * Math.sin(az), x * Math.sin(az) + y * Math.cos(az), z];
    }
    function project(v, scale) {
      const d = 1 + v[2] * 0.14;
      return [v[0] * scale * d, v[1] * scale * d];
    }
    function makeLine(group, p1, p2) {
      const l = document.createElementNS(svgNS, 'line');
      l.setAttribute('x1', p1[0].toFixed(2)); l.setAttribute('y1', p1[1].toFixed(2));
      l.setAttribute('x2', p2[0].toFixed(2)); l.setAttribute('y2', p2[1].toFixed(2));
      group.appendChild(l);
    }
    function makeRect(group, p, sz) {
      const r = document.createElementNS(svgNS, 'rect');
      r.setAttribute('x', (p[0] - sz / 2).toFixed(2)); r.setAttribute('y', (p[1] - sz / 2).toFixed(2));
      r.setAttribute('width', sz.toFixed(2)); r.setAttribute('height', sz.toFixed(2));
      r.setAttribute('rx', '0.5');
      group.appendChild(r);
    }

    const start = performance.now();
    function render(now) {
      const t = (now - start) * 0.001;
      edgeGroup.replaceChildren();
      activeEdgeGroup.replaceChildren();
      vertexGroup.replaceChildren();
      vertexActiveGroup.replaceChildren();
      const breathe = 1 + 0.03 * Math.sin(t * 1.4);
      const sway = Math.sin(t * 0.45) * 0.22;
      const os = (0.94 + 0.06 * Math.sin(t * 2.2)) * breathe;
      const is = (0.85 + 0.15 * Math.cos(t * 2.2)) * breathe;
      const po = octVerts.map(v => project(rotate3D([v[0]*os, v[1]*os, v[2]*os], 0.615 + sway, t * 0.65, sway * 0.5), 28));
      const pi = cubeVerts.map(v => project(rotate3D([v[0]*is, v[1]*is, v[2]*is], 0.615 - sway, -t * 1.1, Math.sin(t*0.8)*0.3), 24));
      octEdges.forEach(([i, j]) => makeLine(edgeGroup, po[i], po[j]));
      cubeEdges.forEach(([i, j]) => makeLine(activeEdgeGroup, pi[i], pi[j]));
      po.forEach((p, idx) => {
        const pulse = 0.5 + 0.5 * Math.sin(t * 4 + idx * 1.1);
        const sz = 2.4 + pulse * 0.8;
        if (pulse > 0.7) makeRect(vertexActiveGroup, p, sz);
        else makeRect(vertexGroup, p, sz);
      });
      _ringAnimRaf = requestAnimationFrame(render);
    }
    _ringAnimRaf = requestAnimationFrame(render);
  }

  function _ringStopAnim() {
    if (_ringAnimRaf) {
      cancelAnimationFrame(_ringAnimRaf);
      _ringAnimRaf = null;
    }
    const pctEl = el('tel-pct');
    if (pctEl) {
      pctEl.textContent = '0%';
      const svg = pctEl.querySelector('svg');
      if (svg) svg.remove();
    }
  }

  const _CREEP_T = 30;
  const _CREEP_MAX = 0.99;
  const _TARGET_SPEED = 0.5;

  function _resetAnim() {
    _animReal = -1;
    _animFrom = 0;
    _animT0 = 0;
    _animDur = 0;
    _realChangedAt = 0;
    _curDp = 0;
    if (_ringFull) {
      _ringFull = false;
      const ring = el('tel-ring');
      if (ring) ring.classList.remove('tel-ring-full');
      const tc = el('tel-count');
      if (tc) tc.hidden = false;
      const tp = el('tel-pkg');
      if (tp) tp.hidden = false;
      _ringStopAnim();
    }
  }

  function _elapsedNow(c) {
    const be = c.elapsed || 0;
    if (c.status !== 'running') return be;
    if (be !== _elBase) {
      _elBase = be;
      _elBaseAt = Date.now();
    }
    return be + (Date.now() - _elBaseAt) / 1000;
  }

  function _easeOutCubic(p) {
    return 1 - Math.pow(1 - p, 3);
  }

  function _computeDp(c) {
    const real = c.current || 0;
    if (c.status === 'done') return c.total || real;
    if (c.status !== 'running') return real;
    const now = Date.now();
    if (real !== _animReal) {
      _animFrom = _curDp;
      _animReal = real;
      _animT0 = now;
      _realChangedAt = now;
      const jump = Math.abs(real - _animFrom);
      _animDur = Math.max(jump / _TARGET_SPEED, 0.1) * 1000;
    }
    const p = Math.min(1, (now - _animT0) / _animDur);
    let dp = _animFrom + (real - _animFrom) * _easeOutCubic(p);
    if (c.total && real < c.total) {
      const t = (now - _realChangedAt) / 1000;
      dp += _CREEP_MAX * Math.pow(t / (t + _CREEP_T), 2);
    }
    _curDp = dp;
    return dp;
  }

  function _renderFrame() {
    const c = window.__counters;
    if (!c) return;
    const status = c.status || 'idle';
    const running = status === 'running';
    const total = c.total;
    const real = c.current || 0;
    const dp = _computeDp(c);

    const fullMode = running && (c.stage === 'config' || c.stage === 'listing' || c.stage === 'crawl');
    const ring = el('tel-ring');
    const tc = el('tel-count');
    const tp = el('tel-pkg');

    if (fullMode && !_ringFull) {
      _ringFull = true;
      if (ring) ring.classList.add('tel-ring-full');
      if (tc) tc.hidden = true;
      if (tp) tp.hidden = true;
      _ringStartAnim();
    } else if (!fullMode && _ringFull) {
      _ringFull = false;
      if (ring) ring.classList.remove('tel-ring-full');
      if (tc) tc.hidden = false;
      if (tp) tp.hidden = false;
      _ringStopAnim();
    }

    if (ring) {
      ring.classList.toggle('tel-indet', running);
      let pct = 0;
      if (status === 'done') pct = 100;
      else if (total) pct = Math.min(100, (dp / total) * 100);
      ring.style.setProperty('--pct', pct + '%');
    }

    if (!_ringFull) {
      let pctText;
      if (status === 'done') pctText = '100%';
      else if (running && total) pctText = Math.round(Math.min(100, (dp / total) * 100)) + '%';
      else if (running) pctText = '';
      else pctText = '0%';
      setText('tel-pct', pctText);

      setText(
        'tel-count',
        running
          ? real + ' / ' + (total == null ? '?' : total)
          : total != null
            ? total + ' img'
            : '--'
      );
    }

    const w = el('device-widget');
    if (w) {
      const fill = w.querySelector('.device-progress-fill');
      if (fill && total) fill.style.width = Math.min(100, (dp / total) * 100) + '%';
    }
  }

  function _tick() {
    const c = window.__counters;
    if (!c || c.status !== 'running') {
      _animRaf = null;
      return;
    }
    _renderFrame();
    _animRaf = requestAnimationFrame(_tick);
  }

  function _ensureAnimLoop() {
    if (!_animRaf && typeof requestAnimationFrame === 'function') {
      _animRaf = requestAnimationFrame(_tick);
    }
  }

  let _masterTimer = null;
  let _dataTimer = null;

  function masterTick() {
    const c = window.__counters;
    if (c && c.status === 'running') {
      const e = fmt(_elapsedNow(c));
      setText('tel-elapsed', e);
      setText('device-elapsed', e);
    }
    const s = runSt();
    etaFeed(s);
    renderAll();
    if (s) renderRunBadge(s.status);
    if (typeof window.updateDeviceWidget === 'function') window.updateDeviceWidget();
    if (typeof window.runUpdateWidget === 'function') window.runUpdateWidget(s);
    if (typeof runRenderLivePanes === 'function') runRenderLivePanes();
    const delay = 1000 - (Date.now() % 1000);
    _masterTimer = setTimeout(masterTick, delay);
  }

  function dataTick() {
    if (typeof runCrawlRefresh === 'function') runCrawlRefresh();
    refreshDevice(false);
    watchdog();
  }

  function renderCounters() {
    const c = window.__counters;
    if (!c) return;

    const status = c.status || 'idle';
    const running = status === 'running';
    const images = qaImages();

    if (running && _animReal === -1) _resetAnim();
    if (!running && _animReal !== -1) _resetAnim();
    if (running) _ensureAnimLoop();
    if (!running) {
      const e = fmt(_elapsedNow(c));
      setText('tel-elapsed', e);
      setText('device-elapsed', e);
    }

    const totalImg = c.total != null ? c.total : images;

    const bi = el('tel-issues');
    const bw = el('tel-warnings');
    if (bi) {
      bi.textContent = c.issues || 0;
      bi.classList.toggle('is-zero', (c.issues || 0) === 0);
    }
    if (bw) {
      bw.textContent = c.warnings || 0;
      bw.classList.toggle('is-zero', (c.warnings || 0) === 0);
    }
    setText('tel-images', totalImg != null ? totalImg : '--');

    const w = el('device-widget');
    if (w) {
      const fill = w.querySelector('.device-progress-fill');
      if (fill) {
        fill.classList.remove('indeterminate', 'is-warn', 'is-err');
        if (hub.device.status === 'lost') fill.classList.add('is-err');
        else if (status === 'error') fill.classList.add('is-err');
        else if (status === 'cancelled') fill.classList.add('is-warn');
        else if (running && !c.total) {
          fill.style.width = '100%';
          fill.classList.add('indeterminate');
        }
      }
      const iss = el('device-issues');
      if (iss) {
        iss.textContent = T('run.issuesShort', c.issues || 0);
        iss.classList.toggle('has-issues', (c.issues || 0) > 0);
      }
    }

    _renderFrame();

    if (typeof runRenderSummaryPane === 'function') runRenderSummaryPane();
  }

  function renderTelemetry() {
    if (!el('tel-ring')) return;

    const s = runSt();
    const p = hub.project;
    const d = hub.device;

    const status = s ? s.status : 'idle';
    const running = status === 'running';

    const badge = el('tel-badge');
    if (badge) {
      badge.textContent = d.status === 'lost' ? T('hub.lost') : T('run.status.' + status);

      badge.className =
        'tel-stage-badge' +
        (running
          ? ' is-running'
          : status === 'done'
            ? ' is-done'
            : status === 'error' || status === 'cancelled'
              ? ' is-error'
              : d.status === 'disconnected' || d.status === 'adb-error'
                ? ' is-off'
                : '');
    }

    setText('tel-stage-label', running ? (s.stage ? T('run.step.' + s.stage) : '--') : (p.name || projectLabel()));

    const pkgEl = el('tel-pkg');
    if (pkgEl) {
      const path = p.status === 'none' ? '--' : p.path || '--';
      pkgEl.textContent = path;
      pkgEl.title = path;
    }

    const durs = STAGES.map(stageDur);
    const max = Math.max.apply(
      null,
      durs.map(x => x || 0).concat([1])
    );

    STAGES.forEach((name, i) => {
      const barEl = el('tel-bar-' + name);
      const lab = el('tel-dur-' + name);

      const t = hub.run.times[name];
      const dd = durs[i];

      let cls = '';
      if (t && t.end) cls = t.error ? 'is-error' : 'is-done';
      else if (t && t.start) cls = 'is-active';

      if (barEl) {
        barEl.className = cls;
        barEl.style.width = dd == null ? '0%' : Math.max(2, Math.round((dd / max) * 100)) + '%';
      }

      if (lab) lab.textContent = dd == null ? '00:00' : fmt(dd);
    });

    const barsCard = el('tel-barscard');
    if (barsCard) barsCard.classList.toggle('is-dim', !Object.keys(hub.run.times).length);
  }

  function renderAll() {
    detectProject();
    renderSidebar();
    renderDevicePanel();
    renderTelemetry();
    renderCounters();
    if (typeof window.dcLoad === 'function') window.dcLoad();
  }

  (function () {
    const orig = window.openAndLoad;
    if (typeof orig !== 'function') return;

    window.openAndLoad = async function (path) {
      const a = api();

      if (a && typeof a.listDir === 'function') {
        let l = null;
        try {
          l = await a.listDir(path);
        } catch (e) {
          l = null;
        }

        if (l && !l.ok) {
          if (typeof showToast === 'function') {
            showToast(
              l.error === 'denied' ? T('proj.denied') : T('proj.invalid', path),
              'danger',
              4200
            );
          }

          if (typeof loadRecentProjects === 'function') {
            try {
              await loadRecentProjects();
            } catch (e) {}
          }

          return;
        }
      }

      const r = await orig.apply(this, arguments);
      hub.project.origin = 'opened';
      renderAll();
      return r;
    };
  })();

  window.updateDeviceWidget = async function () {
    await refreshDevice(true);
    renderAll();
  };

  window.renderCounters = renderCounters;

  window._updateDeviceWidget = window.updateDeviceWidget;

  window.runUpdateWidget = function (s) {
    etaFeed(s);
    renderSidebar();
    renderTelemetry();
    renderCounters();
  };

  window.runFmtEta = function (s) {
    etaFeed(s);

    if (!s) return '--:--';
    if (s.status === 'done') return '00:00';
    if (s.status !== 'running') return '--:--';

    const rem = etaValue();
    return rem == null ? '--:--' : fmt(rem);
  };

  window.runSetBadge = function (status) {
    renderRunBadge(status);
  };

  const origStep = window.onPipelineStep;
  window.onPipelineStep = function (step, state) {
    const now = Date.now();

    if (state === 'active') {
      hub.run.times[step] = { start: now, end: null };
      if (step === 'listing') _durListing = null;
      else if (step === 'crawl') _durCrawl = null;
      else if (step === 'qa') _durQa = null;
      else if (step === 'autoexport') _durAutoexport = null;
    } else if ((state === 'done' || state === 'error') && hub.run.times[step]) {
      hub.run.times[step].end = now;
      const dur = (now - hub.run.times[step].start) / 1000;
      if (step === 'listing') _durListing = dur;
      else if (step === 'crawl') _durCrawl = dur;
      else if (step === 'qa') _durQa = dur;
      else if (step === 'autoexport') _durAutoexport = dur;
      if (state === 'error') hub.run.times[step].error = true;
    }

    if (origStep) origStep(step, state);
    renderAll();
  };

  const origProgress = window.onPipelineProgress;
  window.onPipelineProgress = function (ev) {
    if (origProgress) origProgress(ev);
    renderAll();
  };

  ['onPipelineDone', 'onPipelineError', 'onPipelineExit'].forEach(k => {
    const o = window[k];
    window[k] = function () {
      if (o) o.apply(this, arguments);
      renderAll();
    };
  });

  function wrapFn(name, after) {
    const o = window[name];
    if (typeof o !== 'function') return;

    window[name] = function () {
      const r = o.apply(this, arguments);

      const done = () => {
        if (after) after();
        renderAll();
      };

      if (r && typeof r.then === 'function') r.then(done, done);
      else done();

      return r;
    };
  }

  wrapFn('loadQaReport');
  wrapFn('runClear', () => {
    hub.run.times = {};
    _durListing = null; _durCrawl = null; _durQa = null; _durAutoexport = null;
  });

  document.addEventListener('shown.bs.tab', setCtx);
  document.addEventListener('click', e => {
    if (e.target.closest('.nav-btn[data-bs-target]')) setTimeout(setCtx, 60);
  });

  let tickN = 0;
  let timer = null;

  function boot() {
    buildTelemetry();
    setCtx();
    renderAll();

    const s = runSt();
    if (s) renderRunBadge(s.status);

    if (!_masterTimer) masterTick();
    if (!_dataTimer) _dataTimer = setInterval(dataTick, 100);

    refreshDevice(true).then(renderAll);

    try {
      if (window.I18N) I18N.apply(I18N.current);
    } catch (e) {}

    if (typeof applyExtraI18n === 'function') applyExtraI18n();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }

  window.addEventListener('pywebviewready', boot);
})();