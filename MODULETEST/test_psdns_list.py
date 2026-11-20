# -*- coding: utf-8 -*-
"""
PSDNS 2-column list test. Interacts with .psdns-list inputs.
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
        page.evaluate("() => { if (typeof wzHide === 'function') wzHide(); else { document.getElementById('wz-backdrop').hidden = true; if(typeof wzActive!=='undefined') wzActive=false; } }")
        page.wait_for_timeout(500)
        page.click("#toggleSidebarBtn")
        page.wait_for_timeout(500)
        page.click('[data-bs-target="#pane-settings"]')
        page.wait_for_timeout(1500)
        page.wait_for_function("() => { const ta=document.getElementById('pipe-filter-t'); const w=ta.closest('.psdns-wrap'); const l=w&&w.querySelector('.psdns-list'); return l&&getComputedStyle(l).display!=='none'; }", timeout=10000)
        page.wait_for_timeout(500)

        def val():
            return page.evaluate("() => document.getElementById('pipe-filter-t').value")

        WRAP = "#pipe-filter-t"
        def wrap_list():
            return page.locator(WRAP).locator("xpath=ancestor::div[contains(@class,'psdns-wrap')]")
        def rows():
            return wrap_list().locator(".psdns-row")
        def last_input():
            return wrap_list().locator(".psdns-list .psdns-row:last-child .psdns-input")

        def report(step, action, expected, actual, ok):
            status = "OK" if ok else "BUG"
            print(f"  [{status}] {step}: {action}")
            if not ok:
                print(f"         expected: {expected!r}")
                print(f"         actual:   {actual!r}")
                fails.append(f"{step}: {action}")

        # ============================================================
        print("=== 1: Type in active line + Enter ===")
        li = last_input()
        li.click()
        page.wait_for_timeout(200)
        page.keyboard.type("com.android.deskclock", delay=30)
        page.wait_for_timeout(100)
        page.keyboard.press("Enter")
        page.wait_for_timeout(200)
        page.keyboard.type("com.vivo.calculator", delay=30)
        page.wait_for_timeout(100)
        page.keyboard.press("Enter")
        page.wait_for_timeout(200)
        v = val()
        lines = [l for l in v.split('\n') if l.strip()]
        report("1", "type 2 lines + Enter", ["com.android.deskclock","com.vivo.calculator"], lines, lines == ["com.android.deskclock","com.vivo.calculator"])
        print()

        # ============================================================
        print("=== 2: Name column shows label ===")
        name0 = page.evaluate("() => { const ta=document.getElementById('pipe-filter-t'); const l=ta.closest('.psdns-wrap').querySelector('.psdns-list'); const r=l.querySelector('.psdns-row'); return r?r.querySelector('.psdns-name').textContent:''; }")
        report("2", "name column shows label", "Clock", name0, name0 == "Clock")
        print()

        # ============================================================
        print("=== 3: Dblclick confirmed line -> edit mode ===")
        row0 = rows().first
        row0.dblclick()
        page.wait_for_timeout(300)
        editing = page.evaluate("() => { const ta=document.getElementById('pipe-filter-t'); const l=ta.closest('.psdns-wrap').querySelector('.psdns-list'); const r=l.querySelector('.psdns-row'); return r?r.classList.contains('psdns-row-edit'):false; }")
        inp_disabled = page.evaluate("() => { const ta=document.getElementById('pipe-filter-t'); const l=ta.closest('.psdns-wrap').querySelector('.psdns-list'); const r=l.querySelector('.psdns-row'); const i=r?r.querySelector('.psdns-input'):null; return i?i.disabled:true; }")
        report("3a", "row highlighted in edit mode", "true", f"{editing}", editing)
        report("3b", "input enabled in edit mode", "false", f"{inp_disabled}", not inp_disabled)
        print()

        # ============================================================
        print("=== 4: Edit line + Enter (confirm) ===")
        inp0 = rows().first.locator(".psdns-input")
        inp0.click()
        page.keyboard.press("Control+a")
        page.wait_for_timeout(100)
        page.keyboard.type("com.vivo.camera", delay=30)
        page.wait_for_timeout(100)
        page.keyboard.press("Enter")
        page.wait_for_timeout(300)
        v = val()
        lines = [l for l in v.split('\n') if l.strip()]
        report("4", "edit confirmed", "com.vivo.camera in lines", lines, "com.vivo.camera" in lines)
        print()

        # ============================================================
        print("=== 5: Edit line, clear, Enter -> line deleted ===")
        row0 = rows().first
        row0.dblclick()
        page.wait_for_timeout(300)
        inp0 = rows().first.locator(".psdns-input")
        inp0.click()
        page.keyboard.press("Control+a")
        page.wait_for_timeout(100)
        page.keyboard.press("Delete")
        page.wait_for_timeout(100)
        page.keyboard.press("Enter")
        page.wait_for_timeout(300)
        v = val()
        lines = [l for l in v.split('\n') if l.strip()]
        report("5", "clear+Enter deletes line", "com.vivo.camera NOT in lines", lines, "com.vivo.camera" not in lines)
        print()

        # ============================================================
        print("=== 6: Trash icon + confirm popup deletes line ===")
        row0 = rows().first
        row0.hover()
        page.wait_for_timeout(200)
        trash = rows().first.locator(".psdns-trash")
        trash.click()
        page.wait_for_timeout(500)
        popup_visible = page.evaluate("() => { const bd=document.querySelector('.popup-backdrop'); return bd && !bd.hidden; }")
        report("6a", "confirm popup appears", "true", f"{popup_visible}", popup_visible)
        page.click(".popup-backdrop .popup-btn-danger")
        page.wait_for_timeout(500)
        v = val()
        lines = [l for l in v.split('\n') if l.strip()]
        report("6b", "line deleted after confirm", "0 lines left", f"{len(lines)} lines", len(lines) == 0)
        print()

        # ============================================================
        print("=== 7: Trash icon + Cancel keeps line ===")
        li = last_input()
        li.click()
        page.wait_for_timeout(200)
        page.keyboard.type("com.vivo.imanager", delay=30)
        page.wait_for_timeout(100)
        page.keyboard.press("Enter")
        page.wait_for_timeout(300)
        row0 = rows().first
        row0.hover()
        page.wait_for_timeout(200)
        trash = rows().first.locator(".psdns-trash")
        trash.click()
        page.wait_for_timeout(500)
        page.click(".popup-backdrop .popup-btn-ghost")
        page.wait_for_timeout(500)
        v = val()
        lines = [l for l in v.split('\n') if l.strip()]
        report("7", "cancel keeps line", "1 line still there", f"{len(lines)} lines", len(lines) == 1)
        print()

        # ============================================================
        print("=== 8: Unknown package shows warning in name column ===")
        li = last_input()
        li.click()
        page.wait_for_timeout(200)
        page.keyboard.type("com.unknown.pkg", delay=30)
        page.wait_for_timeout(100)
        page.keyboard.press("Enter")
        page.wait_for_timeout(300)
        warn = page.evaluate("() => { const ta=document.getElementById('pipe-filter-t'); const l=ta.closest('.psdns-wrap').querySelector('.psdns-list'); const rows=l.querySelectorAll('.psdns-row'); for(const r of rows){ const i=r.querySelector('.psdns-input'); if(i&&i.value==='com.unknown.pkg'){ const n=r.querySelector('.psdns-name'); return n?n.textContent:''; } } return 'NOTFOUND'; }")
        report("8", "warning in name column", "contains 'not indexed'", warn, "not indexed" in warn)
        print()

        # ============================================================
        print("=== 9: PSDNS off -> list stays, name hidden, warn moves ===")
        page.click("#psdns-enabled")
        page.wait_for_timeout(500)
        list_display = page.evaluate("() => { const ta=document.getElementById('pipe-filter-t'); const l=ta.closest('.psdns-wrap').querySelector('.psdns-list'); return l?getComputedStyle(l).display:'none'; }")
        ta_display = page.evaluate("() => { const ta=document.getElementById('pipe-filter-t'); return getComputedStyle(ta).display; }")
        no_name = page.evaluate("() => { const ta=document.getElementById('pipe-filter-t'); const l=ta.closest('.psdns-wrap').querySelector('.psdns-list'); return l?l.classList.contains('no-name'):false; }")
        report("9a", "list still visible when off", "block", list_display, list_display == "block")
        report("9b", "textarea still hidden when off", "none", ta_display, ta_display == "none")
        report("9c", "no-name class applied", "true", f"{no_name}", no_name)
        warn_pos = page.evaluate("() => { const ta=document.getElementById('pipe-filter-t'); const l=ta.closest('.psdns-wrap').querySelector('.psdns-list'); const rows=l.querySelectorAll('.psdns-row'); for(const r of rows){ const i=r.querySelector('.psdns-input'); if(i&&i.value==='com.unknown.pkg'){ const w=r.querySelector('.psdns-warn'); if(!w) return 'NO_WARN'; const name=r.querySelector('.psdns-name'); const nameHasWarn=name&&name.querySelector('.psdns-warn-inline'); return nameHasWarn?'IN_NAME':'AFTER_INPUT'; } } return 'NOTFOUND'; }")
        report("9d", "warning after input (not in name)", "AFTER_INPUT", warn_pos, warn_pos == "AFTER_INPUT")
        print()

        # Re-enable
        page.click("#psdns-enabled")
        page.wait_for_timeout(300)

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
