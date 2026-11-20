import builtins
import time
import sys
import traceback

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

_orig = builtins.print

def print(*args, **kwargs):
    ts = f"[{time.strftime('%H:%M:%S')}] "
    text = " ".join(str(a) for a in args)
    lines = text.split("\n")
    _orig("\n".join(ts + line if line else line for line in lines), **kwargs)

def _excepthook(exc_type, exc_value, exc_tb):
    try:
        with open("crash.log", "w", encoding="utf-8") as f:
            f.write("".join(traceback.format_exception(exc_type, exc_value, exc_tb)))
        _orig("FATAL ERROR - see crash.log")
    except:
        pass

sys.excepthook = _excepthook
builtins.print = print