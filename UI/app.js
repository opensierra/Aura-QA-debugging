// ============================================================
// AURA QA - app.js corregido
// ============================================================

function bindUi(id, type, fn) {
  const el = document.getElementById(id);
  if (el) el.addEventListener(type, fn);
  return el;
}

const STORAGE_KEY = 'aura-qa-settings';
const VALID_LANGS = ['en', 'es', 'id', 'pt', 'th', 'ur', 'vi', 'zh'];

const themes = {
  'blender-dark': {
    '--bg-app': '#333333',
    '--bg-panel': '#2e2e2e',
    '--bg-input': '#202020',
    '--bg-terminal': '#151515',
    '--text-primary': '#e0e0e0',
    '--text-muted': '#888888',
    '--border-color': '#1a1a1a',
    '--border-soft': '#2d2d2d'
  },
  'deep-carbon': {
    '--bg-app': '#121212',
    '--bg-panel': '#1a1a1a',
    '--bg-input': '#0d0d0d',
    '--bg-terminal': '#050505',
    '--text-primary': '#e0e0e0',
    '--text-muted': '#777777',
    '--border-color': '#111111',
    '--border-soft': '#222222'
  },
  'slate-gray': {
    '--bg-app': '#1e222b',
    '--bg-panel': '#262b36',
    '--bg-input': '#1a1e26',
    '--bg-terminal': '#14171e',
    '--text-primary': '#dce0e8',
    '--text-muted': '#7a8299',
    '--border-color': '#161920',
    '--border-soft': '#2a3040'
  },
  'light': {
    '--bg-app': '#f0f0f0',
    '--bg-panel': '#ffffff',
    '--bg-input': '#e8e8e8',
    '--bg-terminal': '#d4d4d4',
    '--text-primary': '#1a1a1a',
    '--text-muted': '#666666',
    '--border-color': '#cccccc',
    '--border-soft': '#dddddd'
  }
};

function hasPywebview() {
  return !!(window.pywebview && window.pywebview.api);
}

const XT = {
  en: {
    'export.images': 'Images',
    'export.issues': 'Issues',
    'export.hint.noProject': 'Open a project to export its report.',
    'export.hint.ready': 'Counts update as you change the options below.',
    'export.hint.zero': 'Nothing matches these filters.',
    'export.destination': 'Destination',
    'export.folder': 'Folder',
    'export.browse': 'Choose folder',
    'export.filename': 'File name',
    'export.addDate': "Append today's date",
    'export.include': 'Include',
    'export.screenshots': 'Screenshots',
    'export.screenshotsSub': 'Thumbnails with issues outlined',
    'export.thumbSize': 'Thumbnail size',
    'export.warnings': 'OCR warnings',
    'export.warningsSub': 'Adds a count column per image',
    'export.onlyIssues': 'Only images with issues',
    'export.onlyIssuesSub': 'Leave out clean images',
    'export.filters': 'Filters',
    'export.packages': 'Package',
    'export.allPackages': 'All packages ({0})',
    'export.severity': 'Severity',
    'export.quality': 'Quality',
    'sev.high': 'High',
    'sev.medium': 'Medium',
    'sev.low': 'Low',
    'q.excellent': 'Excellent',
    'q.good': 'Good',
    'q.poor': 'Poor',
    'q.na': 'N/A',
    'export.run': 'Export to Excel',
    'export.running': 'Exporting…',
    'export.done': 'Report saved',
    'export.doneDetail': '{0} images · {1} issues · {2}',
    'export.openFile': 'Open file',
    'export.openFolder': 'Show in folder',
    'export.err.title': 'Export failed',
    'export.err.locked': 'The file is open in another program (probably Excel). Close it and try again.',
    'export.err.no_rows': 'Nothing to export with the current filters.',
    'export.err.no_project': 'No project is open.',
    'export.err.bad_destination': "The destination folder can't be created or written to.",
    'export.err.deps': 'A Python dependency is missing (openpyxl / Pillow): {0}',
    'export.err.generic': 'Unexpected error: {0}',
    'export.err.noBridge': 'Export only works inside the AURA QA window.',
    'recent.notFound': 'That folder no longer exists.',
    'new.err': "Couldn't create the new project.",
    'new.exists': 'A project with that name already exists there.',
    'proj.opened': 'Project "{0}" is ready.',
    'proj.invalid': 'Not a valid project: {0}',
    'proj.denied': 'That folder cannot be read. Check permissions.',
    'proj.empty': 'This project has no packages yet.',
    'proj.created': 'Project created in {0}',
    'proj.verifyFailed': 'The folder was created but could not be verified: {0}',
    'proj.createFailed': 'The new project folder could not be verified.',
    'proj.stateFromQa': 'Summary rebuilt from the last QA report.',
    'proj.stateFromRun': 'Last run restored from run_state.json.',
    'proj.needFolder': 'Select a folder first.',
    'bc.badge.idle': 'Idle',
    'bc.badge.starting': 'Starting…',
    'bc.badge.connected': 'Connected',
    'bc.badge.error': 'Error',
    'bc.idle.title': 'BlueCode is stopped',
    'bc.idle.text': 'Start the local server to use BlueCode inside AURA QA.',
    'bc.start': 'Start BlueCode',
    'bc.cancel': 'Cancel',
    'bc.retry': 'Try again',
    'bc.starting.title': 'Starting BlueCode…',
    'bc.starting.text': 'This usually takes a few seconds.',
    'bc.step.launch': 'Launch server',
    'bc.step.address': 'Detect address',
    'bc.step.server': 'Wait for server',
    'bc.step.ui': 'Load interface',
    'bc.error.title': "Couldn't start BlueCode",
    'bc.error.exited': 'The server stopped unexpectedly (exit code {0}).',
    'bc.error.timeout': "The server didn't respond after {0} s. Check that BlueCode is installed and try again.",
    'bc.error.nobridge': 'BlueCode can only run inside the AURA QA window.',
    'bc.error.start': "Couldn't launch the process: {0}",
    'run.running': 'Running pipeline…',
    'run.currentPkg': 'Package',
    'run.currentItem': 'Item',
    'run.progress': 'Progress',
    'run.exitCode': 'exit code {0}',
    'run.issuesShort': '{0} issues',
    'run.etaRate': '{0} items/s · {1} of {2}',
    'run.etaUnknown': 'Remaining time unknown for this stage.',
    'run.status.idle': 'Idle',
    'run.status.running': 'Running',
    'run.status.done': 'Done',
    'run.status.error': 'Error',
    'run.status.cancelled': 'Cancelled',
    'dev.none': 'No device',
    'dev.unknown': 'Unknown',
    'dev.error': 'Error',
    'dev.connected': 'Connected',
    'dev.android': 'Android {0}',
    'device.os': 'Android {0}',
    'cfg.loadFailed': 'Could not read the configuration file.',
    'cfg.saveFailed': 'Could not save the configuration file.',
    'dev.infoFailed': 'Could not read the device info.'
  },
  es: {
    'export.images': 'Imágenes',
    'export.issues': 'Hallazgos',
    'export.hint.noProject': 'Abre un proyecto para exportar su reporte.',
    'export.hint.ready': 'Los conteos se actualizan al cambiar las opciones.',
    'export.hint.zero': 'Ningún resultado con estos filtros.',
    'export.destination': 'Destino',
    'export.folder': 'Carpeta',
    'export.browse': 'Elegir carpeta',
    'export.filename': 'Nombre del archivo',
    'export.addDate': 'Añadir la fecha de hoy',
    'export.include': 'Incluir',
    'export.screenshots': 'Capturas',
    'export.screenshotsSub': 'Miniaturas con los hallazgos marcados',
    'export.thumbSize': 'Tamaño de miniatura',
    'export.warnings': 'Advertencias OCR',
    'export.warningsSub': 'Añade una columna con el conteo por imagen',
    'export.onlyIssues': 'Solo imágenes con hallazgos',
    'export.onlyIssuesSub': 'Omite las imágenes sin hallazgos',
    'export.filters': 'Filtros',
    'export.packages': 'Paquete',
    'export.allPackages': 'Todos los paquetes ({0})',
    'export.severity': 'Severidad',
    'export.quality': 'Calidad',
    'sev.high': 'Alta',
    'sev.medium': 'Media',
    'sev.low': 'Baja',
    'q.excellent': 'Excelente',
    'q.good': 'Buena',
    'q.poor': 'Deficiente',
    'q.na': 'N/D',
    'export.run': 'Exportar a Excel',
    'export.running': 'Exportando…',
    'export.done': 'Reporte guardado',
    'export.doneDetail': '{0} imágenes · {1} hallazgos · {2}',
    'export.openFile': 'Abrir archivo',
    'export.openFolder': 'Ver en carpeta',
    'export.err.title': 'No se pudo exportar',
    'export.err.locked': 'El archivo está abierto en otro programa (probablemente Excel). Ciérralo e inténtalo de nuevo.',
    'export.err.no_rows': 'No hay nada que exportar con los filtros actuales.',
    'export.err.no_project': 'No hay ningún proyecto abierto.',
    'export.err.bad_destination': 'No se puede crear o escribir la carpeta de destino.',
    'export.err.deps': 'Falta una dependencia de Python (openpyxl / Pillow): {0}',
    'export.err.generic': 'Error inesperado: {0}',
    'export.err.noBridge': 'La exportación solo funciona dentro de la ventana de AURA QA.',
    'recent.notFound': 'Esa carpeta ya no existe.',
    'new.err': 'No se pudo crear el nuevo proyecto.',
    'new.exists': 'Ya existe un proyecto con ese nombre en esa carpeta.',
    'proj.opened': 'Proyecto "{0}" listo.',
    'proj.invalid': 'No es un proyecto válido: {0}',
    'proj.denied': 'Esa carpeta no se puede leer. Revisa los permisos.',
    'proj.empty': 'Este proyecto todavía no tiene paquetes.',
    'proj.created': 'Proyecto creado en {0}',
    'proj.verifyFailed': 'La carpeta se creó pero no se pudo verificar: {0}',
    'proj.createFailed': 'No se pudo verificar la carpeta del proyecto nuevo.',
    'proj.stateFromQa': 'Resumen reconstruido desde el último reporte de QA.',
    'proj.stateFromRun': 'Última ejecución restaurada desde run_state.json.',
    'proj.needFolder': 'Selecciona una carpeta primero.',
    'bc.badge.idle': 'Detenido',
    'bc.badge.starting': 'Iniciando…',
    'bc.badge.connected': 'Conectado',
    'bc.badge.error': 'Error',
    'bc.idle.title': 'BlueCode está detenido',
    'bc.idle.text': 'Inicia el servidor local para usar BlueCode dentro de AURA QA.',
    'bc.start': 'Iniciar BlueCode',
    'bc.cancel': 'Cancelar',
    'bc.retry': 'Reintentar',
    'bc.starting.title': 'Iniciando BlueCode…',
    'bc.starting.text': 'Suele tardar unos segundos.',
    'bc.step.launch': 'Lanzar el servidor',
    'bc.step.address': 'Detectar la dirección',
    'bc.step.server': 'Esperar al servidor',
    'bc.step.ui': 'Cargar la interfaz',
    'bc.error.title': 'No se pudo iniciar BlueCode',
    'bc.error.exited': 'El servidor se detuvo inesperadamente (código {0}).',
    'bc.error.timeout': 'El servidor no respondió tras {0} s. Comprueba que BlueCode esté instalado e inténtalo de nuevo.',
    'bc.error.nobridge': 'BlueCode solo puede ejecutarse dentro de la ventana de AURA QA.',
    'bc.error.start': 'No se pudo lanzar el proceso: {0}',
    'run.running': 'Ejecutando pipeline…',
    'run.currentPkg': 'Paquete',
    'run.currentItem': 'Elemento',
    'run.progress': 'Progreso',
    'run.exitCode': 'código de salida {0}',
    'run.issuesShort': '{0} hallazgos',
    'run.etaRate': '{0} elem/s · {1} de {2}',
    'run.etaUnknown': 'Tiempo restante desconocido en esta etapa.',
    'run.status.idle': 'En reposo',
    'run.status.running': 'Ejecutando',
    'run.status.done': 'Completado',
    'run.status.error': 'Error',
    'run.status.cancelled': 'Cancelado',
    'dev.none': 'Sin dispositivo',
    'dev.unknown': 'Desconocido',
    'dev.error': 'Error',
    'dev.connected': 'Conectado',
    'dev.android': 'Android {0}',
    'device.os': 'Android {0}',
    'cfg.loadFailed': 'No se pudo leer el archivo de configuración.',
    'cfg.saveFailed': 'No se pudo guardar el archivo de configuración.',
    'dev.infoFailed': 'No se pudo leer la información del dispositivo.'
  }
};

function uiLang() {
  const el = document.getElementById('setting-ui-language');
  const v = el && el.value;
  return VALID_LANGS.indexOf(v) !== -1 ? v : 'en';
}

function xt(key, ...args) {
  const lang = uiLang();
  const DATA = window.I18N_DATA || {};
  let str = null;
  if (DATA[lang] && DATA[lang][key] != null) str = DATA[lang][key];
  else if (DATA.en && DATA.en[key] != null) str = DATA.en[key];
  else if (XT[lang] && XT[lang][key] != null) str = XT[lang][key];
  else if (XT.en && XT.en[key] != null) str = XT.en[key];
  else str = key;
  args.forEach((a, i) => {
    str = str.split('{' + i + '}').join(a == null ? '' : a);
  });
  return str;
}

// Compatibilidad segura con I18N.t / I18N.apply usada por statehub/dialogs.
// Si ya existe un I18N real, se respeta. Si no, se crea un shim mínimo.
window.I18N = window.I18N || {
  current: 'en',
  apply(lang) {
    this.current = VALID_LANGS.indexOf(lang) !== -1 ? lang : 'en';
  },
  t(key, ...args) {
    const lang = this.current || uiLang();
    const data = window.I18N_DATA || {};
    let str = null;

    if (data[lang] && data[lang][key] != null) str = data[lang][key];
    else if (data.en && data.en[key] != null) str = data.en[key];
    else if (XT[lang] && XT[lang][key] != null) str = XT[lang][key];
    else if (XT.en && XT.en[key] != null) str = XT.en[key];
    else str = key;

    args.forEach((a, i) => {
      str = str.split('{' + i + '}').join(a == null ? '' : a);
    });
    return str;
  }
};

function tAny(key, ...args) {
  try {
    if (window.I18N && typeof window.I18N.t === 'function') {
      return window.I18N.t(key, ...args);
    }
  } catch (e) {}
  return xt(key, ...args);
}

function applyExtraI18n() {
  document.querySelectorAll('[data-xt]').forEach(el => {
    el.textContent = xt(el.dataset.xt);
  });
  document.querySelectorAll('[data-xt-title]').forEach(el => {
    el.title = xt(el.dataset.xtTitle);
  });
  document.querySelectorAll('[data-xt-ph]').forEach(el => {
    el.placeholder = xt(el.dataset.xtPh);
  });
  document.querySelectorAll('[data-xt-aria]').forEach(el => {
    el.setAttribute('aria-label', xt(el.dataset.xtAria));
  });

  if (typeof window.pkApplyI18n === 'function') {
    try {
      window.pkApplyI18n();
    } catch (e) {}
  }
}

function showToast(message, kind = 'success', delay = 2500) {
  const toastEl = document.getElementById('settings-toast');
  if (!toastEl) return;
  const bodySpan = toastEl.querySelector('.toast-body span');
  if (bodySpan) bodySpan.textContent = message;
  toastEl.className = `toast align-items-center text-bg-${kind} border-0`;
  if (window.bootstrap && bootstrap.Toast) {
    bootstrap.Toast.getOrCreateInstance(toastEl, { delay }).show();
  }
}

// Bug #2 corregido: escape HTML real.
function qaEsc(s) {
  return String(s == null ? '' : s).replace(/[&<>"']/g, c => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;'
  }[c]));
}

applyExtraI18n();

function safeElement(id) {
  return document.getElementById(id);
}

function safeValue(id) {
  const el = safeElement(id);
  return el ? el.value : '';
}

function safeChecked(id) {
  const el = safeElement(id);
  return el ? !!el.checked : false;
}

function intVal(id) {
  const el = safeElement(id);
  if (!el) return null;
  const v = el.value;
  if (v === '' || v == null) return null;
  const n = parseInt(v, 10);
  return isNaN(n) ? null : n;
}

function floatVal(id) {
  const el = safeElement(id);
  if (!el) return null;
  const v = el.value;
  if (v === '' || v == null) return null;
  const n = parseFloat(v);
  return isNaN(n) ? null : n;
}

async function loadSettings() {
  if (hasPywebview()) {
    try {
      const data = await window.pywebview.api.loadConfig();
      if (data) return JSON.parse(data);
    } catch (e) {
      console.warn('[AURA QA] ' + xt('cfg.loadFailed'), e);
    }
  }
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY)) || {};
  } catch (e) {
    return {};
  }
}

async function saveSettings(settings) {
  const json = JSON.stringify(settings, null, 2);
  if (hasPywebview()) {
    try {
      const ok = await window.pywebview.api.saveConfig(json);
      if (ok) return true;
      console.warn('[AURA QA] ' + xt('cfg.saveFailed') + ' (saveConfig -> false)');
    } catch (e) {
      console.warn('[AURA QA] ' + xt('cfg.saveFailed'), e);
    }
  }
  try {
    localStorage.setItem(STORAGE_KEY, json);
    return true;
  } catch (e) {
    console.warn('[AURA QA] ' + xt('cfg.saveFailed'), e);
    return false;
  }
}

async function persistCurrent() {
  return saveSettings(collectSettings());
}

function applyTheme(themeName) {
  const theme = themes[themeName];
  if (!theme) return;
  const root = document.documentElement;
  for (const [prop, val] of Object.entries(theme)) {
    root.style.setProperty(prop, val);
  }
  document.querySelectorAll('.theme-card').forEach(c => c.classList.remove('active'));
  const card = document.querySelector(`.theme-card[data-theme="${themeName}"]`);
  if (card) card.classList.add('active');
}

function applyAccent(color) {
  document.documentElement.style.setProperty('--accent-blue', color);
  document.documentElement.style.setProperty(
    '--accent-blue-hover',
    `color-mix(in srgb, ${color} 85%, white)`
  );
  document.querySelectorAll('.accent-swatch').forEach(s => s.classList.remove('active'));
  const swatch = document.querySelector(`.accent-swatch[data-accent="${color}"]`);
  if (swatch) swatch.classList.add('active');
}

function applySettings(settings) {
  if (settings.theme) applyTheme(settings.theme);
  if (settings.accent) applyAccent(settings.accent);

  const col = document.querySelector('.sidebar-col');
  if (col) {
    if (settings.sidebarMode === 'collapsed') col.classList.add('collapsed');
    else if (settings.sidebarMode === 'expanded') col.classList.remove('collapsed');
  }

  document.body.classList.toggle('compact-mode', !!settings.compact);
  document.body.classList.toggle('no-animations', settings.animations === false);
}

function collectSettings() {
  const s = {};

  const activeTheme = document.querySelector('.theme-card.active');
  if (activeTheme) s.theme = activeTheme.dataset.theme;

  const activeAccent = document.querySelector('.accent-swatch.active');
  if (activeAccent) s.accent = activeAccent.dataset.accent;

  const sidebarModeEl = safeElement('setting-sidebar-mode');
  s.sidebarMode = sidebarModeEl ? sidebarModeEl.value : 'expanded';
  s.compact = safeChecked('setting-compact');
  s.animations = safeChecked('setting-animations');
  s.uiLanguage = uiLang();
  s.psdnsEnabled = psdnsEnabled();

  s.pipeline = {
    filterT: safeValue('pipe-filter-t').split('\n').map(x => x.trim()).filter(Boolean),
    filterE: safeValue('pipe-filter-e').split('\n').map(x => x.trim()).filter(Boolean),
    pairSource: safeValue('pipe-pair-source'),
    pairTarget: safeValue('pipe-pair-target'),
    maxDepth: intVal('pipe-max-depth'),
    maxScroll: intVal('pipe-max-scroll'),
    speedFactor: floatVal('pipe-speed'),
    similarityThreshold: floatVal('pipe-similarity'),
    ghostThreshold: floatVal('pipe-ghost'),
    maxBack: intVal('pipe-max-back'),
    maxRelaunch: intVal('pipe-max-relaunch'),
    marginTop: floatVal('pipe-margin-top'),
    marginBottom: floatVal('pipe-margin-bottom'),
    marginLeft: floatVal('pipe-margin-left'),
    marginRight: floatVal('pipe-margin-right'),
    duration: floatVal('pipe-duration'),
    sleepStable: floatVal('pipe-sleep-stable'),
    sleepBack: floatVal('pipe-sleep-back'),
    sleepExit: floatVal('pipe-sleep-exit'),
    sleepStart: floatVal('pipe-sleep-start'),
    enableCapture: safeChecked('pipe-enable-capture'),
    rootName: safeValue('pipe-root-name').trim(),
    docOrientation: safeChecked('pipe-doc-orientation'),
    docUnwarping: safeChecked('pipe-doc-unwarping'),
    textlineOrientation: safeChecked('pipe-textline-orientation'),
    bcHost: safeValue('pipe-bc-host').trim(),
    bcPort: intVal('pipe-bc-port'),
    bcTimeout: intVal('pipe-bc-timeout'),
    qaPasses: intVal('pipe-qa-passes')
  };

  return s;
}

