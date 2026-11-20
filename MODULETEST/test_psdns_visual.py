# -*- coding: utf-8 -*-
"""
Visual test: select text with MOUSE DRAG like a human, screenshot the result.
Verifies the ::selection fix (text must be invisible when selected).
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
    print("[visual] catalog:", len(catalog), "packages")

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
        page.evaluate("""
            () => {
                document.getElementById('wz-backdrop').hidden = true;
                if (typeof wzActive !== 'undefined') wzActive = false;
            }
        """)
        page.wait_for_timeout(500)
        page.evaluate("() => { document.querySelector('[data-bs-target=\"#pane-settings\"]').click(); }")
        page.wait_for_timeout(1500)
        page.wait_for_function(
            "() => { const ta = document.getElementById('pipe-filter-t'); const w = ta.closest('.psdns-wrap'); const ov = w && w.querySelector('.psdns-overlay'); return ov && ov.style.display !== 'none'; }",
            timeout=10000,
        )
        page.wait_for_timeout(500)

        ta = page.locator("#pipe-filter-t")
        box = ta.bounding_box()
        print(f"[visual] textarea box: {box}")

        # --- Like a human: click in the textarea and type packages ---
        print("\n[1] Human clicks textarea and types packages...")
        ta.click()
        page.keyboard.type("com.android.deskclock")
        page.wait_for_timeout(100)
        page.keyboard.press("Enter")
        page.wait_for_timeout(200)
        page.keyboard.type("com.vivo.calculator")
        page.wait_for_timeout(100)
        page.keyboard.press("Enter")
        page.wait_for_timeout(200)
        page.keyboard.type("com.vivo.feedback")
        page.wait_for_timeout(100)
        page.keyboard.press("Enter")
        page.wait_for_timeout(300)

        val = page.evaluate("() => document.getElementById('pipe-filter-t').value")
        print(f"[visual] value: {val!r}")

        # Screenshot: normal state (no selection)
        page.screenshot(path=os.path.join(OUT_DIR, "psdns_visual_01_normal.png"))
        print("[visual] Screenshot 1: normal state")

        # --- Like a human: click at start of text, drag to end (select all) ---
        print("\n[2] Human selects all text with mouse drag...")
        # Click at the very beginning of the textarea content
        start_x = box["x"] + 10
        start_y = box["y"] + 10
        # Drag to the end of the text
        end_x = box["x"] + 300
        end_y = box["y"] + 70

        page.mouse.move(start_x, start_y)
        page.mouse.down()
        page.mouse.move(end_x, end_y, steps=10)
        page.mouse.up()
        page.wait_for_timeout(300)

        # Screenshot: selected state
        page.screenshot(path=os.path.join(OUT_DIR, "psdns_visual_02_selected.png"))
        print("[visual] Screenshot 2: text selected (mouse drag)")

        # --- Like a human: click somewhere else to deselect, then select just one line ---
        print("\n[3] Human clicks to deselect, then selects just line 2...")
        page.mouse.click(box["x"] + 10, box["y"] + 80)
        page.wait_for_timeout(200)

        # Select just the second line by dragging
        line2_y = box["y"] + 25
        page.mouse.move(box["x"] + 10, line2_y)
        page.mouse.down()
        page.mouse.move(box["x"] + 250, line2_y, steps=5)
        page.mouse.up()
        page.wait_for_timeout(300)

        page.screenshot(path=os.path.join(OUT_DIR, "psdns_visual_03_line_selected.png"))
        print("[visual] Screenshot 3: single line selected")

        # --- Like a human: Ctrl+A ---
        print("\n[4] Human presses Ctrl+A...")
        ta.click()
        page.keyboard.press("Control+a")
        page.wait_for_timeout(300)
        page.screenshot(path=os.path.join(OUT_DIR, "psdns_visual_04_ctrl_a.png"))
        print("[visual] Screenshot 4: Ctrl+A")

        # --- Now disable PSDNS and do the same selection ---
        print("\n[5] Disable PSDNS, select all again (text SHOULD be visible)...")
        page.evaluate("""
            () => {
                const cb = document.getElementById('psdns-enabled');
                cb.checked = false;
                cb.dispatchEvent(new Event('change', {bubbles: true}));
            }
        """)
        page.wait_for_timeout(500)
        ta.click()
        page.keyboard.press("Control+a")
        page.wait_for_timeout(300)
        page.screenshot(path=os.path.join(OUT_DIR, "psdns_visual_05_off_selected.png"))
        print("[visual] Screenshot 5: PSDNS off, text selected (should be VISIBLE)")

        browser.close()

    print("\n[done] Check screenshots:")
    print("  01_normal.png       - no selection, overlay visible, text hidden")
    print("  02_selected.png     - mouse drag select, text must be HIDDEN")
    print("  03_line_selected.png - single line selected, text must be HIDDEN")
    print("  04_ctrl_a.png       - Ctrl+A, text must be HIDDEN")
    print("  05_off_selected.png - PSDNS off, text must be VISIBLE")

if __name__ == "__main__":
    main()
