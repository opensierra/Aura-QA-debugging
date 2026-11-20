# -*- coding: utf-8 -*-
import json
from pathlib import Path

dns = Path(__file__).resolve().parent.parent / "Customlib" / "psdns.json"
with open(dns, encoding="utf-8-sig") as f:
    data = json.load(f)
antes = len(data)
data.pop("com.vivo.appstore", None)
with open(dns, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4, sort_keys=True)
    f.write("\n")
print(f"Antes: {antes} -> Despues: {len(data)}")
