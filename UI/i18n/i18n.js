window.I18N = (function () {
    const RTL = ['ur'];
    let current = 'en';
    let dict = {};

    function t(key, arg) {
        const DATA = window.I18N_DATA || {};
        let s;
        if (dict[key] !== undefined) s = dict[key];
        else if (DATA.en && DATA.en[key] !== undefined) s = DATA.en[key];
        else s = key;
        if (arg !== undefined) s = s.replace('{0}', arg);
        return s;
    }

    function apply(code) {
        const DATA = window.I18N_DATA || {};
        if (!DATA[code]) code = 'en';
        current = code;
        dict = DATA[code] || {};
        const root = document.documentElement;
        root.lang = code;
        root.dir = RTL.indexOf(code) !== -1 ? 'rtl' : 'ltr';

        document.querySelectorAll('[data-i18n]').forEach(function (el) {
            const key = el.getAttribute('data-i18n');
            if (dict[key] !== undefined) el.textContent = dict[key];
        });
        document.querySelectorAll('[data-i18n-title]').forEach(function (el) {
            const key = el.getAttribute('data-i18n-title');
            if (dict[key] !== undefined) el.setAttribute('title', dict[key]);
        });
        document.querySelectorAll('[data-i18n-placeholder]').forEach(function (el) {
            const key = el.getAttribute('data-i18n-placeholder');
            if (dict[key] !== undefined) el.setAttribute('placeholder', dict[key]);
        });
    }

    return {
        apply: apply,
        t: t,
        get current() { return current; }
    };
})();
