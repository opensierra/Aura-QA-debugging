"""
DUT configuration module (extracted from GUI Assisted Mapping panel).
Provides device checks and configuration via adb shell.
"""
import os
import subprocess
import time

_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0

DC_MAX_ATTEMPTS = 3
DC_ADB_TIMEOUT = 10
DC_TARGET_SERIAL = os.environ.get("ANDROID_SERIAL") or None


class DeviceError(RuntimeError):
    pass


def _run(cmd, timeout=5):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                          creationflags=_NO_WINDOW)


def _dc_numeric_equal(value, target):
    try:
        return float(value) == float(target)
    except (ValueError, TypeError):
        return False


def _dc_positive_integer(value):
    try:
        return int(value) > 0
    except (ValueError, TypeError):
        return False


def _dc_timeout_ok(value):
    try:
        return int(value) >= 600000
    except (ValueError, TypeError):
        return False


DC_CHECKS = [
    {"id": "usbDebug", "label": "USB Debugging", "namespace": "global", "key": "adb_enabled",
     "expect": lambda v: v == "1", "tip": "dc.tip.usbDebug",
     "apply": None, "reset": None, "target": "1"},
    {"id": "stayOn", "label": "Stay on while plugged in", "namespace": "global", "key": "stay_on_while_plugged_in",
     "expect": _dc_positive_integer, "tip": "dc.tip.stayOn",
     "apply": "7", "reset": "0", "target": "7"},
    {"id": "screenTimeout", "label": "Screen timeout", "namespace": "system", "key": "screen_off_timeout",
     "expect": _dc_timeout_ok, "tip": "dc.tip.screenTimeout",
     "apply": "2147483647", "reset": "300000", "target": "2147483647"},
    {"id": "rotationLocked", "label": "Rotation locked", "namespace": "system", "key": "accelerometer_rotation",
     "expect": lambda v: v == "0", "tip": "dc.tip.rotationLocked",
     "apply": "0", "reset": "1", "target": "0"},
    {"id": "showTouches", "label": "Show touches", "namespace": "system", "key": "show_touches",
     "expect": lambda v: v == "1", "tip": "dc.tip.showTouches",
     "apply": "1", "reset": "0", "target": "1"},
    {"id": "windowAnim", "label": "Window animations", "namespace": "global", "key": "window_animation_scale",
     "expect": lambda v: _dc_numeric_equal(v, 0), "tip": "dc.tip.windowAnim",
     "apply": "0", "reset": "1", "target": "0"},
    {"id": "transitionAnim", "label": "Transition animations", "namespace": "global", "key": "transition_animation_scale",
     "expect": lambda v: _dc_numeric_equal(v, 0), "tip": "dc.tip.transitionAnim",
     "apply": "0", "reset": "1", "target": "0"},
    {"id": "animatorScale", "label": "Animator duration", "namespace": "global", "key": "animator_duration_scale",
     "expect": lambda v: _dc_numeric_equal(v, 0), "tip": "dc.tip.animatorScale",
     "apply": "0", "reset": "1", "target": "0"},
]


def _dc_run_adb(args, serial=None, timeout=DC_ADB_TIMEOUT):
    cmd = ["adb"] + (["-s", serial] if serial else []) + args
    try:
        r = _run(cmd, timeout=timeout)
        return {"ok": r.returncode == 0, "returncode": r.returncode,
                "stdout": r.stdout.strip(), "stderr": r.stderr.strip(), "command": cmd}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"ok": False, "returncode": None, "stdout": "", "stderr": str(exc), "command": cmd}


def _dc_run_shell(serial, args, log=None):
    result = _dc_run_adb(["shell"] + args, serial=serial)
    if log is not None:
        log.append(result)
    return result


def _dc_get_device():
    result = _dc_run_adb(["devices"])
    if not result["ok"]:
        raise DeviceError(result["stderr"] or result["stdout"] or "adb devices failed")
    devices = []
    for line in result["stdout"].splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[1] == "device":
            devices.append(parts[0])
    if DC_TARGET_SERIAL:
        if DC_TARGET_SERIAL not in devices:
            raise DeviceError("Configured device unavailable or unauthorized: %s" % DC_TARGET_SERIAL)
        return DC_TARGET_SERIAL
    if len(devices) > 1:
        raise DeviceError("Multiple devices connected. Set ANDROID_SERIAL.")
    return devices[0] if devices else None


def _dc_get_model(serial):
    result = _dc_run_shell(serial, ["getprop", "ro.product.model"])
    return result["stdout"] if result["ok"] else None


def _dc_get_current_user(serial):
    for args in (["am", "get-current-user"], ["cmd", "activity", "get-current-user"]):
        result = _dc_run_shell(serial, args)
        if result["ok"] and result["stdout"].isdigit():
            return result["stdout"]
    raise DeviceError("Could not resolve the active Android user. No changes were made.")


def _dc_setting_command(check, operation, user, value=None):
    args = ["settings"]
    if check["namespace"] != "global":
        args.extend(["--user", str(user)])
    args.extend([operation, check["namespace"], check["key"]])
    if value is not None:
        args.append(str(value))
    return args


def _dc_read_setting(serial, user, check, log=None):
    result = _dc_run_shell(serial, _dc_setting_command(check, "get", user), log)
    value = result["stdout"] if result["ok"] else None
    return value, result


