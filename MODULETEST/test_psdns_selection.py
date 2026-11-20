# -*- coding: utf-8 -*-
"""
Verify ::selection fix: select text in PSDNS textarea, screenshot.
Closes wizard via JS to access settings panel.
"""
import json, os, sys
from playwright.sync_api import sync_playwright

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UI_INDEX = os.path.join(BASE, "UI", "index.html")
CATALOG = os.path.join(BASE, "Customlib", "psdns.json")
OUT_DIR = os.path.join(BASE, "MODULETEST")

INSTALLED = [
    "com.android.deskclock",
    "com.vivo.calculator",
    "com.vivo.feedback",
    "com.vivo.imanager",
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
          ok: true,
          serial: "TEST-SERIAL",
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

def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    catalog = load_catalog()
    print("[test] catalog packages:", len(catalog))

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        page.add_init_script(build_init_script(catalog))
        page.goto("file:///" + UI_INDEX.replace("\\", "/"))

        page.wait_for_function(
            "() => { const bd = document.getElementById('wz-backdrop'); return bd && !bd.hidden; }",
            timeout=20000,
        )
        page.wait_for_timeout(2000)

        # Force-close the wizard via JS
        page.evaluate("""
            () => {
                const bd = document.getElementById('wz-backdrop');
                if (bd) bd.hidden = true;
                if (typeof wzActive !== 'undefined') wzActive = false;
            }
        """)
        page.wait_for_timeout(1000)

        # Click settings tab
        page.evaluate("""
            () => {
                const btn = document.querySelector('[data-bs-target="#pane-settings"]');
                if (btn) btn.click();
            }
        """)
        page.wait_for_timeout(1000)

        # Wait for settings panel overlay to be active
        page.wait_for_function(
            "() => { const ta = document.getElementById('pipe-filter-t'); if (!ta) return false; const wrap = ta.closest('.psdns-wrap'); if (!wrap) return false; const ov = wrap.querySelector('.psdns-overlay'); return ov && ov.style.display !== 'none'; }",
            timeout=10000,
        )
        page.wait_for_timeout(500)
        print("[test] Settings panel overlay active")

        # Set values
        page.evaluate("""
            () => {
                const ta = document.getElementById('pipe-filter-t');
                ta.value = 'com.android.deskclock\\ncom.vivo.calculator\\ncom.vivo.feedback\\n';
                ta.dispatchEvent(new Event('input', {bubbles: true}));
            }
        """)
        page.wait_for_timeout(500)

        # Select all text
        page.evaluate("() => { const ta = document.getElementById('pipe-filter-t'); ta.focus(); ta.select(); }")
        page.wait_for_timeout(300)

        shot = os.path.join(OUT_DIR, "psdns_selection_FIXED.png")
        page.screenshot(path=shot)
        print(f"[test] Screenshot (selected): {shot}")

        # Normal state
        page.evaluate("() => { const ta = document.getElementById('pipe-filter-t'); ta.blur(); }")
        page.wait_for_timeout(200)
        shot2 = os.path.join(OUT_DIR, "psdns_selection_NORMAL.png")
        page.screenshot(path=shot2)
        print(f"[test] Screenshot (normal): {shot2}")

        browser.close()

    print("\n[done]")

if __name__ == "__main__":
    main()
