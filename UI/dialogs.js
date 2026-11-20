(function () {
  'use strict';

  if (window.__auraDialogs) return;
  window.__auraDialogs = true;

  function t(key, ...args) {
    let s = key;

    try {
      if (window.I18N && typeof window.I18N.t === 'function') {
        s = window.I18N.t(key);
      }
    } catch (e) {}

    args.forEach((a, i) => {
      s = s.split('{' + i + '}').join(a == null ? '' : a);
    });

    return s;
  }

  // Bug #2 también cubierto aquí.
  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, c => ({
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#39;'
    }[c]));
  }

  function api() {
    return window.pywebview && window.pywebview.api ? window.pywebview.api : null;
  }

  function toast(msg, kind, ms) {
    try {
      if (typeof window.showToast === 'function') {
        window.showToast(msg, kind || 'success', ms || 2800);
        return;
      }

      const el = document.getElementById('settings-toast');
      if (!el || !window.bootstrap) return;

      const span = el.querySelector('.toast-body span');
      if (span) span.textContent = msg;

      el.className = 'toast align-items-center text-bg-' + (kind || 'success') + ' border-0';
      window.bootstrap.Toast.getOrCreateInstance(el, { delay: ms || 2800 }).show();
    } catch (e) {}
  }

  function call(name, ...args) {
    try {
      const fn = window[name];
      if (typeof fn === 'function') return fn.apply(null, args);
    } catch (e) {}
    return undefined;
  }

  function getCur() {
    try {
      return typeof currentProject !== 'undefined' && currentProject ? currentProject : '';
    } catch (e) {
      return '';
    }
  }

  function setCur(v) {
    try {
      currentProject = v;
    } catch (e) {
      try {
        window.currentProject = v;
      } catch (e2) {}
    }
  }

  const ICO = {
    folder: `<svg class="ax-ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.9a2 2 0 0 1-1.69-.9L9.6 3.9A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2Z"/></svg>`,
    project: `<svg class="ax-ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.9a2 2 0 0 1-1.69-.9L9.6 3.9A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2Z"/><path d="M9 13h6"/></svg>`,
    home: `<svg class="ax-ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>`,
    drive: `<svg class="ax-ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="8" width="20" height="8" rx="2"/><path d="M6 12h.01M10 12h4"/></svg>`,
    up: `<svg class="ax-ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="19" x2="12" y2="5"/><polyline points="5 12 12 5 19 12"/></svg>`,
    refresh: `<svg class="ax-ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg>`,
    x: `<svg class="ax-ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>`,
    chev: `<svg class="ax-chev" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>`
  };

  let root = null;

  const S = {
    mode: 'folder',
    title: '',
    path: null,
    parent: null,
    dirs: [],
    sel: null,
    busy: false,
    done: null,
    roots: null,
    copy: false
  };

  const byId = id => document.getElementById(id);

  function build() {
    if (root) return root;

    const el = document.createElement('div');
    el.className = 'ax-backdrop';
    el.id = 'ax-backdrop';
    el.hidden = true;

    el.innerHTML =
      '<div class="ax-modal" role="dialog" aria-modal="true" aria-labelledby="ax-title">' +
      '<div class="ax-head">' +
      '<span class="ax-head-ico">' + ICO.folder + '</span>' +
      '<span class="ax-title" id="ax-title"></span>' +
      '<button type="button" class="ax-icon-btn" id="ax-close">' + ICO.x + '</button>' +
      '</div>' +
      '<div class="ax-toolbar">' +
      '<button type="button" class="ax-icon-btn" id="ax-up">' + ICO.up + '</button>' +
      '<div class="ax-crumbs" id="ax-crumbs"></div>' +
      '<input type="text" class="ax-path-input" id="ax-path-input" spellcheck="false" autocomplete="off" hidden>' +
      '<button type="button" class="ax-icon-btn" id="ax-refresh">' + ICO.refresh + '</button>' +
      '</div>' +
      '<div class="ax-body">' +
      '<div class="ax-side">' +
      '<div class="ax-side-title" id="ax-side-title"></div>' +
      '<div class="ax-side-list" id="ax-side-list"></div>' +
      '</div>' +
      '<div class="ax-list" id="ax-list" tabindex="0"></div>' +
      '</div>' +
      '<div class="ax-create" id="ax-create" hidden>' +
      '<label class="ax-create-label" id="ax-name-label" for="ax-name"></label>' +
      '<input type="text" class="ax-input" id="ax-name" spellcheck="false" autocomplete="off">' +
      '<div class="ax-create-err" id="ax-name-err" hidden></div>' +
      '</div>' +
      '<div class="ax-foot">' +
      '<span class="ax-foot-hint" id="ax-foot-hint"></span>' +
      '<label class="ax-copy" id="ax-copy" hidden><input type="checkbox" id="ax-copy-chk"><span id="ax-copy-label"></span></label>' +
      '<div class="ax-foot-actions">' +
      '<button type="button" class="ax-btn ax-btn-ghost" id="ax-cancel"></button>' +
      '<button type="button" class="ax-btn ax-btn-primary" id="ax-ok"></button>' +
      '</div>' +
      '</div>' +
      '</div>';

    document.body.appendChild(el);
    root = el;
    bind();

    return el;
  }

  function bind() {
    byId('ax-backdrop').addEventListener('mousedown', e => {
      if (e.target === root) close(null);
    });

    byId('ax-close').addEventListener('click', () => close(null));
    byId('ax-cancel').addEventListener('click', () => close(null));
    byId('ax-ok').addEventListener('click', confirmDialog);

    byId('ax-copy-chk').addEventListener('change', e => {
      S.copy = !!e.target.checked;
    });

    byId('ax-up').addEventListener('click', () => {
      if (S.parent && !S.busy) go(S.parent);
    });

    byId('ax-refresh').addEventListener('click', () => {
      if (!S.busy) go(S.path);
    });

    byId('ax-crumbs').addEventListener('click', e => {
      const b = e.target.closest('.ax-crumb');
      if (b && b.dataset.path) {
        go(b.dataset.path);
        return;
      }
      startEdit();
    });

    byId('ax-path-input').addEventListener('keydown', e => {
      e.stopPropagation();

      if (e.key === 'Enter') {
        e.preventDefault();
        const v = e.target.value;
        stopEdit();
        go(v);
      } else if (e.key === 'Escape') {
        e.preventDefault();
        stopEdit();
      }
    });

    byId('ax-path-input').addEventListener('blur', stopEdit);

    byId('ax-name').addEventListener('input', () => {
      byId('ax-name-err').hidden = true;
      updateFoot();
    });

    byId('ax-name').addEventListener('keydown', e => {
      e.stopPropagation();
      if (e.key === 'Enter') {
        e.preventDefault();
        confirmDialog();
      }
    });

    byId('ax-list').addEventListener('keydown', e => {
      const items = Array.prototype.slice.call(byId('ax-list').querySelectorAll('.ax-item'));
      if (!items.length) return;

      const cur = items.indexOf(document.activeElement);

      if (e.key === 'ArrowDown') {
        e.preventDefault();
        items[Math.min(items.length - 1, cur + 1)].focus();
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        items[Math.max(0, cur - 1)].focus();
      } else if (e.key === 'Enter' && cur >= 0) {
        e.preventDefault();

        if (e.altKey) go(items[cur].dataset.path);
        else {
          select(items[cur].dataset.path);
          confirmDialog();
        }
      }
    });

    document.addEventListener('keydown', e => {
      if (!root || root.hidden) return;
      if (e.key === 'Escape') {
        e.preventDefault();
        close(null);
      }
    });
  }

  function setList(html) {
    const l = byId('ax-list');
    if (l) l.innerHTML = html;
  }

  async function go(path) {
    const a = api();

    if (!root || S.busy) return;

    if (!a) {
      setList('<div class="ax-empty ax-empty-err">' + esc(t('pk.noBridge')) + '</div>');
      return;
    }

    S.busy = true;
    S.sel = null;

    setList('<div class="ax-empty"><span class="ax-spinner"></span>' + esc(t('pk.loading')) + '</div>');

    let res = null;
    try {
      res = await a.listDir(path || null);
    } catch (err) {
      res = { ok: false, error: 'unexpected', detail: String(err) };
    }

    S.busy = false;

    if (!root || root.hidden) return;

    if (!res || !res.ok) {
      S.dirs = [];

      const newP = (res && typeof res.detail === 'string' && res.detail) ? res.detail : (path ? String(path) : '');
      if (newP && isValidAbsPath(newP)) S.path = newP;

      renderCrumbs(S.path);

      const msg =
        res && res.error === 'denied'
          ? t('pk.denied')
          : t('pk.err', (res && (res.detail || res.error)) || '?');

      setList('<div class="ax-empty ax-empty-err">' + esc(msg) + '</div>');

      byId('ax-up').disabled = !S.parent;
      updateFoot();
      return;
    }

    S.path = res.path;
    S.parent = res.parent || null;
    S.dirs = res.dirs || [];

    byId('ax-path-input').value = res.path;
    byId('ax-up').disabled = !S.parent;

    renderCrumbs(res.path);
    renderList();
    markSide();
    updateFoot();
  }

  function isValidAbsPath(p) {
    const s = String(p || '');
    if (/^[a-zA-Z]:[\\\/]/.test(s)) {
      return (s.match(/:/g) || []).length === 1;
    }
    if (/^\\\\/.test(s)) return true;
    return false;
  }

  function splitPath(p) {
    const s = String(p || '');
    const isWin = /^[a-zA-Z]:[\/\\]/.test(s);
    const segs = s.split(/[\/\\]+/).filter(Boolean);

    const out = [];

    if (isWin) {
      const d = segs.shift();
      out.push({ label: d, path: d + '\\' });
    } else {
      out.push({ label: '/', path: '/' });
    }

    let acc = out[0].path;

    segs.forEach(seg => {
      acc = isWin
        ? acc + seg + '\\'
        : acc === '/'
          ? '/' + seg
          : acc + '/' + seg;

      out.push({ label: seg, path: acc });
    });

    return out;
  }

  function renderCrumbs(p) {
    const box = byId('ax-crumbs');
    if (!box) return;

    if (!p) {
      box.innerHTML = '<span class="ax-crumb ax-crumb-static">--</span>';
      return;
    }

    const parts = splitPath(p);

    box.innerHTML = parts
      .map(
        (c, i) =>
          '<button type="button" class="ax-crumb' +
          (i === parts.length - 1 ? ' ax-crumb-last' : '') +
          '" data-path="' + esc(c.path) + '">' + esc(c.label) + '</button>' +
          (i < parts.length - 1 ? ICO.chev : '')
      )
      .join('');

    box.scrollLeft = box.scrollWidth;
  }

  function startEdit() {
    const c = byId('ax-crumbs');
    const i = byId('ax-path-input');

    if (!c || !i) return;

    c.hidden = true;
    i.hidden = false;
    i.value = S.path || '';
    i.focus();
    i.select();
  }

  function stopEdit() {
    const c = byId('ax-crumbs');
    const i = byId('ax-path-input');

    if (!c || !i || i.hidden) return;

    i.hidden = true;
    c.hidden = false;
  }

  function renderList() {
    const dirs = S.dirs || [];

    if (!dirs.length) {
      setList('<div class="ax-empty">' + esc(t('pk.empty')) + '</div>');
      return;
    }

    setList(
      dirs
        .map(
          (d, i) =>
            '<div class="ax-item" data-i="' + i + '" data-path="' + esc(d.path) + '" tabindex="0" role="button">' +
            ICO.folder +
            '<span class="ax-item-name" title="' + esc(d.path) + '">' + esc(d.name) + '</span>' +
            '</div>'
        )
        .join('')
    );

    byId('ax-list')
      .querySelectorAll('.ax-item')
      .forEach(el => {
        const target = el.dataset.path;

        el.addEventListener('click', () => select(target));
        el.addEventListener('dblclick', () => go(target));
      });

    applySel();
  }

  function applySel() {
    byId('ax-list')
      .querySelectorAll('.ax-item')
      .forEach(el => {
        el.classList.toggle('sel', !!S.sel && el.dataset.path === S.sel);
      });
  }

  function select(path) {
    S.sel = path;
    applySel();
    updateFoot();
  }

  async function renderSide() {
    const box = byId('ax-side-list');
    if (!box) return;

    if (!S.roots) {
      box.innerHTML = '<div class="ax-empty ax-empty-sm">' + esc(t('pk.loading')) + '</div>';

      let res = null;
      const a = api();

      try {
        res = a && typeof a.browseRoots === 'function' ? await a.browseRoots() : null;
      } catch (e) {
        res = null;
      }

      S.roots = res && res.ok && Array.isArray(res.roots) ? res.roots : [];
    }

    box.innerHTML = S.roots
      .map(
        (r, i) =>
          '<button type="button" class="ax-side-item" data-i="' + i + '" data-path="' + esc(r.path) +
          '" data-kind="' + esc(r.kind || 'place') + '" title="' + esc(r.path) + '">' +
          (ICO[r.kind] || ICO.folder) +
          '<span>' + esc(r.label) + '</span>' +
          '</button>'
      )
      .join('');

    box.querySelectorAll('.ax-side-item').forEach(b =>
      b.addEventListener('click', () => go(b.dataset.path))
    );

    markSide();
  }

  function markSide() {
    const norm = s =>
      String(s || '')
        .toLowerCase()
        .replace(/[\/]+$/, '');

    const cur = norm(S.path);

    byId('ax-side-list')
      .querySelectorAll('.ax-side-item')
      .forEach(b => {
        b.classList.toggle('active', norm(b.dataset.path) === cur);
      });
  }

  function cleanName(v) {
    const s = String(v == null ? '' : v)
      .trim()
      .replace(/[\\/:*?"<>|]/g, '_');

    return s && s !== '.' && s !== '..' ? s : '';
  }

  function joinPath(parent, name) {
    if (!parent) return name;
    if (/[\\/]$/.test(parent)) return parent + name;

    return parent + (parent.indexOf('\\') !== -1 ? '\\' : '/') + name;
  }

  function updateFoot() {
    const hint = byId('ax-foot-hint');
    const ok = byId('ax-ok');

    if (!hint || !ok) return;

    const target = S.sel || S.path || '';

    if (S.mode === 'new') {
      const name = cleanName((byId('ax-name') || {}).value);

      hint.textContent = name && target ? t('pk.willCreate', joinPath(target, name)) : t('pk.willCreateIn');
      hint.title = hint.textContent;

      ok.disabled = !(name && target);
    } else {
      hint.textContent = target || '--';
      hint.title = target || '';
      ok.disabled = !target;
    }
  }

  function confirmDialog() {
    const target = S.sel || S.path;

    if (!target) {
      toast(t('proj.needFolder'), 'danger', 2800);
      return;
    }

    if (S.mode === 'new') {
      const nameEl = byId('ax-name');
      const errEl = byId('ax-name-err');

      const name = cleanName(nameEl.value);

      if (!name) {
        errEl.textContent = t('pk.nameBad');
        errEl.hidden = false;
        nameEl.focus();
        return;
      }

      errEl.hidden = true;
      close({ path: target, name, copy: S.copy });
      return;
    }

    close({ path: target, name: null, copy: S.copy });
  }

  function close(result) {
    if (!root) return;

    const cb = S.done;
    S.done = null;

    stopEdit();

    root.classList.remove('ax-in');

    const node = root;
    setTimeout(() => {
      node.hidden = true;
    }, 140);

    if (cb) cb(result || null);
  }

  function applyI18n() {
    if (!root) return;

    byId('ax-title').textContent = S.title || t('pk.title.folder');
    byId('ax-side-title').textContent = t('pk.roots');
    byId('ax-name-label').textContent = t('pk.name');
    byId('ax-name').placeholder = t('pk.namePh');
    byId('ax-cancel').textContent = t('pk.cancel');

    byId('ax-close').setAttribute('aria-label', t('pk.cancel'));
    byId('ax-up').title = t('pk.up');
    byId('ax-refresh').title = t('pk.refresh');
    byId('ax-crumbs').title = t('pk.editPath');

    byId('ax-ok').textContent =
      S.mode === 'new' ? t('pk.create') : S.mode === 'open' ? t('pk.open') : t('pk.select');

    const copyBox = byId('ax-copy');
    if (copyBox) {
      copyBox.hidden = S.mode !== 'screenshot';
      byId('ax-copy-label').textContent = t('ss.copy');
    }

    const err = byId('ax-name-err');
    if (err && !err.hidden) err.textContent = t('pk.nameBad');

    renderList();
    updateFoot();
  }

  async function axOpen(opts) {
    opts = opts || {};

    if (!api()) {
      toast(t('pk.noBridge'), 'danger', 3200);
      return null;
    }

    build();

    S.mode = opts.mode || 'folder';
    S.title = opts.title || t('pk.title.folder');
    S.sel = null;
    S.path = null;
    S.parent = null;
    S.dirs = [];
    S.copy = S.mode === 'screenshot';

    byId('ax-create').hidden = S.mode !== 'new';
    byId('ax-name').value = opts.name || '';
    byId('ax-name-err').hidden = true;
    byId('ax-copy-chk').checked = S.copy;

    applyI18n();

    const promise = new Promise(resolve => {
      S.done = resolve;
    });

    root.hidden = false;
    void root.offsetWidth;
    root.classList.add('ax-in');

    updateFoot();
    renderSide();

    let start = String(opts.start || '').trim();

    if (!start) {
      try {
        const a = api();
        if (a && typeof a.browseStart === 'function') {
          const r = await a.browseStart(opts.kind || 'generic');
          if (r && r.ok) start = r.path;
        }
      } catch (e) {
        start = '';
      }
    }

    await go(start || null);

    setTimeout(() => {
      if (root.hidden) return;

      if (S.mode === 'new') byId('ax-name').focus();
      else byId('ax-list').focus();
    }, 60);

    return promise;
  }

  function resetRoots() {
    S.roots = null;
  }

  async function actNewProject() {
    const a = api();
    if (!a) return;

    const res = await axOpen({
      mode: 'new',
      title: t('pk.title.new'),
      kind: 'project',
      start: getCur()
    });

    if (!res || !res.name || !res.path) return;

    let out = null;
    try {
      out = await a.newProject(res.name, res.path);
    } catch (e) {
      out = null;
    }

    if (!out || !out.ok) {
      toast(
        out && out.error === 'exists'
          ? t('new.exists')
          : out && out.error === 'create_failed'
            ? t('proj.createFailed')
            : t('new.err'),
        'danger',
        4000
      );
      return;
    }

    let verify = null;
    try {
      verify = await a.openProject(out.path);
    } catch (e) {
      verify = null;
    }

    if (!verify || !verify.ok) {
      toast(t('proj.verifyFailed', out.path), 'danger', 5200);
      return;
    }

    location.reload();
  }

  // Start test sin proyecto abierto: pide crear uno y, si el usuario ya marcó
  // "Start from screenshot" con una carpeta, guarda la intención de copia para
  // que se ejecute tras el reload (ver ssPendingCopyResume en app.js).
  async function actStartNoProject() {
    const a = api();
    if (!a) return;

    if (typeof window.Popup !== 'object' || !window.Popup.confirm) {
      actNewProject();
      return;
    }

    const res = await window.Popup.confirm({
      title: t('ss.newTitle'),
      body: t('ss.newDesc'),
      okLabel: t('pk.create'),
      cancelLabel: t('pk.open')
    });

    if (res === 'cancel') {
      actOpenProject();
      return;
    }
    if (res !== 'ok') return;

    const ssField = document.getElementById('run-screenshot-folder');
    const ssChk = document.getElementById('run-from-screenshot');
    const ssSrc = ssField && ssField.value.trim();
    const ssOn = ssChk && ssChk.checked;

    const r = await axOpen({
      mode: 'new',
      title: t('pk.title.new'),
      kind: 'project',
      start: getCur()
    });

    if (!r || !r.name || !r.path) return;

    let out = null;
    try {
      out = await a.newProject(r.name, r.path);
    } catch (e) {
      out = null;
    }

    if (!out || !out.ok) {
      toast(
        out && out.error === 'exists'
          ? t('new.exists')
          : out && out.error === 'create_failed'
            ? t('proj.createFailed')
            : t('new.err'),
        'danger',
        4000
      );
      return;
    }

    let verify = null;
    try {
      verify = await a.openProject(out.path);
    } catch (e) {
      verify = null;
    }

    if (!verify || !verify.ok) {
      toast(t('proj.verifyFailed', out.path), 'danger', 5200);
      return;
    }

    if (ssOn && ssSrc) {
      try {
        localStorage.setItem('aura-ss-pending-copy', ssSrc);
      } catch (e) {}
    }

    location.reload();
  }

  async function actOpenProject() {
    const res = await axOpen({
      mode: 'open',
      title: t('pk.title.open'),
      kind: 'project',
      start: getCur()
    });

    if (res && res.path) {
      resetRoots();
      await window.openAndLoad(res.path);
    }
  }

  async function actRunOut() {
    const field = document.getElementById('run-out');

    const res = await axOpen({
      mode: 'folder',
      title: t('pk.title.output'),
      kind: 'output',
      start: (field && field.value.trim()) || getCur()
    });

    if (res && res.path) {
      if (field) field.value = res.path;

      setCur(res.path);

      call('setExportDefaults', res.path);
      call('refreshExportPreview');
    }
  }

  async function actExport() {
    let cur = getCur();

    try {
      const f = document.getElementById('export-path');
      if (f && f.value) cur = f.value;
    } catch (e) {}

    const res = await axOpen({
      mode: 'folder',
      title: t('pk.title.export'),
      kind: 'export',
      start: cur
    });

    if (res && res.path) {
      call('setExportPath', res.path);
      call('hideExportResult');
      call('refreshExportPreview');
    }
  }

  async function actScreenshot() {
    const field = document.getElementById('run-screenshot-folder');

    const res = await axOpen({
      mode: 'screenshot',
      title: t('ss.title'),
      kind: 'generic',
      start: (field && field.value.trim()) || ''
    });

    if (!res || !res.path) return;

    if (field) field.value = res.path;

    if (res.copy) {
      await copyScreenshotFolder(res.path);
    }
  }

  async function copyScreenshotFolder(src) {
    const a = api();
    const out = document.getElementById('run-out');
    const dest = (out && out.value.trim()) || getCur();

    if (!a || typeof a.copyToUnstructure !== 'function') {
      toast(t('ss.copyNoBridge'), 'danger', 3200);
      return;
    }

    if (!dest) {
      toast(t('ss.copyNoDest'), 'danger', 3200);
      return;
    }

    const st = window.ssCopyState;
    if (st) st.status = 'copying';
    window.dispatchEvent(new CustomEvent('sscopy:changed'));

    const prog = document.getElementById('ss-copy-progress');
    const text = document.getElementById('ss-copy-progress-text');
    if (prog) prog.hidden = false;
    if (text) text.textContent = t('ss.copyStarting');

    let res = null;
    try {
      res = await a.copyToUnstructure(src, dest);
    } catch (e) {
      res = null;
    }

    if (!res || !res.ok) {
      if (st) st.status = 'error';
      window.dispatchEvent(new CustomEvent('sscopy:changed'));
      if (prog) prog.hidden = true;
      toast(t('ss.copyErr', (res && (res.detail || res.error)) || '?'), 'danger', 4200);
      return;
    }

    if (st) st.seq = res.seq;
  }

  async function actScreenshotCopy() {
    const field = document.getElementById('run-screenshot-folder');
    const src = field && field.value.trim();
    if (!src) return;
    await copyScreenshotFolder(src);
  }

  const ACTIONS = {
    'btn-test-new': actNewProject,
    'btn-test-open': actOpenProject,
    'btn-run-open': actOpenProject,
    'btn-run-out-browse': actRunOut,
    'export-browse': actExport,
    'export-path': actExport,
    'btn-screenshot-browse': actScreenshot,
    'btn-screenshot-copy': actScreenshotCopy
  };

  const SELECTOR = Object.keys(ACTIONS)
    .map(id => '#' + id)
    .join(', ');

  window.addEventListener(
    'click',
    function (e) {
      const btn = e.target && e.target.closest ? e.target.closest(SELECTOR) : null;
      if (!btn || !ACTIONS[btn.id]) return;

      e.preventDefault();
      e.stopImmediatePropagation();
      e.stopPropagation();

      ACTIONS[btn.id]();
    },
    true
  );

  window.pkOpen = axOpen;
  window.pickFolder = axOpen;
  window.pkResetRoots = resetRoots;
  window.pkApplyI18n = applyI18n;
  window.actStartNoProject = actStartNoProject;
  window.copyScreenshotFolder = copyScreenshotFolder;
  window.auraDialogs = { open: axOpen, state: S };

  // ============================================================
  // ABOUT CARD (HTML estático en index.html)
  // ============================================================
  const aboutRoot = document.getElementById('about-backdrop');

  function aboutOpen() {
    if (!aboutRoot) return;
    aboutRoot.hidden = false;
    requestAnimationFrame(() => aboutRoot.classList.add('ax-in'));
  }

  function aboutClose() {
    if (!aboutRoot) return;
    aboutRoot.classList.remove('ax-in');
    setTimeout(() => { aboutRoot.hidden = true; }, 200);
  }

  if (aboutRoot) {
    aboutRoot.addEventListener('mousedown', e => {
      if (e.target === aboutRoot) aboutClose();
    });
    const aboutCloseBtn = document.getElementById('about-close');
    if (aboutCloseBtn) aboutCloseBtn.addEventListener('click', aboutClose);
    const aboutDocsBtn = document.getElementById('about-docs-link');
    if (aboutDocsBtn) {
      aboutDocsBtn.addEventListener('click', () => {
        const a = api();
        if (a && typeof a.openDocs === 'function') a.openDocs();
      });
    }
    document.addEventListener('keydown', e => {
      if (aboutRoot.hidden) return;
      if (e.key === 'Escape') {
        e.preventDefault();
        aboutClose();
      }
    });
  }

  window.auraAbout = aboutOpen;

  function boot() {
    const sel = document.getElementById('setting-ui-language');
    if (sel) sel.addEventListener('change', applyI18n);

    const prune = async () => {
      const a = api();
      if (!a) return;

      try {
        await a.getRecentProjects();
      } catch (e) {}

      try {
        await window.loadRecentProjects();
      } catch (e) {}
    };

    if (api()) prune();
    else window.addEventListener('pywebviewready', prune, { once: true });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot, { once: true });
  } else {
    boot();
  }
})();