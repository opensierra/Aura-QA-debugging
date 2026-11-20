# -*- coding: utf-8 -*-
"""
ADVERSARIAL test: try to break the PSDNS edit rules.
Goal: find any way to corrupt confirmed lines, bypass protection, or create inconsistent state.
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
    print("[adversarial] catalog:", len(catalog), "packages")

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
        shot_n = 0
        def snap(label):
            nonlocal shot_n
            shot_n += 1
            path = os.path.join(OUT_DIR, f"psdns_adv_{shot_n:02d}_{label}.png")
            page.screenshot(path=path)

        def get_val():
            return page.evaluate("() => document.getElementById('pipe-filter-t').value")

        def get_sel():
            return page.evaluate("() => document.getElementById('pipe-filter-t').selectionStart")

        def set_val(v):
            page.evaluate(f"() => {{ const ta = document.getElementById('pipe-filter-t'); ta.value = {json.dumps(v)}; ta.dispatchEvent(new Event('input', {{bubbles: true}})); }}")
            page.wait_for_timeout(200)

        def focus_at(pos):
            page.evaluate(f"() => {{ const ta = document.getElementById('pipe-filter-t'); ta.focus(); ta.setSelectionRange({pos}, {pos}); }}")
            page.wait_for_timeout(50)

        # ================================================================
        print("\n" + "="*60)
        print("SETUP: Build a known state with 3 confirmed lines")
        print("="*60)
        set_val("com.android.deskclock\ncom.vivo.calculator\ncom.vivo.feedback\n")
        page.wait_for_timeout(300)
        val = get_val()
        check("Setup: 3 lines + empty last", val == "com.android.deskclock\ncom.vivo.calculator\ncom.vivo.feedback\n", f"val={val!r}")

        # ================================================================
        print("\n" + "="*60)
        print("ATTACK 1: Paste multiple lines on last line")
        print("="*60)
        focus_at(len(val))
        # Simulate paste of multiple lines
        page.evaluate("""
            () => {
                const ta = document.getElementById('pipe-filter-t');
                ta.focus();
                ta.setSelectionRange(ta.value.length, ta.value.length);
                const dt = new DataTransfer();
                dt.setData('text/plain', 'com.vivo.imanager\\ncom.android.settings\\n');
                const ev = new ClipboardEvent('paste', {clipboardData: dt, bubbles: true, cancelable: true});
                ta.dispatchEvent(ev);
            }
        """)
        page.wait_for_timeout(300)
        val = get_val()
        lines = [l for l in val.split('\n') if l.strip()]
        print(f"  [info] After paste: {len(lines)} non-empty lines")
        print(f"  [info] Value: {val!r}")
        # The paste should have been blocked by beforeinput (insertFromPaste)
        # OR it went through and now we have extra lines
        # Either way, confirmed lines should NOT be modified
        check("Confirmed line 1 intact", val.startswith("com.android.deskclock"), f"val={val!r}")
        check("Confirmed line 2 intact", "com.vivo.calculator" in val, f"val={val!r}")
        check("Confirmed line 3 intact", "com.vivo.feedback" in val, f"val={val!r}")
        snap("paste_multi")

        # ================================================================
        print("\n" + "="*60)
        print("ATTACK 2: Ctrl+A then type (replace all)")
        print("="*60)
        set_val("com.android.deskclock\ncom.vivo.calculator\ncom.vivo.feedback\n")
        focus_at(0)
        page.keyboard.press("Control+a")
        page.wait_for_timeout(100)
        page.keyboard.type("HACKED")
        page.wait_for_timeout(300)
        val = get_val()
        print(f"  [info] After Ctrl+A + type: {val!r}")
        # beforeinput should block insertText when selection spans confirmed lines
        # But Ctrl+A selects everything including the last empty line
        # The cursor is at 0 (confirmed line), so beforeinput should block
        check("Ctrl+A + type blocked or contained", "com.android.deskclock" in val or val == "HACKED\n", f"val={val!r}")
        snap("ctrl_a_type")

        # ================================================================
        print("\n" + "="*60)
        print("ATTACK 3: Arrow keys to navigate into confirmed lines, then type")
        print("="*60)
        set_val("com.android.deskclock\ncom.vivo.calculator\ncom.vivo.feedback\n")
        focus_at(len("com.android.deskclock\ncom.vivo.calculator\ncom.vivo.feedback\n"))
        # Navigate up with arrow keys
        page.keyboard.press("ArrowUp")
        page.wait_for_timeout(50)
        page.keyboard.press("ArrowUp")
        page.wait_for_timeout(50)
        page.keyboard.press("ArrowLeft")
        page.wait_for_timeout(50)
        page.keyboard.press("ArrowLeft")
        page.wait_for_timeout(50)
        sel = get_sel()
        print(f"  [info] Cursor after arrows: {sel}")
        # Now try to type
        val_before = get_val()
        page.keyboard.type("X")
        page.wait_for_timeout(200)
        val_after = get_val()
        check("Typing after arrow navigation blocked", val_before == val_after, f"before={val_before!r} after={val_after!r}")
        check("Cursor snapped to end", get_sel() == len(val_after), f"sel={get_sel()} len={len(val_after)}")
        snap("arrow_nav_type")

        # ================================================================
        print("\n" + "="*60)
        print("ATTACK 4: Shift+Arrow to select confirmed text, then type")
        print("="*60)
        set_val("com.android.deskclock\ncom.vivo.calculator\ncom.vivo.feedback\n")
        focus_at(0)
        # Select first line with Shift+End
        page.keyboard.press("Shift+End")
        page.wait_for_timeout(100)
        # Now type (should replace selection)
        page.keyboard.type("REPLACED")
        page.wait_for_timeout(200)
        val = get_val()
        print(f"  [info] After Shift+End + type: {val!r}")
        check("Selection replace blocked", "com.android.deskclock" in val, f"val={val!r}")
        snap("shift_select_type")

        # ================================================================
        print("\n" + "="*60)
        print("ATTACK 5: Delete key at start of confirmed line")
        print("="*60)
        set_val("com.android.deskclock\ncom.vivo.calculator\ncom.vivo.feedback\n")
        # Put cursor at start of line 2 (position = len("com.android.deskclock\n"))
        pos_line2 = len("com.android.deskclock\n")
        focus_at(pos_line2)
        page.wait_for_timeout(50)
        val_before = get_val()
        page.keyboard.press("Delete")
        page.wait_for_timeout(200)
        val_after = get_val()
        check("Delete at start of confirmed line blocked", val_before == val_after, f"before={val_before!r} after={val_after!r}")
        snap("delete_confirmed")

        # ================================================================
        print("\n" + "="*60)
        print("ATTACK 6: Backspace at start of last line (not empty) - should delete char")
        print("="*60)
        set_val("com.android.deskclock\ncom.vivo.calculator\ncom.vivo.feedb")
        # Cursor at end of "com.vivo.feedb" (last line, not empty)
        focus_at(len("com.android.deskclock\ncom.vivo.calculator\ncom.vivo.feedb"))
        val_before = get_val()
        page.keyboard.press("Backspace")
        page.wait_for_timeout(200)
        val_after = get_val()
        # This should work normally (deleting a char on the active line)
        check("Backspace on non-empty last line works", val_after == val_before[:-1], f"before={val_before!r} after={val_after!r}")
        snap("backspace_active")

        # ================================================================
        print("\n" + "="*60)
        print("ATTACK 7: Rapid double Backspace (3x in a row)")
        print("="*60)
        set_val("com.android.deskclock\ncom.vivo.calculator\ncom.vivo.feedback\n")
        focus_at(len("com.android.deskclock\ncom.vivo.calculator\ncom.vivo.feedback\n"))
        # 3 backspaces in rapid succession
        page.keyboard.press("Backspace")
        page.wait_for_timeout(50)
        page.keyboard.press("Backspace")
        page.wait_for_timeout(50)
        page.keyboard.press("Backspace")
        page.wait_for_timeout(200)
        val = get_val()
        lines = [l for l in val.split('\n') if l.strip()]
        print(f"  [info] After 3x Backspace: {len(lines)} lines, val={val!r}")
        # First BS: sets flag. Second BS: deletes line. Third BS: sets flag again (no delete)
        check("Only one line deleted (not two)", len(lines) == 2, f"lines={lines}")
        snap("triple_backspace")

        # ================================================================
        print("\n" + "="*60)
        print("ATTACK 8: Type on last line, then Backspace to empty it, then Backspace again")
        print("="*60)
        set_val("com.android.deskclock\ncom.vivo.calculator\n")
        focus_at(len("com.android.deskclock\ncom.vivo.calculator\n"))
        page.keyboard.type("abc")
        page.wait_for_timeout(100)
        # Now backspace 3 times to empty the line
        page.keyboard.press("Backspace")
        page.wait_for_timeout(50)
        page.keyboard.press("Backspace")
        page.wait_for_timeout(50)
        page.keyboard.press("Backspace")
        page.wait_for_timeout(100)
        val = get_val()
        check("Line emptied", val == "com.android.deskclock\ncom.vivo.calculator\n", f"val={val!r}")
        # Now one more backspace (should set flag, not delete)
        page.keyboard.press("Backspace")
        page.wait_for_timeout(100)
        val = get_val()
        check("Single BS on empty line does nothing", val == "com.android.deskclock\ncom.vivo.calculator\n", f"val={val!r}")
        # And one more (should delete)
        page.keyboard.press("Backspace")
        page.wait_for_timeout(100)
        val = get_val()
        check("Second BS deletes line", val == "com.android.deskclock\n", f"val={val!r}")
        snap("type_empty_delete")

        # ================================================================
        print("\n" + "="*60)
        print("ATTACK 9: Enter with Shift (should insert newline, not confirm)")
        print("="*60)
        set_val("com.android.deskclock\ncom.vivo.calculator\n")
        focus_at(len("com.android.deskclock\ncom.vivo.calculator\n"))
        page.keyboard.type("test")
        page.wait_for_timeout(100)
        val_before = get_val()
        page.keyboard.press("Shift+Enter")
        page.wait_for_timeout(200)
        val_after = get_val()
        print(f"  [info] After Shift+Enter: {val_after!r}")
        # Shift+Enter should NOT be intercepted (our handler checks !e.shiftKey)
        # It should insert a newline normally
        check("Shift+Enter inserts newline (not confirm)", val_after != val_before, f"before={val_before!r} after={val_after!r}")
        snap("shift_enter")

        # ================================================================
        print("\n" + "="*60)
        print("ATTACK 10: Tab key (should not be blocked)")
        print("="*60)
        set_val("com.android.deskclock\ncom.vivo.calculator\n")
        focus_at(len("com.android.deskclock\ncom.vivo.calculator\n"))
        val_before = get_val()
        page.keyboard.press("Tab")
        page.wait_for_timeout(200)
        val_after = get_val()
        # Tab should move focus away (not insert tab, not be blocked)
        # The textarea should lose focus
        has_focus = page.evaluate("() => document.getElementById('pipe-filter-t') === document.activeElement")
        check("Tab moves focus away", not has_focus, f"has_focus={has_focus}")
        snap("tab_key")

        # ================================================================
        print("\n" + "="*60)
        print("ATTACK 11: Ctrl+Z (undo) after a blocked action")
        print("="*60)
        set_val("com.android.deskclock\ncom.vivo.calculator\ncom.vivo.feedback\n")
        focus_at(len("com.android.deskclock\ncom.vivo.calculator\ncom.vivo.feedback\n"))
        # Type something (allowed on last line)
        page.keyboard.type("new")
        page.wait_for_timeout(100)
        # Undo
        page.keyboard.press("Control+z")
        page.wait_for_timeout(200)
        val = get_val()
        print(f"  [info] After Ctrl+Z: {val!r}")
        # Undo should restore the previous state (native browser behavior)
        # This is hard to control - just verify it doesn't crash
        check("No crash after Ctrl+Z", val is not None)
        snap("ctrl_z")

        # ================================================================
        print("\n" + "="*60)
        print("ATTACK 12: IME composition (isComposing)")
        print("="*60)
        set_val("com.android.deskclock\ncom.vivo.calculator\n")
        focus_at(len("com.android.deskclock\ncom.vivo.calculator\n"))
        # Simulate IME composition start
        page.evaluate("""
            () => {
                const ta = document.getElementById('pipe-filter-t');
                ta.focus();
                ta.setSelectionRange(ta.value.length, ta.value.length);
                const ev = new CompositionEvent('compositionstart', {bubbles: true});
                ta.dispatchEvent(ev);
            }
        """)
        page.wait_for_timeout(100)
        # During composition, Enter should NOT confirm
        val_before = get_val()
        page.evaluate("""
            () => {
                const ta = document.getElementById('pipe-filter-t');
                const ev = new KeyboardEvent('keydown', {key: 'Enter', bubbles: true, cancelable: true});
                // Simulate isComposing
                Object.defineProperty(ev, 'isComposing', {value: true});
                ta.dispatchEvent(ev);
            }
        """)
        page.wait_for_timeout(200)
        val_after = get_val()
        check("Enter during IME composition does NOT confirm", val_before == val_after, f"before={val_before!r} after={val_after!r}")
        # End composition
        page.evaluate("""
            () => {
                const ta = document.getElementById('pipe-filter-t');
                const ev = new CompositionEvent('compositionend', {bubbles: true, data: 'test'});
                ta.dispatchEvent(ev);
            }
        """)
        snap("ime_composition")

        # ================================================================
        print("\n" + "="*60)
        print("ATTACK 13: Rapid Enter spam (empty line)")
        print("="*60)
        set_val("com.android.deskclock\ncom.vivo.calculator\n")
        focus_at(len("com.android.deskclock\ncom.vivo.calculator\n"))
        for _ in range(5):
            page.keyboard.press("Enter")
            page.wait_for_timeout(30)
        val = get_val()
        lines = val.split('\n')
        check("Rapid Enter on empty line: no extra lines", val == "com.android.deskclock\ncom.vivo.calculator\n", f"val={val!r}")
        snap("enter_spam")

        # ================================================================
        print("\n" + "="*60)
        print("ATTACK 14: Double-click on LAST (empty) line - should NOT enter edit mode")
        print("="*60)
        set_val("com.android.deskclock\ncom.vivo.calculator\n")
        focus_at(len("com.android.deskclock\ncom.vivo.calculator\n"))
        page.evaluate("""
            () => {
                const ta = document.getElementById('pipe-filter-t');
                ta.setSelectionRange(ta.value.length, ta.value.length);
                const ev = new MouseEvent('dblclick', {bubbles: true});
                ta.dispatchEvent(ev);
            }
        """)
        page.wait_for_timeout(200)
        edit_line = page.evaluate("() => document.getElementById('pipe-filter-t')._psdnsEditLine")
        check("Dblclick on empty last line: no edit mode", edit_line is None, f"editLine={edit_line}")
        snap("dblclick_empty")

        # ================================================================
        print("\n" + "="*60)
        print("ATTACK 15: Edit mode + Backspace to delete entire line content")
        print("="*60)
        set_val("com.android.deskclock\ncom.vivo.calculator\n")
        focus_at(5)
        page.evaluate("""
            () => {
                const ta = document.getElementById('pipe-filter-t');
                ta.setSelectionRange(5, 5);
                const ev = new MouseEvent('dblclick', {bubbles: true});
                ta.dispatchEvent(ev);
            }
        """)
        page.wait_for_timeout(200)
        # In edit mode, select all of line 0 and delete
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
        page.keyboard.press("Backspace")
        page.wait_for_timeout(100)
        # Now line 0 is empty, press Enter to confirm
        page.keyboard.press("Enter")
        page.wait_for_timeout(200)
        val = get_val()
        lines = val.split('\n')
        print(f"  [info] After edit+delete+enter: {val!r}")
        # Empty line confirmed = just an empty line (or removed?)
        # Our psdnsConfirmLine checks if line is empty -> returns false (no confirm)
        # So the empty line stays as-is
        edit_line = page.evaluate("() => document.getElementById('pipe-filter-t')._psdnsEditLine")
        check("Edit mode exited", edit_line is None, f"editLine={edit_line}")
        snap("edit_delete_enter")

        # ================================================================
        print("\n" + "="*60)
        print("ATTACK 16: Toggle PSDNS off while in edit mode")
        print("="*60)
        set_val("com.android.deskclock\ncom.vivo.calculator\n")
        focus_at(5)
        page.evaluate("""
            () => {
                const ta = document.getElementById('pipe-filter-t');
                ta.setSelectionRange(5, 5);
                const ev = new MouseEvent('dblclick', {bubbles: true});
                ta.dispatchEvent(ev);
            }
        """)
        page.wait_for_timeout(200)
        edit_line = page.evaluate("() => document.getElementById('pipe-filter-t')._psdnsEditLine")
        check("In edit mode", edit_line is not None, f"editLine={edit_line}")
        # Toggle PSDNS off
        page.evaluate("""
            () => {
                const cb = document.getElementById('psdns-enabled');
                cb.checked = false;
                cb.dispatchEvent(new Event('change', {bubbles: true}));
            }
        """)
        page.wait_for_timeout(300)
        # Edit state should be cleared
        edit_line = page.evaluate("() => document.getElementById('pipe-filter-t')._psdnsEditLine")
        check("Edit mode cleared when PSDNS off", edit_line is None, f"editLine={edit_line}")
        color = page.evaluate("() => document.getElementById('pipe-filter-t').style.color")
        check("Text visible when PSDNS off", color == "", f"color={color!r}")
        snap("toggle_off_edit")

        # Re-enable
        page.evaluate("""
            () => {
                const cb = document.getElementById('psdns-enabled');
                cb.checked = true;
                cb.dispatchEvent(new Event('change', {bubbles: true}));
            }
        """)
        page.wait_for_timeout(300)

        # ================================================================
        print("\n" + "="*60)
        print("ATTACK 17: Very long line (stress)")
        print("="*60)
        long_pkg = "com." + "a" * 200 + ".package"
        set_val("com.android.deskclock\n")
        focus_at(len("com.android.deskclock\n"))
        page.keyboard.type(long_pkg)
        page.wait_for_timeout(200)
        page.keyboard.press("Enter")
        page.wait_for_timeout(300)
        val = get_val()
        check("Long line confirmed", long_pkg in val, f"val_len={len(val)}")
        check("New empty line after long line", val.endswith("\n"), f"val_end={val[-20:]!r}")
        snap("long_line")

        # ================================================================
        print("\n" + "="*60)
        print("ATTACK 18: Unicode / special characters")
        print("="*60)
        set_val("com.android.deskclock\n")
        focus_at(len("com.android.deskclock\n"))
        page.keyboard.type("com.ünïcödé.app")
        page.wait_for_timeout(200)
        page.keyboard.press("Enter")
        page.wait_for_timeout(200)
        val = get_val()
        check("Unicode line confirmed", "com.ünïcödé.app" in val, f"val={val!r}")
        snap("unicode")

        # ================================================================
        print("\n" + "="*60)
        print("ATTACK 19: Only one line total, double Backspace")
        print("="*60)
        set_val("com.android.deskclock\n")
        focus_at(len("com.android.deskclock\n"))
        page.keyboard.press("Backspace")
        page.wait_for_timeout(50)
        page.keyboard.press("Backspace")
        page.wait_for_timeout(200)
        val = get_val()
        print(f"  [info] After double BS with 1 line: {val!r}")
        # Should delete the only confirmed line, leaving just "\n" or ""
        check("Line deleted (or empty)", val.strip() == "" or val == "\n", f"val={val!r}")
        snap("single_line_bs")

        # ================================================================
        print("\n" + "="*60)
        print("ATTACK 20: Empty textarea, type + Enter")
        print("="*60)
        set_val("")
        focus_at(0)
        page.keyboard.type("com.vivo.imanager")
        page.wait_for_timeout(100)
        page.keyboard.press("Enter")
        page.wait_for_timeout(200)
        val = get_val()
        check("First line from empty", "com.vivo.imanager" in val, f"val={val!r}")
        check("Ends with newline", val.endswith("\n"), f"val={val!r}")
        snap("empty_start")

        browser.close()

    # Summary
    passed = sum(1 for _, s, _ in results if s == "PASS")
    failed = sum(1 for _, s, _ in results if s == "FAIL")
    print(f"\n{'='*60}")
    print(f"ADVERSARIAL RESULTS: {passed} passed, {failed} failed, {len(results)} total")
    if failed:
        print("\nFAILED:")
        for name, s, detail in results:
            if s == "FAIL":
                print(f"  - {name}: {detail}")
    print(f"{'='*60}")
    return failed

if __name__ == "__main__":
    sys.exit(main())
