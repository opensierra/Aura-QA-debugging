# -*- coding: utf-8 -*-
r"""
Headless verification of the PSDNS annotation layer on the WELCOME dialog.

Hypothesis under test:
  In init() (UI/app.js), psdnsRefresh() is called AFTER `await wzShow()`,
  and wzShow() only resolves when the user clicks Finish. Therefore, while
  the welcome dialog is open, psdnsState is empty and the welcome textareas
  (wz-filter-t / wz-filter-e) are NEVER annotated.

This script:
  1. Stubs window.pywebview.api faithfully (real catalog from Customlib/psdns.json).
  2. Loads UI/index.html in headless Chromium.
  3. Waits for the welcome dialog to open.
  4. Records the annotation-box state WHILE the dialog is open  (bug evidence).
  5. Closes the dialog (Next -> pick langs -> Finish).
  6. Records the annotation-box state AFTER the dialog is closed.
  7. Saves screenshots + a JSON summary.

Run from project root with the embedded python (plk.bat):
    .\plk.bat MODULETEST\test_psdns_welcome_headless.py
"""
import json
import os
import sys
import time

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UI_INDEX = os.path.join(BASE, "UI", "index.html")
CATALOG = os.path.join(BASE, "Customlib", "psdns.json")
OUT_DIR = os.path.join(BASE, "MODULETEST")

# Packages we pretend are installed on the DUT.
# 4 of the welcome default lines are installed (-> known_package + label),
# com.android.bbk.lockscreen3 is installed but NOT in catalog (-> pending_extraction),
# the rest are in catalog but not installed (-> pending_discovery),
# com.vivo.simplelauncher is in neither (-> unknown).
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


def snapshot_boxes(page):
    """Return per-textarea annotation state for the 4 PSDNS textareas."""
    return page.evaluate(
        """
        () => {
          const ids = ['wz-filter-t','wz-filter-e','pipe-filter-t','pipe-filter-e'];
          const out = {};
          for (const id of ids) {
            const ta = document.getElementById(id);
            const box = document.getElementById('psdns-ann-' + id);
            if (!ta || !box) { out[id] = { present: false }; continue; }
            const lines = Array.from(box.querySelectorAll('.psdns-ann-line'));
            out[id] = {
              present: true,
              taValueLines: ta.value.split('\\n').map(s=>s.trim()).filter(Boolean).length,
              annLineCount: lines.length,
              annVisible: box.offsetHeight > 0 && box.innerHTML.trim().length > 0,
              states: lines.map(l => (l.className.replace('psdns-ann-line','').trim() || 'known')),
              sample: box.innerText.slice(0, 400)
            };
          }
          const bd = document.getElementById('wz-backdrop');
          out.__dialogOpen = !!(bd && !bd.hidden);
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
    print("[test] catalog packages:", len(catalog))
    print("[test] index:", UI_INDEX)

    from playwright.sync_api import sync_playwright

    console_msgs = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        page.on("console", lambda m: console_msgs.append(f"[{m.type}] {m.text}"))
        page.on("pageerror", lambda e: console_msgs.append(f"[pageerror] {e}"))
        page.add_init_script(build_init_script(catalog))

        page.goto("file:///" + UI_INDEX.replace("\\", "/"))

        # Wait for the welcome dialog to open.
        page.wait_for_function(
            "() => { const bd = document.getElementById('wz-backdrop'); return bd && !bd.hidden; }",
            timeout=20000,
        )
        # Give any async init / debounce time to settle.
        page.wait_for_timeout(3000)

        # Go to step 2 (where the textareas live) while the dialog is STILL open.
        page.click("#wz-next")
        page.wait_for_timeout(1500)

        before = snapshot_boxes(page)
        shot1 = os.path.join(OUT_DIR, "psdns_welcome_BEFORE_finish.png")
        page.screenshot(path=shot1)
        print("[test] dialog open (step 2), captured BEFORE finish")

        # Close the dialog: pick source/target -> Finish.
        page.select_option("#wz-source", "es")
        page.select_option("#wz-target", "en")
        page.wait_for_timeout(200)
        page.click("#wz-finish")
        # Wait for dialog to hide + psdnsRefresh (post-dialog) to run.
        page.wait_for_function(
            "() => { const bd = document.getElementById('wz-backdrop'); return bd && bd.hidden; }",
            timeout=20000,
        )
        page.wait_for_timeout(3000)

        after = snapshot_boxes(page)
        shot2 = os.path.join(OUT_DIR, "psdns_welcome_AFTER_finish.png")
        page.screenshot(path=shot2)
        print("[test] dialog closed, captured AFTER finish")

        browser.close()

    summary = {
        "before_finish": before,
        "after_finish": after,
        "console": console_msgs[-40:],
    }
    out_json = os.path.join(OUT_DIR, "psdns_welcome_headless_summary.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print("\n================ SUMMARY ================")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print("\n[screenshots]")
    print("  ", shot1)
    print("  ", shot2)
    print("  ", out_json)


if __name__ == "__main__":
    main()
