#!/usr/bin/env python3
"""Run the existing finite replay contract from an extracted source ZIP.

Unlike the clean Git-snapshot orchestrator, this entry point needs no .git
directory. Supply the resolved Lean cache and historical Tectonic executable.
The file inventory is checked BEFORE commands regenerate current artifacts.
This is executed finite/structural evidence, not external proof review.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import clean_snapshot_replay as clean
import reproduction_manifest as rm

PAPER = Path(__file__).resolve().parents[1]
ROOT = PAPER.parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lean-cache", type=Path, required=True)
    parser.add_argument("--tectonic", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=PAPER / "verification/runs/archive-replay-current.json")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not __debug__:
        raise SystemExit("Assertions must be enabled")
    if args.self_test:
        clean.self_test()
        rm.self_test()
    manifest_path = PAPER / "verification/runs/reproduction-manifest.json"
    input_manifest_hash = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    commands = clean.nested_commands(manifest)
    rows, fatal, link_created = [], "", False
    link = ROOT / "verification/lean/.lake"
    try:
        for item in manifest["files"] + manifest["replay_inputs"]:
            if rm.sha256(ROOT / item["path"]) != item["sha256"]:
                raise ValueError("Input hash differs before replay: " + item["path"])
        clean.interpreter_record(Path(sys.executable))
        environment = clean.tex_environment(os.environ.copy(), args.tectonic)
        environment["PYTHONUTF8"] = "1"
        environment["TECT_PYTHON"] = sys.executable
        if not link.exists():
            clean.link_lean_cache(args.lean_cache.resolve(), link)
            link_created = True
        elif link.resolve() != args.lean_cache.resolve():
            raise ValueError("Existing Lean cache differs; no replacement is allowed")
        for item in commands:
            parts = item["command"].split()
            script = clean.command_script(item["command"])
            process = subprocess.run([sys.executable, *parts[1:]], cwd=ROOT,
                                     env=environment, capture_output=True,
                                     text=True, encoding="utf-8", timeout=600)
            combined = process.stdout + "\n" + process.stderr
            passed = process.returncode == 0 and all(t in combined for t in clean.EXPECTED_TOKENS[script])
            rows.append({"command": item["command"], "returncode": process.returncode,
                         "passed": passed, "output_tail": combined[-4000:]})
            print(("PASS " if passed else "FAIL ") + script, flush=True)
    except Exception as error:
        fatal = f"{type(error).__name__}: {error}"
    finally:
        if link_created:
            clean.remove_cache_link(link)
    count = sum(row["passed"] for row in rows)
    result = {"schema": "tect/archived-paper-replay/1.0", "git_required": False,
              "input_manifest_sha256": input_manifest_hash,
              "python": sys.version, "lean_cache": str(args.lean_cache.resolve()),
              "tectonic": str(args.tectonic.resolve()),
              "passed": count, "total": len(commands), "results": rows,
              "fatal_error": fatal,
              "verdict": "PASS" if not fatal and count == len(commands) else "FAIL",
              "non_claims": ["Finite replay only; not external mathematical or novelty review.",
                             "Runtime dependencies and resolved Lean cache are external inputs."]}
    rm.atomic_write(args.output, json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(f"ARCHIVED-SOURCE-{result['verdict']}: {count}/{len(commands)}")
    return 0 if result["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
