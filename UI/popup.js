// ============================================================
// UI/popup.js — Mecanismo reutilizable de popups modales.
// Cargar ANTES de app.js / dialogs.js.
// Expone window.Popup con:
//   Popup.confirm(opts) -> Promise<'ok'|'cancel'|'dismiss'>
//   Popup.open(cardEl, opts) -> Promise (para cards personalizadas)
//   Popup.close()
// ============================================================
window.Popup = (function () {
  let active = null;

  function makeBackdrop() {
    const bd = document.createElement('div');
    bd.className = 'popup-backdrop';
    bd.hidden = true;
    document.body.appendChild(bd);
    return bd;
  }

  function animateIn(bd) {
    bd.hidden = false;
    requestAnimationFrame(() => bd.classList.add('ax-in'));
  }

  function animateOut(bd, done) {
    bd.classList.remove('ax-in');
    setTimeout(() => {
      bd.hidden = true;
      if (typeof done === 'function') done();
    }, 200);
  }

  function onKey(e) {
    if (e.key === 'Escape' && active && active.dismissable) {
      e.preventDefault();
      finish('dismiss');
    }
  }

  function finish(result) {
    if (!active) return;
    const a = active;
    active = null;
    document.removeEventListener('keydown', onKey, true);
    animateOut(a.backdrop, () => {
      a.backdrop.remove();
      if (typeof a.onClose === 'function') a.onClose(result);
    });
    a.resolve(result);
  }

  // Abre una card ya construida (elemento DOM) dentro del backdrop.
  function open(cardEl, opts) {
    opts = opts || {};
    if (active) finish('dismiss');

    const bd = makeBackdrop();
    bd.appendChild(cardEl);
    const dismissable = opts.dismissable !== false;

    active = {
      backdrop: bd,
      card: cardEl,
      dismissable: dismissable,
      onClose: opts.onClose || null,
      resolve: null
    };

    const p = new Promise(res => { active.resolve = res; });

    if (dismissable) {
      bd.addEventListener('mousedown', function (e) {
        if (e.target === bd) finish('dismiss');
      });
      document.addEventListener('keydown', onKey, true);
    }

    animateIn(bd);
    return p;
  }

  // Popup de confirmación simple: título, cuerpo y botones.
  // opts: { title, body, okLabel, cancelLabel, danger, dismissable, onClose }
  // body: string (HTML) o elemento DOM.
  function confirm(opts) {
    opts = opts || {};
    const card = document.createElement('div');
    card.className = 'popup-card';
    card.setAttribute('role', 'dialog');
    card.setAttribute('aria-modal', 'true');

    if (opts.title) {
      const t = document.createElement('div');
      t.className = 'popup-title';
      t.textContent = opts.title;
      card.appendChild(t);
    }

    if (opts.body) {
      const b = document.createElement('div');
      b.className = 'popup-body';
      if (typeof opts.body === 'string') b.innerHTML = opts.body;
      else b.appendChild(opts.body);
      card.appendChild(b);
    }

    const foot = document.createElement('div');
    foot.className = 'popup-foot';

    const hasCancel = !!opts.cancelLabel;
    if (hasCancel) {
      const c = document.createElement('button');
      c.type = 'button';
      c.className = 'popup-btn popup-btn-ghost';
      c.textContent = opts.cancelLabel;
      c.addEventListener('click', () => finish('cancel'));
      foot.appendChild(c);
    }

    const ok = document.createElement('button');
    ok.type = 'button';
    ok.className = 'popup-btn popup-btn-primary' + (opts.danger ? ' popup-btn-danger' : '');
    ok.textContent = opts.okLabel || 'OK';
    ok.addEventListener('click', () => finish('ok'));
    foot.appendChild(ok);

    card.appendChild(foot);

    return open(card, {
      dismissable: opts.dismissable,
      onClose: opts.onClose
    });
  }

  function close() {
    if (active) finish('dismiss');
  }

  return { open: open, confirm: confirm, close: close };
})();