function syncControls(settings) {
  const sidebarModeEl = safeElement('setting-sidebar-mode');
  if (sidebarModeEl && settings.sidebarMode) sidebarModeEl.value = settings.sidebarMode;

  const compactEl = safeElement('setting-compact');
  if (compactEl) compactEl.checked = !!settings.compact;

  const animEl = safeElement('setting-animations');
  if (animEl) animEl.checked = settings.animations !== false;

  const langEl = safeElement('setting-ui-language');
  if (langEl) {
    langEl.value =
      settings.uiLanguage && VALID_LANGS.indexOf(settings.uiLanguage) !== -1
        ? settings.uiLanguage
        : 'en';
  }

  const psdnsEl = safeElement('psdns-enabled');
  if (psdnsEl) psdnsEl.checked = !!settings.psdnsEnabled;

  const p = settings.pipeline;
  if (!p) return;

  const setVal = (id, v) => {
    const el = safeElement(id);
    if (el && v != null && !isNaN(v)) el.value = v;
  };

  const setTxt = (id, v) => {
    const el = safeElement(id);
    if (el && v != null) el.value = v;
  };

  const setChk = (id, v) => {
    const el = safeElement(id);
    if (el) el.checked = !!v;
  };

  if (p.filterT) setTxt('pipe-filter-t', p.filterT.join('\n'));
  if (p.filterE) setTxt('pipe-filter-e', p.filterE.join('\n'));
  if (p.pairSource) setTxt('pipe-pair-source', p.pairSource);
  if (p.pairTarget) setTxt('pipe-pair-target', p.pairTarget);

  setVal('pipe-max-depth', p.maxDepth);
  setVal('pipe-max-scroll', p.maxScroll);
  setVal('pipe-speed', p.speedFactor);
  setVal('pipe-similarity', p.similarityThreshold);
  setVal('pipe-ghost', p.ghostThreshold);
  setVal('pipe-max-back', p.maxBack);
  setVal('pipe-max-relaunch', p.maxRelaunch);
  setVal('pipe-margin-top', p.marginTop);
  setVal('pipe-margin-bottom', p.marginBottom);
  setVal('pipe-margin-left', p.marginLeft);
  setVal('pipe-margin-right', p.marginRight);
  setVal('pipe-duration', p.duration);

  // Bug #20 corregido: ID correcto sin espacio.
  setVal('pipe-sleep-stable', p.sleepStable);
  setVal('pipe-sleep-back', p.sleepBack);
  setVal('pipe-sleep-exit', p.sleepExit);
  setVal('pipe-sleep-start', p.sleepStart);

  setChk('pipe-enable-capture', p.enableCapture !== false);
  if (p.rootName != null) setTxt('pipe-root-name', p.rootName);

  setChk('pipe-doc-orientation', !!p.docOrientation);
  setChk('pipe-doc-unwarping', !!p.docUnwarping);
  setChk('pipe-textline-orientation', !!p.textlineOrientation);

  if (p.bcHost != null) setTxt('pipe-bc-host', p.bcHost);
  setVal('pipe-bc-port', p.bcPort);
  setVal('pipe-bc-timeout', p.bcTimeout);
  setVal('pipe-qa-passes', p.qaPasses);
}

let deviceUpdating = false;

async function updateDeviceWidget() {
  if (deviceUpdating) return;
  deviceUpdating = true;
  try {
    await _updateDeviceWidget();
  } finally {
    deviceUpdating = false;
  }
}

async function _updateDeviceWidget() {
  const setText = (id, val) => {
    const el = document.getElementById(id);
    if (el) el.textContent = val || '--';
  };

  let info = null;
  let failed = false;

  if (hasPywebview()) {
    try {
      info = await window.pywebview.api.getDeviceInfo();
    } catch (e) {
      console.warn('[AURA QA] ' + xt('dev.infoFailed'), e);
      failed = true;
    }
  }

  const connected = !!(info && info.connected);
  const modelText = connected
    ? info.model || xt('dev.unknown')
    : failed
      ? xt('dev.error')
      : xt('dev.none');

  const osText = connected && info.release ? tAny('device.os', info.release) : '--';

  document.querySelectorAll('.badge-dut').forEach(b => {
    b.textContent = connected ? xt('dev.connected') : modelText;
    b.classList.toggle('badge-connected', connected);
  });

  setText('device-model', modelText);
  setText('device-os', osText);

  setText('hero-model', modelText);
  setText('hero-os', osText);

  setText('spec-model', modelText);
  setText('spec-release', osText);
  setText('spec-build', connected && info.build_id);
  setText('spec-language', connected && info.language);
  setText('spec-resolution', connected && info.resolution);
  setText('spec-density', connected && info.density);
  setText('spec-serial', connected && info.serial);

  psdnsOnDeviceChange(connected && info.serial);
}

// ============================================================
// Device checks (Assisted mapping panel)
// ============================================================

const DC_SHORT = {
  usbDebug: 'dc.usbDebug',
  stayOn: 'dc.stayOn',
  screenTimeout: 'dc.screenTimeout',
  rotationLocked: 'dc.rotationLocked',
  showTouches: 'dc.showTouches',
  windowAnim: 'dc.windowAnim',
  transitionAnim: 'dc.transitionAnim',
  animatorScale: 'dc.animatorScale'
};

function dcSettingNumber(value) {
  if (value === null || value === undefined) return null;
  const text = String(value).trim();
  if (text === '' || text === 'null') return null;
  const number = Number(text);
  return Number.isFinite(number) ? number : null;
}

function dcFormatToggle(value) {
  const n = dcSettingNumber(value);
  if (n === 1) return 'ON';
  if (n === 0) return 'OFF';
  return '\u2014';
}

function dcFormatAnimation(value) {
  const n = dcSettingNumber(value);
  if (n === null || n < 0) return '\u2014';
  return n === 0 ? 'OFF' : n + 'x';
}

const DC_FMT = {
  usbDebug: dcFormatToggle,
  stayOn: value => {
    const n = dcSettingNumber(value);
    if (n === null || !Number.isInteger(n) || n < 0) return '\u2014';
    if (n === 0) return 'OFF';
    const parts = [];
    if (n & 1) parts.push('AC');
    if (n & 2) parts.push('USB');
    if (n & 4) parts.push('Wireless');
    const other = n & ~7;
    if (other || !parts.length) parts.push('Mask ' + n);
    return parts.join('+');
  },
  windowAnim: dcFormatAnimation,
  transitionAnim: dcFormatAnimation,
  animatorScale: dcFormatAnimation,
  screenTimeout: value => {
    const ms = dcSettingNumber(value);
    if (ms === null || ms < 0) return '\u2014';
    if (ms >= 2147483647) return 'Max';
    if (ms < 60000) return Math.round(ms / 1000) + ' s';
    return Math.round(ms / 60000) + ' min';
  },
  rotationLocked: value => {
    const n = dcSettingNumber(value);
    if (n === 0) return 'Locked';
    if (n === 1) return 'Auto ON';
    return '\u2014';
  },
  showTouches: dcFormatToggle
};

const dcEsc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

function dcRender(data) {
  const strip = document.getElementById('dc-strip');
  const btnApply = document.getElementById('dc-apply');
  const btnReset = document.getElementById('dc-reset');
  if (!strip) return;

  strip.innerHTML = '';

  data.checks.forEach(c => {
    const state = c.pass === true ? 'ok' : c.pass === false ? 'fail' : 'none';
    const cell = document.createElement('div');
    cell.className = 'dc-cell is-' + state;

    const displayVal = DC_FMT[c.id]
      ? DC_FMT[c.id](c.value)
      : (c.value !== null && c.value !== undefined && c.value !== 'null' ? c.value : '\u2014');

    const details = [
      c.label || c.id,
      'Valor le\u00eddo: ' + (c.value != null ? c.value : 'sin respuesta'),
      c.error ? 'Error: ' + c.error : '',
      c.tip ? tAny(c.tip) : '',
      'La lectura del ajuste no confirma su efecto visual.'
    ];
    cell.title = details.filter(Boolean).join('\n');

    cell.innerHTML =
      '<span class="dc-cell-label">' + dcEsc(tAny(DC_SHORT[c.id] || c.id)) + '</span>' +
      '<span class="dc-cell-value">' + dcEsc(displayVal) + '</span>';

    strip.appendChild(cell);
  });

  if (btnApply) btnApply.disabled = !data.connected;
  if (btnReset) btnReset.disabled = !data.connected;
}

let dcOperationInProgress = false;
let dcRequestVersion = 0;
let dcLastLoad = 0;
const DC_LOAD_THROTTLE = 2000;

function dcShowError(message) {
  if (typeof showToast === 'function') showToast(message, 'danger', 5000);
}

function dcSetButtonsDisabled(disabled) {
  const a = document.getElementById('dc-apply');
  const r = document.getElementById('dc-reset');
  if (a) a.disabled = disabled;
  if (r) r.disabled = disabled;
}

async function dcApiCall(method) {
  if (!hasPywebview()) throw new Error('pywebview no disponible');
  const result = await window.pywebview.api[method]();
  if (!result || typeof result !== 'object') throw new Error('Respuesta inesperada del servidor');
  return result;
}

async function dcLoad(force) {
  if (dcOperationInProgress) return;
  if (!hasPywebview()) return;
  const now = Date.now();
  if (!force && now - dcLastLoad < DC_LOAD_THROTTLE) return;
  dcLastLoad = now;
  const version = ++dcRequestVersion;
  try {
    const data = await dcApiCall('getDeviceChecks');
    if (version !== dcRequestVersion || dcOperationInProgress) return;
    if (!Array.isArray(data.checks)) throw new Error(data.msg || 'Respuesta sin checks');
    dcRender(data);
    dcSetButtonsDisabled(!data.connected);
  } catch (error) {
    if (version !== dcRequestVersion || dcOperationInProgress) return;
    dcShowError(error.message || 'No se pudo consultar el dispositivo');
    dcSetButtonsDisabled(true);
  }
}

async function dcRunOperation(method, btn) {
  if (dcOperationInProgress) return;
  dcOperationInProgress = true;
  ++dcRequestVersion;
  let connected = false;
  dcSetButtonsDisabled(true);
  if (btn) btn.classList.add('is-loading');
  try {
    const data = await dcApiCall(method);
    const hasState = data.state && Array.isArray(data.state.checks);
    if (hasState) {
      dcRender(data.state);
      connected = Boolean(data.state.connected);
      dcSetButtonsDisabled(true);
    }
    if (data.ok !== true) {
      const failed = Array.isArray(data.failed) ? data.failed.join(', ') : '';
      const message = data.msg || 'No se complet\u00f3 la operaci\u00f3n';
      dcShowError(failed ? message + ' \u2014 ' + failed : message);
      console.error('Diagn\u00f3stico ADB:', data);
    } else if (!hasState) {
      throw new Error('El servidor no devolvi\u00f3 el estado final');
    }
  } catch (error) {
    dcShowError(error.message || 'No se pudo completar la operaci\u00f3n');
    console.error('Error de comunicaci\u00f3n:', error);
  } finally {
    if (btn) btn.classList.remove('is-loading');
    dcOperationInProgress = false;
    dcSetButtonsDisabled(!connected);
  }
}

// Wire up device checks buttons
(function initDeviceChecks() {
  const btnApply = document.getElementById('dc-apply');
  const btnReset = document.getElementById('dc-reset');

  function confirmOp(op, btn) {
    if (typeof window.Popup !== 'object' || !window.Popup.confirm) {
      dcRunOperation(op, btn);
      return;
    }
    const body = document.createElement('div');
    const warn = document.createElement('div');
    warn.className = 'popup-warn';
    warn.textContent = tAny('dc.popup.warn');
    const manual = document.createElement('div');
    manual.textContent = tAny('dc.popup.manual');
    body.appendChild(warn);
    body.appendChild(manual);

    window.Popup.confirm({
      title: tAny('dc.popup.title'),
      body: body,
      okLabel: tAny('dc.popup.continue'),
      dismissable: false
    }).then(function (res) {
      if (res === 'ok') dcRunOperation(op, btn);
    });
  }

  if (btnApply) btnApply.addEventListener('click', () => confirmOp('applyDeviceChecks', btnApply));
  if (btnReset) btnReset.addEventListener('click', () => confirmOp('resetDeviceChecks', btnReset));

  // Load checks when the device tab is shown
  document.querySelectorAll('button[data-bs-target="#pane-device"]').forEach(btn => {
    btn.addEventListener('shown.bs.tab', () => dcLoad());
  });

  dcLoad();
  window.dcLoad = dcLoad;
})();

// ============================================================
// PSDNS visual overlay (never modifies textarea values)
// ============================================================

const PSDNS_TEXTAREAS = ['pipe-filter-t', 'pipe-filter-e', 'wz-filter-t', 'wz-filter-e'];

const psdnsState = {
  catalog: {},
  installed: null,
  installedSet: new Set(),
  byName: {},
  byPackage: {},
  serial: null,
  unverifiable: false
};

let psdnsTaskId = null;
let psdnsInputTimer = null;
const PSDNS_INPUT_DEBOUNCE_MS = 100;

function psdnsNormalizeName(value) {
  return String(value).trim().split(/\s+/).join(' ').toLowerCase();
}

function psdnsNormalizeLang(value) {
  let v = String(value || '').replace(/\x00/g, '').trim();
  if (!v) return 'default';
  v = v.toLowerCase().replace(/_/g, '-');
  if (v.indexOf('b+') === 0) v = v.slice(2).replace(/\+/g, '-');
  const parts = v.split('-');
  if (parts.length > 1 && parts[1].indexOf('r') === 0) {
    const region = parts[1].slice(1);
    if (region.length === 2 || /^\d+$/.test(region)) parts[1] = region;
  }
  const map = { in: 'id', iw: 'he', ji: 'yi' };
  parts[0] = map[parts[0]] || parts[0];
  return parts.join('-');
}

function psdnsBuildIndexes(catalog) {
  const byName = {};
  const byPackage = {};
  Object.keys(catalog || {}).forEach(pkg => {
    const translations = catalog[pkg];
    const labels = {};
    if (translations && typeof translations === 'object') {
      Object.keys(translations).forEach(lang => {
        const names = translations[lang];
        if (!Array.isArray(names)) return;
        names.forEach(name => {
          if (typeof name !== 'string' || !name.trim()) return;
          const key = psdnsNormalizeName(name);
          if (!key) return;
          if (!(key in labels)) labels[key] = name;
          if (!byName[key]) byName[key] = [];
          if (byName[key].indexOf(pkg) === -1) byName[key].push(pkg);
        });
      });
    }
    byPackage[pkg] = labels;
  });
  return { byName, byPackage };
}

function psdnsPickLabel(translations, lang) {
  const all = [];
  if (translations && typeof translations === 'object') {
    Object.keys(translations).forEach(k => {
      const names = translations[k];
      if (!Array.isArray(names)) return;
      names.forEach(n => {
        if (typeof n === 'string' && n.trim() && all.indexOf(n) === -1) all.push(n);
      });
    });
  }
  const norm = psdnsNormalizeLang(lang);
  const base = norm !== 'default' ? norm.split('-')[0] : null;

  function firstOf(key) {
    const names = translations ? translations[key] : null;
    if (Array.isArray(names)) {
      for (let i = 0; i < names.length; i++) {
        if (typeof names[i] === 'string' && names[i].trim()) return names[i];
      }
    }
    return null;
  }

  const order = [];
  [norm, base, 'default'].forEach(k => {
    if (k && order.indexOf(k) === -1) order.push(k);
  });
  for (let i = 0; i < order.length; i++) {
    const label = firstOf(order[i]);
    if (label) return { label, all };
  }
  return { label: null, all };
}

function psdnsValidateEntry(value, lang) {
  const st = psdnsState;
  const item = { entry: value, state: 'unknown', label: null, labels: [], candidates: [] };
  const inCatalog = Object.prototype.hasOwnProperty.call(st.catalog, value);
  const inInstalled = st.installedSet.has(value);

  if (inCatalog) {
    const pick = psdnsPickLabel(st.catalog[value], lang);
    item.label = pick.label || value;
    item.labels = pick.all;
    if (inInstalled) {
      item.state = 'known_package';
    } else {
      const associated = new Set();
      Object.keys(st.byPackage[value] || {}).forEach(key => {
        (st.byName[key] || []).forEach(p => associated.add(p));
      });
      const present = Array.from(associated).filter(p => st.installedSet.has(p)).sort();
      if (present.length === 1) {
        item.state = 'known_package';
        item.candidates = present;
      } else if (present.length > 1) {
        item.state = 'ambiguous';
        item.candidates = present;
      } else {
        item.state = 'pending_discovery';
      }
    }
  } else if (inInstalled) {
    item.state = 'pending_extraction';
  } else {
    const key = psdnsNormalizeName(value);
    const associated = st.byName[key] || [];
    const present = associated.filter(p => st.installedSet.has(p)).sort();
    if (present.length === 1) {
      item.state = 'known_name';
      item.candidates = present;
    } else if (present.length > 1) {
      item.state = 'ambiguous';
      item.candidates = present;
    } else if (associated.length > 0) {
      item.state = 'pending_discovery';
    } else {
      item.state = 'unknown';
    }
  }

  if (st.unverifiable) item.state = 'unverifiable';
  return item;
}

function psdnsSnapToEnd(ta) {
  const len = ta.value.length;
  ta.setSelectionRange(len, len);
  ta.scrollTop = ta.scrollHeight;
}

function psdnsResolveLine(line) {
  if (!line) return line;
  if (Object.prototype.hasOwnProperty.call(psdnsState.catalog, line)) return line;
  const key = psdnsNormalizeName(line);
  const pkgs = (psdnsState.byName[key] || []).slice().sort();
  if (pkgs.length === 1) return pkgs[0];
  return line;
}

function psdnsEnterEditMode(ta, lineIdx) {
  const lines = ta.value.split('\n');
  if (lineIdx < 0 || lineIdx >= lines.length - 1) return;
  ta._psdnsEditLine = lineIdx;
  ta._psdnsEditOriginal = lines[lineIdx];
  psdnsAnnotateAll();
}

function psdnsExitEditMode(ta, restore) {
  if (ta._psdnsEditLine == null) return;
  if (restore) {
    const lines = ta.value.split('\n');
    lines[ta._psdnsEditLine] = ta._psdnsEditOriginal;
    ta.value = lines.join('\n');
  }
  ta._psdnsEditLine = null;
  ta._psdnsEditOriginal = null;
  psdnsSnapToEnd(ta);
  psdnsAnnotateAll();
}

function psdnsAttachListHandlers(ta, list) {
  list.addEventListener('click', e => {
    const row = e.target.closest('.psdns-row');
    if (!row) return;
    const idx = parseInt(row.dataset.idx, 10);
    const lines = ta.value.split('\n');
    const lastIdx = lines.length - 1;

    if (e.target.closest('.psdns-trash')) {
      if (idx === lastIdx) return;
      ta._psdnsSkipBlur = true;
      const pkg = lines[idx];
      const label = psdnsValidateEntry(pkg, psdnsLang()).label || pkg;
      if (typeof window.Popup === 'object' && window.Popup.confirm) {
        const body = document.createElement('div');
        body.appendChild(document.createTextNode(tAny('psdns.deleteConfirmPrefix')));
        const b = document.createElement('b');
        b.textContent = label;
        body.appendChild(b);
        body.appendChild(document.createTextNode(tAny('psdns.deleteConfirmSuffix')));
        window.Popup.confirm({
          title: tAny('psdns.deleteTitle'),
          body: body,
          okLabel: tAny('psdns.delete'),
          cancelLabel: tAny('psdns.cancel'),
          danger: true
        }).then(res => {
          if (res === 'ok') {
            const ls = ta.value.split('\n');
            ls.splice(idx, 1);
            ta.value = ls.join('\n');
            psdnsAnnotateAll();
            psdnsFocusActive(ta, list);
          }
        });
      }
      return;
    }

    if (idx === lastIdx) {
      const inp = row.querySelector('.psdns-input');
      if (inp) inp.focus();
      return;
    }

    if (ta._psdnsEditLine === idx) return;
    if (lines[idx].trim()) psdnsEnterEditMode(ta, idx);
  });

  list.addEventListener('dblclick', e => {
    const row = e.target.closest('.psdns-row');
    if (!row) return;
    const idx = parseInt(row.dataset.idx, 10);
    const lines = ta.value.split('\n');
    const lastIdx = lines.length - 1;
    if (idx === lastIdx) return;
    if (ta._psdnsEditLine === idx) return;
    if (lines[idx].trim()) psdnsEnterEditMode(ta, idx);
  });

  list.addEventListener('input', e => {
    if (!(e.target.classList && e.target.classList.contains('psdns-input'))) return;
    const row = e.target.closest('.psdns-row');
    if (!row) return;
    const idx = parseInt(row.dataset.idx, 10);
    const lines = ta.value.split('\n');
    if (idx < 0 || idx >= lines.length) return;
    lines[idx] = e.target.value;
    ta.value = lines.join('\n');
    const line = e.target.value.trim();
    const item = line ? psdnsValidateEntry(line, psdnsLang()) : null;
    const isWarn = item && (item.state === 'unknown' || item.state === 'unverifiable');
    if (psdnsEnabled()) {
      const nameEl = row.querySelector('.psdns-name');
      if (nameEl) {
        nameEl.textContent = '';
        if (item) {
          if (isWarn) {
            const w = document.createElement('span');
            w.className = 'psdns-warn-inline';
            w.textContent = '\u26A0 ' + tAny('psdns.notIndexed');
            nameEl.appendChild(w);
          } else if (item.label && item.label !== item.entry) {
            nameEl.textContent = item.label;
          }
        }
      }
    } else {
      let warnEl = row.querySelector('.psdns-warn');
      if (isWarn) {
        if (!warnEl) {
          warnEl = document.createElement('span');
          warnEl.className = 'psdns-warn';
          row.insertBefore(warnEl, row.querySelector('.psdns-trash') || null);
        }
        warnEl.textContent = '\u26A0 ' + tAny('psdns.notIndexed');
      } else if (warnEl) {
        warnEl.remove();
      }
    }
  });

  list.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey && !e.ctrlKey && !e.altKey && !e.metaKey) {
      e.preventDefault();
      const row = e.target.closest('.psdns-row');
      if (!row) return;
      const idx = parseInt(row.dataset.idx, 10);
      const lines = ta.value.split('\n');
      const lastIdx = lines.length - 1;
      const val = e.target.value.trim();
      if (idx === lastIdx) {
        if (val) {
          lines[idx] = psdnsResolveLine(val);
          lines.push('');
          ta.value = lines.join('\n');
          psdnsAnnotateAll();
          psdnsFocusActive(ta, list);
        }
      } else {
        if (val) {
          lines[idx] = psdnsResolveLine(val);
        } else {
          lines.splice(idx, 1);
        }
        ta.value = lines.join('\n');
        ta._psdnsEditLine = null;
        ta._psdnsEditOriginal = null;
        psdnsAnnotateAll();
        psdnsFocusActive(ta, list);
      }
    } else if (e.key === 'Escape' && ta._psdnsEditLine != null) {
      e.preventDefault();
      psdnsExitEditMode(ta, true);
      psdnsFocusActive(ta, list);
    }
  });

  list.addEventListener('focusout', e => {
    if (!psdnsEnabled()) return;
    if (ta._psdnsSkipBlur) {
      ta._psdnsSkipBlur = false;
      return;
    }
    if (ta._psdnsEditLine != null) {
      const related = e.relatedTarget;
      if (related && list.contains(related)) return;
      psdnsExitEditMode(ta, true);
    }
  });
}

