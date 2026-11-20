# -*- coding: utf-8 -*-
"""
PSDNS edit rules test — each test is fully isolated.
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
        page.evaluate("() => { document.querySelector('[data-bs-target=\"#pane-settings\"]').click(); }")
        page.wait_for_timeout(1500)
        page.wait_for_function("() => { const ta=document.getElementById('pipe-filter-t'); const w=ta.closest('.psdns-wrap'); const ov=w&&w.querySelector('.psdns-overlay'); return ov&&ov.style.display!=='none'; }", timeout=10000)
        page.wait_for_timeout(500)

        def reset(value):
            page.evaluate(f"""() => {{
                const ta = document.getElementById('pipe-filter-t');
                ta._psdnsEditLine = null;
                ta._psdnsEditOriginal = null;
                ta._psdnsLastBackspace = false;
                ta.value = {json.dumps(value)};
                ta.dispatchEvent(new Event('input', {{bubbles:true}}));
            }}""")
            page.wait_for_timeout(200)

        def val():
            return page.evaluate("() => document.getElementById('pipe-filter-t').value")

        def report(step, action, expected, actual, ok):
            status = "OK" if ok else "BUG"
            print(f"  [{status}] {step}: {action}")
            if not ok:
                print(f"         expected: {expected!r}")
                print(f"         actual:   {actual!r}")
                fails.append(f"{step}: {action}")

        ta = page.locator("#pipe-filter-t")
        box = ta.bounding_box()

        # ============================================================
        print("=== TEST 1: Type on last line + Enter ===")
        reset("com.android.deskclock\ncom.vivo.calculator\n")
        ta.click(position={"x": box["width"]-20, "y": box["height"]-10})
        page.wait_for_timeout(100)
        page.keyboard.type("com.vivo.imanager")
        page.wait_for_timeout(100)
        page.keyboard.press("Enter")
        page.wait_for_timeout(100)
        v = val()
        report("1", "type+Enter confirms line", "com.vivo.imanager\n", v, v == "com.android.deskclock\ncom.vivo.calculator\ncom.vivo.imanager\n")
        print()

        # ============================================================
        print("=== TEST 2: Click confirmed line -> cursor snaps to end ===")
        reset("com.android.deskclock\ncom.vivo.calculator\n")
        ta.click(position={"x": 30, "y": 8})
        page.wait_for_timeout(100)
        sel = page.evaluate("() => document.getElementById('pipe-filter-t').selectionStart")
        vlen = page.evaluate("() => document.getElementById('pipe-filter-t').value.length")
        report("2", "click on confirmed line snaps cursor to end", f"sel==len ({vlen})", f"sel={sel}", sel == vlen)
        print()

        # ============================================================
        print("=== TEST 3: Dblclick confirmed line -> edit mode ===")
        reset("com.android.deskclock\ncom.vivo.calculator\n")
        ta.dblclick(position={"x": 30, "y": 8})
        page.wait_for_timeout(200)
        edit_line = page.evaluate("() => document.getElementById('pipe-filter-t')._psdnsEditLine")
        color = page.evaluate("() => document.getElementById('pipe-filter-t').style.color")
        report("3a", "dblclick enters edit mode on line 0", "editLine=0", f"editLine={edit_line}", edit_line == 0)
        report("3b", "text visible in edit mode", "color=''", f"color={color!r}", color == "")
        print()

        # ============================================================
        print("=== TEST 4: Edit line + Enter confirms ===")
        reset("com.android.deskclock\ncom.vivo.calculator\n")
        ta.dblclick(position={"x": 30, "y": 8})
        page.wait_for_timeout(200)
        page.evaluate("""() => {
            const ta = document.getElementById('pipe-filter-t');
            const lines = ta.value.split('\\n');
            const idx = ta._psdnsEditLine;
            const start = lines.slice(0,idx).join('\\n').length + (idx>0?1:0);
            ta.setSelectionRange(start, start + lines[idx].length);
        }""")
        page.wait_for_timeout(100)
        page.keyboard.type("com.vivo.camera")
        page.wait_for_timeout(100)
        page.keyboard.press("Enter")
        page.wait_for_timeout(100)
        v = val()
        edit_line = page.evaluate("() => document.getElementById('pipe-filter-t')._psdnsEditLine")
        report("4a", "line updated", "com.vivo.camera in value", v, "com.vivo.camera" in v)
        report("4b", "edit mode exited", "editLine=None", f"editLine={edit_line}", edit_line is None)
        print()

        # ============================================================
        print("=== TEST 5: Escape in edit mode restores ===")
        reset("com.android.deskclock\ncom.vivo.calculator\n")
        ta.dblclick(position={"x": 30, "y": 8})
        page.wait_for_timeout(200)
        original = page.evaluate("() => document.getElementById('pipe-filter-t')._psdnsEditOriginal")
        page.evaluate("""() => {
            const ta = document.getElementById('pipe-filter-t');
            const lines = ta.value.split('\\n');
            const idx = ta._psdnsEditLine;
            const start = lines.slice(0,idx).join('\\n').length + (idx>0?1:0);
            ta.setSelectionRange(start, start + lines[idx].length);
        }""")
        page.wait_for_timeout(100)
        page.keyboard.type("HACKED")
        page.wait_for_timeout(100)
        page.keyboard.press("Escape")
        page.wait_for_timeout(100)
        v = val()
        lines = v.split('\n')
        report("5", "Escape restores original", original, lines[0] if lines else "", lines[0] == original)
        print()

        # ============================================================
        print("=== TEST 6: Double Backspace on empty last line ===")
        reset("com.android.deskclock\ncom.vivo.calculator\n")
        page.evaluate("() => { const ta=document.getElementById('pipe-filter-t'); ta.focus(); ta.setSelectionRange(ta.value.length, ta.value.length); }")
        page.wait_for_timeout(100)
        v_before = val()
        page.keyboard.press("Backspace")
        page.wait_for_timeout(100)
        v_mid = val()
        report("6a", "single Backspace on empty line does nothing", v_before, v_mid, v_before == v_mid)
        page.keyboard.press("Backspace")
        page.wait_for_timeout(100)
        v_after = val()
        lines_before = [l for l in v_before.split('\n') if l.strip()]
        lines_after = [l for l in v_after.split('\n') if l.strip()]
        report("6b", "double Backspace deletes previous line", f"{len(lines_before)-1} lines", f"{len(lines_after)} lines", len(lines_after) == len(lines_before) - 1)
        print()

        # ============================================================
        print("=== TEST 7: Backspace on non-empty last line deletes char ===")
        reset("com.android.deskclock\ncom.vivo.calculator\nabc")
        page.evaluate("() => { const ta=document.getElementById('pipe-filter-t'); ta.focus(); ta.setSelectionRange(ta.value.length, ta.value.length); }")
        page.wait_for_timeout(100)
        v_before = val()
        page.keyboard.press("Backspace")
        page.wait_for_timeout(100)
        v_after = val()
        report("7", "Backspace deletes char", v_before[:-1], v_after, v_after == v_before[:-1])
        print()

        # ============================================================
        print("=== TEST 8: Ctrl+A + type doesn't corrupt confirmed lines ===")
        reset("com.android.deskclock\ncom.vivo.calculator\n")
        ta.click()
        page.keyboard.press("Control+a")
        page.wait_for_timeout(100)
        page.keyboard.type("ZZZ")
        page.wait_for_timeout(100)
        v = val()
        report("8", "Ctrl+A+type preserves confirmed lines", "com.android.deskclock in value", v, "com.android.deskclock" in v)
        print()

        # ============================================================
        print("=== TEST 9: Paste on confirmed line blocked ===")
        reset("com.android.deskclock\ncom.vivo.calculator\n")
        ta.click(position={"x": 30, "y": 8})
        page.wait_for_timeout(100)
        v_before = val()
        page.evaluate("""() => {
            const ta = document.getElementById('pipe-filter-t');
            const dt = new DataTransfer();
            dt.setData('text/plain', 'PASTED');
            const ev = new ClipboardEvent('paste', {clipboardData: dt, bubbles: true, cancelable: true});
            ta.dispatchEvent(ev);
        }""")
        page.wait_for_timeout(100)
        v_after = val()
        report("9", "paste on confirmed line blocked", v_before, v_after, v_before == v_after)
        print()

        # ============================================================
        print("=== TEST 10: PSDNS off = normal textarea ===")
        page.evaluate("() => { const cb=document.getElementById('psdns-enabled'); cb.checked=false; cb.dispatchEvent(new Event('change',{bubbles:true})); }")
        page.wait_for_timeout(200)
        reset("hello\nworld")
        ta.click(position={"x": 30, "y": 8})
        page.wait_for_timeout(100)
        v_before = val()
        page.keyboard.type("X")
        page.wait_for_timeout(100)
        v_after = val()
        report("10", "PSDNS off: typing anywhere works", "X inserted", v_after, v_after != v_before and "X" in v_after)
        color = page.evaluate("() => document.getElementById('pipe-filter-t').style.color")
        report("10b", "PSDNS off: text visible", "color=''", f"color={color!r}", color == "")
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
