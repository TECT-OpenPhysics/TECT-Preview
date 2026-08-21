#!/usr/bin/env python3
"""Validate the repository-wide Lean policy and optionally compile every entrypoint.

The registry is the single source for the pinned Lean/Lake files and the exact
LF-normalised hash of every ``verification/lean/Tect/*.lean`` entrypoint.  The
default metadata mode is safe for release/CI environments without Lean
installed.  ``--compile`` additionally resolves the exact pinned elan
toolchain and runs ``lake env lean`` once per registered entrypoint.  This is a
toolchain/integrity gate, not a physics result and it never changes claim
tiers, gates, or result ledgers.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
REGISTRY = REPO / "verification" / "lean" / "registry.json"
LEAN_ROOT = REPO / "verification" / "lean"
FORBIDDEN = ("sorry", "admit", "axiom", "unsafe")
ENTRYPOINT_PATTERN = re.compile(r"verification/lean/Tect/[A-Za-z0-9_]+\.lean")
DECLARATION_PATTERN = re.compile(r"(?m)^\s*(?:theorem|lemma|example)\s+([A-Za-z0-9_]+)")
HANGUL_PATTERN = re.compile(r"[\u1100-\u11FF\u3130-\u318F\uAC00-\uD7AF]")


def normalised_bytes(path: Path) -> bytes:
    return path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def sha256(path: Path) -> str:
    return hashlib.sha256(normalised_bytes(path)).hexdigest()


def check(rows: list[dict[str, Any]], name: str, condition: bool, actual: Any, expected: Any) -> None:
    rows.append({"name": name, "pass": bool(condition), "actual": actual, "expected": expected})
    if not condition:
        raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")


def find_pinned_lake(toolchain: str) -> Path | None:
    encoded = toolchain.replace("/", "--").replace(":", "---")
    candidate = Path.home() / ".elan" / "toolchains" / encoded / "bin"
    for name in ("lake.exe", "lake"):
        path = candidate / name
        if path.is_file():
            return path
    return None


def referenced_entrypoints() -> set[str]:
    found: set[str] = set()
    for path in (REPO / "strategy").rglob("*.json"):
        text = path.read_text(encoding="utf-8", errors="replace")
        found.update(ENTRYPOINT_PATTERN.findall(text))
    return found


def metadata_checks(registry: dict[str, Any], rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    check(rows, "registry schema", registry.get("schema") == "tect/lean-cross-verification-registry/1.0", registry.get("schema"), "tect/lean-cross-verification-registry/1.0")
    toolchain = registry["toolchain"]
    hash_keys = {"toolchain_file": "toolchain_sha256", "lakefile": "lakefile_sha256", "lockfile": "lockfile_sha256"}
    for key in ("toolchain_file", "lakefile", "lockfile"):
        path = REPO / toolchain[key]
        check(rows, f"{key} exists", path.is_file(), str(path), True)
        expected_hash = toolchain[hash_keys[key]]
        check(rows, f"{key} hash", sha256(path) == expected_hash, sha256(path), expected_hash)
    pin_path = REPO / toolchain["toolchain_file"]
    actual_pin = pin_path.read_text(encoding="utf-8").strip()
    check(rows, "toolchain pin", actual_pin == toolchain["toolchain"], actual_pin, toolchain["toolchain"])
    lakefile = (REPO / toolchain["lakefile"]).read_text(encoding="utf-8")
    check(rows, "lakefile pins mathlib revision", f'rev = "{toolchain["mathlib_input_revision"]}"' in lakefile, lakefile, toolchain["mathlib_input_revision"])
    lock = json.loads((REPO / toolchain["lockfile"]).read_text(encoding="utf-8"))
    mathlib = next((item for item in lock.get("packages", []) if item.get("name") == "mathlib"), None)
    check(rows, "lock pins mathlib", mathlib is not None and mathlib.get("inputRev") == toolchain["mathlib_input_revision"] and mathlib.get("rev") == toolchain["mathlib_revision"], mathlib, {"inputRev": toolchain["mathlib_input_revision"], "rev": toolchain["mathlib_revision"]})

    registered = registry.get("entrypoints", [])
    registered_paths = {item["path"] for item in registered}
    actual_paths = {p.relative_to(REPO).as_posix() for p in (LEAN_ROOT / "Tect").glob("*.lean")}
    check(rows, "entrypoint registry is complete", registered_paths == actual_paths, sorted(registered_paths ^ actual_paths), [])
    check(rows, "entrypoint paths are unique", len(registered_paths) == len(registered), len(registered_paths), len(registered))
    for item in registered:
        path = REPO / item["path"]
        check(rows, f"source exists {item['path']}", path.is_file(), str(path), True)
        raw = path.read_bytes()
        text = raw.decode("utf-8")
        check(rows, f"LF source {item['path']}", b"\r" not in raw and raw.endswith(b"\n"), True, True)
        check(rows, f"source hash {item['path']}", sha256(path) == item["sha256"], sha256(path), item["sha256"])
        check(rows, f"source language {item['path']}", not HANGUL_PATTERN.search(text), False, False)
        declarations = DECLARATION_PATTERN.findall(text)
        check(rows, f"theorem declaration {item['path']}", bool(declarations), declarations, "at least one theorem/lemma/example")
        for token in registry["source_policy"]["forbidden_tokens"]:
            hits = re.findall(rf"\b{re.escape(token)}\b", text)
            check(rows, f"escape token {token} absent in {item['path']}", not hits, hits, [])
        for declaration in item.get("declarations", []):
            check(rows, f"declaration marker {declaration}", declaration in declarations, declarations, declaration)
    references = referenced_entrypoints()
    check(rows, "strategy manifest bridges registered", references <= registered_paths, sorted(references - registered_paths), [])
    return sorted(registered_paths)


def compile_entrypoints(paths: list[str], toolchain: str, rows: list[dict[str, Any]]) -> None:
    lake = find_pinned_lake(toolchain)
    check(rows, "pinned lake executable", lake is not None, str(lake) if lake else None, "local elan pinned toolchain")
    if lake is None:
        return
    for rel in paths:
        completed = subprocess.run([str(lake), "env", "lean", rel.removeprefix("verification/lean/")], cwd=LEAN_ROOT, text=True, encoding="utf-8", errors="replace", capture_output=True, check=False)
        combined = f"{completed.stdout}\n{completed.stderr}"
        check(rows, f"Lean compile {rel}", completed.returncode == 0 and "error:" not in combined.lower(), {"returncode": completed.returncode, "output": combined[-500:]}, "exit 0 without errors")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metadata", action="store_true", help="run the metadata-only gate (the default)")
    parser.add_argument("--compile", action="store_true", help="also compile every registered Lean entrypoint")
    parser.add_argument("--json", action="store_true", help="emit the assertion payload as JSON")
    args = parser.parse_args()
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []
    try:
        paths = metadata_checks(registry, rows)
        if args.compile:
            compile_entrypoints(paths, registry["toolchain"]["toolchain"], rows)
    except (AssertionError, KeyError, json.JSONDecodeError, UnicodeError) as error:
        print(f"LEAN TOOLCHAIN CHECK: FAIL ({error})")
        if args.json:
            print(json.dumps({"status": "FAIL", "assertions": rows}, indent=2, ensure_ascii=True))
        return 1
    payload = {
        "schema": "tect/lean-toolchain-check/1.0",
        "status": "PASS",
        "mode": "compile" if args.compile else "metadata",
        "toolchain": registry["toolchain"]["toolchain"],
        "entrypoint_count": len(paths),
        "assertion_count": len(rows),
        "assertions": rows,
        "boundary": "This gate checks the pinned Lean/Lake inputs and the encoded entrypoint sources. It does not prove any analytic, variational, physical, or limit theorem beyond the propositions compiled by an individual result package."
    }
    print(f"LEAN TOOLCHAIN CHECK: PASS ({payload['mode']}, {len(paths)} entrypoints, {len(rows)} assertions)")
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