function psdnsFocusActive(ta, list) {
  const lines = ta.value.split('\n');
  const lastIdx = lines.length - 1;
  const row = list.querySelector('.psdns-row[data-idx="' + lastIdx + '"]');
  if (row) {
    const inp = row.querySelector('.psdns-input');
    if (inp) {
      inp.focus();
      inp.setSelectionRange(inp.value.length, inp.value.length);
      list.scrollTop = list.scrollHeight;
    }
  }
}

function psdnsTrashIcon() {
  const NS = 'http://www.w3.org/2000/svg';
  const svg = document.createElementNS(NS, 'svg');
  svg.setAttribute('viewBox', '0 0 24 24');
  svg.setAttribute('fill', 'none');
  svg.setAttribute('stroke', 'currentColor');
  svg.setAttribute('stroke-width', '2');
  svg.setAttribute('stroke-linecap', 'round');
  svg.setAttribute('stroke-linejoin', 'round');
  const poly = document.createElementNS(NS, 'polyline');
  poly.setAttribute('points', '3 6 5 6 21 6');
  svg.appendChild(poly);
  const path = document.createElementNS(NS, 'path');
  path.setAttribute('d', 'M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2');
  svg.appendChild(path);
  const l1 = document.createElementNS(NS, 'line');
  l1.setAttribute('x1', '10'); l1.setAttribute('y1', '11'); l1.setAttribute('x2', '10'); l1.setAttribute('y2', '17');
  svg.appendChild(l1);
  const l2 = document.createElementNS(NS, 'line');
  l2.setAttribute('x1', '14'); l2.setAttribute('y1', '11'); l2.setAttribute('x2', '14'); l2.setAttribute('y2', '17');
  svg.appendChild(l2);
  return svg;
}

function psdnsEnsureOverlay(taId) {
  const ta = document.getElementById(taId);
  if (!ta) return null;
  let wrap = ta.closest('.psdns-wrap');
  if (!wrap) {
    wrap = document.createElement('div');
    wrap.className = 'psdns-wrap';
    ta.parentNode.insertBefore(wrap, ta);
    wrap.appendChild(ta);
  }
  let list = wrap.querySelector(':scope > .psdns-list');
  if (!list) {
    list = document.createElement('div');
    list.className = 'psdns-list';
    wrap.appendChild(list);
    psdnsAttachListHandlers(ta, list);
  }
  return list;
}

function psdnsEnabled() {
  // During the welcome wizard the settings panel doesn't exist yet; the
  // toggle lives in the wizard (wz-psdns-enabled). Otherwise use settings.
  if (wzActive) {
    const el = document.getElementById('wz-psdns-enabled');
    if (el) return el.checked;
  }
  const el = document.getElementById('psdns-enabled');
  return el ? el.checked : false;
}

// Exposed for tests / external inspection.
Object.defineProperty(window, 'wzActive', {
  get() { return wzActive; },
  set(v) { wzActive = !!v; }
});

function psdnsLang() {
  // During the welcome wizard the settings panel doesn't exist yet; the active
  // language lives in the wizard's own select (wz-lang). Otherwise use settings.
  if (wzActive) {
    const sel = document.getElementById('wz-lang');
    const v = sel && sel.value;
    if (v && VALID_LANGS.indexOf(v) !== -1) return v;
  }
  return uiLang();
}

function psdnsRenderOverlay(taId) {
  const ta = document.getElementById(taId);
  if (!ta) return;
  const enabled = psdnsEnabled();
  const list = psdnsEnsureOverlay(taId);
  if (!list) return;
  const wrap = ta.closest('.psdns-wrap');
  if (wrap) wrap.classList.add('psdns-active');
  list.classList.toggle('no-name', !enabled);

  const lang = psdnsLang();
  let lines = ta.value.split('\n');
  if (lines.length === 0 || lines[lines.length - 1] !== '') {
    lines.push('');
    ta.value = lines.join('\n');
  }
  const lastIdx = lines.length - 1;
  const inEdit = ta._psdnsEditLine != null;

  list.textContent = '';
  lines.forEach((raw, i) => {
    const row = document.createElement('div');
    row.className = 'psdns-row' + (i === ta._psdnsEditLine ? ' psdns-row-edit' : '');
    row.dataset.idx = i;

    const line = raw.trim();
    const item = line ? psdnsValidateEntry(line, lang) : null;
    const isWarn = item && (item.state === 'unknown' || item.state === 'unverifiable');

    const name = document.createElement('span');
    name.className = 'psdns-name';
    if (enabled && item) {
      if (isWarn) {
        const w = document.createElement('span');
        w.className = 'psdns-warn-inline';
        w.textContent = '\u26A0 ' + tAny('psdns.notIndexed');
        name.appendChild(w);
      } else if (item.label && item.label !== item.entry) {
        name.textContent = item.label;
      }
    }
    row.appendChild(name);

    const input = document.createElement('input');
    input.className = 'psdns-input';
    input.type = 'text';
    input.spellcheck = false;
    input.value = raw;
    const isActive = (i === lastIdx && !inEdit) || i === ta._psdnsEditLine;
    if (isActive) {
      input.disabled = false;
      if (i === lastIdx && !raw) input.placeholder = tAny('psdns.placeholder');
    } else {
      input.disabled = true;
    }
    row.appendChild(input);

    if (!enabled && isWarn) {
      const w = document.createElement('span');
      w.className = 'psdns-warn';
      w.textContent = '\u26A0 ' + tAny('psdns.notIndexed');
      row.appendChild(w);
    }

    if (enabled && item && item.candidates && item.candidates.length) {
      const cand = document.createElement('span');
      cand.className = 'psdns-cand';
      cand.textContent = '\u2192 ' + item.candidates.join(', ');
      row.appendChild(cand);
    }

    if (i !== lastIdx) {
      const del = document.createElement('button');
      del.className = 'psdns-trash';
      del.type = 'button';
      del.title = tAny('psdns.delete');
      del.appendChild(psdnsTrashIcon());
      row.appendChild(del);
    }

    list.appendChild(row);
  });
}

function psdnsAnnotateTextarea(taId) {
  psdnsRenderOverlay(taId);
}

function psdnsAnnotateAll() {
  PSDNS_TEXTAREAS.forEach(psdnsAnnotateTextarea);
}

async function psdnsRefresh() {
  if (!hasPywebview()) return;
  try {
    const res = await window.pywebview.api.refreshPsdns();
    if (!res) return;
    psdnsState.catalog = res.catalog || {};
    psdnsState.installed = res.installed;
    psdnsState.installedSet = new Set(res.installed || []);
    psdnsState.serial = res.serial || null;
    psdnsState.unverifiable = !res.ok;
    const idx = psdnsBuildIndexes(psdnsState.catalog);
    psdnsState.byName = idx.byName;
    psdnsState.byPackage = idx.byPackage;
    psdnsAnnotateAll();
  } catch (e) {
    console.warn('[AURA QA] psdnsRefresh failed', e);
  }
}

function psdnsOnDeviceChange(serial) {
  if (serial !== psdnsState.serial) psdnsRefresh();
}

function psdnsOnInput() {
  if (psdnsInputTimer) clearTimeout(psdnsInputTimer);
  psdnsInputTimer = setTimeout(psdnsAnnotateAll, PSDNS_INPUT_DEBOUNCE_MS);
}

async function psdnsUpdate() {
  if (!hasPywebview() || psdnsTaskId) return;
  const btn = document.getElementById('psdns-update-btn');
  try {
    const res = await window.pywebview.api.updatePsdns(null, false);
    if (res && res.ok) {
      psdnsTaskId = res.taskId;
      if (btn) btn.disabled = true;
      runLog(tAny('psdns.updating'), 'INFO');
    } else if (res && res.error === 'already_running') {
      psdnsTaskId = res.taskId;
      if (btn) btn.disabled = true;
    }
  } catch (e) {
    runLog(tAny('psdns.updateFailed') + ': ' + e, 'ERROR');
  }
}

async function psdnsTaskFinished() {
  psdnsTaskId = null;
  const btn = document.getElementById('psdns-update-btn');
  if (btn) btn.disabled = false;
  psdnsSyncUpdateBtn();
  await psdnsRefresh();
}

window.onPsdnsEvent = function (ev) {
  if (!ev || !ev.kind) return;
  if (ev.kind === 'progress') {
    runLog('[PSDNS] ' + (ev.message || ''), 'INFO');
    psdnsUpdateProgress(ev.message || '');
  } else if (ev.kind === 'done') {
    runLog(tAny('psdns.updated') + (ev.count != null ? ' (' + ev.count + ')' : ''), 'SUCCESS');
    psdnsHideProgress();
    psdnsTaskFinished();
  } else if (ev.kind === 'error') {
    runLog(tAny('psdns.updateFailed') + ': ' + (ev.message || ''), 'ERROR');
    psdnsHideProgress();
    psdnsTaskFinished();
  }
};

PSDNS_TEXTAREAS.forEach(id => {
  const el = document.getElementById(id);
  if (el) el.addEventListener('input', psdnsOnInput);
});

const psdnsUpdateBtn = document.getElementById('psdns-update-btn');
if (psdnsUpdateBtn) psdnsUpdateBtn.addEventListener('click', psdnsUpdate);

const BC_TIMEOUT_MS = 60000;
const BC_POLL_MS = 700;
const BC_STEPS = ['launch', 'address', 'server', 'ui'];

let bcPoll = null;
let bcRunning = false;
let bcStartedAt = 0;
let bcState = 'idle';
let bcOverlayOpts = {};

function bcSetBadge(key, connected) {
  const badge = document.getElementById('bluecode-badge');
  if (!badge) return;
  badge.textContent = xt('bc.badge.' + key);
  badge.classList.toggle('badge-connected', !!connected);
}

function bcSetSteps(active, failed) {
  const idx = active ? BC_STEPS.indexOf(active) : -1;
  BC_STEPS.forEach((name, i) => {
    const li = document.querySelector(`#bc-steps [data-step="${name}"]`);
    if (!li) return;

    let status = 'pending';
    if (idx !== -1) {
      if (i < idx) status = 'done';
      else if (i === idx) status = failed ? 'error' : 'active';
      else status = 'pending';
    }
    li.dataset.status = status;
  });
}

function bcSetOverlay(state, opts = {}) {
  bcState = state;
  bcOverlayOpts = opts;

  const overlay = document.getElementById('bluecode-overlay');
  if (!overlay) return;

  if (state === 'connected') {
    overlay.style.display = 'none';
    return;
  }

  overlay.style.display = '';
  overlay.dataset.state = state;

  const title = document.getElementById('bc-overlay-title');
  const text = document.getElementById('bc-overlay-text');
  const log = document.getElementById('bc-overlay-log');
  const action = document.getElementById('bc-overlay-action');
  const label = document.getElementById('bc-overlay-action-label');

  const failed = state === 'error' || state === 'exited';

  if (state === 'starting') {
    if (title) title.textContent = xt('bc.starting.title');
    if (text) text.textContent = xt('bc.starting.text');
  } else if (failed) {
    if (title) title.textContent = xt('bc.error.title');
    if (text) text.textContent = opts.message || '';
  } else {
    if (title) title.textContent = xt('bc.idle.title');
    if (text) text.textContent = xt('bc.idle.text');
    bcSetSteps(null);
  }

  if (log) {
    log.textContent = failed ? opts.log || '' : '';
    log.hidden = !(failed && opts.log);
  }

  if (label) {
    label.textContent = xt(state === 'starting' ? 'bc.cancel' : failed ? 'bc.retry' : 'bc.start');
  }

  if (action) {
    action.classList.toggle('welcome-btn-primary', state !== 'starting');
    action.classList.toggle('welcome-btn-secondary', state === 'starting');
  }
}

function bcStopPoll() {
  if (bcPoll) {
    clearTimeout(bcPoll);
    bcPoll = null;
  }
}

function bcFail(message, log, failedStep) {
  bcStopPoll();
  bcRunning = false;

  const st = document.querySelector('#bc-steps [data-status="active"]');
  if (st) bcSetSteps(st.dataset.step, true);
  else if (failedStep) bcSetSteps(failedStep, true);

  bcSetBadge('error');
  bcSetOverlay('error', { message, log });
}

async function bcStart() {
  if (!hasPywebview()) {
    bcFail(xt('bc.error.nobridge'), '', 'launch');
    return;
  }

  bcStopPoll();
  bcRunning = true;
  bcStartedAt = Date.now();

  bcSetBadge('starting');
  bcSetSteps('launch');
  bcSetOverlay('starting');

  let res;
  try {
    res = await window.pywebview.api.startBlueCode();
  } catch (e) {
    res = { ok: false, error: String(e) };
  }

  if (!bcRunning) return;
  if (!res || res.ok === false) {
    bcFail(xt('bc.error.start', (res && res.error) || '?'));
    return;
  }

  bcSetSteps('address');
  bcPollStatus();
}

async function bcPollStatus() {
  if (!bcRunning) return;

  let st;
  try {
    st = await window.pywebview.api.getBlueCodeStatus();
  } catch (e) {
    st = { state: 'exited', code: '?', log: String(e) };
  }

  if (!bcRunning) return;

  if (st.state === 'ready') {
    bcLoadFrame(st.url);
    return;
  }

  if (st.state === 'exited' || st.state === 'idle') {
    bcFail(xt('bc.error.exited', st.code != null ? st.code : '?'), st.log);
    return;
  }

  bcSetSteps(st.stage === 'wait_http' ? 'server' : 'address');

  if (Date.now() - bcStartedAt > BC_TIMEOUT_MS) {
    let log = '';
    try {
      const last = await window.pywebview.api.getBlueCodeStatus();
      log = last.log || '';
    } catch (e) {}
    try {
      await window.pywebview.api.stopBlueCode();
    } catch (e) {}

    bcFail(xt('bc.error.timeout', BC_TIMEOUT_MS / 1000), log);
    return;
  }

  bcPoll = setTimeout(bcPollStatus, BC_POLL_MS);
}

function bcLoadFrame(url) {
  const frame = document.getElementById('bluecode-frame');
  if (!frame) return;

  bcSetSteps('ui');

  const done = () => {
    if (!bcRunning || bcState === 'connected') return;
    frame.onload = null;
    bcStopPoll();
    bcSetBadge('connected', true);
    bcSetOverlay('connected');
    bcPoll = setTimeout(bcMonitor, 5000);
  };

  frame.onload = done;
  frame.src = url;
  bcPoll = setTimeout(done, 8000);
}

async function bcMonitor() {
  if (!bcRunning || bcState !== 'connected') return;

  let st = null;
  try {
    st = await window.pywebview.api.getBlueCodeStatus();
  } catch (e) {}

  if (!bcRunning) return;

  if (st && (st.state === 'exited' || st.state === 'idle')) {
    bcSetSteps('ui', true);
    bcFail(xt('bc.error.exited', st.code != null ? st.code : '?'), st.log);
    return;
  }

  bcPoll = setTimeout(bcMonitor, 5000);
}

function bcStop() {
  if (!hasPywebview()) return;

  bcStopPoll();
  bcRunning = false;

  const frame = document.getElementById('bluecode-frame');
  if (frame) {
    frame.onload = null;
    frame.src = 'about:blank';
  }

  try {
    window.pywebview.api.stopBlueCode();
  } catch (e) {}

  bcSetBadge('idle');
  bcSetOverlay('idle');
}

bindUi('btn-bc-start', 'click', bcStart);
bindUi('btn-bc-stop', 'click', bcStop);
bindUi('bc-overlay-action', 'click', () => {
  if (bcState === 'starting') bcStop();
  else bcStart();
});

bindUi('btn-bc-refresh', 'click', function () {
  this.classList.add('spinning');
  const frame = document.getElementById('bluecode-frame');
  if (bcRunning && bcState === 'connected' && frame && frame.src && frame.src !== 'about:blank') {
    frame.src = frame.src;
  }
  setTimeout(() => this.classList.remove('spinning'), 100);
});

bcSetBadge('idle');
bcSetOverlay('idle');

function unlockApp() {
  const root = document.querySelector('.app-root');
  if (root) root.removeAttribute('data-locked');
}

function hideWelcome() {
  const btn = document.querySelector('[data-bs-target="#pane-test"]');
  if (btn) btn.click();
}

function showWelcome() {
  const btn = document.querySelector('[data-bs-target="#pane-home"]');
  if (btn) btn.click();
}

let currentProject = null;
let qaData = null;
let qaState = { pkg: 'all', search: '', sort: 'issues_desc', detailList: null, detailPos: 0 };

// Carga completa de un proyecto abierto (recents, device, QA, run state, etc.).
async function restoreProject(path) {
  const absPath = String(path || '').trim();
  if (!absPath) return;

  unlockApp();
  hideWelcome();

  const out = document.getElementById('run-out');
  if (out) out.value = absPath;

  currentProject = absPath;

  setExportDefaults(absPath);
  resetRunState('idle');
  if (typeof window.ssSync === 'function') window.ssSync();

  try {
    const logRes = await window.pywebview.api.getProjectLog();
    if (logRes && logRes.ok && logRes.lines.length) {
      logRes.lines.forEach(line => {
        const parts = line.split('\t');
        runLog(parts.slice(2).join('\t'), parts[1] || 'INFO');
      });
    }
  } catch (e) {}

  await loadQaReport();
  refreshExportPreview();
  await restoreRunState();
  runRenderLivePanes();

  await Promise.all([loadRecentProjects(), updateDeviceWidget()]).catch(() => {});

  ssPendingCopyResume();
}

// Tras crear un proyecto desde "Start test" sin proyecto abierto, se guarda la
// intención de copiar la carpeta de screenshots (localStorage). Al restaurar el
// proyecto recién creado, se fija la carpeta/checkbox y se lanza la copia.
function ssPendingCopyResume() {
  let src = null;
  try {
    src = localStorage.getItem('aura-ss-pending-copy');
    if (src) localStorage.removeItem('aura-ss-pending-copy');
  } catch (e) {
    return;
  }
  if (!src) return;

  const chk = document.getElementById('run-from-screenshot');
  const folder = document.getElementById('run-screenshot-folder');
  if (chk) chk.checked = true;
  if (folder) folder.value = src;
  if (typeof window.ssSync === 'function') window.ssSync();

  if (typeof window.copyScreenshotFolder === 'function') {
    window.copyScreenshotFolder(src);
  }
}

// Tarea 2: doble verificación antes de dar un proyecto por abierto.
async function openAndLoad(path) {
  if (!hasPywebview()) return;

  const p = String(path || '').trim();
  if (!p) return;

  let opened = null;
  try {
    opened = await window.pywebview.api.openProject(p);
  } catch (e) {
    opened = null;
  }

  if (!opened || !opened.ok) {
    showToast(xt('proj.invalid', p), 'danger', 4000);
    await loadRecentProjects();
    return;
  }

  const absPath = opened.path || p;

  let listing = null;
  try {
    if (typeof window.pywebview.api.listDir === 'function') {
      listing = await window.pywebview.api.listDir(absPath);
    }
  } catch (e) {
    listing = null;
  }

  if (listing && !listing.ok) {
    showToast(
      listing.error === 'denied' ? xt('proj.denied') : xt('proj.invalid', absPath),
      'danger',
      4200
    );
    await loadRecentProjects();
    return;
  }

  location.reload();
}

// Bug #5 corregido: regex válidos para normalizar rutas.
function setExportDefaults(path) {
  const norm = String(path || '')
    .replace(/\\/g, '/')
    .replace(/\/+$/, '');

  const parts = norm.split('/');
  const name = parts.pop() || '';
  const dir = parts.join('/') || norm;

  setExportPath(dir);

  const f = document.getElementById('export-filename');
  if (f) f.value = name;

  hideExportResult();
}

function _timeAgo(ts) {
  if (!ts) return '';
  const diff = Date.now() / 1000 - ts;
  const m = Math.floor(diff / 60);
  if (m < 1) return 'just now';
  if (m < 60) return m + 'm ago';
  const h = Math.floor(m / 60);
  if (h < 24) return h + 'h ago';
  const d = Math.floor(h / 24);
  return d + 'd ago';
}

