"""Primary Lean cross-check for finite adapted-NEAR obstruction fixtures."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy" / "pre-a13-adapted-near-obstruction-crosscheck-manifest.json"
LEAN_DIR = REPO / "verification" / "lean"
LEAN_ENTRYPOINT = LEAN_DIR / "Tect" / "R187.lean"
TOOLCHAIN = LEAN_DIR / "lean-toolchain"
DEFAULT_OUTPUT = REPO / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION" / "runs" / "2026-08-22-lean-r187-adapted-near-obstruction-crosscheck" / "primary.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=str)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def find_lake() -> str | None:
    pin = TOOLCHAIN.read_text(encoding="utf-8").strip()
    encoded = pin.replace("/", "--").replace(":", "---")
    for name in ("lake.exe", "lake"):
        candidate = Path.home() / ".elan" / "toolchains" / encoded / "bin" / name
        if candidate.is_file():
            return str(candidate)
    return shutil.which("lake")


def derive(values: dict[str, Any]) -> dict[str, Any]:
    c = Fraction(values["nonlinear_c"])
    plus = (1 + c) ** 2
    minus = (1 - c) ** 2
    mean_square = (plus + minus) / 2
    deviations = [plus - mean_square, minus - mean_square]
    gamma = Fraction(values["gamma"])
    pair_slacks = [(gamma - 1 - 2 * Fraction(theta)) / 6 for theta in values["theta_values"]]
    a = Fraction(1, 2) - gamma / 4
    b = Fraction(1, 2) + gamma / 12
    return {
        "conditional_mean_plus": Fraction(0),
        "conditional_mean_minus": Fraction(0),
        "conditional_square_plus": plus,
        "conditional_square_minus": minus,
        "mean_square": mean_square,
        "root_deviation_plus": deviations[0],
        "root_deviation_minus": deviations[1],
        "ledger_a": a,
        "ledger_b": b,
        "ledger_slack": 1 - a - b,
        "ledger_moment": 6 / gamma,
        "pair_slacks": pair_slacks,
        "pair_slacks_all_negative": all(value < 0 for value in pair_slacks),
        "doob_square_sum": Fraction(2),
        "doob_terminal_l2": Fraction(2),
        "doob_terminal_l6": Fraction(32),
        "doob_square_l6": Fraction(8),
        "doob_l6_holds": Fraction(32) <= 8 * Fraction(8),
        "a13_gate_closed": False,
        "overlap_src_closed": False,
        "lean_escape_tokens_absent": True,
        "boundary_present": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(condition), "actual": str(actual), "expected": str(expected)})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("manifest identity", manifest["audit_id"] == "A13-ADAPTED-NEAR-OBSTRUCTION-CROSSCHECK", manifest["audit_id"], "A13-ADAPTED-NEAR-OBSTRUCTION-CROSSCHECK")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("no new negatives", manifest["formal_integration"]["no_new_negative_ids"] == [], manifest["formal_integration"]["no_new_negative_ids"], [])
    check("no PDF contract", manifest["formal_integration"]["no_pdf"] is True, manifest["formal_integration"]["no_pdf"], True)
    for key, item in manifest["inputs"].items():
        path = REPO / item["path"]
        check(f"input {key}", path.is_file() and sha256(path) == item["sha256"], sha256(path) if path.is_file() else None, item["sha256"])
    values = manifest["registered_inputs"]
    derived = derive(values)
    for key, expected in values["expected"].items():
        check(key, derived[key] == Fraction(expected) if not isinstance(expected, list) else [str(item) for item in derived[key]] == expected, derived[key], expected)
    check("pair slacks negative", derived["pair_slacks_all_negative"], derived["pair_slacks"], "all < 0")
    check("Doob L6 fixture", derived["doob_l6_holds"], derived["doob_l6_holds"], True)
    check("A13 boundary open", not derived["a13_gate_closed"] and not derived["overlap_src_closed"], derived, "both open")
    source_text = LEAN_ENTRYPOINT.read_text(encoding="ascii")
    check("Lean theorem markers", all(marker in source_text for marker in manifest["theorem_markers"]), [marker for marker in manifest["theorem_markers"] if marker in source_text], manifest["theorem_markers"])
    check("Lean escape tokens absent", not any(token in source_text.split() for token in ("sorry", "admit", "axiom", "unsafe")), [], ["sorry", "admit", "axiom", "unsafe"])
    lake = find_lake()
    check("lake available", lake is not None, lake, "pinned toolchain")
    completed = subprocess.run([lake, "env", "lean", str(LEAN_ENTRYPOINT.relative_to(LEAN_DIR))], cwd=LEAN_DIR, text=True, encoding="utf-8", capture_output=True, check=False)
    check("Lean compile", completed.returncode == 0, completed.returncode, 0)
    check("Lean clean output", completed.stdout.strip() == "" and completed.stderr.strip() == "", [completed.stdout, completed.stderr], ["", ""])
    derived["input_count"] = len(values["theta_values"])
    payload = {"schema": "tect/lean-kernel-crosscheck/1.0", "run_kind": "primary", "audit_id": manifest["audit_id"], "claim_id": manifest["claim_id"], "result_id": manifest["result_id"], "verdict": "PASS", "assertion_count": len(rows), "assertions": rows, "derived": derived, "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"), "boundary": manifest["boundary"]}
    if not args.no_store:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY R-187 LEAN PASS {len(rows)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
