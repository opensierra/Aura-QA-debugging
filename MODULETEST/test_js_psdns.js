// Test the real app.js psdns logic in a minimal DOM sandbox.
const fs = require('fs');
const vm = require('vm');
const path = require('path');

const BASE = path.resolve(__dirname, '..');
const code = fs.readFileSync(path.join(BASE, 'UI', 'app.js'), 'utf8');

function makeEl() {
  return {
    style: {}, value: '', checked: false, textContent: '', innerHTML: '',
    classList: { add() {}, remove() {}, toggle() {}, contains() { return false; } },
    appendChild() {}, setAttribute() {}, addEventListener() {},
    querySelectorAll() { return []; },
  };
}

const sandbox = {
  console,
  setTimeout: () => 0,
  clearTimeout: () => {},
  setInterval: () => 0,
  clearInterval: () => {},
  localStorage: { getItem: () => null, setItem: () => {} },
  navigator: { clipboard: { writeText: async () => {} } },
  fetch: async () => ({ ok: false, json: async () => ({}) }),
  document: {
    getElementById: () => null,
    querySelector: () => null,
    querySelectorAll: () => [],
    addEventListener: () => {},
    createElement: makeEl,
    documentElement: { lang: 'en', dir: 'ltr' },
  },
  addEventListener: () => {},
};
sandbox.window = sandbox;
vm.createContext(sandbox);
vm.runInContext(code, sandbox, { filename: 'app.js' });

const testCode = `
(function () {
  const catalog = {
    'com.android.deskclock': { es: ['Reloj'], en: ['Clock'] },
    'com.samsung.clock': { es: ['Reloj'], en: ['Clock'] },
    'com.vivo.calculator': { es: ['Calculadora'], en: ['Calculator'] },
  };
  const installed = ['com.android.deskclock', 'com.vivo.calculator', 'com.other.app'];

  psdnsState.catalog = catalog;
  psdnsState.installed = installed;
  psdnsState.installedSet = new Set(installed);
  psdnsState.serial = 'TEST';
  psdnsState.unverifiable = false;
  const idx = psdnsBuildIndexes(catalog);
  psdnsState.byName = idx.byName;
  psdnsState.byPackage = idx.byPackage;

  let failed = 0;
  function check(name, actual, expected) {
    const ok = JSON.stringify(actual) === JSON.stringify(expected);
    console.log((ok ? 'OK  ' : 'FAIL') + ' ' + name + ' -> ' + JSON.stringify(actual));
    if (!ok) { console.log('     expected: ' + JSON.stringify(expected)); failed++; }
  }

  check('1 known_package', psdnsValidateEntry('com.android.deskclock', 'es'),
    { entry: 'com.android.deskclock', state: 'known_package', label: 'Reloj',
      labels: ['Reloj', 'Clock'], candidates: [] });

  check('2 absent pkg, sibling', psdnsValidateEntry('com.samsung.clock', 'es'),
    { entry: 'com.samsung.clock', state: 'known_package', label: 'Reloj',
      labels: ['Reloj', 'Clock'], candidates: ['com.android.deskclock'] });

  check('3 known_name', psdnsValidateEntry('Reloj', 'es'),
    { entry: 'Reloj', state: 'known_name', label: null, labels: [],
      candidates: ['com.android.deskclock'] });

  check('4 pending_extraction', psdnsValidateEntry('com.other.app', 'es'),
    { entry: 'com.other.app', state: 'pending_extraction', label: null, labels: [], candidates: [] });

  check('5 unknown', psdnsValidateEntry('Inventedt', 'es'),
    { entry: 'Inventedt', state: 'unknown', label: null, labels: [], candidates: [] });

  psdnsState.unverifiable = true;
  const r6 = psdnsValidateEntry('com.android.deskclock', 'es');
  check('6 unverifiable state', r6.state, 'unverifiable');
  check('6 unverifiable label kept', r6.label, 'Reloj');
  psdnsState.unverifiable = false;

  check('7 label en', psdnsValidateEntry('com.vivo.calculator', 'en').label, 'Calculator');

  check('8 normalize', psdnsNormalizeName('  Reloj   GRANDE '), 'reloj grande');

  // Ambiguous: two installed packages share the name
  psdnsState.catalog = {
    'com.a.clock': { es: ['Reloj'] },
    'com.b.clock': { es: ['Reloj'] },
  };
  psdnsState.installedSet = new Set(['com.a.clock', 'com.b.clock']);
  const idx2 = psdnsBuildIndexes(psdnsState.catalog);
  psdnsState.byName = idx2.byName;
  psdnsState.byPackage = idx2.byPackage;
  check('9 ambiguous', psdnsValidateEntry('Reloj', 'es'),
    { entry: 'Reloj', state: 'ambiguous', label: null, labels: [],
      candidates: ['com.a.clock', 'com.b.clock'] });

  // Pending discovery: name known in catalog, no installed association
  psdnsState.catalog = { 'com.x.clock': { es: ['Reloj'] } };
  psdnsState.installedSet = new Set(['com.other.app']);
  const idx3 = psdnsBuildIndexes(psdnsState.catalog);
  psdnsState.byName = idx3.byName;
  psdnsState.byPackage = idx3.byPackage;
  check('10 pending_discovery', psdnsValidateEntry('Reloj', 'es'),
    { entry: 'Reloj', state: 'pending_discovery', label: null, labels: [], candidates: [] });

  console.log(failed ? '=== JS TESTS FAILED: ' + failed + ' ===' : '=== JS TESTS OK ===');
  return failed;
})()
`;

const failed = vm.runInContext(testCode, sandbox, { filename: 'test.js' });
process.exit(failed ? 1 : 0);
