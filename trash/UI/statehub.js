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

    // Idiomas restantes: fallback seguro a inglés (evita romper UI).
    ['id', 'pt', 'th', 'ur', 'vi'].forEach(lang => {
      add(lang, Object.assign({}, D.en));
    });
  })(window.I18N_DATA = window.I18N_DATA || {});

  // Extiende XT si existe (claves de telemetría/hub).
  if (typeof XT !== 'undefined') {
    Object.assign(XT.en, {
      'tel.title': 'Run telemetry',
      'tel.current': 'Current item',
      'tel.stages': 'Stage durations',
      'tel.images': 'Images',
      'tel.issues': 'Issues',
      'tel.warnings': 'Warnings',
      'tel.elapsed': 'Elapsed',
      'hub.noProject': 'No project open',
      'hub.newProject': 'New project',
      'hub.lost': 'Device lost',
      'hub.aborted': 'Run aborted: device disconnected',
      'hub.reconnected': 'Device reconnected',
      'hub.adbError': 'adb not responding',
      'hub.noDevice': 'No device',
      'hub.eta': 'ETA',
      'hub.elapsed': 'Elapsed',
      'hub.noRun': 'No run yet'
    });

    Object.assign(XT.es, {
      'tel.title': 'Telemetría de ejecución',
      'tel.current': 'Ítem actual',
      'tel.stages': 'Duración por etapa',
      'tel.images': 'Imágenes',
      'tel.issues': 'Hallazgos',
      'tel.warnings': 'Advertencias',
      'tel.elapsed': 'Transcurrido',
      'hub.noProject': 'Ningún proyecto abierto',
      'hub.newProject': 'Proyecto nuevo',
      'hub.lost': 'Dispositivo perdido',
      'hub.aborted': 'Ejecución abortada: dispositivo desconectado',
      'hub.reconnected': 'Dispositivo reconectado',
      'hub.adbError': 'adb no responde',
      'hub.noDevice': 'Sin dispositivo',
      'hub.eta': 'ETA',
      'hub.elapsed': 'Transcurrido',
      'hub.noRun': 'Sin ejecución aún'
    });
  }

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
    .sidebar-main:has(#pane-test.active) ~ #right-col { display: flex !important; }
    #right-col[data-ctx="none"] { display: none !important; }
    .right-ctx { display: flex; flex-direction: column; flex: 1 1 auto; min-height: 0; }
    #right-col[data-ctx="test"] #right-export { display: none !important; }
    #right-col[data-ctx="reports"] #right-run { display: none !important; }
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

    #pane-device.is-offline .device-compact { opacity: 0.55; }

    .right-run { text-align: left; }

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
      background: conic-gradient(var(--accent-blue) 0 0%, var(--bg-terminal) 0% 100%);
    }
    .tel-ring-in {
      width: 74px; height: 74px; border-radius: 50%;
      background: var(--bg-input); display: grid; place-items: center;
      font-size: 17px; font-weight: 700; font-variant-numeric: tabular-nums;
    }
    .tel-ring.tel-indet {
      background: var(--bg-terminal) !important;
      border: 3px solid color-mix(in srgb, var(--accent-blue) 30%, transparent);
      border-top-color: var(--accent-blue);
      animation: spin 0.9s linear infinite;
    }
    .tel-ringmeta { display: flex; flex-direction: column; gap: 2px; min-width: 0; overflow: hidden; }
    .tel-ringmeta b { font-size: var(--fs-md); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .tel-ringmeta span { font-size: var(--fs-xs); color: var(--text-muted); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

    .tel-tiles { display: grid; grid-template-columns: 1fr 1fr; gap: var(--s2); flex-shrink: 0; }
    .tel-tile {
       background: var(--bg-input); border: 1px solid var(--border-soft);
       border-radius: var(--radius-standard); padding: var(--s2) var(--s3);
    }
    .tel-tile small {
      display: block; font-size: 9px; text-transform: uppercase;
      letter-spacing: var(--letter-spacing-wide); color: var(--text-muted);
      margin-bottom: 2px;
    }
    .tel-tile b { font-size: 15px; font-variant-numeric: tabular-nums; }
    .tel-tile b.mono { font-family: var(--font-mono); font-size: 13px; }
    .tel-tile.tel-warn b { color: var(--accent-warn); }
    .tel-tile.tel-warn b.is-zero { color: var(--text-primary); }

    .tel-bar-row {
      display: grid; grid-template-columns: 52px 1fr 52px;
      gap: var(--s2); align-items: center;
      font-size: var(--fs-xs); color: var(--text-muted);
      margin-bottom: 6px;
    }
    .tel-bar-row:last-child { margin-bottom: 0; }
    .tel-bar { height: 6px; background: var(--bg-terminal); border-radius: 3px; overflow: hidden; }
    .tel-bar i {
      display: block; height: 100%; width: 0; border-radius: 3px;
      background: var(--border-soft); transition: width var(--transition-med);
    }
    .tel-bar i.is-done { background: var(--accent-green); }
    .tel-bar i.is-active { background: var(--accent-blue); animation: tel-pulse 1.2s ease-in-out infinite; }
    .tel-bar i.is-error { background: var(--accent-danger); }
    .tel-bar-v { text-align: right; }

    @keyframes tel-pulse { 50% { opacity: 0.55; } }
    .mono { font-family: var(--font-mono); }

  `;
  document.head.appendChild(style);

  const STAGES = ['listing', 'crawl', 'qa', 'graphs'];

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
      qaPollAt: 0
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
      '<div class="tel-tile"><small data-xt="tel.images">Images</small><b id="tel-images">--</b></div>' +
      '<div class="tel-tile tel-warn"><small data-xt="tel.issues">Issues</small><b id="tel-issues" class="is-zero">0</b></div>' +
      '<div class="tel-tile tel-warn"><small data-xt="tel.warnings">Warnings</small><b id="tel-warnings" class="is-zero">0</b></div>' +
      '<div class="tel-tile"><small data-xt="tel.elapsed">Elapsed</small><b class="mono" id="tel-elapsed">00:00</b></div></div>' +
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

    if (gone && s && s.status === 'running' && !d.aborting) {
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

  async function pollQaIssues() {
    const a = api();
    const s = runSt();

    if (!a || !s || s.status !== 'running' || s.stage !== 'qa') return;

    const now = Date.now();
    if (now - hub.run.qaPollAt < 10000) return;
    hub.run.qaPollAt = now;

    try {
      const rep = await a.getQaReport();
      if (!rep || !rep.ok || !rep.paquetes) return;

      let iss = 0;
      let wrn = 0;

      rep.paquetes.forEach(p =>
        (p.resultados || []).forEach(r => {
          iss += (r.issues || []).length;
          wrn += (r.ocr_warnings || []).length;
        })
      );

      if (iss > (s.issues || 0)) s.issues = iss;
      if (wrn > (s.warnings || 0)) s.warnings = wrn;
    } catch (e) {}
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

    const fill = w.querySelector('.device-progress-fill');
    if (fill) {
      let pct = 0;
      if (s && s.total_items > 0) {
        pct = Math.min(100, Math.round((s.current / s.total_items) * 100));
      }

      fill.classList.remove('indeterminate', 'is-warn', 'is-err');

      if (d.status === 'lost') {
        fill.classList.add('is-err');
        fill.style.width = pct + '%';
      } else if (running) {
        if (s.total_items > 0) fill.style.width = pct + '%';
        else {
          fill.style.width = '100%';
          fill.classList.add('indeterminate');
        }
      } else if (status === 'done') {
        fill.style.width = '100%';
      } else if (status === 'error' || status === 'cancelled') {
        fill.classList.add('is-warn');
        fill.style.width = pct + '%';
      } else {
        fill.style.width = '0%';
      }
    }

    const bar = el('device-progress');
    if (bar) {
      const rem = running ? etaValue() : null;

      bar.title =
        (running || status === 'done'
          ? T('hub.elapsed') + ' ' + fmt(s ? s.elapsed : 0)
          : '') +
        (rem != null
          ? ' · ' + T('hub.eta') + ' ~' + fmt(rem)
          : running
            ? ' · ' + T('hub.eta') + ' --:--'
            : '');
    }

    setText(
      'device-elapsed',
      running || status === 'done' || status === 'error' || status === 'cancelled'
        ? fmt(s ? s.elapsed : 0)
        : '00:00'
    );

    const n = s ? s.issues || 0 : 0;
    const iss = el('device-issues');
    if (iss) {
      iss.textContent = T('run.issuesShort', n);
      iss.classList.toggle('has-issues', n > 0);
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

    const pane = el('pane-device');
    if (pane) pane.classList.toggle('is-offline', !connected);

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
    const t = hub.run.times[s];
    if (!t || !t.start) return null;
    return ((t.end || Date.now()) - t.start) / 1000;
  }

  function qaImages() {
    const q = qa();
    if (!q || !q.paquetes) return null;
    return q.paquetes.reduce((a, p) => a + (p.total_imagenes || 0), 0);
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

    let pct = 0;
    let indet = false;

    if (status === 'done') pct = 100;
    else if (running) {
      if (s.total_items > 0) pct = Math.min(100, Math.round((s.current / s.total_items) * 100));
      else indet = true;
    }

    const ring = el('tel-ring');
    if (ring) {
      ring.classList.toggle('tel-indet', indet);

      if (!indet) {
        ring.style.background =
          'conic-gradient(var(--accent-blue) 0 ' +
          pct +
          '%, var(--bg-terminal) ' +
          pct +
          '% 100%)';
      }
    }

    setText('tel-pct', indet ? '…' : pct + '%');
    setText('tel-stage-label', running ? s.stage || '--' : (p.name || projectLabel()));

    setText(
      'tel-count',
      running
        ? (s.current || 0) + ' / ' + (s.total_items == null ? '?' : s.total_items)
        : qaImages() != null
          ? qaImages() + ' img'
          : '--'
    );

    const pkgEl = el('tel-pkg');
    if (pkgEl) {
      const path = p.status === 'none' ? '--' : p.path || '--';
      pkgEl.textContent = path;
      pkgEl.title = path;
    }

    setText(
      'tel-images',
      running ? (s.total_items != null ? s.total_items : '--') : qaImages() != null ? qaImages() : '--'
    );

    const issN = s ? s.issues || 0 : 0;
    const wrnN = s ? s.warnings || 0 : 0;

    const bi = el('tel-issues');
    const bw = el('tel-warnings');

    if (bi) {
      bi.textContent = issN;
      bi.classList.toggle('is-zero', issN === 0);
    }

    if (bw) {
      bw.textContent = wrnN;
      bw.classList.toggle('is-zero', wrnN === 0);
    }

    setText('tel-elapsed', fmt(s ? s.elapsed || 0 : 0));

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

      if (lab) lab.textContent = dd == null ? '—' : fmt(dd);
    });

    const barsCard = el('tel-barscard');
    if (barsCard) barsCard.classList.toggle('is-dim', !Object.keys(hub.run.times).length);
  }

  function renderAll() {
    detectProject();
    renderSidebar();
    renderDevicePanel();
    renderTelemetry();
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

  window._updateDeviceWidget = window.updateDeviceWidget;

  window.runUpdateWidget = function (s) {
    etaFeed(s);
    renderSidebar();
    renderTelemetry();
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
    } else if (hub.run.times[step]) {
      hub.run.times[step].end = now;
      if (state === 'error') hub.run.times[step].error = true;
    }

    if (origStep) origStep(step, state);
    renderAll();
  };

  ['onPipelineProgress', 'onPipelineDone', 'onPipelineError', 'onPipelineExit'].forEach(k => {
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
  });

  document.addEventListener('shown.bs.tab', setCtx);
  document.addEventListener('click', e => {
    if (e.target.closest('.nav-btn[data-bs-target]')) setTimeout(setCtx, 60);
  });

  let tickN = 0;
  let timer = null;

  async function tick() {
    tickN++;

    // Bug #13 mitigado: polling consolidado y menos agresivo.
    if (tickN % 3 === 0 || hub.device.status === 'unknown') {
      await refreshDevice(false);
    }

    await watchdog();
    await pollQaIssues();

    etaFeed(runSt());
    renderAll();

    const s = runSt();
    if (s) renderRunBadge(s.status);
  }

  function boot() {
    buildTelemetry();
    setCtx();
    renderAll();

    const s = runSt();
    if (s) renderRunBadge(s.status);

    if (!timer) timer = setInterval(tick, 1500);

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