async function loadRecentProjects() {
  const list = document.getElementById('recent-projects-list');
  if (!hasPywebview() || !list) return;

  try {
    const projects = await window.pywebview.api.getRecentProjects();
    if (!projects || projects.length === 0) {
      list.innerHTML = '<div class="welcome-recent-empty">' + window.I18N.t('welcome.recentEmpty') + '</div>';
      return;
    }

    list.innerHTML = projects
      .slice(0, 7)
      .map(p => {
        const path = typeof p === 'string' ? p : p.path;
        const name = typeof p === 'string' ? String(p).split(/[\/\\]/).filter(Boolean).pop() : p.name;
        const mtime = (typeof p === 'object' && p.mtime) ? p.mtime : null;
        const modified = mtime
          ? '<span class="wr-modified">' + window.I18N.t('welcome.recentModified', _timeAgo(mtime)) + '</span>'
          : '';
        return `<div class="welcome-recent-item" data-project="${qaEsc(path)}" title="${qaEsc(path)}"><div class="wr-content"><span class="wr-name">${qaEsc(name)}</span><span class="wr-row"><span class="wr-path">${qaEsc(path)}</span>${modified}</span></div><button type="button" class="wr-remove" title="Remove from recent" aria-label="Remove from recent"><svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></button></div>`;
      })
      .join('');

    list.querySelectorAll('.welcome-recent-item').forEach(el => {
      el.addEventListener('click', () => openAndLoad(el.dataset.project));
      const rm = el.querySelector('.wr-remove');
      if (rm) {
        rm.addEventListener('click', async (ev) => {
          ev.stopPropagation();
          try {
            await window.pywebview.api.removeRecentProject(el.dataset.project);
          } catch (e) {
            console.warn('[AURA QA] removeRecentProject failed', e);
          }
          el.remove();
          if (!list.querySelector('.welcome-recent-item')) {
            list.innerHTML = '<div class="welcome-recent-empty">' + window.I18N.t('welcome.recentEmpty') + '</div>';
          }
        });
      }
    });
  } catch (e) {
    // Bug #22 corregido: no dejar el error silencioso.
    console.warn('[AURA QA] loadRecentProjects failed', e);
  }
}

const runChips = { t: [], e: [], o: [] };

function runChipRender(which) {
  const box = document.getElementById('run-chips-' + which);
  if (!box) return;

  box.innerHTML = '';

  runChips[which].forEach((val, i) => {
    const chip = document.createElement('span');
    chip.className = 'run-chip';
    chip.textContent = val;

    const x = document.createElement('button');
    x.type = 'button';
    x.className = 'run-chip-x';
    x.textContent = '\u00d7';
    x.addEventListener('click', () => {
      runChips[which].splice(i, 1);
      runChipRender(which);
    });

    chip.appendChild(x);
    box.appendChild(chip);
  });

  const taId = which === 't' ? 'pipe-filter-t' : which === 'e' ? 'pipe-filter-e' : null;
  if (taId) {
    const ta = document.getElementById(taId);
    if (ta) {
      const newValue = runChips[which].join('\n');
      if (ta.value !== newValue) {
        // Bug #16 mitigado: preservar selección/cursor en la medida de lo posible.
        const selStart = ta.selectionStart;
        const selEnd = ta.selectionEnd;
        ta.value = newValue;
        try {
          ta.setSelectionRange(selStart, selEnd);
        } catch (e) {}
      }
    }
  }
}

function runChipAdd(which, value) {
  value = (value || '').trim();
  if (!value) return;
  if (runChips[which].indexOf(value) === -1) {
    runChips[which].push(value);
    runChipRender(which);
  }
}

function runChipInit(which) {
  const input = document.getElementById('run-chips-' + which + '-input');
  if (!input) return;

  input.addEventListener('keydown', e => {
    if (e.key === 'Enter') {
      e.preventDefault();
      runChipAdd(which, input.value);
      input.value = '';
    }
  });
}

function runSyncFromSettings() {
  const src = document.getElementById('pipe-pair-source');
  const tgt = document.getElementById('pipe-pair-target');
  const pair = document.getElementById('run-pair');

  if (src && tgt && pair && src.value && tgt.value) {
    pair.value = src.value + '-' + tgt.value;
  }

  const ft = document.getElementById('pipe-filter-t');
  const fe = document.getElementById('pipe-filter-e');

  if (ft) runChips.t = ft.value.split('\n').map(x => x.trim()).filter(Boolean);
  if (fe) runChips.e = fe.value.split('\n').map(x => x.trim()).filter(Boolean);

  runChipRender('t');
  runChipRender('e');
  runChipRender('o');
}

function runCollectConfig() {
  const chk = id => {
    const el = document.getElementById(id);
    return el ? el.checked : false;
  };

  const stages = [];
  ['config', 'listing', 'crawl', 'qa', 'autoexport'].forEach(s => {
    const el = document.getElementById('run-stage-' + s);
    if (el && el.checked) stages.push(s);
  });

  const pairEl = document.getElementById('run-pair');
  const srcEl = document.getElementById('pipe-pair-source');
  const tgtEl = document.getElementById('pipe-pair-target');
  let pair = safeValue('run-pair').trim();
  if (!pair && srcEl && tgtEl && srcEl.value && tgtEl.value) {
    pair = srcEl.value + '-' + tgtEl.value;
    if (pairEl) pairEl.value = pair;
  }

  return {
    extOut: safeValue('run-out').trim() || (currentProject || ''),
    pair: pair,
    fromScreenshot: chk('run-from-screenshot'),
    filterT: runChips.t.slice(),
    filterE: runChips.e.slice(),
    filterO: runChips.o.slice(),
    stages,
    exportLang: uiLang(),
    pipeline: {
      maxDepth: intVal('pipe-max-depth'),
      maxScroll: intVal('pipe-max-scroll'),
      speedFactor: floatVal('pipe-speed'),
      similarityThreshold: floatVal('pipe-similarity'),
      ghostThreshold: floatVal('pipe-ghost'),
      maxBack: intVal('pipe-max-back'),
      maxRelaunch: intVal('pipe-max-relaunch'),
      marginTop: floatVal('pipe-margin-top'),
      marginBottom: floatVal('pipe-margin-bottom'),
      marginLeft: floatVal('pipe-margin-left'),
      marginRight: floatVal('pipe-margin-right'),
      duration: floatVal('pipe-duration'),
      sleepStable: floatVal('pipe-sleep-stable'),
      sleepBack: floatVal('pipe-sleep-back'),
      sleepExit: floatVal('pipe-sleep-exit'),
      sleepStart: floatVal('pipe-sleep-start'),
      enableCapture: chk('pipe-enable-capture'),
      rootName: safeValue('pipe-root-name').trim(),
      docOrientation: chk('pipe-doc-orientation'),
      docUnwarping: chk('pipe-doc-unwarping'),
      textlineOrientation: chk('pipe-textline-orientation'),
      bcHost: safeValue('pipe-bc-host').trim(),
      bcPort: intVal('pipe-bc-port'),
      bcTimeout: intVal('pipe-bc-timeout'),
      qaPasses: intVal('pipe-qa-passes')
    }
  };
}

function runSetStep(step, state) {
  const el = document.getElementById('run-step-' + step);
  if (!el) return;

  el.classList.remove('active', 'done', 'skipped', 'error');
  if (state) el.classList.add(state);
}

let runState = {
  status: 'idle',
  stage: null,
  current_package: null,
  current_item: null,
  current: 0,
  total_items: null,
  issues: 0,
  warnings: 0,
  elapsed: 0,
  exit_code: null,
  error: null,
  source: null,
  export: null
};

window.__counters = {
  status: 'idle',
  stage: null,
  current: 0,
  total: null,
  issues: 0,
  warnings: 0,
  elapsed: 0
};
let _runStartedAt = 0;

window.onCounters = function (ev) {
  if (!ev || typeof ev !== 'object') return;
  Object.assign(window.__counters, ev);
  if (typeof renderCounters === 'function') renderCounters();
};

let runStepIndex = -1;
let runPackages = [];

let keepState = {};

function resetRunState(status) {
  runState = {
    status: status || 'idle',
    stage: null,
    current_package: null,
    current_item: null,
    current: 0,
    total_items: null,
    issues: 0,
    warnings: 0,
    elapsed: 0,
    exit_code: null,
    error: null,
    source: null,
    export: null
  };
  keepState = {};
  etaReset();
}

function runFmtElapsed(sec) {
  sec = Math.max(0, Math.round(sec || 0));
  const h = Math.floor(sec / 3600);
  const m = Math.floor((sec % 3600) / 60);
  const s = sec % 60;
  const p = n => String(n).padStart(2, '0');
  return h > 0 ? h + ':' + p(m) + ':' + p(s) : p(m) + ':' + p(s);
}

const RUN_STATUS = {
  idle: { key: 'run.status.idle', cls: '' },
  running: { key: 'run.status.running', cls: 'badge-running' },
  done: { key: 'run.status.done', cls: 'badge-done' },
  error: { key: 'run.status.error', cls: 'badge-error' },
  cancelled: { key: 'run.status.cancelled', cls: 'badge-cancelled' }
};

function runStatusLabel(status) {
  return xt((RUN_STATUS[status] || RUN_STATUS.idle).key);
}

function runSetBadge(status) {
  const badge = document.getElementById('run-badge');
  if (!badge) return;

  badge.classList.remove('badge-running', 'badge-done', 'badge-error', 'badge-cancelled');
  const s = RUN_STATUS[status] || RUN_STATUS.idle;
  badge.textContent = xt(s.key);
  if (s.cls) badge.classList.add(s.cls);
}

function runSetRunning(running) {
  runSetBadge(running ? 'running' : 'idle');

  const start = document.getElementById('btn-run-start');
  const stop = document.getElementById('btn-run-stop');

  if (start) start.classList.toggle('d-none', running);
  if (stop) stop.classList.toggle('d-none', !running);
  if (typeof window.ssSync === 'function') window.ssSync();
}

// Tarea 5: ETA rehecho.
const ETA_WINDOW_MS = 120000;
let etaTracker = { stage: null, samples: [], rate: 0, total: null, running: false };

function etaReset() {
  etaTracker = { stage: null, samples: [], rate: 0, total: null, running: false };
}

function etaFeed(st) {
  if (!st || st.status !== 'running') {
    if (!st || st.status === 'idle') etaReset();
    else etaTracker.running = false;
    return;
  }

  if (!etaTracker.running) {
    etaReset();
    etaTracker.running = true;
  }

  const stage = st.stage || null;
  if (stage !== etaTracker.stage) {
    etaTracker.stage = stage;
    etaTracker.samples = [];
    etaTracker.rate = 0;
    etaTracker.total = null;
  }

  if (st.total_items != null && st.total_items > 0) etaTracker.total = st.total_items;

  const cur = Number(st.current) || 0;
  const now = Date.now();
  const last = etaTracker.samples[etaTracker.samples.length - 1];

  if (!last || last.c !== cur || now - last.t > 1500) {
    etaTracker.samples.push({ c: cur, t: now });
  }

  const cutoff = now - ETA_WINDOW_MS;
  while (etaTracker.samples.length > 2 && etaTracker.samples[0].t < cutoff) {
    etaTracker.samples.shift();
  }

  if (etaTracker.samples.length > 80) {
    etaTracker.samples.splice(0, etaTracker.samples.length - 80);
  }
}

function etaRemaining() {
  if (etaTracker.total == null || etaTracker.samples.length < 2) return null;

  const a = etaTracker.samples[0];
  const b = etaTracker.samples[etaTracker.samples.length - 1];

  const dt = (b.t - a.t) / 1000;
  const dc = b.c - a.c;

  if (dt <= 0.5 || dc <= 0) return null;

  const inst = dc / dt;
  etaTracker.rate = etaTracker.rate > 0 ? etaTracker.rate * 0.6 + inst * 0.4 : inst;

  if (etaTracker.rate <= 0) return null;

  const rem = (etaTracker.total - b.c) / etaTracker.rate;
  return isFinite(rem) && rem >= 0 ? rem : null;
}

function runFmtEta(st) {
  etaFeed(st);

  if (!st) return '--:--';
  if (st.status === 'done') return '00:00';
  if (st.status !== 'running') return '--:--';

  const rem = etaRemaining();
  const el = document.getElementById('device-elapsed');
  if (el) {
    el.title =
      rem == null
        ? xt('run.etaUnknown')
        : xt('run.etaRate', etaTracker.rate.toFixed(2), st.current || 0, etaTracker.total || '?');
  }

  return rem == null ? '--:--' : runFmtElapsed(rem);
}

// Tarea 5: el state poll no puede borrar con null lo que ya sabemos.
function runGuardState(st) {
  if (!st || typeof st !== 'object') return st;

  if (st.status !== 'running') {
    keepState = {};
    if (st.status === 'idle') etaReset();
    return st;
  }

  const guard = (k, field) => {
    if (st[field] == null || st[field] === '') {
      if (keepState[k] != null && keepState[k] !== '') st[field] = keepState[k];
    } else {
      keepState[k] = st[field];
    }
  };

  guard('total', 'total_items');
  guard('stage', 'stage');
  guard('cur', 'current');
  guard('pkg', 'current_package');
  guard('item', 'current_item');
  guard('issues', 'issues');
  guard('warn', 'warnings');

  return st;
}

function runUpdateWidget(st) {
  st = runGuardState(st);

  const step = document.getElementById('device-step');
  const statusEl = document.getElementById('device-status');
  const fill = document.querySelector('#device-widget .device-progress-fill');
  const bar = document.getElementById('device-progress');
  const eta = document.getElementById('device-elapsed');
  const issues = document.getElementById('device-issues');

  if (statusEl) statusEl.textContent = runStatusLabel(st ? st.status : 'idle');

  if (step) {
    step.textContent = st && st.status === 'running' && st.stage ? st.stage : '--';
  }

  if (fill) {
    const pct = st && st.total_items
      ? Math.min(100, Math.round((st.current / st.total_items) * 100))
      : 0;

    fill.classList.remove('indeterminate');

    if (st && st.status === 'running') {
      if (st.total_items) fill.style.width = pct + '%';
      else {
        fill.style.width = '100%';
        fill.classList.add('indeterminate');
      }
    } else if (st && st.status === 'done') {
      fill.style.width = '100%';
    } else if (st && (st.status === 'error' || st.status === 'cancelled')) {
      fill.style.width = (st.total_items ? pct : 0) + '%';
    } else {
      fill.style.width = '0%';
    }
  }

  if (bar) {
    bar.title = st && st.total_items ? st.current + ' / ' + st.total_items : '';
  }

  if (eta) eta.textContent = runFmtEta(st);

  if (issues) {
    const n = st ? st.issues || 0 : 0;
    issues.textContent = xt('run.issuesShort', n);
    issues.classList.toggle('has-issues', n > 0);
  }
}

function runRenderSummaryPane() {
  const pane = document.getElementById('run-pane-summary');
  if (!pane) return;

  if (runState.status === 'idle') {
    pane.innerHTML = '<div class="run-console-empty">' + qaEsc(tAny('run.waiting')) + '</div>';
    return;
  }

  const st = runState;
  const c = window.__counters;
  const prog = c.total ? c.current + ' / ' + c.total : c.current || 0;

  const rows = [
    [tAny('run.sum.status'), runStatusLabel(st.status)],
    [tAny('run.sum.stage'), st.stage || '--'],
    [tAny('run.sum.progress'), prog],
    [tAny('run.sum.elapsed'), runFmtElapsed(c.elapsed)],
    [tAny('run.sum.issues'), String(c.issues || 0)],
    [tAny('run.sum.warnings'), String(c.warnings || 0)]
  ];

  if (st.error) rows.push([tAny('run.sum.error'), st.error]);

  pane.innerHTML =
    '<table class="run-live-table">' +
    rows
      .map(
        r =>
          '<tr><td class="run-live-k">' +
          qaEsc(r[0]) +
          '</td><td class="run-live-v">' +
          qaEsc(r[1]) +
          '</td></tr>'
      )
      .join('') +
    '</table>';
}

function runRunningBlock(withItem) {
  return `<div class="run-console-empty" style="text-align:center; padding:2rem;">
    <strong style="font-size:1.2rem;">${qaEsc(xt('run.running'))}</strong><br><br>
    <b>${qaEsc(xt('run.currentPkg'))}:</b> ${qaEsc(runState.current_package || '--')}<br>
    ${withItem ? `<b>${qaEsc(xt('run.currentItem'))}:</b> ${qaEsc(runState.current_item || '--')}<br>` : ''}
    <b>${qaEsc(xt('run.progress'))}:</b> ${runState.current} / ${runState.total_items == null ? '?' : runState.total_items}
  </div>`;
}

function runRenderResultsPane() {
  const pane = document.getElementById('run-pane-results');
  if (!pane) return;

  if (runState.status === 'running') {
    pane.innerHTML = runRunningBlock(true);
    return;
  }

  if (runState.status === 'idle') {
    pane.innerHTML = '<div class="run-console-empty">' + qaEsc(tAny('run.waiting')) + '</div>';
    return;
  }

  if (!qaData || !qaData.paquetes || !qaData.paquetes.length) {
    pane.innerHTML = '<div class="run-console-empty">' + qaEsc(tAny('run.notAvailable')) + '</div>';
    return;
  }

  let html =
    '<table class="run-live-table run-results-table"><thead><tr>' +
    '<th>' + qaEsc(tAny('run.res.pkg')) + '</th>' +
    '<th>' + qaEsc(tAny('run.res.image')) + '</th>' +
    '<th>' + qaEsc(tAny('run.res.quality')) + '</th>' +
    '<th>' + qaEsc(tAny('run.res.issues')) + '</th>' +
    '<th>' + qaEsc(tAny('run.res.status')) + '</th>' +
    '</tr></thead><tbody>';

  qaData.paquetes.forEach(p => {
    (p.resultados || []).forEach(r => {
      const n = (r.issues || []).length;
      html +=
        '<tr>' +
        '<td>' + qaEsc(p.paquete) + '</td>' +
        '<td>' + qaEsc(r.imagen) + '</td>' +
        '<td>' + qaEsc(r.quality || 'N/A') + '</td>' +
        '<td>' + n + '</td>' +
        '<td class="' + (r.ok ? 'run-ok' : 'run-fail') + '">' +
        qaEsc(r.ok ? tAny('run.res.ok') : tAny('run.res.fail')) +
        '</td>' +
        '</tr>';
    });
  });

  pane.innerHTML = html + '</tbody></table>';
}

function runRenderExportPane() {
  const pane = document.getElementById('run-pane-autoexport');
  if (!pane) return;

  if (runState.status === 'running') {
    pane.innerHTML = runRunningBlock(false);
    return;
  }

  if (runState.status === 'idle') {
    pane.innerHTML = '<div class="run-console-empty">' + qaEsc(tAny('run.waiting')) + '</div>';
    return;
  }

  const st = runState.export || {};
  if (!st.path) {
    pane.innerHTML = '<div class="run-console-empty">' + qaEsc(tAny('run.notAvailable')) + '</div>';
    return;
  }

  const shortPath = String(st.path).split(/[\\/]/).slice(-2).join('/');
  pane.innerHTML =
    '<table class="run-live-table"><tbody>' +
    '<tr><td class="run-live-k">' + qaEsc(tAny('run.exp.file')) + '</td><td class="run-live-v">' + qaEsc(shortPath) + '</td></tr>' +
    '<tr><td class="run-live-k">' + qaEsc(tAny('run.exp.images')) + '</td><td class="run-live-v">' + (st.images != null ? st.images : '--') + '</td></tr>' +
    '<tr><td class="run-live-k">' + qaEsc(tAny('run.exp.issues')) + '</td><td class="run-live-v">' + (st.issues != null ? st.issues : '--') + '</td></tr>' +
    '</tbody></table>';
}

// Bug #14 mitigado: throttling con requestAnimationFrame para no re-renderizar en exceso.
let _livePanesQueued = false;

function runRenderLivePanesNow() {
  runRenderSummaryPane();
  runRenderResultsPane();
  runRenderExportPane();
}

function runRenderLivePanes() {
  if (_livePanesQueued) return;
  _livePanesQueued = true;

  const cb = () => {
    _livePanesQueued = false;
    runRenderLivePanesNow();
  };

  if (window.requestAnimationFrame) requestAnimationFrame(cb);
  else setTimeout(cb, 80);
}

// Tarea 3: estado de ejecución al abrir un proyecto.
function deriveStateFromQa() {
  if (!qaData || !qaData.paquetes || !qaData.paquetes.length) return null;

  let imgs = 0;
  let issues = 0;
  let warns = 0;
  const pkgs = [];

  qaData.paquetes.forEach(p => {
    const rs = p.resultados || [];
    imgs += p.total_imagenes || rs.length;
    pkgs.push(p.paquete);

    rs.forEach(r => {
      issues += (r.issues || []).length;
      warns += (r.ocr_warnings || []).length;
    });
  });

  return {
    status: 'done',
    stage: 'qa',
    current: imgs,
    total_items: imgs,
    issues,
    warnings: warns,
    elapsed: 0,
    error: null,
    exit_code: 0,
    packages: pkgs
  };
}

function stateFromRunFile(rs) {
  const stages = rs.stages || {};
  const order = rs.stage_order || Object.keys(stages);

  let lastDone = null;
  order.forEach(n => {
    if (stages[n] && stages[n].state === 'done') lastDone = n;
  });

  const failed = order.filter(n => stages[n] && stages[n].state === 'error');
  const prog = rs.progress || {};
  const qa = stages.qa || {};
  const exp = stages.autoexport || {};

  return {
    status: failed.length ? 'error' : rs.exit_code === 0 ? 'done' : 'error',
    stage: lastDone || order[order.length - 1] || null,
    current_package: prog.package || null,
    current_item: prog.item || null,
    current: prog.current || 0,
    // Bug #10 corregido: comparación correcta contra null.
    total_items: prog.total != null ? prog.total : null,
    issues: qa.issues != null ? qa.issues : 0,
    warnings: qa.warnings != null ? qa.warnings : 0,
    elapsed: rs.duration_s || 0,
    exit_code: rs.exit_code,
    error: rs.error || null,
    packages: rs.packages || [],
    export: exp.path ? { path: exp.path, images: exp.images, issues: exp.issues } : null
  };
}

