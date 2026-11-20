# -*- coding: utf-8 -*-
"""
Headless test for PSDNS edit rules.
Dispatches events directly to the textarea element to avoid Playwright focus issues.
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


# JS helper that simulates a keydown event on the textarea
KEYDOWN_JS = """
    (key, opts = {}) => {
        const ta = document.getElementById('wz-filter-t');
        ta.focus();
        const ev = new KeyboardEvent('keydown', {
            key: key,
            bubbles: true,
            cancelable: true,
            ...opts
        });
        ta.dispatchEvent(ev);
        return ev.defaultPrevented;
    }
"""

# JS helper that simulates a beforeinput event
BEFOREINPUT_JS = """
    (inputType, data) => {
        const ta = document.getElementById('wz-filter-t');
        ta.focus();
        const ev = new InputEvent('beforeinput', {
            inputType: inputType,
            data: data,
            bubbles: true,
            cancelable: true
        });
        ta.dispatchEvent(ev);
        return ev.defaultPrevented;
    }
"""


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    catalog = load_catalog()
    print("[test] catalog packages:", len(catalog))

    from playwright.sync_api import sync_playwright

    results = []

    def check(name, cond, detail=""):
        status = "PASS" if cond else "FAIL"
        results.append({"name": name, "status": status, "detail": detail})
        print(f"  [{status}] {name}" + (f" — {detail}" if detail and not cond else ""))

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
        page.click("#wz-next")
        page.wait_for_timeout(1500)

        page.wait_for_function(
            "() => { const ov = document.querySelector('.psdns-overlay'); return ov && ov.style.display !== 'none'; }",
            timeout=10000,
        )
        page.wait_for_timeout(500)

        # Register JS helpers
        page.evaluate(KEYDOWN_JS.replace("    (key, opts = {}) => {", "window.__key = (key, opts = {}) => {"))
        page.evaluate(BEFOREINPUT_JS.replace("    (inputType, data) => {", "window.__beforeinput = (inputType, data) => {"))

        def set_value(val):
            page.evaluate(f"() => {{ const ta = document.getElementById('wz-filter-t'); ta.value = {json.dumps(val)}; ta.dispatchEvent(new Event('input', {{bubbles: true}})); }}")
            page.wait_for_timeout(200)

        def get_value():
            return page.evaluate("() => document.getElementById('wz-filter-t').value")

        def set_cursor(pos):
            page.evaluate(f"() => {{ const ta = document.getElementById('wz-filter-t'); ta.focus(); ta.setSelectionRange({pos}, {pos}); }}")
            page.wait_for_timeout(50)

        def cursor_pos():
            return page.evaluate("() => document.getElementById('wz-filter-t').selectionStart")

        def key(k, **opts):
            opts_js = json.dumps(opts) if opts else "{}"
            return page.evaluate(f"window.__key({json.dumps(k)}, {opts_js})")

        def beforeinput(input_type, data=None):
            data_js = json.dumps(data) if data else "null"
            return page.evaluate(f"window.__beforeinput({json.dumps(input_type)}, {data_js})")

        # --- TEST 1: Enter on last line with text confirms + new empty line ---
        print("\n[TEST 1] Enter confirms line + creates new empty line")
        set_value("com.android.deskclock\ncom.vivo.calculator\n")
        # Cursor at end (last empty line)
        set_cursor(len("com.android.deskclock\ncom.vivo.calculator\n"))
        # Simulate Enter
        prevented = key("Enter")
        page.wait_for_timeout(200)
        val = get_value()
        lines = val.split('\n')
        check("Enter prevented default", prevented == True, f"prevented={prevented}")
        check("New empty line created", lines[-1] == '', f"lines={lines}")
        check("com.vivo.calculator confirmed", 'com.vivo.calculator' in val, f"val={val!r}")
        check("com.android.deskclock preserved", 'com.android.deskclock' in val, f"val={val!r}")
        check("Cursor at end", cursor_pos() == len(val), f"cursor={cursor_pos()}, len={len(val)}")

        # --- TEST 2: Enter on empty last line does nothing ---
        print("\n[TEST 2] Enter on empty last line does nothing")
        val_before = get_value()
        set_cursor(len(val_before))
        prevented = key("Enter")
        page.wait_for_timeout(200)
        val_after = get_value()
        check("Value unchanged", val_before == val_after, f"before={val_before!r} after={val_after!r}")

        # --- TEST 3: Double Backspace deletes previous line ---
        print("\n[TEST 3] Double Backspace on empty last line deletes previous")
        val_before = get_value()
        lines_before = val_before.split('\n')
        set_cursor(len(val_before))
        # First backspace
        key("Backspace")
        page.wait_for_timeout(100)
        val_mid = get_value()
        check("Single Backspace does nothing", val_mid == val_before, f"val={val_mid!r}")
        # Second backspace
        key("Backspace")
        page.wait_for_timeout(200)
        val_after = get_value()
        lines_after = val_after.split('\n')
        check("Double Backspace deletes a line", len(lines_after) == len(lines_before) - 1,
              f"before={len(lines_before)} after={len(lines_after)} val={val_after!r}")
        check("Last line still empty", lines_after[-1] == '', f"last={lines_after[-1]!r}")

        # --- TEST 4: beforeinput blocked on confirmed line ---
        print("\n[TEST 4] beforeinput blocked on confirmed line")
        set_value("com.android.deskclock\ncom.vivo.calculator\n")
        # Cursor on first line (confirmed)
        set_cursor(5)
        prevented = beforeinput("insertText", "X")
        page.wait_for_timeout(100)
        val = get_value()
        check("beforeinput prevented", prevented == True, f"prevented={prevented}")
        check("Value unchanged", val == "com.android.deskclock\ncom.vivo.calculator\n", f"val={val!r}")
        check("Cursor snapped to end", cursor_pos() == len(val), f"cursor={cursor_pos()}, len={len(val)}")

        # --- TEST 5: beforeinput allowed on last line ---
        print("\n[TEST 5] beforeinput allowed on last line")
        set_value("com.android.deskclock\n")
        set_cursor(len("com.android.deskclock\n"))
        prevented = beforeinput("insertText", "X")
        page.wait_for_timeout(100)
        check("beforeinput NOT prevented on last line", prevented == False, f"prevented={prevented}")

        # --- TEST 6: Double-click enters edit mode ---
        print("\n[TEST 6] Double-click enters edit mode")
        set_value("com.android.deskclock\ncom.vivo.calculator\n")
        set_cursor(5)
        page.evaluate("""
            () => {
                const ta = document.getElementById('wz-filter-t');
                ta.setSelectionRange(5, 5);
                const ev = new MouseEvent('dblclick', {bubbles: true});
                ta.dispatchEvent(ev);
            }
        """)
        page.wait_for_timeout(300)
        edit_line = page.evaluate("() => document.getElementById('wz-filter-t')._psdnsEditLine")
        check("Edit mode active (line 0)", edit_line == 0, f"_psdnsEditLine={edit_line}")
        color = page.evaluate("() => document.getElementById('wz-filter-t').style.color")
        check("Text visible in edit mode", color == '', f"color={color!r}")

        # --- TEST 7: Escape restores original ---
        print("\n[TEST 7] Escape in edit mode restores original")
        original = page.evaluate("() => document.getElementById('wz-filter-t')._psdnsEditOriginal")
        check("Original captured", original == "com.android.deskclock", f"original={original!r}")
        # Modify the line
        set_value("com.modified.package\ncom.vivo.calculator\n")
        key("Escape")
        page.wait_for_timeout(200)
        val = get_value()
        lines = val.split('\n')
        check("Original restored", lines[0] == "com.android.deskclock", f"line0={lines[0]!r}")
        in_edit = page.evaluate("() => { const v = document.getElementById('wz-filter-t')._psdnsEditLine; return v !== null && v !== undefined; }")
        check("Edit mode exited", not in_edit)

        # --- TEST 8: Enter in edit mode re-confirms ---
        print("\n[TEST 8] Enter in edit mode re-confirms")
        # Enter edit mode
        set_value("com.android.deskclock\ncom.vivo.calculator\n")
        set_cursor(5)
        page.evaluate("""
            () => {
                const ta = document.getElementById('wz-filter-t');
                ta.setSelectionRange(5, 5);
                const ev = new MouseEvent('dblclick', {bubbles: true});
                ta.dispatchEvent(ev);
            }
        """)
        page.wait_for_timeout(200)
        # Modify to valid package
        set_value("com.vivo.feedback\ncom.vivo.calculator\n")
        key("Enter")
        page.wait_for_timeout(200)
        val = get_value()
        lines = val.split('\n')
        check("Line updated", lines[0] == 'com.vivo.feedback', f"line0={lines[0]!r}")
        in_edit = page.evaluate("() => { const v = document.getElementById('wz-filter-t')._psdnsEditLine; return v !== null && v !== undefined; }")
        check("Edit mode exited after Enter", not in_edit)

        # --- TEST 9: PSDNS disabled -> normal behavior ---
        print("\n[TEST 9] PSDNS disabled -> normal textarea")
        page.evaluate("() => { const cb = document.getElementById('wz-psdns-enabled'); cb.checked = false; cb.dispatchEvent(new Event('change', {bubbles: true})); }")
        page.wait_for_timeout(300)
        set_value("com.android.deskclock\n")
        set_cursor(5)
        prevented = beforeinput("insertText", "X")
        page.wait_for_timeout(100)
        check("beforeinput NOT prevented when PSDNS off", prevented == False, f"prevented={prevented}")

        # Re-enable
        page.evaluate("() => { const cb = document.getElementById('wz-psdns-enabled'); cb.checked = true; cb.dispatchEvent(new Event('change', {bubbles: true})); }")

        shot = os.path.join(OUT_DIR, "psdns_edit_rules_test.png")
        page.screenshot(path=shot)
        print(f"\n[screenshot] {shot}")
        browser.close()

    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    print(f"\n{'='*50}")
    print(f"RESULTS: {passed} passed, {failed} failed, {len(results)} total")
    if failed:
        print("\nFAILED TESTS:")
        for r in results:
            if r["status"] == "FAIL":
                print(f"  - {r['name']}: {r['detail']}")
    print(f"{'='*50}")
    return failed


if __name__ == "__main__":
    sys.exit(main())
