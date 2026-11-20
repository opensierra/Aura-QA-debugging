# -*- coding: utf-8 -*-
r"""
READ-ONLY verification: does the PSDNS label substitution respond to
interface-language changes?

Steps:
  1. Stub window.pywebview.api (real catalog from Customlib/psdns.json).
  2. Load UI/index.html headless, open welcome dialog, go to step 2.
  3. Read the label shown for com.android.deskclock (expect English "Clock").
  4. Change the interface language (wz-lang) to "es".
  5. Read the label again (expect Spanish "Reloj" if it works).
  6. Report whether the label changed.

No code is modified. Run with:  .\plk.bat MODULETEST\test_psdns_lang_headless.py
"""
import json
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UI_INDEX = os.path.join(BASE, "UI", "index.html")
CATALOG = os.path.join(BASE, "Customlib", "psdns.json")
OUT_DIR = os.path.join(BASE, "MODULETEST")

INSTALLED = [
    "com.android.deskclock",
    "com.vivo.calculator",
    "com.vivo.feedback",
    "com.vivo.imanager",
    "com.android.bbk.lockscreen3",
]


def load_catalog():
    with open(CATALOG, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def build_init_script(catalog):
    catalog_js = json.dumps(catalog, ensure_ascii=False)
    installed_js = json.dumps(INSTALLED, ensure_ascii=False)
    return r"""
    (function () {
      window.__psdnsCatalog = __CATALOG__;
      window.__psdnsInstalled = __INSTALLED__;
      const api = {
        loadConfig: async () => null,
        saveConfig: async () => true,
        getRecentProjects: async () => [],
        removeRecentProject: async () => true,
        getCurrentProject: async () => null,
        openProject: async () => ({ ok: false }),
        getDeviceInfo: async () => ({ connected: false }),
        refreshPsdns: async () => ({
          ok: true, serial: "TEST-SERIAL",
          catalog: window.__psdnsCatalog,
          installed: window.__psdnsInstalled,
          catalogPackages: Object.keys(window.__psdnsCatalog).length
        }),
        updatePsdns: async () => ({ ok: false, error: "not_supported" }),
        getRunState: async () => null,
        getPipelineState: async () => ({ status: "idle" }),
        getQaReport: async () => null,
        getCrawlLatest: async () => null,
        getImageData: async () => null,
        startPipeline: async () => ({ ok: false }),
        stopPipeline: async () => {},
        startBlueCode: async () => ({ ok: false }),
        getBlueCodeStatus: async () => ({ running: false }),
        stopBlueCode: async () => {},
        getProjectLog: async () => null,
        listDir: async () => null,
        previewExport: async () => null,
        exportXlsx: async () => null,
        openExport: async () => {},
        openDocs: async () => {},
        close: async () => {},
        minimize: async () => {},
        maximize: async () => {},
        moveBy: async () => {}
      };
      window.pywebview = { api: api };
    })();
    """.replace("__CATALOG__", catalog_js).replace("__INSTALLED__", installed_js)


def read_labels(page):
    """Return {packageLine: labelText} for the wz-filter-t annotation box."""
    return page.evaluate(
        """
        () => {
          const box = document.getElementById('psdns-ann-wz-filter-t');
          if (!box) return null;
          const rows = Array.from(box.querySelectorAll('.psdns-ann-line'));
          const out = {};
          for (const r of rows) {
            const orig = r.querySelector('.psdns-ann-orig');
            const lab = r.querySelector('.psdns-ann-label');
            if (orig) out[orig.textContent] = lab ? lab.textContent : '(no label)';
          }
          return out;
        }
        """
    )


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    catalog = load_catalog()

    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        page.add_init_script(build_init_script(catalog))
        page.goto("file:///" + UI_INDEX.replace("\\", "/"))

        page.wait_for_function(
            "() => { const bd = document.getElementById('wz-backdrop'); return bd && !bd.hidden; }",
            timeout=20000,
        )
        page.click("#wz-next")
        page.wait_for_timeout(2500)

        lang_before = page.evaluate("() => (document.getElementById('wz-lang')||{}).value")
        labels_en = read_labels(page)

        # Change interface language to Spanish.
        page.select_option("#wz-lang", "es")
        page.wait_for_timeout(2500)

        lang_after = page.evaluate("() => (document.getElementById('wz-lang')||{}).value")
        labels_es = read_labels(page)

        browser.close()

    result = {
        "lang_before": lang_before,
        "lang_after": lang_after,
        "labels_before": labels_en,
        "labels_after": labels_es,
        "changed": labels_en != labels_es,
    }
    out_json = os.path.join(OUT_DIR, "psdns_lang_headless_summary.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print("lang before:", lang_before, "-> after:", lang_after)
    print("labels BEFORE (en):")
    for k, v in (labels_en or {}).items():
        print("   ", k, "=>", v)
    print("labels AFTER (es):")
    for k, v in (labels_es or {}).items():
        print("   ", k, "=>", v)
    print("LABEL CHANGED ON LANG SWITCH:", result["changed"])
    print("summary:", out_json)


if __name__ == "__main__":
    main()