async function restoreRunState() {
  if (runState.status === 'running') return;

  let backend = null;
  let next = null;
  let provenance = null;

  if (hasPywebview() && typeof window.pywebview.api.getRunState === 'function') {
    try {
      backend = await window.pywebview.api.getRunState();
    } catch (e) {
      backend = null;
    }
  }

  if (backend && backend.ok && backend.state) {
    next = stateFromRunFile(backend.state);
    provenance = 'run_state.json';
  } else {
    next = deriveStateFromQa();
    provenance = 'qa_report.json';
  }

  if (!next) {
    runRenderLivePanes();
    return;
  }

  Object.keys(next).forEach(k => {
    runState[k] = next[k];
  });

  runState.source = provenance;

  runSetRunning(false);
  runSetBadge(next.status || 'done');

  ['listing', 'crawl', 'qa', 'autoexport'].forEach(s => {
    const done =
      provenance === 'run_state.json'
        ? !!(
            backend.state.stages &&
            backend.state.stages[s] &&
            backend.state.stages[s].state === 'done'
          )
        : s === 'qa' || s === 'listing' || s === 'crawl';

    runSetStep(s, done ? 'done' : null);
  });

  runUpdateWidget(runState);
  runRenderLivePanes();

  showToast(xt(provenance === 'run_state.json' ? 'proj.stateFromRun' : 'proj.stateFromQa'), 'info', 3000);
}

function runCheckFilters(cfg) {
  const warn = document.getElementById('run-warn-filters');
  if (!warn) return;

  const msgs = [];

  const needsPkgs = cfg.stages.indexOf('crawl') !== -1 || cfg.stages.indexOf('listing') !== -1;
  if (needsPkgs && (!cfg.filterT || cfg.filterT.length === 0)) {
    msgs.push(tAny('run.warnAllPackages'));
  }

  const pair = (cfg.pair || '').trim();
  if (pair) {
    const parts = pair.split('-');
    const ok =
      parts.length === 2 &&
      VALID_LANGS.indexOf(parts[0]) !== -1 &&
      VALID_LANGS.indexOf(parts[1]) !== -1;

    if (!ok) msgs.push(tAny('run.warnBadPair', pair));
  }

  if (msgs.length) {
    warn.textContent = msgs.join(' ');
    warn.hidden = false;
  } else {
    warn.hidden = true;
  }
}

// Bug #6 corregido: regex correcta para timestamps embebidos.
const _TS_RE = /^\s*(?:\d{2}:\d{2}:\d{2}\s*)+/;

function runLog(msg, level) {
  const pane = document.getElementById('run-pane-logs');
  if (!pane) return;

  const line = document.createElement('div');
  line.className = 'run-log-line';

  const stamp = new Date().toTimeString().slice(0, 8);

  const time = document.createElement('span');
  time.className = 'run-log-time';
  time.textContent = '[' + stamp + ']';

  const lvl = document.createElement('span');
  lvl.className = 'run-log-level run-log-level-' + (level || 'INFO').toLowerCase();
  lvl.textContent = '[' + (level || 'INFO') + ']';

  const text = document.createElement('span');
  text.className = 'run-log-msg';
  text.textContent = ' ' + String(msg).replace(_TS_RE, '');

  line.appendChild(time);
  line.appendChild(lvl);
  line.appendChild(text);
  pane.appendChild(line);

  const auto = document.getElementById('run-autoscroll');
  if (auto && auto.checked) {
    const consoleEl = document.getElementById('run-console');
    if (consoleEl) consoleEl.scrollTop = consoleEl.scrollHeight;
  }
}

function runClear() {
  const pane = document.getElementById('run-pane-logs');
  if (pane) pane.innerHTML = '';

  ['listing', 'crawl', 'qa', 'autoexport'].forEach(s => runSetStep(s, null));

  resetRunState('idle');
  runStepIndex = -1;
  runPackages = [];
  runPkgDeselected.clear();
  runSetBadge('idle');
  if (runAutoNextTimer) { clearTimeout(runAutoNextTimer); runAutoNextTimer = null; }
  runCrawlStopPoll();
  runCrawlRenderEmpty();
  runUpdateWidget(runState);
  runUpdateActionButton();
  runRenderLivePanes();
}

window.onPipelineLog = function (ev) {
  runLog(ev.msg, ev.level);
};

window.onPipelineStep = function (step, state) {
  runSetStep(step, state);
  if (state === 'active') runState.stage = step;

  if (step === 'crawl') {
    if (state === 'active') {
      runSwitchTab('crawl');
      runCrawlStartPoll();
    } else {
      runCrawlStopPoll();
    }
  }

  if (step === 'qa' && state === 'active') {
    runSwitchTab('logs');
  }

  runRenderSummaryPane();
};

window.onPipelineProgress = function (ev) {
  runState.stage = ev.stage || runState.stage;
  runState.current = ev.current || 0;

  if (ev.total !== undefined && ev.total !== null) runState.total_items = ev.total;
  if (ev.package) runState.current_package = ev.package;
  if (ev.item) runState.current_item = ev.item;
  if (ev.issues !== undefined && ev.issues !== null) runState.issues = ev.issues;
  if (ev.warnings !== undefined && ev.warnings !== null) runState.warnings = ev.warnings;

  window.__counters.status = 'running';
  window.__counters.stage = ev.stage || null;
  window.__counters.current = ev.current || 0;
  window.__counters.total = ev.total != null ? ev.total : null;
  window.__counters.issues = ev.issues || 0;
  window.__counters.warnings = ev.warnings || 0;
  window.__counters.elapsed = _runStartedAt ? (Date.now() - _runStartedAt) / 1000 : 0;
  if (typeof renderCounters === 'function') renderCounters();

  runUpdateWidget(runState);
  runRenderLivePanes();
};

window.onPipelineDone = function (ev) {
  runLog(tAny('run.done'), 'SUCCESS');

  runState.status = 'done';
  runSetRunning(false);
  runSetBadge('done');
  runUpdateWidget(runState);

  window.__counters.status = 'done';
  window.__counters.elapsed = _runStartedAt ? (Date.now() - _runStartedAt) / 1000 : 0;
  if (typeof renderCounters === 'function') renderCounters();

  if (runStepIndex >= 0) runStepIndex += 1;
  runUpdateActionButton();

  if (ev && ev.export) {
    runState.export = ev.export;
  }

  if (ev && ev.extOut) {
    const out = document.getElementById('run-out');
    if (out) out.value = ev.extOut;

    currentProject = ev.extOut;
    setExportDefaults(ev.extOut);
  }

  if (hasPywebview()) {
    loadQaReport().then(() => restoreRunState());
  }

  const autoEl = document.getElementById('run-auto-next');
  if (autoEl && autoEl.checked) {
    const stages = runStepStages();
    if (runStepIndex >= 0 && runStepIndex < stages.length) {
      const step = runStepIndex;
      if (runAutoNextTimer) clearTimeout(runAutoNextTimer);
      runAutoNextTimer = setTimeout(() => {
        runAutoNextTimer = null;
        if (runState.status === 'done' && runStepIndex === step) runNext();
      }, 600);
    }
  }
};

window.onPipelineError = function (msg) {
  runLog(msg, 'ERROR');
  runState.error = msg;
  runRenderSummaryPane();

  window.__counters.status = 'error';
  window.__counters.elapsed = _runStartedAt ? (Date.now() - _runStartedAt) / 1000 : 0;
  if (typeof renderCounters === 'function') renderCounters();
};

window.onExportDone = function (res) {
  if (res && res.ok) {
    runState.export = { path: res.path, images: res.images, issues: res.issues };
    runLog(tAny('run.exportDone') || 'Reporte exportado: ' + res.path, 'SUCCESS');
  } else {
    runLog((res && (res.detail || res.error)) || 'export failed', 'ERROR');
  }
  runRenderLivePanes();
};

window.onPipelineExit = function (code) {
  if (runState.status === 'running') runState.status = code === 0 ? 'done' : 'error';

  runState.exit_code = code;
  runSetRunning(false);
  runSetBadge(runState.status);

  runLog(xt('run.exitCode', code), code === 0 ? 'INFO' : 'ERROR');

  window.__counters.status = runState.status;
  window.__counters.elapsed = _runStartedAt ? (Date.now() - _runStartedAt) / 1000 : 0;
  if (typeof renderCounters === 'function') renderCounters();

  runUpdateWidget(runState);
  runRenderLivePanes();
  runUpdateActionButton();
  runCrawlStopPoll();
};

let runStatePoll = null;
let runAutoNextTimer = null;

function runStartStatePoll() {
  if (runStatePoll) return;

  runStatePoll = setInterval(async () => {
    if (!hasPywebview()) return;

    try {
      const st = await window.pywebview.api.getPipelineState();
      if (!st) return;

      const wasRunning = runState.status === 'running';
      runState = runGuardState(Object.assign(runState, st));
      runUpdateWidget(runState);
      runRenderLivePanes();

      if (st.status !== 'running' && runStatePoll) {
        if (wasRunning) {
          runSetRunning(false);
          runSetBadge(runState.status);
          runUpdateActionButton();
        }
        clearInterval(runStatePoll);
        runStatePoll = null;
      }
    } catch (e) {}
  }, 100);
}

const RUN_STAGE_ORDER = ['config', 'listing', 'crawl', 'qa', 'autoexport'];

function runStepStages() {
  return RUN_STAGE_ORDER.filter(s => {
    const el = document.getElementById('run-stage-' + s);
    return el && el.checked;
  });
}

function runSelectedPackages() {
  const boxes = document.querySelectorAll('#run-pane-packages input.run-pkg-check');
  const sel = [];
  boxes.forEach(b => { if (b.checked) sel.push(b.value); });
  return sel;
}

let runPkgSearch = '';
let runPkgFilterMode = 'default';
const runPkgDeselected = new Set();

function runPkgApplyFilters(pkgs, applyFilters) {
  if (!applyFilters) return pkgs;
  const ft = safeValue('pipe-filter-t').split('\n').map(x => x.trim().toLowerCase()).filter(Boolean);
  const fe = safeValue('pipe-filter-e').split('\n').map(x => x.trim().toLowerCase()).filter(Boolean);
  let out = pkgs;
  if (ft.length) out = out.filter(p => ft.some(f => p.toLowerCase().indexOf(f) !== -1));
  if (fe.length) out = out.filter(p => !fe.some(f => p.toLowerCase().indexOf(f) !== -1));
  return out;
}

function runPkgPreselect(pkgs) {
  const ft = safeValue('pipe-filter-t').split('\n').map(x => x.trim().toLowerCase()).filter(Boolean);
  runPkgDeselected.clear();
  if (ft.length) {
    pkgs.forEach(p => {
      if (!ft.some(f => p.toLowerCase().indexOf(f) !== -1)) {
        runPkgDeselected.add(p);
      }
    });
  }
}

async function runPkgRegenerate(applyFilters) {
  if (!hasPywebview() || typeof window.pywebview.api.listPackages !== 'function') return;
  const pane = document.getElementById('run-pane-packages');
  if (pane) {
    const list = pane.querySelector('.run-pkg-list');
    if (list) list.innerHTML = '<div class="run-console-empty"><span class="ax-spinner"></span></div>';
  }
  try {
    const res = await window.pywebview.api.listPackages();
    if (!res || !res.ok) return;
    const names = (res.packages || []).map(p => p.name);
    const newList = runPkgApplyFilters(names, applyFilters);
    const oldSet = new Set(runPackages);
    const newSet = new Set(newList);
    const same = oldSet.size === newSet.size && newList.every(p => oldSet.has(p));
    runPackages = newList;
    if (!same) {
      const ft = safeValue('pipe-filter-t').split('\n').map(x => x.trim().toLowerCase()).filter(Boolean);
      newList.forEach(p => {
        if (!oldSet.has(p) && ft.length && !ft.some(f => p.toLowerCase().indexOf(f) !== -1)) {
          runPkgDeselected.add(p);
        }
      });
      for (const p of Array.from(runPkgDeselected)) {
        if (!newSet.has(p)) runPkgDeselected.delete(p);
      }
    }
    runRenderPackagesPane();
  } catch (e) {}
}

function runPkgPsdnsLabel(pkg) {
  const chk = document.getElementById('run-psdns');
  if (!chk || !chk.checked) return null;
  const st = psdnsState;
  if (!st || !st.catalog || !Object.prototype.hasOwnProperty.call(st.catalog, pkg)) return null;
  const pick = psdnsPickLabel(st.catalog[pkg], psdnsLang());
  return (pick && pick.label && pick.label !== pkg) ? pick.label : null;
}

function runRenderPackagesPane() {
  const pane = document.getElementById('run-pane-packages');
  if (!pane) return;

  const q = runPkgSearch.toLowerCase();
  const matches = p => {
    if (!q) return true;
    if (p.toLowerCase().indexOf(q) !== -1) return true;
    const lbl = runPkgPsdnsLabel(p);
    return lbl && lbl.toLowerCase().indexOf(q) !== -1;
  };
  const visible = runPackages.filter(p => {
    if (runPkgFilterMode === 'selected') return !runPkgDeselected.has(p);
    if (runPkgFilterMode === 'unselected') return runPkgDeselected.has(p);
    return matches(p);
  });

  const filterLabel = tAny('run.pkg.filter.' + runPkgFilterMode);

  let html = '<div class="run-pkg-toolbar">' +
    '<label class="run-pkg-master"><input type="checkbox" id="run-pkg-master"></label>' +
    '<div class="run-pkg-search-wrap">' +
    '<svg class="run-pkg-search-ico" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>' +
    '<input type="text" class="run-pkg-search" id="run-pkg-search" placeholder="' + qaEsc(tAny('run.pkg.search')) + '" value="' + qaEsc(runPkgSearch) + '">' +
    '<div class="run-pkg-filter-wrap">' +
    '<button type="button" class="run-pkg-filter-btn' + (runPkgFilterMode !== 'default' ? ' active' : '') + '" id="run-pkg-filter-btn" title="' + qaEsc(filterLabel) + '">' +
    '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="4" y1="6" x2="20" y2="6"/><line x1="7" y1="12" x2="17" y2="12"/><line x1="10" y1="18" x2="14" y2="18"/></svg>' +
    '</button>' +
    '<div class="run-pkg-filter-menu" id="run-pkg-filter-menu" hidden>' +
    '<button type="button" class="run-pkg-filter-opt' + (runPkgFilterMode === 'default' ? ' active' : '') + '" data-mode="default">' + qaEsc(tAny('run.pkg.filter.default')) + '</button>' +
    '<button type="button" class="run-pkg-filter-opt' + (runPkgFilterMode === 'all' ? ' active' : '') + '" data-mode="all">' + qaEsc(tAny('run.pkg.filter.all')) + '</button>' +
    '<button type="button" class="run-pkg-filter-opt' + (runPkgFilterMode === 'selected' ? ' active' : '') + '" data-mode="selected">' + qaEsc(tAny('run.pkg.filter.selected')) + '</button>' +
    '<button type="button" class="run-pkg-filter-opt' + (runPkgFilterMode === 'unselected' ? ' active' : '') + '" data-mode="unselected">' + qaEsc(tAny('run.pkg.filter.unselected')) + '</button>' +
    '</div>' +
    '</div>' +
    '</div>' +
    '<span class="run-pkg-count" id="run-pkg-count"></span>' +
    '</div><div class="run-pkg-list">';

  if (!runPackages.length) {
    html += '<div class="run-console-empty">' + qaEsc(tAny('run.waiting')) + '</div>';
  } else {
    visible.forEach(p => {
      const lbl = runPkgPsdnsLabel(p);
      const labelHtml = lbl ? '<span class="run-pkg-psdns">' + qaEsc(lbl) + '</span>' : '';
      const chk = document.getElementById('run-psdns');
      const psdnsOn = chk && chk.checked;
      const inCatalog = psdnsState && psdnsState.catalog && Object.prototype.hasOwnProperty.call(psdnsState.catalog, p);
      const warnHtml = (psdnsOn && !inCatalog) ? '<span class="run-pkg-warn" title="' + qaEsc(tAny('psdns.notIndexed')) + '">\u26A0</span>' : '';
      const checked = runPkgDeselected.has(p) ? '' : ' checked';
      html += '<label class="run-pkg-item"><input type="checkbox" class="run-pkg-check" value="' + qaEsc(p) + '"' + checked + '>' + labelHtml + warnHtml + '<span class="run-pkg-name">' + qaEsc(p) + '</span></label>';
    });
    if (!visible.length) {
      html += '<div class="run-console-empty">' + qaEsc(tAny('run.empty')) + '</div>';
    }
  }

  html += '</div>';
  pane.innerHTML = html;

  const count = document.getElementById('run-pkg-count');
  const master = document.getElementById('run-pkg-master');
  const updateCount = () => {
    if (!count) return;
    const total = runPackages.length;
    const sel = total - runPkgDeselected.size;
    count.textContent = sel + ' / ' + total;
    if (master) {
      const visTotal = visible.length;
      const visSel = pane.querySelectorAll('.run-pkg-check:checked').length;
      master.checked = visTotal > 0 && visSel === visTotal;
      master.indeterminate = visSel > 0 && visSel < visTotal;
    }
  };
  updateCount();

  if (master) {
    master.addEventListener('change', () => {
      const on = master.checked;
      pane.querySelectorAll('.run-pkg-check').forEach(b => {
        b.checked = on;
        if (on) runPkgDeselected.delete(b.value);
        else runPkgDeselected.add(b.value);
      });
      updateCount();
    });
  }

  const search = document.getElementById('run-pkg-search');
  if (search) {
    search.addEventListener('input', () => {
      runPkgSearch = search.value;
      runRenderPackagesPane();
      const s = document.getElementById('run-pkg-search');
      if (s) { s.focus(); s.setSelectionRange(s.value.length, s.value.length); }
    });
  }

  const filterBtn = document.getElementById('run-pkg-filter-btn');
  const filterMenu = document.getElementById('run-pkg-filter-menu');
  if (filterBtn && filterMenu) {
    filterBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      filterMenu.hidden = !filterMenu.hidden;
    });
    filterMenu.querySelectorAll('.run-pkg-filter-opt').forEach(opt => {
      opt.addEventListener('click', (e) => {
        e.stopPropagation();
        const mode = opt.dataset.mode;
        filterMenu.hidden = true;

        if (mode === 'default') {
          runPkgFilterMode = 'default';
          runPkgRegenerate(true);
          return;
        }
        if (mode === 'all') {
          runPkgFilterMode = 'all';
          runPkgRegenerate(false);
          return;
        }

        runPkgFilterMode = mode;
        runRenderPackagesPane();
        const s = document.getElementById('run-pkg-search');
        if (s) { s.focus(); s.setSelectionRange(s.value.length, s.value.length); }
      });
    });
  }

  pane.querySelectorAll('.run-pkg-check').forEach(b => b.addEventListener('change', () => {
    if (b.checked) runPkgDeselected.delete(b.value);
    else runPkgDeselected.add(b.value);
    updateCount();
  }));
}

window.onPipelinePackages = function (pkgs) {
  runPackages = Array.isArray(pkgs) ? pkgs.slice() : [];
  runPkgPreselect(runPackages);
  runRenderPackagesPane();
};

document.addEventListener('click', (e) => {
  const menu = document.getElementById('run-pkg-filter-menu');
  if (menu && !menu.hidden && !menu.contains(e.target) && !e.target.closest('#run-pkg-filter-btn')) {
    menu.hidden = true;
  }
});

// ---- Crawl live view: miniatura de screenshot + nodos detectados ----
const crawlView = { poll: null, lastKey: '' };

function runSwitchTab(name) {
  document.querySelectorAll('.run-console-tab').forEach(t => t.classList.toggle('active', t.dataset.tab === name));
  document.querySelectorAll('.run-console-pane').forEach(p => p.classList.toggle('active', p.id === 'run-pane-' + name));
  const isPkg = name === 'packages';
  const isLogs = name === 'logs';
  const autoWrap = document.getElementById('run-autoscroll-wrap');
  const psdnsWrap = document.getElementById('run-psdns-wrap');
  const psdnsBtn = document.getElementById('run-psdns-update-btn');
  if (autoWrap) autoWrap.hidden = !isLogs;
  if (psdnsWrap) psdnsWrap.hidden = !isPkg;
  if (psdnsBtn) psdnsBtn.hidden = !isPkg;
}
runSwitchTab('packages');
runRenderPackagesPane();

function runCrawlStartPoll() {
  crawlView.lastKey = '';
  runCrawlRefresh();
}

function runCrawlStopPoll() {
  crawlView.lastKey = '';
}

async function runCrawlRefresh() {
  if (!hasPywebview() || typeof window.pywebview.api.getCrawlLatest !== 'function') return;
  let res = null;
  try { res = await window.pywebview.api.getCrawlLatest(); } catch (e) { return; }
  if (!res || !res.ok) return;
  const node = res.node;
  if (!node) { runCrawlRenderEmpty(); return; }
  const key = node.pkg + '/' + node.node_id + '/' + (node.screenshots || []).length;
  if (key === crawlView.lastKey) return;
  crawlView.lastKey = key;
  runCrawlRender(node);
}

