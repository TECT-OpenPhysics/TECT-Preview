"""Integrated verifier for the EXP-000976 frequency crosswalk."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pre-a13-a1-fref-root-frequency-crosswalk-manifest.json"
PRIMARY = ROOT / "verification/scripts/a13_a1_fref_root_frequency_crosswalk.py"
INDEPENDENT = ROOT / "codes/foundations/a13_a1_fref_root_frequency_crosswalk_independent.py"
DEFAULT_OUTPUT = ROOT / "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/runs/2026-08-23-integrated-fref-root-frequency-crosswalk/result.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def atomic_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def run_child(command: list[str]) -> tuple[dict, str]:
    completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        raise RuntimeError(completed.stdout + completed.stderr)
    path = Path(command[command.index("--output") + 1])
    return json.loads(path.read_text(encoding="utf-8")), completed.stdout + completed.stderr


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    parser.add_argument("--staged", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows = []
    def check(name, condition, actual, expected):
        rows.append({"name": name, "pass": bool(condition), "actual": actual, "expected": expected})
        if not condition:
            raise AssertionError(f"{name}: {actual!r} != {expected!r}")
    check("identity", manifest["audit_id"] == "A13-A1-FREF-ROOT-FREQUENCY-CROSSWALK", manifest["audit_id"], "A13-A1-FREF-ROOT-FREQUENCY-CROSSWALK")
    check("no formal result/event/negative", manifest["formal_integration"]["results"] == [] and manifest["formal_integration"]["events"] == [] and manifest["formal_integration"]["negatives"] == [], manifest["formal_integration"], "all empty")
    check("eight hostile mutations", len(manifest["hostile_mutations"]) == 8, len(manifest["hostile_mutations"]), 8)
    for key, item in manifest["source_authorities"].items():
        path = ROOT / item["path"]
        check(f"source {key} hash", path.is_file() and sha(path) == item["sha256"], sha(path) if path.is_file() else None, item["sha256"])
    for path in (PRIMARY, INDEPENDENT):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        check(f"AST {path.name}", tree is not None, True, True)
    py = sys.executable
    primary_path = ROOT / "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/runs/2026-08-23-primary-fref-root-frequency-crosswalk/result.json"
    independent_path = ROOT / "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/runs/2026-08-23-independent-fref-root-frequency-crosswalk/result.json"
    primary, _ = run_child([py, str(PRIMARY), "--output", str(primary_path)])
    independent, _ = run_child([py, str(INDEPENDENT), "--output", str(independent_path)])
    check("primary PASS", primary["verdict"] == "PASS", primary["verdict"], "PASS")
    check("independent PASS", independent["verdict"] == "PASS", independent["verdict"], "PASS")
    shared_keys = ["manifest_formula_mismatch", "nearest_fref_shell_norm_square", "production_owner", "r192_first_missing_slot", "root_norm_squares"]
    shared_ok = all(primary["derived"][key] == independent["derived"][key] for key in shared_keys)
    numeric_keys = ("qstar_ratio_over_step_square_numeric", "kinetic_n2_1_numeric", "kinetic_n2_3_numeric", "kinetic_n2_4_numeric")
    numeric_ok = all(abs(float(primary["derived"][key]) - float(independent["derived"][key.replace("_numeric", "")])) < 1e-12 for key in numeric_keys)
    check("derived agreement", shared_ok and numeric_ok, {key: primary["derived"][key] for key in shared_keys}, {key: independent["derived"][key] for key in shared_keys})
    check("mismatch finding", primary["derived"]["manifest_formula_mismatch"] is True, primary["derived"]["manifest_formula_mismatch"], True)
    check("shell/root separation", primary["derived"]["nearest_fref_shell_norm_square"] == 3 and primary["derived"]["root_norm_squares"] == [1, 4], primary["derived"], "3 versus [1,4]")
    check("R-192 boundary", primary["derived"]["r192_first_missing_slot"] == "heat_root_incidence" and primary["derived"]["production_owner"] is False, primary["derived"], "owner absent")
    payload = {"schema": "tect/lean-kernel-crosscheck/1.0", "audit_id": manifest["audit_id"], "run_kind": "integrated", "verdict": "PASS", "assertion_count": len(rows), "assertions": rows, "derived": primary["derived"], "boundary": manifest["boundary"]}
    if not args.no_store:
        atomic_json(args.output, payload)
    print(f"A13 FREF ROOT FREQUENCY CROSSWALK INTEGRATED PASS {len(rows)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