def _dc_read_all_settings(serial, user):
    parts = []
    for check in DC_CHECKS:
        if check["namespace"] != "global":
            parts.append("settings --user %s get %s %s" % (user, check["namespace"], check["key"]))
        else:
            parts.append("settings get %s %s" % (check["namespace"], check["key"]))
    script = "; ".join(parts)
    cmd = ["adb"] + (["-s", serial] if serial else []) + ["shell", script]
    try:
        r = _run(cmd, timeout=DC_ADB_TIMEOUT)
        result = {"ok": r.returncode == 0, "returncode": r.returncode,
                  "stdout": r.stdout.strip(), "stderr": r.stderr.strip(), "command": cmd}
    except (OSError, subprocess.TimeoutExpired) as exc:
        result = {"ok": False, "returncode": None, "stdout": "", "stderr": str(exc), "command": cmd}
    lines = result["stdout"].splitlines() if result["ok"] else []
    values = {}
    for i, check in enumerate(DC_CHECKS):
        values[check["id"]] = lines[i].strip() if i < len(lines) else None
    return values, result


def get_checks(serial=None, user=None):
    if serial is None:
        serial = _dc_get_device()
    if serial and user is None:
        user = _dc_get_current_user(serial)
    checks = []
    values, result = ({}, None)
    if serial:
        values, result = _dc_read_all_settings(serial, user)
    for check in DC_CHECKS:
        value = values.get(check["id"])
        error = None
        if serial and not result["ok"]:
            error = result["stderr"] or result["stdout"] or "Could not read settings"
        checks.append({
            "id": check["id"], "label": check["label"], "value": value,
            "pass": check["expect"](value) if value is not None else None,
            "tip": check["tip"], "applicable": check["apply"] is not None,
            "error": error, "verification": "settings_readback",
            "target": check.get("target"),
        })
    return {
        "connected": bool(serial), "serial": serial,
        "model": _dc_get_model(serial) if serial else None,
        "user": user, "checks": checks,
    }


def _dc_detect_capabilities(serial):
    window_help = _dc_run_shell(serial, ["cmd", "window", "help"])
    power_help = _dc_run_shell(serial, ["svc", "power"])
    return {
        "window_user_rotation": window_help["ok"] and "user-rotation" in window_help["stdout"],
        "power_stayon": "stayon" in (power_help["stdout"] + "\n" + power_help["stderr"]),
    }


def _dc_expected_value(check, value, reset):
    if value is None:
        return False
    if not reset:
        return check["expect"](value)
    return _dc_numeric_equal(value, check["reset"])


def _dc_apply_service_route(serial, check, reset, capabilities, log):
    if check["id"] == "stayOn" and capabilities["power_stayon"]:
        _dc_run_shell(serial, ["svc", "power", "stayon", "false" if reset else "true"], log)
    if check["id"] == "rotationLocked" and capabilities["window_user_rotation"]:
        _dc_run_shell(serial, ["cmd", "window", "user-rotation", "free" if reset else "lock"], log)


def _dc_configure_one(serial, user, check, reset, capabilities):
    log = []
    before, _ = _dc_read_setting(serial, user, check, log)
    target = check["reset"] if reset else check["apply"]
    verified = False
    value = before
    attempt = 0
    for attempt in range(1, DC_MAX_ATTEMPTS + 1):
        _dc_run_shell(serial, _dc_setting_command(check, "put", user, target), log)
        _dc_apply_service_route(serial, check, reset, capabilities, log)
        time.sleep(0.25 * attempt)
        value, _ = _dc_read_setting(serial, user, check, log)
        if _dc_expected_value(check, value, reset):
            time.sleep(0.5)
            value, _ = _dc_read_setting(serial, user, check, log)
            if _dc_expected_value(check, value, reset):
                verified = True
                break
    return {
        "id": check["id"], "before": before, "target": target, "value": value,
        "ok": verified, "attempts": attempt, "verification": "settings_readback",
        "effect_verified": False, "log": log,
    }


def configure(reset=False):
    serial = _dc_get_device()
    if not serial:
        return {"ok": False, "msg": "No authorized device connected", "state": get_checks()}
    user = _dc_get_current_user(serial)
    capabilities = _dc_detect_capabilities(serial)
    results = []
    for check in DC_CHECKS:
        if check["apply"] is None:
            continue
        results.append(_dc_configure_one(serial, user, check, reset, capabilities))
    time.sleep(0.7)
    state = get_checks(serial=serial, user=user)
    final_values = {c["id"]: c["value"] for c in state["checks"]}
    specs = {c["id"]: c for c in DC_CHECKS}
    for result in results:
        check = specs[result["id"]]
        result["value"] = final_values[result["id"]]
        result["ok"] = _dc_expected_value(check, result["value"], reset)
    failed = [r["id"] for r in results if not r["ok"]]
    return {
        "ok": not failed,
        "msg": ("Preset values verified" if reset else "Requested settings verified")
               if not failed else "Some settings could not be verified",
        "operation": "reset" if reset else "apply",
        "verification": "settings_readback", "effect_verified": False,
        "failed": failed, "capabilities": capabilities, "results": results, "state": state,
    }