function runCrawlRender(node) {
  const pane = document.getElementById('run-pane-crawl');
  if (!pane) return;
  const shots = node.screenshots || [];
  const shotRel = shots.length ? node.pkg + '/' + shots[shots.length - 1] : null;
  const clickables = node.clickables || [];

  let html = '<div class="run-crawl-view">';
  html += '<div class="run-crawl-shot"><img id="run-crawl-img" alt=""><div class="run-crawl-shot-empty" id="run-crawl-shot-empty">' + qaEsc(tAny('run.crawl.noScreenshot')) + '</div></div>';
  html += '<div class="run-crawl-nodes">';
  html += '<div class="run-crawl-head">' + qaEsc(tAny('run.crawl.nodes')) + ' <span class="run-crawl-count">' + clickables.length + '</span></div>';
  html += '<div class="run-crawl-meta">' + qaEsc(tAny('run.crawl.node')) + ' ' + qaEsc(node.node_id) + ' · ' + qaEsc(tAny('run.crawl.depth')) + ' ' + (node.depth != null ? node.depth : 0) + '</div>';
  if (clickables.length) {
    html += '<ul class="run-crawl-list">';
    clickables.forEach(c => {
      const label = c.text || c.contentDescription || c.resourceName || c.className || '—';
      html += '<li class="run-crawl-item"><span class="run-crawl-label">' + qaEsc(label) + '</span>';
      if (c.resourceName) html += '<span class="run-crawl-res" title="' + qaEsc(c.resourceName) + '">' + qaEsc(c.resourceName) + '</span>';
      html += '</li>';
    });
    html += '</ul>';
  } else {
    html += '<div class="run-console-empty">' + qaEsc(tAny('run.crawl.noNodes')) + '</div>';
  }
  html += '</div></div>';
  pane.innerHTML = html;

  if (shotRel) {
    const img = document.getElementById('run-crawl-img');
    const empty = document.getElementById('run-crawl-shot-empty');
    window.pywebview.api.getImageData(shotRel, 320).then(data => {
      if (!data) return;
      if (img) { img.src = data; img.classList.add('loaded'); }
      if (empty) empty.classList.add('d-none');
    });
  }
}

function runCrawlRenderEmpty() {
  const pane = document.getElementById('run-pane-crawl');
  if (!pane) return;
  pane.innerHTML = '<div class="run-console-empty">' + qaEsc(tAny('run.waiting')) + '</div>';
}

function runUpdateActionButton() {
  const btn = document.getElementById('btn-run-start');
  const label = document.getElementById('btn-run-start-label');
  if (!btn || !label) return;

  const stages = runStepStages();
  const running = runState.status === 'running';

  if (running) {
    label.textContent = tAny('run.running');
    btn.disabled = true;
    return;
  }

  if (runStepIndex < 0 || runStepIndex >= stages.length) {
    label.textContent = tAny('run.start');
    btn.disabled = stages.length === 0;
    return;
  }

  const stage = stages[runStepIndex];
  const isLast = runStepIndex === stages.length - 1;
  const hasAutoexport = stages.indexOf('autoexport') !== -1;

  if (stage === 'autoexport') label.textContent = tAny('run.export');
  else if (isLast && !hasAutoexport) label.textContent = tAny('run.finish');
  else label.textContent = tAny('run.next');
  btn.disabled = false;
}

function runLaunchStage(stage, newSession) {
  const cfg = runCollectConfig();
  cfg.stages = [stage];
  cfg.newSession = !!newSession;

  if (stage !== 'listing' && runPackages.length) {
    const sel = runSelectedPackages();
    if (sel.length) cfg.filterT = sel;
  }

  runState.status = 'running';
  _runStartedAt = Date.now();
  runSetBadge('running');
  runSetRunning(true);
  runUpdateActionButton();
  hideWelcome();
  runStartStatePoll();

  window.pywebview.api.startPipeline(cfg).then(res => {
    if (!res || !res.ok) {
      runLog((res && res.error) || 'start failed', 'ERROR');
      runState.status = 'error';
      runSetRunning(false);
      runSetBadge('error');
      runUpdateActionButton();
      if (runStatePoll) { clearInterval(runStatePoll); runStatePoll = null; }
    }
  }).catch(err => {
    runLog(String((err && err.message) || err), 'ERROR');
    runState.status = 'error';
    runSetRunning(false);
    runSetBadge('error');
    runUpdateActionButton();
    if (runStatePoll) { clearInterval(runStatePoll); runStatePoll = null; }
  });
}

// Solo listing y crawl necesitan el DUT (adb/uiautomator2); qa y autoexport
// solo leen archivos en disco. Si un run que usa adb no tiene DUT conectado,
// pide conectarlo antes de arrancar. Devuelve true si se puede continuar.
async function dutGuard(stages) {
  if (!stages || (stages.indexOf('config') === -1 && stages.indexOf('listing') === -1 && stages.indexOf('crawl') === -1)) return true;
  if (!hasPywebview()) return true;

  let connected = false;
  try {
    const info = await window.pywebview.api.getDeviceInfo();
    connected = !!(info && info.connected);
  } catch (e) {
    connected = false;
  }

  if (connected) return true;

  if (typeof window.Popup === 'object' && window.Popup.confirm) {
    await window.Popup.confirm({
      title: tAny('dut.title'),
      body: tAny('dut.desc'),
      okLabel: tAny('dut.ok')
    });
  }
  return false;
}

function runStart() {
  if (!hasPywebview()) return;

  if (window.ssCopyState && window.ssCopyState.status === 'copying') {
    runLog(tAny('ss.copyBusy'), 'ERROR');
    return;
  }

  const cfg = runCollectConfig();
  if (!cfg.extOut) { runLog(tAny('run.errNoOut'), 'ERROR'); return; }

  const stages = runStepStages();
  if (stages.length === 0) { runLog(tAny('run.errNoStages'), 'ERROR'); return; }

  runCheckFilters(cfg);
  runClear();
  runPackages = [];
  runPkgDeselected.clear();
  runStepIndex = 0;

  runLaunchStage(stages[0], true);
}

function runNext() {
  if (!hasPywebview()) return;
  if (runState.status === 'running') return;

  const stages = runStepStages();
  if (runStepIndex < 0 || runStepIndex >= stages.length) return;

  runLaunchStage(stages[runStepIndex], false);
}

function runStop() {
  if (!hasPywebview()) return;

  if (runAutoNextTimer) { clearTimeout(runAutoNextTimer); runAutoNextTimer = null; }
  window.pywebview.api.stopPipeline();

  runState.status = 'cancelled';
  runSetRunning(false);
  runSetBadge('cancelled');

  runUpdateWidget(runState);
  runRenderSummaryPane();
  runUpdateActionButton();

  if (runStatePoll) {
    clearInterval(runStatePoll);
    runStatePoll = null;
  }
}

bindUi('btn-run-start', 'click', async function () {
  if (runState.status === 'running') return;
  const stages = runStepStages();
  if (runStepIndex < 0 || runStepIndex >= stages.length) {
    if (!currentProject && typeof window.actStartNoProject === 'function') {
      window.actStartNoProject();
      return;
    }
    if (await dutGuard(stages)) runStart();
  }
  else runNext();
});
bindUi('btn-run-stop', 'click', runStop);
bindUi('btn-run-clear', 'click', runClear);

bindUi('btn-run-refresh', 'click', function () {
  this.classList.add('spinning');
  Promise.all([updateDeviceWidget(), loadQaReport()]).finally(() => {
    setTimeout(() => this.classList.remove('spinning'), 100);
  });
});

['t', 'e', 'o'].forEach(runChipInit);

document.querySelectorAll('.run-console-tab').forEach(tab => {
  tab.addEventListener('click', function () {
    runSwitchTab(this.dataset.tab);
    if (this.dataset.tab === 'crawl') {
      crawlView.lastKey = '';
      runCrawlRefresh();
    }
  });
});

const runPsdnsChk = document.getElementById('run-psdns');
if (runPsdnsChk) runPsdnsChk.addEventListener('change', async function () {
  if (this.checked && typeof window.Popup === 'object' && window.Popup.confirm) {
    const res = await window.Popup.confirm({
      title: tAny('psdns.enable'),
      body: tAny('psdns.enableInfo'),
      okLabel: tAny('psdns.popup.accept'),
      cancelLabel: tAny('psdns.popup.dismiss')
    });
    if (res !== 'ok') {
      this.checked = false;
      return;
    }
  }
  psdnsSyncUpdateBtn();
  runRenderPackagesPane();
});

const runPsdnsUpdateBtn = document.getElementById('run-psdns-update-btn');
if (runPsdnsUpdateBtn) {
  runPsdnsUpdateBtn.addEventListener('click', async function () {
    if (psdnsTaskId) return;
    const res = await window.Popup.confirm({
      title: tAny('psdns.update'),
      body: tAny('psdns.updateConfirm'),
      okLabel: tAny('psdns.popup.accept'),
      cancelLabel: tAny('psdns.popup.dismiss')
    });
    if (res !== 'ok') return;
    psdnsShowProgress();
    psdnsUpdate();
  });
}

function psdnsSyncUpdateBtn() {
  const btn = document.getElementById('run-psdns-update-btn');
  if (!btn) return;
  const chk = document.getElementById('run-psdns');
  btn.disabled = !chk || !chk.checked || !!psdnsTaskId;
}

let psdnsProgressEl = null;
let psdnsMsgEl = null;

function psdnsShowProgress() {
  if (psdnsProgressEl) return;
  const bd = document.createElement('div');
  bd.className = 'popup-backdrop ax-in';
  bd.innerHTML =
    '<div class="popup-card psdns-progress-card">' +
    '<div class="psdns-progress-anim" id="psdns-progress-anim" role="status"></div>' +
    '<div class="popup-title" id="psdns-progress-title">' + qaEsc(tAny('psdns.updating')) + '</div>' +
    '<div class="popup-body"><div class="psdns-progress-msg" id="psdns-progress-msg"></div></div>' +
    '</div>';
  document.body.appendChild(bd);
  psdnsProgressEl = bd;
  psdnsMsgEl = document.getElementById('psdns-progress-msg');
  psdnsStartLoader(document.getElementById('psdns-progress-anim'));
  psdnsSyncUpdateBtn();
}

let psdnsLoaderRaf = null;

function psdnsStartLoader(container) {
  if (!container) return;
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
  container.appendChild(svg);

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
    psdnsLoaderRaf = requestAnimationFrame(render);
  }
  psdnsLoaderRaf = requestAnimationFrame(render);
}

function psdnsStopLoader() {
  if (psdnsLoaderRaf) {
    cancelAnimationFrame(psdnsLoaderRaf);
    psdnsLoaderRaf = null;
  }
}

function psdnsUpdateProgress(msg) {
  if (psdnsMsgEl && msg) psdnsMsgEl.textContent = msg;
}

function psdnsHideProgress() {
  if (psdnsProgressEl) {
    psdnsProgressEl.remove();
    psdnsProgressEl = null;
    psdnsMsgEl = null;
  }
  psdnsStopLoader();
  psdnsSyncUpdateBtn();
}

psdnsSyncUpdateBtn();

document.querySelectorAll('button[data-bs-toggle="tab"], .nav-link').forEach(tab => {
  tab.addEventListener('shown.bs.tab', function (e) {
    const target =
      e.target.getAttribute('href') || e.target.getAttribute('aria-controls') || '';

    if (target.includes('test') || target.includes('run')) {
      runSyncFromSettings();
    }
  });
});

function qaCountClass(n) {
  if (n === 0) return 'qa-count qa-count-zero';
  if (n >= 5) return 'qa-count qa-count-high';
  return 'qa-count qa-count-mid';
}

function qaSortOptions() {
  return [
    { v: 'issues_desc', label: tAny('qa.sort.issuesDesc') },
    { v: 'qa_desc', label: tAny('qa.sort.qaDesc') },
    { v: 'qa_asc', label: tAny('qa.sort.qaAsc') },
    { v: 'ocr_desc', label: tAny('qa.sort.ocrDesc') },
    { v: 'ocr_asc', label: tAny('qa.sort.ocrAsc') },
    { v: 'file_asc', label: tAny('qa.sort.fileAsc') }
  ];
}

function qaAllRows() {
  if (!qaData) return [];

  const rows = [];
  const pkgs = qaState.pkg === 'all' ? qaData.paquetes.map((_, i) => i) : [qaState.pkg];

  pkgs.forEach(pi => {
    const pkg = qaData.paquetes[pi];
    if (!pkg) return;

    (pkg.resultados || []).forEach((r, ri) => rows.push({ pi, ri, r }));
  });

  return rows;
}

function qaSortRows(rows) {
  const s = qaState.sort;
  const arr = rows.slice();

  arr.sort((a, b) => {
    switch (s) {
      case 'qa_asc':
        return (a.r.tiempo_qa || 0) - (b.r.tiempo_qa || 0);
      case 'ocr_desc':
        return (b.r.tiempo_ocr || 0) - (a.r.tiempo_ocr || 0);
      case 'ocr_asc':
        return (a.r.tiempo_ocr || 0) - (b.r.tiempo_ocr || 0);
      case 'issues_desc':
        return (b.r.issues || []).length - (a.r.issues || []).length;
      case 'file_asc':
        return String(a.r.imagen).localeCompare(String(b.r.imagen));
      case 'qa_desc':
      default:
        return (b.r.tiempo_qa || 0) - (a.r.tiempo_qa || 0);
    }
  });

  return arr;
}

function qaVisibleRows() {
  let rows = qaAllRows();
  const q = qaState.search.trim().toLowerCase();
  if (q) rows = rows.filter(x => String(x.r.imagen).toLowerCase().includes(q));
  return qaSortRows(rows);
}

function qaUpdateStats() {
  if (!qaData) return;

  const rows = qaAllRows();
  const pkgs = qaState.pkg === 'all' ? qaData.paquetes : [qaData.paquetes[qaState.pkg]].filter(Boolean);

  const nIssues = rows.reduce((a, x) => a + (x.r.issues || []).length, 0);
  const nWarn = rows.reduce((a, x) => a + (x.r.ocr_warnings || []).length, 0);
  const okCount = pkgs.filter(p => p.qa_ok).length;

  const setText = (id, v) => {
    const el = document.getElementById(id);
    if (el) el.textContent = v;
  };

  setText('qa-stat-images', rows.length);
  setText('qa-stat-issues', nIssues);
  setText('qa-stat-warn', nWarn);
  setText('qa-stat-status', !pkgs.length ? '--' : okCount === pkgs.length ? 'OK' : 'FAIL');
}

function qaRebuildControls() {
  if (!qaData) return;

  const sel = document.getElementById('qa-pkg-select');
  if (sel) {
    const allCount = qaData.paquetes.reduce((a, p) => a + (p.total_imagenes || 0), 0);

    sel.innerHTML =
      `<option value="all">${qaEsc(tAny('qa.allPackages', allCount))}</option>` +
      qaData.paquetes
        .map((p, i) => `<option value="${i}">${qaEsc(p.paquete)} (${p.total_imagenes})</option>`)
        .join('');

    sel.value = qaState.pkg === 'all' ? 'all' : String(qaState.pkg);
  }

  const sortSel = document.getElementById('qa-sort');
  if (sortSel) {
    sortSel.innerHTML = qaSortOptions()
      .map(o => `<option value="${o.v}">${qaEsc(o.label)}</option>`)
      .join('');
    sortSel.value = qaState.sort;
  }
}

async function loadQaReport() {
  if (!hasPywebview()) return;

  let res = null;
  try {
    res = await window.pywebview.api.getQaReport();
  } catch (e) {
    res = null;
  }

  if (!res || !res.ok) return;

  qaData = res;
  qaState.pkg = 'all';
  qaState.search = '';
  qaState.sort = 'issues_desc';

  const sel = document.getElementById('qa-pkg-select');
  if (sel) {
    sel.onchange = () => {
      qaState.pkg = sel.value === 'all' ? 'all' : parseInt(sel.value, 10);
      renderQaTable();
    };
  }

  const sortSel = document.getElementById('qa-sort');
  if (sortSel) {
    sortSel.onchange = () => {
      qaState.sort = sortSel.value;
      renderQaTable();
    };
  }

  const search = document.getElementById('qa-search');
  if (search) {
    search.value = '';
    search.oninput = () => {
      qaState.search = search.value;
      renderQaTable();
    };
  }

  qaRebuildControls();

  const emptyEl = document.getElementById('qa-empty');
  const contentEl = document.getElementById('qa-content');

  if (emptyEl) emptyEl.classList.add('d-none');
  if (contentEl) contentEl.classList.remove('d-none');

  if (res.paquetes.length > 0) renderQaTable();

  exportPopulatePackages();
}

function renderQaTable() {
  if (!qaData) return;

  const rows = qaVisibleRows();

  const tbody = document.getElementById('qa-tbody');
  if (!tbody) return;

  const badge = document.getElementById('qa-summary-badge');
  if (badge) {
    badge.textContent = rows.length ? `${rows.length} img` : tAny('qa.noData');
  }

  tbody.innerHTML = rows
    .map(x => {
      const r = x.r;
      const nIssues = (r.issues || []).length;
      const nWarn = (r.ocr_warnings || []).length;
      const qq = (r.quality || 'N/A').toLowerCase();

      const passes =
        r.qa_pass_counts && r.qa_pass_counts.length
          ? `<span class="qa-count-zero">(${qaEsc(r.qa_pass_counts.join('/'))})</span>`
          : '';

      return (
        `<tr data-pi="${x.pi}" data-idx="${x.ri}">` +
        `<td class="qa-col-img"><img class="qa-thumb" data-img="${qaEsc(r.imagen)}" alt=""></td>` +
        `<td><span class="qa-file" title="${qaEsc(r.imagen)}">${qaEsc(String(r.imagen).split(/[\\/]/).pop())}</span></td>` +
        `<td class="qa-col-center"><span class="qa-badge ${r.ok ? 'qa-badge-ok' : 'qa-badge-ko'}">${r.ok ? 'OK' : 'FAIL'}</span></td>` +
        `<td class="qa-col-center"><span class="qa-quality qa-quality-${qaEsc(qq)}">${qaEsc(r.quality)}</span></td>` +
        `<td class="qa-col-center"><span class="${qaCountClass(nIssues)}">${nIssues}</span></td>` +
        `<td class="qa-col-center"><span class="${qaCountClass(nWarn)}">${nWarn}</span></td>` +
        `<td class="qa-col-center">${r.qa_passes || 0}${passes}</td>` +
        `<td class="qa-col-center">${(r.tiempo_ocr || 0).toFixed(1)}</td>` +
        `<td class="qa-col-center">${(r.tiempo_qa || 0).toFixed(1)}</td>` +
        `<td><span class="qa-summary-cell" title="${qaEsc(r.summary)}">${qaEsc(r.summary)}</span></td>` +
        `</tr>`
      );
    })
    .join('');

  tbody.querySelectorAll('tr').forEach(tr => {
    tr.addEventListener('click', () =>
      showQaDetail(parseInt(tr.dataset.pi, 10), parseInt(tr.dataset.idx, 10))
    );
  });

  qaObserveThumbs(tbody);
  qaUpdateStats();
}

let qaObserver = null;

function qaObserveThumbs(scope) {
  if (!hasPywebview()) return;
  if (!('IntersectionObserver' in window)) return;

  if (qaObserver) qaObserver.disconnect();

  qaObserver = new IntersectionObserver(
    async entries => {
      for (const e of entries) {
        if (!e.isIntersecting) continue;

        const img = e.target;
        qaObserver.unobserve(img);

        const data = await window.pywebview.api.getImageData(img.dataset.img, 160);
        if (data) img.src = data;
      }
    },
    {
      root: document.querySelector('.qa-table-wrap'),
      rootMargin: '200px'
    }
  );

  scope.querySelectorAll('img.qa-thumb[data-img]').forEach(img => qaObserver.observe(img));
}

