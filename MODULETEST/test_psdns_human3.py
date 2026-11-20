# -*- coding: utf-8 -*-
"""
PSDNS human test. ONLY real mouse/keyboard. No evaluate for interaction.
"""
import json, os, sys
from playwright.sync_api import sync_playwright

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UI_INDEX = os.path.join(BASE, "UI", "index.html")
CATALOG = os.path.join(BASE, "Customlib", "psdns.json")

INSTALLED = ["com.android.deskclock","com.vivo.calculator","com.vivo.feedback","com.vivo.imanager"]

def load_catalog():
    with open(CATALOG, "r", encoding="utf-8-sig") as f:
        return json.load(f)

def build_init_script(catalog):
    c = json.dumps(catalog, ensure_ascii=False)
    i = json.dumps(INSTALLED, ensure_ascii=False)
    return r"""
    (function () {
      const api = {
        loadConfig: async()=>null, saveConfig: async()=>true, getRecentProjects: async()=>[],
        removeRecentProject: async()=>true, getCurrentProject: async()=>null, openProject: async()=>({ok:false}),
        getDeviceInfo: async()=>({connected:false}),
        refreshPsdns: async()=>({ok:true,serial:"T",catalog:__C__,installed:__I__,catalogPackages:Object.keys(__C__).length}),
        updatePsdns: async()=>({ok:false}), getRunState: async()=>null, getPipelineState: async()=>({status:"idle"}),
        getQaReport: async()=>null, getCrawlLatest: async()=>null, getImageData: async()=>null,
        startPipeline: async()=>({ok:false}), stopPipeline: async()=>{}, startBlueCode: async()=>({ok:false}),
        getBlueCodeStatus: async()=>({running:false}), stopBlueCode: async()=>{}, getProjectLog: async()=>null,
        listDir: async()=>null, previewExport: async()=>null, exportXlsx: async()=>null,
        openExport: async()=>{}, openDocs: async()=>{}, close: async()=>{}, minimize: async()=>{}, maximize: async()=>{}, moveBy: async()=>{}
      };
      window.pywebview = { api };
    })();
    """.replace("__C__", c).replace("__I__", i)

