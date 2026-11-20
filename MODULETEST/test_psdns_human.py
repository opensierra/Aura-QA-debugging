# -*- coding: utf-8 -*-
"""
HUMAN interaction test. No programmatic value checks.
Just: click, type, press keys, screenshot. Show the user what happens.
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

        # Simulate REAL app state: settings loaded from JSON, no trailing newline
        page.evaluate("""
            () => {
                const ta = document.getElementById('pipe-filter-t');
                ta.value = 'com.android.deskclock\\ncom.vivo.calculator\\ncom.vivo.feedback';
                ta.dispatchEvent(new Event('input', {bubbles: true}));
            }
        """)
        page.wait_for_timeout(500)

        n = 0
        def snap(label):
            nonlocal n
            n += 1
            path = os.path.join(OUT_DIR, f"human_{n:02d}_{label}.png")
            page.screenshot(path=path)
            print(f"  [{n:02d}] {label}")

        print("=== HUMAN INTERACTION TEST ===\n")

        # 1. Initial state: settings loaded, no trailing newline
        snap("initial_state")

        # 2. User clicks on the textarea (at the end of the text)
        print("Clicking at end of textarea...")
        ta.click(position={"x": box["width"] - 20, "y": box["height"] - 10})
        page.wait_for_timeout(300)
        snap("clicked_at_end")

        # 3. User types a new package
        print("Typing 'com.vivo.imanager'...")
        page.keyboard.type("com.vivo.imanager")
        page.wait_for_timeout(300)
        snap("typed_new_package")

        # 4. User presses Enter
        print("Pressing Enter...")
        page.keyboard.press("Enter")
        page.wait_for_timeout(300)
        snap("after_enter")

        # 5. User types another package
        print("Typing 'com.android.settings'...")
        page.keyboard.type("com.android.settings")
        page.wait_for_timeout(300)
        snap("typed_second")

        # 6. User presses Enter
        print("Pressing Enter...")
        page.keyboard.press("Enter")
        page.wait_for_timeout(300)
        snap("after_second_enter")

        # 7. User clicks on the FIRST line (confirmed) and tries to type
        print("Clicking on first line, trying to type 'X'...")
        ta.click(position={"x": 50, "y": 10})
        page.wait_for_timeout(200)
        page.keyboard.type("X")
        page.wait_for_timeout(300)
        snap("tried_type_on_confirmed")

        # 8. User double-clicks on first line (edit mode)
        print("Double-clicking on first line...")
        ta.dblclick(position={"x": 50, "y": 10})
        page.wait_for_timeout(300)
        snap("edit_mode")

        # 9. User types in edit mode
        print("Typing in edit mode...")
        page.keyboard.press("Control+a")
        page.wait_for_timeout(100)
        page.keyboard.type("com.vivo.camera")
        page.wait_for_timeout(300)
        snap("edited_line")

        # 10. User presses Enter to confirm edit
        print("Pressing Enter to confirm...")
        page.keyboard.press("Enter")
        page.wait_for_timeout(300)
        snap("after_edit_confirm")

        # 11. User presses Backspace once (on empty last line)
        print("Pressing Backspace once...")
        page.keyboard.press("Backspace")
        page.wait_for_timeout(300)
        snap("backspace_1")

        # 12. User presses Backspace again (should delete line)
        print("Pressing Backspace again...")
        page.keyboard.press("Backspace")
        page.wait_for_timeout(300)
        snap("backspace_2_deleted")

        # 13. User selects all with mouse drag
        print("Selecting all with mouse drag...")
        page.mouse.move(box["x"] + 5, box["y"] + 5)
        page.mouse.down()
        page.mouse.move(box["x"] + 400, box["y"] + 50, steps=10)
        page.mouse.up()
        page.wait_for_timeout(300)
        snap("mouse_select_all")

        # 14. User presses Ctrl+A
        print("Pressing Ctrl+A...")
        ta.click()
        page.keyboard.press("Control+a")
        page.wait_for_timeout(300)
        snap("ctrl_a")

        # 15. Disable PSDNS
        print("Disabling PSDNS...")
        page.evaluate("""
            () => {
                const cb = document.getElementById('psdns-enabled');
                cb.checked = false;
                cb.dispatchEvent(new Event('change', {bubbles: true}));
            }
        """)
        page.wait_for_timeout(500)
        snap("psdns_disabled")

        # 16. Select all with PSDNS off (text should be visible)
        print("Selecting all with PSDNS off...")
        ta.click()
        page.keyboard.press("Control+a")
        page.wait_for_timeout(300)
        snap("psdns_off_selected")

        browser.close()

    print(f"\nDone. {n} screenshots saved to {OUT_DIR}/human_*.png")

if __name__ == "__main__":
    main()
