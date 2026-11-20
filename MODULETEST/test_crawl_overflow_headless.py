# -*- coding: utf-8 -*-
r"""
Headless measurement of the CRAWL tab layout.

Goal: reproduce the "second node breaks the UI" bug by rendering a crawl node
with a LONG resourceName (no spaces) and measuring the real box dimensions of
every element in the chain, detecting horizontal overflow (scrollWidth > clientWidth).

Run:
    .\plk.bat MODULETEST\test_crawl_overflow_headless.py
"""
import json
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UI_INDEX = os.path.join(BASE, "UI", "index.html")
OUT_DIR = os.path.join(BASE, "MODULETEST")

# A node that mimics the "second node": long resourceName without spaces.
LONG_RES = "com.android.settings:id/originui_vtoolbar_navigation_view_btn_rom14_0"

NODE = {
    "pkg": "com.android.settings",
    "node_id": "0.3",
    "depth": 1,
    "screenshots": ["shot_0001.png"],
    "clickables": [
        {"text": "Wi-Fi", "resourceName": LONG_RES, "className": "android.widget.TextView"},
        {"text": "Preferencias de red", "resourceName": LONG_RES, "className": "android.widget.TextView"},
        {"text": "Consumo de datos Wi-Fi", "resourceName": LONG_RES, "className": "android.widget.TextView"},
        {"text": "Otro elemento largo", "resourceName": LONG_RES, "className": "android.widget.TextView"},
    ],
}

INIT_SCRIPT = r"""
(function () {
  const node = __NODE__;
  const api = {
    loadConfig: async () => null,
    saveConfig: async () => true,
    getRecentProjects: async () => [],
    removeRecentProject: async () => true,
    getCurrentProject: async () => null,
    openProject: async () => ({ ok: false }),
    getDeviceInfo: async () => ({ connected: true, release: "14", build_id: "TEST" }),
    refreshPsdns: async () => ({ ok: true, serial: "T", catalog: {}, installed: [], catalogPackages: 0 }),
    updatePsdns: async () => ({ ok: false, error: "x" }),
    getRunState: async () => null,
    getPipelineState: async () => ({ status: "running" }),
    getQaReport: async () => null,
    getCrawlLatest: async () => ({ ok: true, node: node }),
    getImageData: async () => null,
    startPipeline: async () => ({ ok: true }),
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
""".replace("__NODE__", json.dumps(NODE, ensure_ascii=False))

MEASURE = r"""
() => {
  const sel = [
    '#run-console',
    '#run-pane-crawl',
    '.run-crawl-view',
    '.run-crawl-shot',
    '.run-crawl-nodes',
    '.run-crawl-list',
    '.run-crawl-item',
    '.run-crawl-res',
    '#right-col',
    '.sidebar-main',
    '.app-root .row'
  ];
  const out = {};
  for (const s of sel) {
    const el = document.querySelector(s);
    if (!el) { out[s] = { present: false }; continue; }
    const r = el.getBoundingClientRect();
    out[s] = {
      present: true,
      clientW: el.clientWidth,
      scrollW: el.scrollWidth,
      offsetW: el.offsetWidth,
      rectW: Math.round(r.width),
      rectH: Math.round(r.height),
      overflowX: el.scrollWidth > el.clientWidth + 1,
      display: getComputedStyle(el).display,
      overflowX_css: getComputedStyle(el).overflowX,
      overflowY_css: getComputedStyle(el).overflowY
    };
  }
  // document-level overflow
  out.__doc = {
    docScrollW: document.documentElement.scrollWidth,
    docClientW: document.documentElement.clientWidth,
    bodyScrollW: document.body.scrollWidth,
    bodyClientW: document.body.clientWidth,
    docOverflow: document.documentElement.scrollWidth > document.documentElement.clientWidth + 1
  };
  return out;
}
"""


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    print("[test] index:", UI_INDEX)

    from playwright.sync_api import sync_playwright

    console_msgs = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        page.on("console", lambda m: console_msgs.append(f"[{m.type}] {m.text}"))
        page.on("pageerror", lambda e: console_msgs.append(f"[pageerror] {e}"))
        page.add_init_script(INIT_SCRIPT)

        page.goto("file:///" + UI_INDEX.replace("\\", "/"))
        page.wait_for_timeout(1500)

        # Navigate to the test pane (click the play nav button).
        page.evaluate("() => { const b = document.querySelector('.nav-btn[data-bs-target=\"#pane-test\"]'); if (b) b.click(); }")
        page.wait_for_timeout(500)

        # Trigger crawl active: switches tab + starts poll -> runCrawlRefresh -> renders node.
        page.evaluate("() => { if (window.onPipelineStep) window.onPipelineStep('crawl', 'active'); }")
        page.wait_for_timeout(1500)

        # Confirm the crawl pane is active and rendered.
        state = page.evaluate(
            """
            () => {
              const pane = document.getElementById('run-pane-crawl');
              return {
                paneActive: !!(pane && pane.classList.contains('active')),
                paneHTMLlen: pane ? pane.innerHTML.length : -1,
                hasView: !!(pane && pane.querySelector('.run-crawl-view')),
                itemCount: pane ? pane.querySelectorAll('.run-crawl-item').length : 0
              };
            }
            """
        )
        print("[test] crawl pane state:", json.dumps(state))

        m = page.evaluate(MEASURE)
        shot = os.path.join(OUT_DIR, "crawl_overflow.png")
        page.screenshot(path=shot)

        browser.close()

    summary = {"measure": m, "console": console_msgs[-40:]}
    out_json = os.path.join(OUT_DIR, "crawl_overflow_summary.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print("\n================ MEASURE ================")
    print(json.dumps(m, ensure_ascii=False, indent=2))
    print("\n[screenshot]", shot)
    print("[json]", out_json)


if __name__ == "__main__":
    main()