def main():
    catalog = load_catalog()
    fails = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width":1280,"height":900})
        page.add_init_script(build_init_script(catalog))
        page.goto("file:///" + UI_INDEX.replace("\\","/"))

        page.wait_for_function("() => { const bd = document.getElementById('wz-backdrop'); return bd && !bd.hidden; }", timeout=20000)
        page.wait_for_timeout(2000)
        page.evaluate("() => { document.getElementById('wz-backdrop').hidden = true; if(typeof wzActive!=='undefined') wzActive=false; }")
        page.wait_for_timeout(500)
        page.click("#toggleSidebarBtn")
        page.wait_for_timeout(500)
        page.click('[data-bs-target="#pane-settings"]')
        page.wait_for_timeout(1500)
        page.wait_for_function("() => { const ta=document.getElementById('pipe-filter-t'); const w=ta.closest('.psdns-wrap'); const ov=w&&w.querySelector('.psdns-overlay'); return ov&&ov.style.display!=='none'; }", timeout=10000)
        page.wait_for_timeout(500)

        ta = page.locator("#pipe-filter-t")
        box = ta.bounding_box()

        def val():
            return page.evaluate("() => document.getElementById('pipe-filter-t').value")

        def report(step, action, expected, actual, ok):
            status = "OK" if ok else "BUG"
            print(f"  [{status}] {step}: {action}")
            if not ok:
                print(f"         expected: {expected!r}")
                print(f"         actual:   {actual!r}")
                fails.append(f"{step}: {action}")

        # ============================================================
        print("=== 1: Write from scratch ===")
        ta.click(position={"x": 100, "y": 20})
        page.wait_for_timeout(300)
        page.keyboard.type("com.android.deskclock", delay=50)
        page.wait_for_timeout(200)
        page.keyboard.press("Enter")
        page.wait_for_timeout(200)
        page.keyboard.type("com.vivo.calculator", delay=50)
        page.wait_for_timeout(200)
        page.keyboard.press("Enter")
        page.wait_for_timeout(200)
        v = val()
        report("1", "type 2 lines + Enter", "com.android.deskclock\ncom.vivo.calculator\n", v, v == "com.android.deskclock\ncom.vivo.calculator\n")
        print()

        # ============================================================
        print("=== 2: Click confirmed line, try to type ===")
        ta.click(position={"x": 50, "y": 10})
        page.wait_for_timeout(300)
        page.keyboard.type("X", delay=50)
        page.wait_for_timeout(300)
        v = val()
        lines = v.split('\n')
        x_in_confirmed = any('X' in l and l != 'X' for l in lines[:-1])
        report("2", "type on confirmed line blocked", "X not in confirmed lines", v, not x_in_confirmed)
        print()

        # ============================================================
        print("=== 3: Dblclick confirmed line -> edit mode ===")
        ta.dblclick(position={"x": 50, "y": 10})
        page.wait_for_timeout(500)
        edit_line = page.evaluate("() => document.getElementById('pipe-filter-t')._psdnsEditLine")
        color = page.evaluate("() => document.getElementById('pipe-filter-t').style.color")
        report("3a", "dblclick enters edit mode", "editLine=0", f"editLine={edit_line}", edit_line == 0)
        report("3b", "text visible in edit mode", "color not transparent", color, color != 'transparent')
        print()

        # ============================================================
        print("=== 4: Edit + Enter (confirm) ===")
        page.keyboard.press("Control+a")
        page.wait_for_timeout(100)
        page.keyboard.type("com.vivo.camera", delay=50)
        page.wait_for_timeout(200)
        page.keyboard.press("Enter")
        page.wait_for_timeout(300)
        v = val()
        edit_line2 = page.evaluate("() => document.getElementById('pipe-filter-t')._psdnsEditLine")
        report("4a", "edit confirmed", "com.vivo.camera in value", v, "com.vivo.camera" in v)
        report("4b", "edit mode exited", "editLine=None", f"editLine={edit_line2}", edit_line2 is None)
        print()

        # ============================================================
        print("=== 5: Dblclick + Escape (restore) ===")
        ta.dblclick(position={"x": 50, "y": 10})
        page.wait_for_timeout(500)
        edit_line = page.evaluate("() => document.getElementById('pipe-filter-t')._psdnsEditLine")
        if edit_line is not None:
            original = page.evaluate("() => document.getElementById('pipe-filter-t')._psdnsEditOriginal")
            page.keyboard.press("Control+a")
            page.wait_for_timeout(100)
            page.keyboard.type("HACKED", delay=50)
            page.wait_for_timeout(200)
            page.keyboard.press("Escape")
            page.wait_for_timeout(300)
            v = val()
            lines = v.split('\n')
            report("5", "Escape restores", original, lines[0] if lines else "", lines[0] == original)
        else:
            report("5", "FAIL (edit mode not entered)", "editLine=0", f"editLine={edit_line}", False)
        print()

        # ============================================================
        print("=== 6: THE MISSING CASE: dblclick -> click outside -> type again ===")
        ta.dblclick(position={"x": 50, "y": 10})
        page.wait_for_timeout(500)
        edit_line = page.evaluate("() => document.getElementById('pipe-filter-t')._psdnsEditLine")
        print(f"         editLine after dblclick: {edit_line}")
        # Click OUTSIDE the textarea (on the "Target" label)
        page.mouse.click(200, box["y"] - 30)
        page.wait_for_timeout(500)
        edit_line2 = page.evaluate("() => document.getElementById('pipe-filter-t')._psdnsEditLine")
        print(f"         editLine after click outside: {edit_line2}")
        # Click back on the LAST line of the textarea
        ta.click(position={"x": 100, "y": box["height"] - 5})
        page.wait_for_timeout(300)
        # Try to type
        page.keyboard.type("com.vivo.feedback", delay=50)
        page.wait_for_timeout(300)
        v = val()
        report("6", "can type after clicking outside", "com.vivo.feedback in value", v, "com.vivo.feedback" in v)
        print()

        # ============================================================
        print("=== 7: Backspace on empty last line deletes previous ===")
        ta.click(position={"x": 100, "y": box["height"] - 5})
        page.wait_for_timeout(300)
        # Ensure we're on an empty last line: press Enter to create one
        page.keyboard.press("Enter")
        page.wait_for_timeout(200)
        v_before = val()
        lines_before = [l for l in v_before.split('\n') if l.strip()]
        page.keyboard.press("Backspace")
        page.wait_for_timeout(300)
        v_after = val()
        lines_after = [l for l in v_after.split('\n') if l.strip()]
        report("7", "Backspace on empty line deletes previous", f"{len(lines_before)-1} lines", f"{len(lines_after)} lines", len(lines_after) == len(lines_before) - 1)
        print()

        # ============================================================
        print("=== 8: Backspace on active line with text ===")
        ta.click(position={"x": 100, "y": box["height"] - 5})
        page.wait_for_timeout(200)
        page.keyboard.type("abc", delay=50)
        page.wait_for_timeout(200)
        v_before = val()
        page.keyboard.press("Backspace")
        page.wait_for_timeout(200)
        v_after = val()
        report("8", "Backspace deletes char", v_before[:-1], v_after, v_after == v_before[:-1])
        print()

        # ============================================================
        print("=== 8b: Arrow keys cannot navigate to confirmed lines ===")
        # Ensure cursor is at end (last line)
        ta.click(position={"x": 100, "y": box["height"] - 5})
        page.wait_for_timeout(200)
        # Press ArrowUp (should be blocked - stays on last line)
        page.keyboard.press("ArrowUp")
        page.wait_for_timeout(200)
        sel = page.evaluate("() => document.getElementById('pipe-filter-t').selectionStart")
        vlen = page.evaluate("() => document.getElementById('pipe-filter-t').value.length")
        line_idx = page.evaluate("() => document.getElementById('pipe-filter-t').value.substring(0, document.getElementById('pipe-filter-t').selectionStart).split('\\n').length - 1")
        last_idx = page.evaluate("() => document.getElementById('pipe-filter-t').value.split('\\n').length - 1")
        report("8b", "ArrowUp blocked on last line", f"lineIdx==lastIdx ({last_idx})", f"lineIdx={line_idx}", line_idx == last_idx)
        print()

        # ============================================================
        print("=== 9: PSDNS off -> type anywhere ===")
        page.click("#psdns-enabled")
        page.wait_for_timeout(500)
        ta.click(position={"x": 50, "y": 10})
        page.wait_for_timeout(200)
        v_before = val()
        page.keyboard.type("X", delay=50)
        page.wait_for_timeout(200)
        v_after = val()
        color = page.evaluate("() => document.getElementById('pipe-filter-t').style.color")
        report("9a", "PSDNS off: type on confirmed line", "X inserted", v_after, v_after != v_before)
        report("9b", "PSDNS off: text visible", "color not transparent", color, color != 'transparent')
        print()

        browser.close()

    print(f"\n{'='*60}")
    print(f"RESULTS: {len(fails)} BUGS FOUND")
    if fails:
        for f in fails:
            print(f"  BUG: {f}")
    else:
        print("  ALL TESTS PASSED")
    print(f"{'='*60}")
    return len(fails)

if __name__ == "__main__":
    sys.exit(main())
