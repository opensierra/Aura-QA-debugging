# -*- coding: utf-8 -*-
"""
Generate and update psdns.json.

Catalog structure:
    package -> language -> list of observed display names.

Association validation:
    - Installed, catalogued packages validate their associations.
    - Installed, unknown packages are extracted directly.
    - Names are checked against their known installed packages.
    - Absent, catalogued packages are checked through their known names.
    - Missing associations trigger a DUT discovery scan.

Only observed package/name relationships are stored.
No labels are copied from one package to another.

An update is additive:
    Existing names and packages are not removed.
"""
import json
import shutil
import subprocess
import tempfile
import time
from datetime import datetime
from pathlib import Path

from androguard.core.apk import APK
from loguru import logger


logger.disable("androguard")

# Optional log callback (set by the GUI integration layer).
# Signature: callback(message: str) -> None
_log_callback = None


def set_log_callback(callback):
    """Register a callback invoked for every log line. None to clear."""
    global _log_callback
    _log_callback = callback


def _log(message):
    stamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{stamp}] {message}", flush=True)
    if _log_callback is not None:
        try:
            _log_callback(message)
        except Exception:
            pass


def _run(args):
    result = subprocess.run(
        args,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(detail or "Command failed.")

    return result.stdout.strip()


def _prepare_adb(serial=None):
    local = Path(__file__).resolve().parent / "adb.exe"
    adb = str(local) if local.is_file() else shutil.which("adb")

    if not adb:
        raise FileNotFoundError(
            "ADB not found next to the module nor in PATH."
        )

    _log("Checking Android devices...")
    output = _run([adb, "devices"])
    devices = {}

    for line in output.splitlines():
        parts = line.split()

        if len(parts) >= 2 and parts[0] != "List":
            devices[parts[0]] = parts[1]

    if serial is not None:
        if devices.get(serial) != "device":
            raise RuntimeError(
                f"Device {serial} is not available. "
                f"State: {devices.get(serial, 'not detected')}"
            )
    else:
        available = [
            identifier
            for identifier, state in devices.items()
            if state == "device"
        ]

        if not available:
            raise RuntimeError(
                f"No available Android devices. States: {devices}"
            )

        if len(available) > 1:
            raise RuntimeError(
                "Multiple devices found. Provide serial."
            )

        serial = available[0]

    _log(f"Selected device: {serial}")
    return [adb, "-s", serial]


def _normalize_list(values, name):
    if isinstance(values, str):
        raise TypeError(f"{name} must be a list, not a string.")

    result = []
    seen = set()

    for value in values:
        if not isinstance(value, str):
            raise TypeError(f"All items in {name} must be strings.")

        value = value.strip()

        if value and value not in seen:
            seen.add(value)
            result.append(value)

    return result


def _normalize_name(value):
    return " ".join(value.split()).casefold()


def _normalize_language(value):
    value = value.replace("\x00", "").strip()

    if not value:
        return "default"

    value = value.lower().replace("_", "-")

    if value.startswith("b+"):
        value = value[2:].replace("+", "-")

    parts = value.split("-")

    if len(parts) > 1 and parts[1].startswith("r"):
        region = parts[1][1:]

        if len(region) == 2 or region.isdigit():
            parts[1] = region

    parts[0] = {
        "in": "id",
        "iw": "he",
        "ji": "yi",
    }.get(parts[0], parts[0])

    return "-".join(parts)


def _prepare_languages(languages):
    if isinstance(languages, str):
        languages = [languages]

    values = _normalize_list(languages, "languages")
    result = list(dict.fromkeys(
        _normalize_language(value)
        for value in values
    ))

    if not result:
        raise ValueError("At least one language is required.")

    return result


def _validate_catalog(data):
    if not isinstance(data, dict):
        raise ValueError("The catalog must be a JSON object.")

    for package, translations in data.items():
        if not isinstance(package, str) or not package.strip():
            raise ValueError("Invalid package in the catalog.")

        if not isinstance(translations, dict):
            raise ValueError(f"Invalid translations for {package}.")

        for language, names in translations.items():
            if not isinstance(language, str) or not language.strip():
                raise ValueError(f"Invalid language in {package}.")

            if not isinstance(names, list):
                raise ValueError(
                    f"{package}/{language} must contain a list."
                )

            if any(
                not isinstance(name, str) or not name.strip()
                for name in names
            ):
                raise ValueError(
                    f"Invalid names in {package}/{language}."
                )


def _merge_scan(data, scan):
    """Merge observed names. Return whether the catalog changed."""
    changed = False

    for package, translations in scan.items():
        for language, names in translations.items():
            language = _normalize_language(language)
            clean = [
                name.strip()
                for name in names
                if isinstance(name, str) and name.strip()
            ]

            if not clean:
                continue

            target = data.setdefault(package, {})
            existing = target.get(language, [])

            seen = {}

            for name in existing + clean:
                key = _normalize_name(name)

                if key not in seen:
                    seen[key] = name

            merged = sorted(
                seen.values(),
                key=lambda name: (name.casefold(), name),
            )

            if language not in target or merged != existing:
                target[language] = merged
                changed = True

    return changed


def _load_dns(path):
    try:
        with path.open("r", encoding="utf-8-sig") as handle:
            data = json.load(handle)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as error:
        raise ValueError(
            f"Corrupt JSON: {path}. It will not be modified."
        ) from error

    _validate_catalog(data)

    normalized = {}
    _merge_scan(normalized, data)
    return normalized


def _save_json(data, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=path.name + ".",
            suffix=".tmp",
            delete=False,
        ) as handle:
            tmp = Path(handle.name)

            json.dump(
                data,
                handle,
                ensure_ascii=False,
                indent=4,
                sort_keys=True,
            )
            handle.write("\n")

        tmp.replace(path)

    finally:
        if tmp is not None:
            try:
                tmp.unlink(missing_ok=True)
            except OSError as error:
                _log(f"WARNING removing temporary JSON: {error}")


def _get_label(apk):
    label = apk.get_attribute_value("application", "label")

    if label:
        return label

    main_activities = {
        apk.format_value(name)
        for name in apk.get_main_activities()
    }

    for tag_type in ("activity", "activity-alias"):
        for element in apk.find_tags(tag_type):
            name = apk.get_value_from_tag(element, "name")

            if name and apk.format_value(name) in main_activities:
                label = apk.get_value_from_tag(element, "label")

                if label:
                    return label

    raise RuntimeError("No usable label found.")


def _extract_variants(apk):
    label = _get_label(apk)

    if not label.startswith("@"):
        return [("default", label)]

    resources = apk.get_android_resources()

    if resources is None:
        raise RuntimeError("The APK contains no readable resources.")

    resource_id, resource_package = resources.parse_id(label)

    if resource_package and resource_package != apk.get_package():
        raise RuntimeError(
            "The label depends on external resources: "
            f"{resource_package}"
        )

    variants = set()

    for config, text in resources.get_resolved_res_configs(resource_id):
        if not isinstance(text, str):
            continue

        text = text.strip()

        if not text or text.startswith("@"):
            continue

        language = _normalize_language(
            config.get_language_and_region()
        )

        variants.add((language, text))

    if not variants:
        raise RuntimeError(
            f"No variant could be resolved for {label}."
        )

    return sorted(variants)


def _group_names(variants, languages):
    result = {}

    for requested in languages:
        seen = {}

        for variant, name in variants:
            matches = variant == requested

            if requested != "default" and "-" not in requested:
                matches = (
                    matches
                    or variant.startswith(requested + "-")
                )

            if matches:
                seen.setdefault(_normalize_name(name), name)

        if seen:
            result[requested] = sorted(
                seen.values(),
                key=lambda name: (name.casefold(), name),
            )

    return result


def _get_names(adb_cmd, package, workdir, languages):
    apk_file = workdir / "app.apk"

    try:
        _log("  Querying APK path...")
        output = _run(
            adb_cmd + ["shell", "pm", "path", package]
        )

        paths = [
            line.strip().removeprefix("package:")
            for line in output.splitlines()
            if line.strip().startswith("package:")
        ]

        if not paths:
            raise RuntimeError("Android returned no APK path.")

        path = next(
            (item for item in paths if item.endswith("/base.apk")),
            paths[0],
        )

        _log(f"  Pulling APK: {path}")
        _run(adb_cmd + ["pull", path, str(apk_file)])

        if not apk_file.is_file() or apk_file.stat().st_size == 0:
            raise RuntimeError("No valid APK was pulled.")

        size = apk_file.stat().st_size / (1024 * 1024)
        _log(f"  APK pulled: {size:.1f} MB")
        _log("  Parsing manifest and resources...")

        apk = APK(apk_file.read_bytes(), raw=True)

        if apk.get_package() != package:
            raise RuntimeError(
                f"APK package mismatch: {apk.get_package()}"
            )

        variants = _extract_variants(apk)
        result = _group_names(variants, languages)

        for language, names in result.items():
            _log(
                f"  [{language}] "
                + json.dumps(names, ensure_ascii=False)
            )

        if not result:
            _log("  No names in the requested languages.")

        return result

    except Exception as error:
        _log(f"  ERROR in {package}: {error}")
        return {}

    finally:
        try:
            apk_file.unlink(missing_ok=True)
        except OSError as error:
            _log(f"  WARNING removing temporary APK: {error}")


def _list_packages(adb_cmd):
    output = _run(
        adb_cmd + ["shell", "pm", "list", "packages"]
    )

    return {
        line.strip().removeprefix("package:")
        for line in output.splitlines()
        if line.strip().startswith("package:")
    }


def _build_indexes(data):
    """Build direct and reverse associations in memory only."""
    by_name = {}
    by_package = {}

    for package, translations in data.items():
        labels = {}

        for names in translations.values():
            for name in names:
                key = _normalize_name(name)

                if key:
                    labels.setdefault(key, name)
                    by_name.setdefault(key, set()).add(package)

        by_package[package] = labels

    return by_name, by_package


def _make_requests(entries, data, installed):
    """
    Build requests without expanding user-supplied names.

    String:
        A known/installed package, or an exact display-name request.

    List/tuple:
        An explicit group of alternative display names.

    Package requests may use that package's own recorded labels.
    Name requests never inherit other labels from related packages.
    """
    if isinstance(entries, str):
        raise TypeError("entries must be a list, not a string.")

    _, by_package = _build_indexes(data)
    requests = []

    for entry in entries:
        if isinstance(entry, str):
            value = entry.strip()

            if not value:
                continue

            if value in data or value in installed:
                requests.append({
                    "kind": "package",
                    "description": value,
                    "package": value,
                    "labels": dict(by_package.get(value, {})),
                })

            else:
                requests.append({
                    "kind": "name",
                    "description": value,
                    "package": None,
                    "labels": {
                        _normalize_name(value): value,
                    },
                })

        elif isinstance(entry, (list, tuple)):
            names = _normalize_list(entry, "name group")

            if not names:
                continue

            requests.append({
                "kind": "name_group",
                "description": " / ".join(names),
                "package": None,
                "labels": {
                    _normalize_name(name): name
                    for name in names
                },
            })

        else:
            raise TypeError(
                "Each entry must be a string or a list/tuple of names."
            )

    return requests


def _request_status(request, by_name, by_package, installed):
    """
    Validate only the labels allowed by the request type.

    A name request uses exactly the user-supplied name.
    A name-group request uses exactly the supplied alternatives.
    An absent-package request uses that package's recorded labels.
    """
    if request["kind"] == "package":
        package = request["package"]

        if package in installed:
            if by_package.get(package):
                return "present", {package}

            return "extract", {package}

        # Read current catalog labels in case a preceding extraction
        # added information during this update.
        allowed_labels = by_package.get(package, {})

    else:
        allowed_labels = request["labels"]

    associated = set()

    for key in allowed_labels:
        associated.update(by_name.get(key, set()))

    present = associated & installed

    if present:
        return "present", present

    return "discover", set()


def _scan_and_merge(
    adb_cmd,
    packages,
    languages,
    data,
    dns_path,
    attempted,
    incorporated,
):
    pending = sorted(set(packages) - attempted)

    if not pending:
        return

    with tempfile.TemporaryDirectory(prefix="psdns_") as tmp:
        workdir = Path(tmp)

        for index, package in enumerate(pending, start=1):
            start = time.monotonic()
            attempted.add(package)

            _log(
                f"[{index}/{len(pending)}] Processing {package}"
            )

            names = _get_names(
                adb_cmd,
                package,
                workdir,
                languages,
            )

            if names:
                partial = {package: names}
                changed = _merge_scan(data, partial)
                _merge_scan(incorporated, partial)

                if changed or not dns_path.exists():
                    _save_json(data, dns_path)

            _log(
                f"[{index}/{len(pending)}] Done in "
                f"{time.monotonic() - start:.1f}s."
            )


def _print_table(data, languages):
    headers = ["Package"] + languages
    rows = []

    for package, translations in sorted(data.items()):
        row = [package]

        for language in languages:
            names = translations.get(language, [])
            row.append(
                " / ".join(" ".join(name.split()) for name in names)
                or "-"
            )

        rows.append(row)

    widths = [
        max(
            len(headers[column]),
            max(
                (len(row[column]) for row in rows),
                default=0,
            ),
        )
        for column in range(len(headers))
    ]

    separator = "+-" + "-+-".join(
        "-" * width for width in widths
    ) + "-+"

    def print_row(row):
        print(
            "| "
            + " | ".join(
                value.ljust(width)
                for value, width in zip(row, widths)
            )
            + " |",
            flush=True,
        )

    print("", flush=True)
    print(separator, flush=True)
    print_row(headers)
    print(separator, flush=True)

    for row in rows:
        print_row(row)

    print(separator, flush=True)


def update_catalog(
    packages=None,
    output_dir=None,
    languages=("es", "default"),
    serial=None,
    *,
    entries=None,
    refresh=False,
):
    """
    Generate or update psdns.json.

    packages:
        Backward-compatible package-list argument.
        May also contain names or explicit name groups.

    entries:
        Alternative to packages, with clearer semantics:
            ["Calculadora", "com.example.app"]
            [["Calculadora", "Calculator"]]

        Do not supply packages and entries together.

    Neither argument supplied:
        Full extraction of all installed packages.

    Explicit empty list:
        No work. Return the existing catalog.

    languages:
        Languages to STORE in the catalog.
        Discovery can only use labels already catalogued or
        extracted in these languages.

    refresh:
        False:
            Keep associations already backed by an installed
            catalogued package.
        True:
            Additionally re-extract those installed packages.

    Returns:
        The complete updated catalog.

    This function updates associations; it does not choose an app
    for the caller or return filter classifications.
    """
    start = time.monotonic()
    _log("Starting pseudo-DNS update...")

    if packages is not None and entries is not None:
        raise ValueError("Use packages or entries, not both.")

    selected = entries if entries is not None else packages
    full_scan = selected is None

    if not full_scan:
        if isinstance(selected, str):
            raise TypeError("Provide a list of entries.")

        selected = list(selected)

    languages = _prepare_languages(languages)

    if output_dir is None:
        output_dir = Path(__file__).resolve().parent

    dns_path = (
        Path(output_dir).expanduser().resolve()
        / "psdns.json"
    )

    data = _load_dns(dns_path)

    if not full_scan and not selected:
        _log("Empty entry list. Nothing to update.")
        return data

    adb_cmd = _prepare_adb(serial)
    installed = _list_packages(adb_cmd)

    if not installed:
        raise RuntimeError(
            "No installed packages returned. Catalog not modified."
        )

    attempted = set()
    incorporated = {}

    _log(f"Installed packages: {len(installed)}")
    _log(f"Languages: {', '.join(languages)}")
    _log(f"Catalog: {dns_path}")

    if full_scan:
        _log("Full extraction requested.")

        _scan_and_merge(
            adb_cmd,
            installed,
            languages,
            data,
            dns_path,
            attempted,
            incorporated,
        )

    else:
        requests = _make_requests(selected, data, installed)
        by_name, by_package = _build_indexes(data)
        direct = set()

        # First validate known associations and extract installed
        # unknown packages directly.
        for request in requests:
            status, present = _request_status(
                request,
                by_name,
                by_package,
                installed,
            )

            if status == "present":
                _log(
                    f"Association present for "
                    f"{request['description']!r}: "
                    + ", ".join(sorted(present))
                )

                if refresh:
                    direct.update(present)

            elif status == "extract":
                direct.update(present)

            else:
                _log(
                    f"No installed known association for "
                    f"{request['description']!r}."
                )

        _scan_and_merge(
            adb_cmd,
            direct,
            languages,
            data,
            dns_path,
            attempted,
            incorporated,
        )

        # Newly extracted packages may satisfy several requests.
        by_name, by_package = _build_indexes(data)
        unresolved = []

        for request in requests:
            status, _ = _request_status(
                request,
                by_name,
                by_package,
                installed,
            )

            if status != "present":
                unresolved.append(request)

        if unresolved:
            _log(
                f"{len(unresolved)} association(s) still unknown "
                "on this DUT. Starting discovery scan."
            )

            # All remaining installed packages are attempted once.
            # Do not stop at the first match: other packages may
            # legitimately share the same label.
            _scan_and_merge(
                adb_cmd,
                installed,
                languages,
                data,
                dns_path,
                attempted,
                incorporated,
            )

        by_name, by_package = _build_indexes(data)

        for request in requests:
            status, present = _request_status(
                request,
                by_name,
                by_package,
                installed,
            )

            if status == "present":
                _log(
                    f"Validated {request['description']!r}: "
                    + ", ".join(sorted(present))
                )
            else:
                _log(
                    f"Not confirmed: {request['description']!r}. "
                    "No usable matching association was extracted."
                )

    if incorporated:
        _print_table(incorporated, languages)
        _log(f"Catalog saved/merged: {dns_path}")
    else:
        _log(
            "No labels extracted. Existing associations were kept; "
            "no catalog write was required."
        )

    _log(f"Packages attempted: {len(attempted)}")
    _log(f"Finished in {time.monotonic() - start:.1f}s.")

    return data