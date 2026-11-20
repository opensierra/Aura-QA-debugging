# -*- coding: utf-8 -*-
"""
Real user interaction test for PSDNS edit rules.
Interacts with the textbox exactly like a user would:
  - Click, type, Enter, Backspace, double-click, select all
  - Both with PSDNS enabled and disabled
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
    print("[test] catalog:", len(catalog), "packages")

    results = []
    def check(name, cond, detail=""):
        s = "PASS" if cond else "FAIL"
        results.append((name, s, detail))
        print(f"  [{s}] {name}" + (f"  ({detail})" if detail and not cond else ""))

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        page.add_init_script(build_init_script(catalog))
        page.goto("file:///" + UI_INDEX.replace("\\", "/"))

        # Wait for wizard
        page.wait_for_function(
            "() => { const bd = document.getElementById('wz-backdrop'); return bd && !bd.hidden; }",
            timeout=20000,
        )
        page.wait_for_timeout(2000)

        # Close wizard
        page.evaluate("""
            () => {
                document.getElementById('wz-backdrop').hidden = true;
                if (typeof wzActive !== 'undefined') wzActive = false;
            }
        """)
        page.wait_for_timeout(500)

        # Go to settings tab
        page.evaluate("() => { document.querySelector('[data-bs-target=\"#pane-settings\"]').click(); }")
        page.wait_for_timeout(1500)

        # Wait for overlay
        page.wait_for_function(
            "() => { const ta = document.getElementById('pipe-filter-t'); const w = ta.closest('.psdns-wrap'); const ov = w && w.querySelector('.psdns-overlay'); return ov && ov.style.display !== 'none'; }",
            timeout=10000,
        )
        page.wait_for_timeout(500)

        ta = page.locator("#pipe-filter-t")
        shot_n = 0
        def snap(label):
            nonlocal shot_n
            shot_n += 1
            path = os.path.join(OUT_DIR, f"psdns_user_{shot_n:02d}_{label}.png")
            page.screenshot(path=path)
            print(f"  [snap] {path}")

        def get_val():
            return page.evaluate("() => document.getElementById('pipe-filter-t').value")

        def get_sel():
            return page.evaluate("() => document.getElementById('pipe-filter-t').selectionStart")

        # ================================================================
        print("\n" + "="*60)
        print("PHASE 1: PSDNS ENABLED - Normal user flow")
        print("="*60)

        # --- User clicks the textarea and types first package ---
        print("\n[1] User clicks textarea and types 'com.android.deskclock' + Enter")
        ta.click()
        page.keyboard.type("com.android.deskclock")
        page.wait_for_timeout(200)
        page.keyboard.press("Enter")
        page.wait_for_timeout(300)
        val = get_val()
        check("Line confirmed", "com.android.deskclock" in val, f"val={val!r}")
        check("New empty line created", val.endswith("\n"), f"val={val!r}")
        check("Cursor at end", get_sel() == len(val), f"sel={get_sel()} len={len(val)}")
        snap("after_first_enter")

        # --- User types second package ---
        print("\n[2] User types 'com.vivo.calculator' + Enter")
        page.keyboard.type("com.vivo.calculator")
        page.wait_for_timeout(200)
        page.keyboard.press("Enter")
        page.wait_for_timeout(300)
        val = get_val()
        check("Two lines confirmed", val.count("\n") >= 2, f"val={val!r}")
        check("Both packages present", "com.android.deskclock" in val and "com.vivo.calculator" in val)
        snap("after_second_enter")

        # --- User types a label (not a package) ---
        print("\n[3] User types label 'Clock' + Enter (should resolve to package)")
        page.keyboard.type("Clock")
        page.wait_for_timeout(200)
        page.keyboard.press("Enter")
        page.wait_for_timeout(300)
        val = get_val()
        check("Label resolved to package", "com.android.deskclock" in val, f"val={val!r}")
        snap("after_label_enter")

        # --- User tries to type on a confirmed line (should be blocked) ---
        print("\n[4] User clicks on first line and tries to type (should be blocked)")
        # Click at the beginning of the textarea (first line)
        page.evaluate("() => { const ta = document.getElementById('pipe-filter-t'); ta.focus(); ta.setSelectionRange(0, 0); }")
        page.wait_for_timeout(100)
        val_before = get_val()
        page.keyboard.type("X")
        page.wait_for_timeout(200)
        val_after = get_val()
        check("Typing blocked on confirmed line", val_before == val_after, f"before={val_before!r} after={val_after!r}")
        check("Cursor snapped to end", get_sel() == len(val_after), f"sel={get_sel()} len={len(val_after)}")
        snap("after_blocked_type")

        # --- User double-clicks a confirmed line (edit mode) ---
        print("\n[5] User double-clicks first line (edit mode)")
        page.evaluate("() => { const ta = document.getElementById('pipe-filter-t'); ta.focus(); ta.setSelectionRange(5, 5); }")
        page.wait_for_timeout(100)
        # Double-click via mouse at the position of the first line
        box = ta.bounding_box()
        if box:
            # Click at first line position (roughly 1/3 from top of textarea)
            click_x = box["x"] + 50
            click_y = box["y"] + 15
            page.mouse.dblclick(click_x, click_y)
            page.wait_for_timeout(300)
        edit_line = page.evaluate("() => document.getElementById('pipe-filter-t')._psdnsEditLine")
        check("Edit mode active", edit_line is not None, f"editLine={edit_line}")
        color = page.evaluate("() => document.getElementById('pipe-filter-t').style.color")
        check("Text visible in edit mode", color == "", f"color={color!r}")
        snap("edit_mode")

        # --- User presses Escape (cancel edit) ---
        print("\n[6] User presses Escape (cancel edit)")
        page.keyboard.press("Escape")
        page.wait_for_timeout(200)
        edit_line = page.evaluate("() => document.getElementById('pipe-filter-t')._psdnsEditLine")
        check("Edit mode exited", edit_line is None, f"editLine={edit_line}")
        color = page.evaluate("() => document.getElementById('pipe-filter-t').style.color")
        check("Text hidden again", color == "transparent", f"color={color!r}")
        snap("after_escape")

        # --- User double-clicks again, edits, presses Enter ---
        print("\n[7] User double-clicks, edits line, presses Enter (confirm)")
        page.evaluate("() => { const ta = document.getElementById('pipe-filter-t'); ta.focus(); ta.setSelectionRange(5, 5); }")
        page.wait_for_timeout(100)
        box = ta.bounding_box()
        if box:
            page.mouse.dblclick(box["x"] + 50, box["y"] + 15)
            page.wait_for_timeout(300)
        # Now in edit mode, select all in that line and type new value
        page.evaluate("""
            () => {
                const ta = document.getElementById('pipe-filter-t');
                const lines = ta.value.split('\\n');
                const idx = ta._psdnsEditLine;
                const start = lines.slice(0, idx).join('\\n').length + (idx > 0 ? 1 : 0);
                ta.setSelectionRange(start, start + lines[idx].length);
            }
        """)
        page.wait_for_timeout(100)
        page.keyboard.type("com.vivo.feedback")
        page.wait_for_timeout(200)
        page.keyboard.press("Enter")
        page.wait_for_timeout(300)
        val = get_val()
        check("Line updated", "com.vivo.feedback" in val, f"val={val!r}")
        edit_line = page.evaluate("() => document.getElementById('pipe-filter-t')._psdnsEditLine")
        check("Edit mode exited", edit_line is None)
        snap("after_edit_enter")

        # --- User presses Backspace once on empty last line (nothing happens) ---
        print("\n[8] User presses Backspace once on empty line (nothing)")
        page.evaluate("() => { const ta = document.getElementById('pipe-filter-t'); ta.focus(); ta.setSelectionRange(ta.value.length, ta.value.length); }")
        page.wait_for_timeout(100)
        val_before = get_val()
        page.keyboard.press("Backspace")
        page.wait_for_timeout(200)
        val_after = get_val()
        check("Single Backspace does nothing", val_before == val_after, f"val={val_after!r}")

        # --- User presses Backspace again (deletes previous line) ---
        print("\n[9] User presses Backspace again (deletes previous line)")
        page.keyboard.press("Backspace")
        page.wait_for_timeout(200)
        val_after = get_val()
        lines_before_count = val_before.count("\n")
        lines_after_count = val_after.count("\n")
        check("Line deleted", lines_after_count < lines_before_count, f"before={lines_before_count} after={lines_after_count}")
        check("Last line empty", val_after.endswith("\n"), f"val={val_after!r}")
        snap("after_double_backspace")

        # --- User selects all (text should NOT be visible) ---
        print("\n[10] User selects all text (Ctrl+A) - text should be invisible")
        page.evaluate("() => { const ta = document.getElementById('pipe-filter-t'); ta.focus(); }")
        page.wait_for_timeout(100)
        page.keyboard.press("Control+a")
        page.wait_for_timeout(300)
        snap("selected_all")

        # ================================================================
        print("\n" + "="*60)
        print("PHASE 2: PSDNS DISABLED - Normal textarea")
        print("="*60)

        # Disable PSDNS
        page.evaluate("""
            () => {
                const cb = document.getElementById('psdns-enabled');
                cb.checked = false;
                cb.dispatchEvent(new Event('change', {bubbles: true}));
            }
        """)
        page.wait_for_timeout(500)

        # --- User can type anywhere ---
        print("\n[11] PSDNS off: User clicks first line and types freely")
        page.evaluate("() => { const ta = document.getElementById('pipe-filter-t'); ta.focus(); ta.setSelectionRange(0, 0); }")
        page.wait_for_timeout(100)
        val_before = get_val()
        page.keyboard.type("Z")
        page.wait_for_timeout(200)
        val_after = get_val()
        check("Typing works when PSDNS off", val_after != val_before, f"before={val_before!r} after={val_after!r}")
        check("Text inserted at position 0", val_after.startswith("Z"), f"val={val_after!r}")
        snap("psdns_off_typed")

        # --- Enter creates normal newline (no confirmation logic) ---
        print("\n[12] PSDNS off: Enter creates normal newline")
        page.evaluate("() => { const ta = document.getElementById('pipe-filter-t'); ta.focus(); ta.setSelectionRange(ta.value.length, ta.value.length); }")
        page.wait_for_timeout(100)
        val_before = get_val()
        page.keyboard.press("Enter")
        page.wait_for_timeout(200)
        val_after = get_val()
        check("Newline added", val_after == val_before + "\n", f"before={val_before!r} after={val_after!r}")

        # --- Text is visible (not transparent) ---
        print("\n[13] PSDNS off: Text is visible")
        color = page.evaluate("() => document.getElementById('pipe-filter-t').style.color")
        check("Text visible (no transparent)", color == "", f"color={color!r}")
        snap("psdns_off_visible")

        # Re-enable PSDNS
        page.evaluate("""
            () => {
                const cb = document.getElementById('psdns-enabled');
                cb.checked = true;
                cb.dispatchEvent(new Event('change', {bubbles: true}));
            }
        """)
        page.wait_for_timeout(500)

        browser.close()

    # Summary
    passed = sum(1 for _, s, _ in results if s == "PASS")
    failed = sum(1 for _, s, _ in results if s == "FAIL")
    print(f"\n{'='*60}")
    print(f"RESULTS: {passed} passed, {failed} failed, {len(results)} total")
    if failed:
        print("\nFAILED:")
        for name, s, detail in results:
            if s == "FAIL":
                print(f"  - {name}: {detail}")
    print(f"{'='*60}")
    return failed

if __name__ == "__main__":
    sys.exit(main())