async function showQaDetail(pkgIdx, rowIdx) {
  const pkg = qaData.paquetes[pkgIdx];
  const r = pkg.resultados[rowIdx];

  const body = document.getElementById('qa-report-body');
  if (!body) return;

  const navList = qaVisibleRows();
  let navPos = navList.findIndex(x => x.pi === pkgIdx && x.ri === rowIdx);
  if (navPos < 0) navPos = 0;
  qaState.detailList = navList;
  qaState.detailPos = navPos;

  body.querySelectorAll('.qa-detail').forEach(d => {
    if (d._ro) d._ro.disconnect();
    d.remove();
  });

  const detail = document.createElement('div');
  detail.className = 'qa-detail';

  const q = (r.quality || 'N/A').toLowerCase();

  const confCounts = { high: 0, medium: 0, low: 0 };
  (r.issues || []).forEach(iss => {
    const c = (iss.confidence || 'low').toLowerCase();
    if (confCounts[c] != null) confCounts[c]++;
  });

  const chev = `<svg class="qa-chevron" xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m6 9 6 6 6-6"/></svg>`;

  const issuesHtml = (r.issues || [])
    .map((iss, i) => {
      const sev = (iss.severity || 'low').toLowerCase();
      const bbox = iss.bbox || {};

      const suggested = iss.suggestion
        ? `<div class="qa-issue-box"><div class="qa-issue-box-label">${qaEsc(tAny('qa.detail.suggested'))}</div><div class="qa-issue-suggestion">${qaEsc(iss.suggestion)}</div></div>`
        : '';

      return `<details class="qa-issue qa-sev-${qaEsc(sev)}" data-issue="${i}" open>
        <summary class="qa-issue-head">
          <span class="qa-issue-icon">${qaEsc((iss.category || '?').slice(0, 2).toUpperCase())}</span>
          <span class="qa-issue-title">${qaEsc(iss.category)}</span>
          <span class="qa-sev qa-sev-${qaEsc(sev)}">${qaEsc(iss.severity)}</span>
          <span class="qa-count-zero">${qaEsc(tAny('qa.detail.conf'))} ${qaEsc(iss.confidence)}</span>
          ${chev}
        </summary>
        <div class="qa-issue-body">
          <div class="qa-issue-compare">
            <div class="qa-issue-box">
              <div class="qa-issue-box-label">${qaEsc(tAny('qa.detail.detected'))}</div>
              <div class="qa-issue-excerpt">"${qaEsc(iss.text_excerpt)}"</div>
            </div>
            ${suggested}
          </div>
          <div class="qa-issue-explanation">${qaEsc(iss.explanation)}</div>
          <div class="qa-issue-meta">bbox: ${bbox.x ?? 0}, ${bbox.y ?? 0}, ${bbox.width ?? 0}×${bbox.height ?? 0} · regions: ${qaEsc((iss.region_ids || []).join(', '))}</div>
          <div class="qa-issue-action"><span class="qa-action-btn">${qaEsc(tAny('qa.detail.actionRequired'))}</span></div>
        </div>
      </details>`;
    })
    .join('');

  const warnsHtml = (r.ocr_warnings || []).map(w => `<div class="qa-warn-item">${qaEsc(w)}</div>`).join('');
  const ocrHtml = (r.ocr_texts || []).map(t => `<span class="qa-ocr-text">${qaEsc(t)}</span>`).join('');

  detail.innerHTML = `<div class="qa-detail-header">
      <button type="button" class="qa-detail-back" id="qa-detail-back">${qaEsc(tAny('qa.detail.back'))}</button>
      <span class="qa-detail-title">${qaEsc(r.imagen)}</span>
      <span class="qa-quality qa-quality-${qaEsc(q)}" style="margin-left:auto">${qaEsc(r.quality)}</span>
    </div>
    <div class="qa-detail-body">
      <div class="qa-detail-img-pane">
        <div class="qa-detail-img-scroll" id="qa-detail-img-scroll">
          <div class="qa-detail-img-wrap" id="qa-img-wrap">
            <img class="qa-detail-img" id="qa-detail-img" alt="">
          </div>
        </div>
        <button type="button" class="qa-detail-nav qa-detail-nav-prev" id="qa-detail-prev" title="${qaEsc(tAny('qa.detail.prev'))}" ${navPos <= 0 ? 'disabled' : ''}><svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg></button>
        <button type="button" class="qa-detail-nav qa-detail-nav-next" id="qa-detail-next" title="${qaEsc(tAny('qa.detail.next'))}" ${navPos >= navList.length - 1 ? 'disabled' : ''}><svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m9 18 6-6-6-6"/></svg></button>
      </div>
      <div class="qa-detail-info-pane">
        <div class="qa-detail-section">
          <h6>${qaEsc(tAny('qa.detail.summary'))}</h6>
          <div class="qa-detail-summary">${qaEsc(r.summary)}</div>
        </div>

        <div class="qa-detail-section">
          <h6>${qaEsc(tAny('qa.detail.metrics'))}</h6>
          <div class="qa-metrics-grid">
            <div class="qa-metric-card">
              <div class="qa-metric-title">
                <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                ${qaEsc(tAny('qa.detail.time'))}
              </div>
              <div class="qa-metric-row"><span>OCR</span><b>${(r.tiempo_ocr || 0).toFixed(1)}s</b></div>
              <div class="qa-metric-row"><span>QA</span><b>${(r.tiempo_qa || 0).toFixed(1)}s</b></div>
            </div>

            <div class="qa-metric-card">
              <div class="qa-metric-title">
                <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/></svg>
                ${qaEsc(tAny('qa.detail.regionsCard'))}
              </div>
              <div class="qa-metric-row"><span>${qaEsc(tAny('qa.detail.total'))}</span><b>${r.regiones ?? 0}</b></div>
              <div class="qa-metric-row"><span>${qaEsc(tAny('qa.detail.issues'))}</span><b>${(r.issues || []).length}</b></div>
            </div>

            <div class="qa-metric-card">
              <div class="qa-metric-title">
                <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
                ${qaEsc(tAny('qa.detail.confidence'))}
              </div>
              <div class="qa-metric-row"><span>${qaEsc(tAny('qa.detail.high'))}</span><b>${confCounts.high}</b></div>
              <div class="qa-metric-row"><span>${qaEsc(tAny('qa.detail.medLow'))}</span><b>${confCounts.medium} / ${confCounts.low}</b></div>
            </div>
          </div>
        </div>

        <div class="qa-detail-section qa-detail-section-issues">
          <h6>${qaEsc(tAny('qa.detail.issuesTitle', (r.issues || []).length))}</h6>
          ${issuesHtml || `<div class="qa-count-zero">${qaEsc(tAny('qa.detail.noIssues'))}</div>`}
        </div>

        ${(r.ocr_warnings || []).length
          ? `<details class="qa-acc" disabled>
              <summary class="qa-acc-head">${qaEsc(tAny('qa.detail.ocrWarnings', r.ocr_warnings.length))}${chev}</summary>
              <div class="qa-acc-body">${warnsHtml}</div>
            </details>`
          : ''}

        <details class="qa-acc" disabled>
          <summary class="qa-acc-head">${qaEsc(tAny('qa.detail.ocrTexts', (r.ocr_texts || []).length))}${chev}</summary>
          <div class="qa-acc-body">
            <div class="qa-ocr-texts">
              ${ocrHtml || `<span class="qa-count-zero">${qaEsc(tAny('qa.detail.noTexts'))}</span>`}
            </div>
          </div>
        </details>
      </div>
    </div>`;

  body.appendChild(detail);

  const wrap = document.getElementById('qa-img-wrap');
  const img = document.getElementById('qa-detail-img');

  if (!wrap || !img) return;

  let ro = null;

  const drawBoxes = () => {
    wrap.querySelectorAll('.qa-bbox').forEach(el => el.remove());

    if (!img.naturalWidth || !img.naturalHeight) return;

    const scale = img.clientWidth / img.naturalWidth;
    if (!scale) return;

    const wr = wrap.getBoundingClientRect();
    const ir = img.getBoundingClientRect();

    const offX = ir.left - wr.left;
    const offY = ir.top - wr.top;

    (r.issues || []).forEach((iss, i) => {
      const b = iss.bbox;
      if (!b || b.width == null || b.height == null) return;

      const el = document.createElement('div');
      el.className = 'qa-bbox';
      el.style.left = offX + (b.x ?? 0) * scale + 'px';
      el.style.top = offY + (b.y ?? 0) * scale + 'px';
      el.style.width = b.width * scale + 'px';
      el.style.height = b.height * scale + 'px';
      el.innerHTML = `<span class="qa-bbox-label">${i + 1}</span>`;

      wrap.appendChild(el);
    });
  };

  const drawRaf = () => requestAnimationFrame(drawBoxes);

  img.addEventListener('load', drawRaf);

  ro = new ResizeObserver(drawRaf);
  ro.observe(wrap);
  detail._ro = ro;

  const backBtn = document.getElementById('qa-detail-back');
  if (backBtn) {
    backBtn.addEventListener('click', () => {
      if (ro) ro.disconnect();
      detail.remove();
    });
  }

  const prevBtn = document.getElementById('qa-detail-prev');
  const nextBtn = document.getElementById('qa-detail-next');
  if (prevBtn) prevBtn.addEventListener('click', () => qaDetailNav(-1));
  if (nextBtn) nextBtn.addEventListener('click', () => qaDetailNav(1));

  if (hasPywebview()) {
    window.pywebview.api.getImageData(r.imagen).then(data => {
      if (data) {
        img.src = data;
        drawRaf();
      } else if (img.complete && img.naturalWidth) {
        drawRaf();
      }
    });
  }

  detail.querySelectorAll('.qa-issue-body').forEach(el => {
    el.addEventListener('click', () => {
      const issueEl = el.closest('.qa-issue');
      if (!issueEl) return;

      const idx = parseInt(issueEl.dataset.issue, 10);
      const boxes = wrap.querySelectorAll('.qa-bbox');

      boxes.forEach(b => b.classList.remove('qa-bbox-active'));

      const box = boxes[idx];
      if (box) {
        box.classList.add('qa-bbox-active');
        box.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    });
  });
}

function qaDetailNav(delta) {
  const list = qaState.detailList;
  if (!list || !list.length) return;
  const pos = qaState.detailPos + delta;
  if (pos < 0 || pos >= list.length) return;
  const x = list[pos];
  showQaDetail(x.pi, x.ri);
}

function qaCloseDetail() {
  const d = document.querySelector('.qa-detail');
  if (!d) return;
  if (d._ro) d._ro.disconnect();
  d.remove();
}

bindUi('device-refresh', 'click', function () {
  const btn = this;
  btn.classList.add('spinning');
  updateDeviceWidget().finally(() => {
    setTimeout(() => btn.classList.remove('spinning'), 100);
  });
});

document
  .querySelectorAll(
    '.btn-refresh-panel:not(#btn-bc-refresh):not(#btn-bc-start):not(#btn-bc-stop):not(#btn-run-refresh):not(#btn-run-open)'
  )
  .forEach(function (btn) {
    btn.addEventListener('click', function () {
      this.classList.add('spinning');

      const jobs = [updateDeviceWidget()];
      if (this.closest('#pane-reports')) jobs.push(loadQaReport());

      Promise.all(jobs).finally(() => {
        setTimeout(() => this.classList.remove('spinning'), 100);
      });
    });
  });

bindUi('btn-copy-serial', 'click', function () {
  const serialEl = document.getElementById('spec-serial');
  const serial = serialEl ? serialEl.textContent : '';

  if (serial && serial !== '--') {
    navigator.clipboard.writeText(serial);
    this.classList.add('copied');
    setTimeout(() => this.classList.remove('copied'), 800);
  }
});

let initialized = false;
let wzActive = false;
let wzStep = 1;
let wzTheme = 'light';
let wzBound = false;
let wzResolve = null;

// ============================================================
// Wizard de configuración inicial (solo primer arranque)
// ============================================================
function wzEl(id) { return document.getElementById(id); }

function wzMeasureScreen() {
  const s1 = wzEl('wz-screen-1');
  if (!s1) return;
  const inner = s1.querySelector('.wz-screen-inner');
  if (!inner) return;
  const cs = getComputedStyle(s1);
  const padTop = parseFloat(cs.paddingTop) || 0;
  const padBottom = parseFloat(cs.paddingBottom) || 0;
  const h = inner.scrollHeight + padTop + padBottom;
  document.querySelectorAll('.wz-screen').forEach(s => { s.style.height = h + 'px'; });
}

function wzShow() {
  wzActive = true;
  wzStep = 1;
  wzTheme = 'light';
  const bd = wzEl('wz-backdrop');
  if (!bd) return Promise.resolve();
  const wzPsdns = wzEl('wz-psdns-enabled');
  if (wzPsdns) wzPsdns.checked = psdnsEnabled();
  const curAccent = document.querySelector('.accent-swatch.active');
  if (curAccent) {
    document.querySelectorAll('.wz-accent-swatch').forEach(s => s.classList.remove('active'));
    const m = document.querySelector('.wz-accent-swatch[data-wz-accent="' + curAccent.dataset.accent + '"]');
    if (m) m.classList.add('active');
  }
  const wzSidebar = wzEl('wz-sidebar-mode');
  const sidebarEl = safeElement('setting-sidebar-mode');
  if (wzSidebar && sidebarEl) wzSidebar.value = sidebarEl.value;
  const wzCompact = wzEl('wz-compact');
  const compactEl = safeElement('setting-compact');
  if (wzCompact && compactEl) wzCompact.checked = compactEl.checked;
  const wzAnim = wzEl('wz-animations');
  const animEl = safeElement('setting-animations');
  if (wzAnim && animEl) wzAnim.checked = animEl.checked;
  wzBind();
  applyTheme(wzTheme);
  bd.hidden = false;
  requestAnimationFrame(() => bd.classList.add('ax-in'));
  const tbMenu = document.getElementById('titlebar-menu');
  if (tbMenu) tbMenu.classList.add('menu-disabled');
  wzGoStep(1);
  wzMeasureScreen();
  psdnsAnnotateAll();
  return new Promise(resolve => { wzResolve = resolve; });
}

function wzHide() {
  wzActive = false;
  const bd = wzEl('wz-backdrop');
  if (!bd) return;
  bd.classList.remove('ax-in');
  setTimeout(() => { bd.hidden = true; }, 200);
  const tbMenu = document.getElementById('titlebar-menu');
  if (tbMenu) tbMenu.classList.remove('menu-disabled');
  psdnsAnnotateAll();
}

function wzGoStep(n) {
  wzStep = n;
  const s1 = wzEl('wz-screen-1');
  const s2 = wzEl('wz-screen-2');
  const s3 = wzEl('wz-screen-3');
  const back = wzEl('wz-back');
  const next = wzEl('wz-next');
  const finish = wzEl('wz-finish');
  if (s1) s1.hidden = n !== 1;
  if (s2) s2.hidden = n !== 2;
  if (s3) s3.hidden = n !== 3;
  if (back) back.hidden = n === 1;
  if (next) next.hidden = n === 3;
  if (finish) finish.hidden = n !== 3;
  const footHint = document.querySelector('.wz-psdns-foot-hint');
  if (footHint) footHint.hidden = n !== 3;
  if (n === 3) wzValidate();
}

function wzValidate() {
  const src = wzEl('wz-source');
  const tgt = wzEl('wz-target');
  const finish = wzEl('wz-finish');
  if (finish) finish.disabled = !(src && src.value && tgt && tgt.value);
}

async function wzFinish() {
  const lang = (wzEl('wz-lang') || {}).value || 'en';
  const src = (wzEl('wz-source') || {}).value || '';
  const tgt = (wzEl('wz-target') || {}).value || '';
  const ft = (wzEl('wz-filter-t') || {}).value || '';
  const fe = (wzEl('wz-filter-e') || {}).value || '';
  if (!src || !tgt) return;

  const langEl = safeElement('setting-ui-language');
  if (langEl) langEl.value = lang;
  const wzPsdns = wzEl('wz-psdns-enabled');
  const psdnsEl = safeElement('psdns-enabled');
  if (wzPsdns && psdnsEl) psdnsEl.checked = wzPsdns.checked;
  applyTheme(wzTheme);
  const srcEl = safeElement('pipe-pair-source');
  if (srcEl) srcEl.value = src;
  const tgtEl = safeElement('pipe-pair-target');
  if (tgtEl) tgtEl.value = tgt;
  const ftEl = safeElement('pipe-filter-t');
  if (ftEl) ftEl.value = ft;
  const feEl = safeElement('pipe-filter-e');
  if (feEl) feEl.value = fe;

  try {
    if (window.I18N && typeof I18N.apply === 'function') I18N.apply(lang);
  } catch (e) {}
  applyExtraI18n();

  await persistCurrent();
  syncControls(collectSettings());
  wzHide();
  if (wzResolve) { const r = wzResolve; wzResolve = null; r(); }
}

function wzBind() {
  if (wzBound) return;
  wzBound = true;
  const next = wzEl('wz-next');
  const back = wzEl('wz-back');
  const finish = wzEl('wz-finish');
  if (next) next.addEventListener('click', () => wzGoStep(wzStep + 1));
  if (back) back.addEventListener('click', () => wzGoStep(wzStep - 1));
  if (finish) finish.addEventListener('click', wzFinish);
  const src = wzEl('wz-source');
  const tgt = wzEl('wz-target');
  if (src) src.addEventListener('change', wzValidate);
  if (tgt) tgt.addEventListener('change', wzValidate);
  const langSel = wzEl('wz-lang');
  if (langSel) langSel.addEventListener('change', () => {
    try { if (window.I18N && typeof I18N.apply === 'function') I18N.apply(langSel.value); } catch (e) {}
    applyExtraI18n();
    psdnsAnnotateAll();
  });
  const wzPsdns = wzEl('wz-psdns-enabled');
  if (wzPsdns) wzPsdns.addEventListener('change', () => psdnsAnnotateAll());
  document.querySelectorAll('.wz-theme-card').forEach(card => {
    card.addEventListener('click', () => {
      document.querySelectorAll('.wz-theme-card').forEach(c => c.classList.remove('active'));
      card.classList.add('active');
      wzTheme = card.dataset.wzTheme;
      applyTheme(wzTheme);
    });
  });
  document.querySelectorAll('.wz-accent-swatch').forEach(sw => {
    sw.addEventListener('click', () => {
      document.querySelectorAll('.wz-accent-swatch').forEach(s => s.classList.remove('active'));
      sw.classList.add('active');
      const match = document.querySelector('.accent-swatch[data-accent="' + sw.dataset.wzAccent + '"]');
      if (match) {
        document.querySelectorAll('.accent-swatch').forEach(s => s.classList.remove('active'));
        match.classList.add('active');
      }
      applyAccent(sw.dataset.wzAccent);
    });
  });
  const wzSidebar = wzEl('wz-sidebar-mode');
  if (wzSidebar) wzSidebar.addEventListener('change', () => {
    const sidebarEl = safeElement('setting-sidebar-mode');
    if (sidebarEl) sidebarEl.value = wzSidebar.value;
    applySettings(collectSettings());
  });
  const wzCompact = wzEl('wz-compact');
  if (wzCompact) wzCompact.addEventListener('change', () => {
    const compactEl = safeElement('setting-compact');
    if (compactEl) compactEl.checked = wzCompact.checked;
    applySettings(collectSettings());
  });
  const wzAnim = wzEl('wz-animations');
  if (wzAnim) wzAnim.addEventListener('change', () => {
    const animEl = safeElement('setting-animations');
    if (animEl) animEl.checked = wzAnim.checked;
    applySettings(collectSettings());
  });
}

async function wzCheckFirstRun() {
  if (!hasPywebview()) return false;
  try {
    const cfg = await window.pywebview.api.loadConfig();
    if (cfg) return false;
    const recent = await window.pywebview.api.getRecentProjects();
    if (recent && recent.length > 0) return false;
    return true;
  } catch (e) {
    return false;
  }
}

function signalAppReady() {
  try {
    if (window.pywebview && window.pywebview.api && window.pywebview.api.appReady)
      window.pywebview.api.appReady();
  } catch (e) {}
}

function init() {
  if (initialized) return;
  initialized = true;

  (async () => {
    // Annotate the PSDNS textareas before the welcome dialog blocks init.
    // wzShow() below only resolves when the user clicks Finish, so without
    // this early refresh the welcome dialog (wz-filter-t/e) would never be
    // annotated while it is open. Fire-and-forget: the dialog shows
    // immediately and the annotations appear once the bridge resolves.
    psdnsRefresh();
    if (await wzCheckFirstRun()) {
      // wzShow() muestra el wizard de forma sincrona y devuelve un Promise que
      // solo resuelve al hacer Finish. Revelamos la ventana en cuanto el wizard
      // es visible (no al terminar), y seguimos bloqueando init hasta el Finish.
      const wzPromise = wzShow();
      signalAppReady();
      await wzPromise;
    }
    const saved = await loadSettings();
    syncControls(saved);
    applySettings(saved);

    try {
      if (window.I18N && typeof I18N.apply === 'function') I18N.apply(uiLang());
    } catch (e) {}

    applyExtraI18n();
    exportPopulatePackages();
    updateDeviceWidget();
    loadRecentProjects();
    runSyncFromSettings();
    runRenderLivePanes();
    psdnsRefresh();

    try {
      const cur = await window.pywebview.api.getCurrentProject();
      if (cur && cur.path) await restoreProject(cur.path);
    } catch (e) {}
    // Subsequent runs: core UI is ready -> reveal the window.
    signalAppReady();
  })().catch(e => console.warn('[AURA QA] init failed', e));
}

window.addEventListener('pywebviewready', () => {
  initialized = false;
  init();
});

setTimeout(init, 1000);



document.querySelectorAll('.theme-card').forEach(card => {
  card.addEventListener('click', () => applyTheme(card.dataset.theme));
});

document.querySelectorAll('.accent-swatch').forEach(swatch => {
  swatch.addEventListener('click', () => applyAccent(swatch.dataset.accent));
});

bindUi('setting-sidebar-mode', 'change', function () {
  applySettings({ sidebarMode: this.value });
});

bindUi('setting-compact', 'change', function () {
  applySettings({ compact: this.checked });
});

bindUi('setting-animations', 'change', function () {
  applySettings({ animations: this.checked });
});

bindUi('psdns-enabled', 'change', async function () {
  if (this.checked && typeof window.Popup === 'object' && window.Popup.confirm) {
    const res = await window.Popup.confirm({
      title: tAny('psdns.enable'),
      body: tAny('psdns.enableInfo'),
      okLabel: tAny('psdns.popup.accept'),
      cancelLabel: tAny('psdns.popup.dismiss')
    });
    if (res !== 'ok') {
      this.checked = false;
      return;
    }
  }
  psdnsAnnotateAll();
});

bindUi('setting-ui-language', 'change', function () {
  try {
    if (window.I18N && typeof I18N.apply === 'function') I18N.apply(uiLang());
  } catch (e) {}

  applyExtraI18n();
  exportPopulatePackages();
  refreshExportPreview();
  psdnsAnnotateAll();

  runSetBadge(runState.status);
  runUpdateWidget(runState);
  runRenderLivePanes();
  runRenderPackagesPane();

  bcSetBadge(
    bcState === 'connected'
      ? 'connected'
      : bcState === 'starting'
        ? 'starting'
        : bcState === 'idle'
          ? 'idle'
          : 'error',
    bcState === 'connected'
  );

  bcSetOverlay(bcState, bcOverlayOpts);

  if (qaData) {
    qaRebuildControls();
    qaUpdateStats();
    renderQaTable();
  }
});

bindUi('btn-save-settings', 'click', async function () {
  const ok = await persistCurrent();
  if (ok) runSyncFromSettings();

  const btn = this;
  btn.classList.add('saved');
  setTimeout(() => btn.classList.remove('saved'), 1500);

  const toastEl = document.getElementById('settings-toast');
  if (!toastEl) return;

  const bodySpan = toastEl.querySelector('.toast-body span');
  if (bodySpan) bodySpan.textContent = tAny(ok ? 'toast.saved' : 'toast.error');

  toastEl.className = `toast align-items-center text-bg-${ok ? 'success' : 'danger'} border-0`;

  if (window.bootstrap && bootstrap.Toast) {
    bootstrap.Toast.getOrCreateInstance(toastEl, { delay: 2500 }).show();
  }
});

const exportUI = {
  el: id => document.getElementById(id),
  previewTimer: null,
  previewSeq: 0,
  busy: false,
  lastPath: null
};

function setExportPath(dir) {
  const input = exportUI.el('export-path');
  if (input) input.value = dir || '';

  const t = exportUI.el('export-path-text');
  if (t) {
    t.textContent = dir || '--';
    t.title = dir || '';
  }
}

function exportPopulatePackages() {
  const sel = exportUI.el('export-packages');
  if (!sel) return;

  const keep = sel.value;
  const total = qaData ? qaData.paquetes.reduce((a, p) => a + (p.total_imagenes || 0), 0) : 0;

  sel.innerHTML =
    `<option value="all">${qaEsc(xt('export.allPackages', total))}</option>` +
    (qaData
      ? qaData.paquetes
          .map(
            p =>
              `<option value="${qaEsc(p.paquete)}">${qaEsc(p.paquete)} (${p.total_imagenes})</option>`
          )
          .join('')
      : '');

  sel.value = [...sel.options].some(o => o.value === keep) ? keep : 'all';
}

function chipValues(groupId) {
  const chips = [...document.querySelectorAll(`#${groupId} .export-chip`)];
  const on = chips
    .filter(c => c.getAttribute('aria-pressed') === 'true')
    .map(c => c.dataset.v);

  return on.length === chips.length ? [] : on;
}

function collectExportOpts() {
  const pkgEl = exportUI.el('export-packages');
  const pkg = pkgEl ? pkgEl.value : 'all';

  const thumb = document.querySelector('input[name="export-thumb"]:checked');

  const destEl = exportUI.el('export-path');
  const fileEl = exportUI.el('export-filename');

  return {
    destination: destEl ? destEl.value : '',
    filename: fileEl ? fileEl.value : '',
    packages: pkg === 'all' ? [] : [pkg],
    severities: chipValues('export-severity'),
    qualities: chipValues('export-quality'),
    includeScreenshots: safeChecked('export-screenshots'),
    thumbSize: thumb ? thumb.value : 'm',
    includeWarnings: safeChecked('export-warnings'),
    onlyWithIssues: safeChecked('export-only-issues'),
    lang: uiLang()
  };
}

function refreshExportPreview() {
  clearTimeout(exportUI.previewTimer);

  exportUI.previewTimer = setTimeout(async () => {
    const summary = exportUI.el('export-summary');
    const run = exportUI.el('export-run');

    const seq = ++exportUI.previewSeq;

    if (!hasPywebview() || !qaData) {
      if (summary) summary.dataset.state = 'empty';

      const imgCount = exportUI.el('export-count-images');
      const issCount = exportUI.el('export-count-issues');
      const hint = exportUI.el('export-hint');

      if (imgCount) imgCount.textContent = '--';
      if (issCount) issCount.textContent = '--';
      if (hint) hint.textContent = xt('export.hint.noProject');
      if (run) run.disabled = true;
      return;
    }

    let res = null;
    try {
      res = await window.pywebview.api.previewExport(collectExportOpts());
    } catch (e) {}

    if (seq !== exportUI.previewSeq) return;
    if (!res || !res.ok) return;

    const zero = res.images === 0;

    if (summary) summary.dataset.state = zero ? 'zero' : 'ready';

    const imgCount = exportUI.el('export-count-images');
    const issCount = exportUI.el('export-count-issues');
    const hint = exportUI.el('export-hint');

    if (imgCount) imgCount.textContent = res.images;
    if (issCount) issCount.textContent = res.issues;
    if (hint) hint.textContent = xt(zero ? 'export.hint.zero' : 'export.hint.ready');
    if (run) run.disabled = zero || exportUI.busy;
  }, 150);
}

function hideExportResult() {
  const r = exportUI.el('export-result');
  if (r) r.hidden = true;
}

function showExportResult(kind, title, detail, withActions) {
  const r = exportUI.el('export-result');
  if (!r) return;

  const icon =
    kind === 'ok'
      ? `<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>`
      : `<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" x2="12" y1="8" y2="12"/><line x1="12" x2="12.01" y1="16" y2="16"/></svg>`;

  r.dataset.kind = kind;

  r.innerHTML =
    `<div class="export-result-head">${icon}<span>${qaEsc(title)}</span></div>` +
    `<div class="export-result-detail">${qaEsc(detail)}</div>` +
    (withActions
      ? `<div class="export-result-actions">
          <button type="button" class="export-link-btn" data-open="file">${qaEsc(xt('export.openFile'))}</button>
          <button type="button" class="export-link-btn" data-open="folder">${qaEsc(xt('export.openFolder'))}</button>
        </div>`
      : '');

  r.hidden = false;

  r.querySelectorAll('[data-open]').forEach(b =>
    b.addEventListener('click', () => {
      if (hasPywebview()) window.pywebview.api.openExport(b.dataset.open);
    })
  );
}

function exportErrorMessage(res) {
  const code = (res && res.error) || 'generic';
  const key = 'export.err.' + code;

  return XT.en[key] != null
    ? xt(key, (res && res.detail) || '')
    : xt('export.err.generic', (res && (res.detail || res.error)) || '?');
}

// Bug #3 cubierto de forma segura: si el botón export-date no existe, no rompe.
const exportDateBtn = exportUI.el('export-date');
if (exportDateBtn) {
  exportDateBtn.addEventListener('click', () => {
    const f = exportUI.el('export-filename');
    if (!f) return;

    const d = new Date();
    const stamp = `${d.getFullYear()}${String(d.getMonth() + 1).padStart(2, '0')}${String(d.getDate()).padStart(2, '0')}`;

    f.value = f.value.trim().replace(/\d{8}$/, '') + '_' + stamp;
  });
}

bindUi('export-filename', 'input', hideExportResult);

document.querySelectorAll('#export-severity .export-chip, #export-quality .export-chip').forEach(chip => {
  chip.addEventListener('click', () => {
    const group = chip.parentElement;
    const pressed = chip.getAttribute('aria-pressed') === 'true';
    const stillOn = group.querySelectorAll('.export-chip[aria-pressed="true"]').length;

    if (pressed && stillOn === 1) return;

    chip.setAttribute('aria-pressed', pressed ? 'false' : 'true');
    refreshExportPreview();
  });
});

['export-packages', 'export-screenshots', 'export-warnings', 'export-only-issues'].forEach(id => {
  const el = exportUI.el(id);
  if (el) el.addEventListener('change', refreshExportPreview);
});

document.querySelectorAll('input[name="export-thumb"]').forEach(r =>
  r.addEventListener('change', refreshExportPreview)
);

const screenshotsEl = exportUI.el('export-screenshots');
if (screenshotsEl) {
  screenshotsEl.addEventListener('change', function () {
    const row = exportUI.el('export-thumb-row');
    if (row) row.style.display = this.checked ? '' : 'none';
  });
}

bindUi('export-run', 'click', async function () {
  if (exportUI.busy) return;

  if (!hasPywebview()) {
    showExportResult('error', xt('export.err.title'), xt('export.err.noBridge'), false);
    return;
  }

  const btn = this;
  const label = exportUI.el('export-run-label');

  exportUI.busy = true;

  btn.disabled = true;
  btn.classList.add('is-busy');
  if (label) label.textContent = xt('export.running');

  hideExportResult();

  try {
    const res = await window.pywebview.api.exportXlsx(collectExportOpts());

    if (res && res.ok) {
      const shortPath = String(res.path).split(/[\/]/).slice(-2).join('/');
      showExportResult('ok', xt('export.done'), xt('export.doneDetail', res.images, res.issues, shortPath), true);
    } else {
      showExportResult('error', xt('export.err.title'), exportErrorMessage(res), false);
    }
  } catch (e) {
    showExportResult(
      'error',
      xt('export.err.title'),
      xt('export.err.generic', e && e.message ? e.message : e),
      false
    );
  } finally {
    exportUI.busy = false;
    btn.classList.remove('is-busy');
    if (label) label.textContent = xt('export.run');
    refreshExportPreview();
  }
});

// ============================================================
// TITLEBAR MENU
// ============================================================
(function () {
  const menu = document.getElementById('titlebar-menu');
  if (!menu) return;

  function closeAll() {
    menu.querySelectorAll('.menu-item.open, .menu-sub.open').forEach(el => el.classList.remove('open'));
  }

  function openMenu(name) {
    closeAll();
    const item = menu.querySelector('.menu-item[data-menu="' + name + '"]');
    if (item) item.classList.add('open');
  }

  menu.querySelectorAll('.menu-btn[data-menu]').forEach(btn => {
    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      const name = this.dataset.menu;
      const item = this.closest('.menu-item');
      if (item.classList.contains('open')) closeAll();
      else openMenu(name);
    });
  });

  menu.querySelectorAll('.menu-sub-btn').forEach(btn => {
    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      const sub = this.closest('.menu-sub');
      sub.classList.toggle('open');
    });
  });

  document.addEventListener('click', closeAll);

  // --- Recent projects submenu ---
  const recentList = document.getElementById('menu-recent-list');
  const recentSub = document.getElementById('menu-recent');

  async function loadRecentMenu() {
    if (!recentList || !hasPywebview()) return;
    try {
      const projects = await window.pywebview.api.getRecentProjects();
      if (!projects || projects.length === 0) {
        recentList.innerHTML = '<div class="menu-empty">No recent projects</div>';
        return;
      }
      recentList.innerHTML = projects
        .map(p => {
          const path = typeof p === 'string' ? p : p.path;
          const name = typeof p === 'string' ? p.split(/[\/\\]/).pop() : p.name;
          return '<button type="button" class="menu-recent-item" data-path="' + qaEsc(path) + '" title="' + qaEsc(path) + '">' + qaEsc(name) + '</button>';
        })
        .join('');
      recentList.querySelectorAll('.menu-recent-item').forEach(el => {
        el.addEventListener('click', function (e) {
          e.stopPropagation();
          closeAll();
          openAndLoad(this.dataset.path);
        });
      });
    } catch (e) {}
  }

  if (recentSub) {
    recentSub.addEventListener('mouseenter', loadRecentMenu);
  }

  // --- Actions ---
  const NAV_MAP = {
    'nav-home': '#pane-home',
    'nav-test': '#pane-test',
    'nav-device': '#pane-device',
    'nav-reports': '#pane-reports',
    'nav-bluecode': '#pane-bluecode',
    'nav-settings': '#pane-settings'
  };

  function navTo(paneId) {
    const btn = document.querySelector('[data-bs-target="' + paneId + '"]');
    if (btn) btn.click();
  }

  function doAction(action) {
    closeAll();
    switch (action) {
      case 'new-project':
        document.getElementById('btn-test-new') && document.getElementById('btn-test-new').click();
        break;
      case 'open-project':
        document.getElementById('btn-test-open') && document.getElementById('btn-test-open').click();
        break;
      case 'quit':
        if (hasPywebview()) window.pywebview.api.close();
        break;
      case 'clear-console':
        if (typeof runClear === 'function') runClear();
        break;
      case 'toggle-autoscroll':
        const auto = document.getElementById('run-autoscroll');
        if (auto) auto.checked = !auto.checked;
        break;
      case 'start-run':
        if (typeof runStart === 'function') runStart();
        break;
      case 'stop-run':
        if (typeof runStop === 'function') runStop();
        break;
      case 'refresh-device':
        if (typeof updateDeviceWidget === 'function') updateDeviceWidget();
        break;
      case 'toggle-sidebar':
        const col = document.querySelector('.sidebar-col');
        if (col) col.classList.toggle('collapsed');
        break;
      case 'export-xlsx':
        document.getElementById('export-run') && document.getElementById('export-run').click();
        break;
      case 'open-export':
        if (hasPywebview()) window.pywebview.api.openExport('folder');
        break;
      case 'docs':
        if (hasPywebview()) window.pywebview.api.openDocs();
        break;
      case 'about':
        if (typeof window.auraAbout === 'function') window.auraAbout();
        else showToast('AURA QA v1.0', 'info', 3000);
        break;
      default:
        if (NAV_MAP[action]) navTo(NAV_MAP[action]);
        break;
    }
  }

  menu.querySelectorAll('.menu-action[data-action]').forEach(btn => {
    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      doAction(this.dataset.action);
    });
  });

  // --- Window controls ---
  const btnMin = document.getElementById('btn-min');
  const btnMax = document.getElementById('btn-max');
  const btnClose = document.getElementById('btn-close');

  // --- Start from screenshot: input/boton activos solo si el checkbox
  //     esta marcado; al marcarlo se desactivan listing y crawl ---
  const ssChk = document.getElementById('run-from-screenshot');
  const ssFolder = document.getElementById('run-screenshot-folder');
  const ssBrowse = document.getElementById('btn-screenshot-browse');
  const ssCopy = document.getElementById('btn-screenshot-copy');
  const ssListing = document.getElementById('run-stage-listing');
  const ssCrawl = document.getElementById('run-stage-crawl');
  const ssProgress = document.getElementById('ss-copy-progress');
  const ssProgressText = document.getElementById('ss-copy-progress-text');
  const ssRunStart = document.getElementById('btn-run-start');

  // Estado de la copia de screenshots (la emite el puente Python en un hilo).
  // Mientras status==='copying' el boton "Start test" queda bloqueado.
  window.ssCopyState = { status: 'idle', seq: 0, rel: null };

  function ssSetStartBlocked(blocked) {
    if (!ssRunStart) return;
    if (blocked) {
      ssRunStart.disabled = true;
      ssRunStart.classList.add('is-busy');
    } else {
      ssRunStart.disabled = false;
      ssRunStart.classList.remove('is-busy');
    }
  }

  function ssProgressShow() {
    if (ssProgress) ssProgress.hidden = false;
  }
  function ssProgressHide() {
    if (ssProgress) ssProgress.hidden = true;
    if (ssProgress) ssProgress.style.removeProperty('--ss-progress');
  }
  function ssProgressUpdate(done, total, name) {
    const pct = total > 0 ? Math.round((done / total) * 100) : 0;
    if (ssProgressText) ssProgressText.textContent = xt('ss.copyProgress', pct, name || '');
    if (ssProgress) ssProgress.style.setProperty('--ss-progress', pct + '%');
  }

  window.onScreenshotCopy = function (ev) {
    if (!ev || typeof ev !== 'object') return;
    const st = window.ssCopyState;
    if (ev.kind === 'progress') {
      if (st.status !== 'copying') return;
      ssProgressUpdate(ev.done || 0, ev.total || 0, ev.name);
      return;
    }
    if (ev.kind === 'done') {
      st.status = 'done';
      st.rel = ev.path || null;
      if (ssFolder && ev.path) ssFolder.value = ev.path;
      ssProgressUpdate(ev.total || 1, ev.total || 1, '');
      ssSetStartBlocked(false);
      if (typeof ssSync === 'function') ssSync();
      showToast(xt('ss.copyDone', st.rel || ev.path || ''), 'success', 3600);
      setTimeout(ssProgressHide, 900);
      return;
    }
    if (ev.kind === 'error') {
      st.status = 'error';
      st.rel = null;
      ssSetStartBlocked(false);
      if (typeof ssSync === 'function') ssSync();
      ssProgressHide();
      showToast(xt('ss.copyErr', ev.detail || ev.code || '?'), 'danger', 4200);
    }
  };

  function ssSync() {
    const on = !!(ssChk && ssChk.checked);
    const copying = window.ssCopyState.status === 'copying';
    const norm = p => String(p || '').replace(/\\/g, '/').replace(/\/+$/, '').toLowerCase();
    const alreadyCopied = window.ssCopyState.status === 'done' && ssFolder && norm(window.ssCopyState.rel) === norm(ssFolder.value);
    const running = typeof runState !== 'undefined' && runState.status === 'running';
    const hasProj = typeof currentProject !== 'undefined' && !!currentProject;
    if (ssChk) ssChk.disabled = false;
    if (ssFolder) ssFolder.disabled = !on;
    if (ssBrowse) ssBrowse.disabled = !on || copying || running;
    if (ssCopy) {
      ssCopy.hidden = !on || !(ssFolder && ssFolder.value.trim());
      ssCopy.disabled = !on || !hasProj || copying || alreadyCopied || running;
    }
    if (ssListing) { ssListing.disabled = on; if (on) ssListing.checked = false; }
    if (ssCrawl) { ssCrawl.disabled = on; if (on) ssCrawl.checked = false; }
    ssSetStartBlocked(copying);
  }
  window.ssSync = ssSync;
  if (ssChk) ssChk.addEventListener('change', ssSync);
  if (ssFolder) ssFolder.addEventListener('input', ssSync);
  window.addEventListener('sscopy:changed', ssSync);
  ssSync();

  let winMaximized = false;
  const ICON_MAX = '<svg width="10" height="10" viewBox="0 0 10 10"><rect x="1" y="1" width="8" height="8" stroke="currentColor" stroke-width="1" fill="none"/></svg>';
  const ICON_RESTORE = '<svg width="10" height="10" viewBox="0 0 10 10"><rect x="3" y="1" width="6" height="6" stroke="currentColor" stroke-width="1" fill="none"/><path d="M1 3v6h6" stroke="currentColor" stroke-width="1" fill="none"/></svg>';

  function setMaxIcon() {
    if (!btnMax) return;
    btnMax.innerHTML = winMaximized ? ICON_RESTORE : ICON_MAX;
    btnMax.title = winMaximized ? 'Restore' : 'Maximize';
  }

  // Sincronizar con el estado real de la ventana (tras location.reload
  // al abrir un proyecto, winMaximized se reinicia a false).
  winMaximized = (window.outerWidth >= window.screen.availWidth &&
                  window.outerHeight >= window.screen.availHeight);
  setMaxIcon();

  if (btnMin) btnMin.addEventListener('click', () => { if (hasPywebview()) window.pywebview.api.minimize(); });
  if (btnMax) btnMax.addEventListener('click', () => {
    if (!hasPywebview()) return;
    window.pywebview.api.maximize();
    winMaximized = !winMaximized;
    setMaxIcon();
  });
  if (btnClose) btnClose.addEventListener('click', () => { if (hasPywebview()) window.pywebview.api.close(); });

  // --- Drag window from titlebar (frameless) ---
  const titlebar = document.getElementById('titlebar');
  if (titlebar) {
    titlebar.addEventListener('mousedown', function (e) {
      if (e.button !== 0) return;
      const t = e.target;
      if (t.closest('button, input, select, a, .menu-dropdown, .menu-sep, .menu-recent-item')) return;
      if (!hasPywebview()) return;
      e.preventDefault();
      if (winMaximized) {
        window.pywebview.api.maximize();
        winMaximized = false;
        setMaxIcon();
      }
      let lastX = e.screenX, lastY = e.screenY;
      let pending = null, rafId = 0;
      function flush() {
        rafId = 0;
        if (!pending) return;
        const dx = pending.x - lastX;
        const dy = pending.y - lastY;
        lastX = pending.x;
        lastY = pending.y;
        pending = null;
        if (dx !== 0 || dy !== 0) window.pywebview.api.moveBy(dx, dy);
      }
      function onMove(ev) {
        pending = { x: ev.screenX, y: ev.screenY };
        if (!rafId) rafId = requestAnimationFrame(flush);
      }
      function onUp() {
        document.removeEventListener('mousemove', onMove, true);
        document.removeEventListener('mouseup', onUp, true);
        if (rafId) { cancelAnimationFrame(rafId); flush(); }
      }
      document.addEventListener('mousemove', onMove, true);
      document.addEventListener('mouseup', onUp, true);
    });
  }

  // --- Keyboard shortcuts ---
  document.addEventListener('keydown', function (e) {
    const tag = (e.target.tagName || '').toLowerCase();
    const inInput = tag === 'input' || tag === 'textarea' || tag === 'select' || e.target.isContentEditable;
    const qaDetailOpen = !!document.querySelector('.qa-detail');

    if (e.ctrlKey && e.key === 'n') { e.preventDefault(); doAction('new-project'); }
    else if (e.ctrlKey && e.key === 'o') { e.preventDefault(); doAction('open-project'); }
    else if (e.ctrlKey && e.key === 'Enter') { e.preventDefault(); doAction('start-run'); }
    else if (e.ctrlKey && e.key === 'b') { e.preventDefault(); doAction('toggle-sidebar'); }
    else if (e.ctrlKey && e.key === 'e') { e.preventDefault(); doAction('export-xlsx'); }
    else if (e.ctrlKey && e.key === 'l') { e.preventDefault(); doAction('clear-console'); }
    else if (e.key === 'F5') { e.preventDefault(); doAction('refresh-device'); }
    else if (e.key === 'Escape' && !inInput) {
      if (qaDetailOpen) { qaCloseDetail(); return; }
      if (menu.querySelector('.menu-item.open')) { closeAll(); return; }
      if (typeof runState !== 'undefined' && runState.status === 'running') doAction('stop-run');
    }
    else if (qaDetailOpen && !inInput && !e.ctrlKey && !e.altKey && !e.metaKey) {
      if (e.key === 'ArrowLeft') { e.preventDefault(); qaDetailNav(-1); }
      else if (e.key === 'ArrowRight') { e.preventDefault(); qaDetailNav(1); }
    }
    else if (!inInput && !e.ctrlKey && !e.altKey && !e.metaKey) {
      const navKeys = { '1': 'nav-test', '2': 'nav-device', '3': 'nav-reports', '4': 'nav-bluecode', '5': 'nav-settings' };
      if (navKeys[e.key]) { e.preventDefault(); doAction(navKeys[e.key]); }
    }
  });

  // --- Sidebar toggle ---
  const sbToggle = document.getElementById('toggleSidebarBtn');
  if (sbToggle) {
    sbToggle.addEventListener('click', function () {
      const col = document.querySelector('.sidebar-col');
      if (col) col.classList.toggle('collapsed');
    });
  }

  // --- Welcome walkthroughs (right column) ---
  const wDocs = document.getElementById('wtab-docs');
  const wAbout = document.getElementById('wtab-about');
  if (wDocs) {
    wDocs.addEventListener('click', function () {
      if (hasPywebview()) window.pywebview.api.openDocs();
    });
  }
  if (wAbout) {
    wAbout.addEventListener('click', function () {
      if (typeof window.auraAbout === 'function') window.auraAbout();
      else if (typeof showToast === 'function') showToast('AURA QA v1.0', 'info', 3000);
    });
  }
})();