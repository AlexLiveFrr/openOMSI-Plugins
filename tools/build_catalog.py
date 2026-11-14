#!/usr/bin/env python3
"""Builds catalog.json from plugins/<id>/plugin.json and the files beside it, and checks
every plugin against the rules the openOMSI launcher holds them to before it installs one.

    python3 tools/build_catalog.py           write catalog.json
    python3 tools/build_catalog.py --check   fail when a plugin breaks a rule or catalog.json
                                             is not what this script writes (CI)

The launcher downloads each file from this repository and installs it only when its size and
SHA-256 are the catalog's, so catalog.json must be rebuilt with every change of a plugin.
Needs nothing but Python 3.8+.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGINS = ROOT / "plugins"
CATALOG = ROOT / "catalog.json"
VERSION = 1

ID = re.compile(r"^[a-z0-9][a-z0-9-]{1,39}$")
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
PATH = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9_.-]*(/[A-Za-z0-9_][A-Za-z0-9_.-]*)*$")
# (what a Lua plugin uses: its code, its data, pictures and sounds; nothing that runs by itself)
EXTENSIONS = {".lua", ".json", ".txt", ".md", ".csv", ".png", ".jpg", ".ogg", ".wav", ".ttf", ".otf"}
MAX_FILE = 2 * 1024 * 1024
MAX_PLUGIN = 10 * 1024 * 1024
MAX_FILES = 200
LICENSES = {"AGPL-3.0-only", "AGPL-3.0-or-later", "GPL-3.0-only", "GPL-3.0-or-later", "GPL-2.0-or-later",
            "LGPL-3.0-or-later", "MPL-2.0", "MIT", "BSD-2-Clause", "BSD-3-Clause", "Apache-2.0", "ISC",
            "Unlicense", "CC0-1.0", "Zlib"}
FIELDS = {"id", "name", "author", "version", "description", "license", "tags", "homepage", "min_game"}


def problems_of(folder: Path):
    """(entry for the catalog or None, list of problems)"""
    out = []
    meta_path = folder / "plugin.json"
    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        return None, [f"{folder.name}/plugin.json: {e}"]
    if not isinstance(meta, dict):
        return None, [f"{folder.name}/plugin.json: an object is needed"]
    for k in sorted(set(meta) - FIELDS):
        out.append(f"{folder.name}: unknown field {k!r}")
    text = lambda k, n: isinstance(meta.get(k), str) and 0 < len(meta[k].strip()) <= n and "\n" not in meta[k]
    if meta.get("id") != folder.name or not ID.match(folder.name):
        out.append(f"{folder.name}: id must be the folder's name, 2-40 of a-z 0-9 -")
    for k, n in (("name", 60), ("author", 60), ("description", 300)):
        if not text(k, n):
            out.append(f"{folder.name}: {k} is needed, one line of at most {n} characters")
    if not isinstance(meta.get("version"), str) or not SEMVER.match(meta["version"]):
        out.append(f"{folder.name}: version must be MAJOR.MINOR.PATCH")
    if meta.get("license") not in LICENSES:
        out.append(f"{folder.name}: license must be an open source licence's SPDX id ({', '.join(sorted(LICENSES))})")
    tags = meta.get("tags", [])
    if not isinstance(tags, list) or len(tags) > 6 or not all(isinstance(t, str) and re.match(r"^[a-z0-9-]{1,20}$", t) for t in tags):
        out.append(f"{folder.name}: tags must be at most 6 of a-z 0-9 -")
    if "homepage" in meta and not (isinstance(meta["homepage"], str) and re.match(r"^https://[A-Za-z0-9.-]+\.[A-Za-z]{2,}(/[^\s\"'<>\\]*)?$", meta["homepage"]) and len(meta["homepage"]) <= 200):
        out.append(f"{folder.name}: homepage must be a plain https address")
    if "min_game" in meta and not (isinstance(meta["min_game"], str) and SEMVER.match(meta["min_game"])):
        out.append(f"{folder.name}: min_game must be MAJOR.MINOR.PATCH")

    files, total = [], 0
    for p in sorted(folder.rglob("*")):
        rel = p.relative_to(folder).as_posix()
        if p.is_symlink():
            out.append(f"{folder.name}/{rel}: no links")
            continue
        if p.is_dir() or rel == "plugin.json":
            continue
        if not PATH.match(rel) or ".." in rel or len(rel) > 120:
            out.append(f"{folder.name}/{rel}: a path of letters, digits, _ . - and / only")
            continue
        if p.suffix.lower() not in EXTENSIONS:
            out.append(f"{folder.name}/{rel}: {p.suffix or 'no extension'} is not taken ({' '.join(sorted(EXTENSIONS))})")
            continue
        data = p.read_bytes()
        if len(data) > MAX_FILE:
            out.append(f"{folder.name}/{rel}: larger than {MAX_FILE // 1024 // 1024} MB")
        total += len(data)
        files.append({"path": rel, "size": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    if not any(f["path"] == "main.lua" for f in files):
        out.append(f"{folder.name}: main.lua is needed (the plugin is installed as plugins/{folder.name}/main.lua)")
    if len(files) > MAX_FILES:
        out.append(f"{folder.name}: more than {MAX_FILES} files")
    if total > MAX_PLUGIN:
        out.append(f"{folder.name}: larger than {MAX_PLUGIN // 1024 // 1024} MB in all")
    entry = {k: meta[k] for k in ("id", "name", "author", "version", "description", "license", "tags", "homepage", "min_game") if k in meta}
    entry.setdefault("tags", [])
    entry["bytes"] = total
    entry["files"] = files
    return entry, out


def build():
    entries, problems = [], []
    for folder in sorted(p for p in PLUGINS.iterdir() if p.is_dir()) if PLUGINS.is_dir() else []:
        entry, out = problems_of(folder)
        problems += out
        if entry and not out:
            entries.append(entry)
    return {"version": VERSION, "plugins": entries}, problems


def main():
    catalog, problems = build()
    text = json.dumps(catalog, indent=2, ensure_ascii=False) + "\n"
    for p in problems:
        print(f"::error::{p}" if "--check" in sys.argv else f"problem: {p}")
    if "--check" in sys.argv:
        have = CATALOG.read_text(encoding="utf-8") if CATALOG.exists() else ""
        if have != text:
            print("::error::catalog.json is not up to date: run python3 tools/build_catalog.py and commit it")
            return 1
        return 1 if problems else 0
    CATALOG.write_text(text, encoding="utf-8")
    print(f"catalog.json: {len(catalog['plugins'])} plugins")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
