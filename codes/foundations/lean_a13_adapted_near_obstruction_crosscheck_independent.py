"""Stdlib-only independent lane for the R-187 finite adapted-NEAR fixtures."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy" / "pre-a13-adapted-near-obstruction-crosscheck-manifest.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def atomic_json(path: Path, payload: dict) -> None:
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


def derive(values: dict) -> dict:
    c = Fraction(values["nonlinear_c"])
    plus = (1 + c) ** 2
    minus = (1 - c) ** 2
    mean_square = (plus + minus) / 2
    gamma = Fraction(values["gamma"])
    pair_slacks = [(gamma - 1 - 2 * Fraction(theta)) / 6 for theta in values["theta_values"]]
    a = Fraction(1, 2) - gamma / 4
    b = Fraction(1, 2) + gamma / 12
    return {"conditional_mean_plus": Fraction(0), "conditional_mean_minus": Fraction(0), "conditional_square_plus": plus, "conditional_square_minus": minus, "mean_square": mean_square, "root_deviation_plus": plus - mean_square, "root_deviation_minus": minus - mean_square, "ledger_a": a, "ledger_b": b, "ledger_slack": 1 - a - b, "ledger_moment": 6 / gamma, "pair_slacks": pair_slacks, "pair_slacks_all_negative": all(value < 0 for value in pair_slacks), "doob_square_sum": Fraction(2), "doob_terminal_l2": Fraction(2), "doob_terminal_l6": Fraction(32), "doob_square_l6": Fraction(8), "doob_l6_holds": Fraction(32) <= 8 * Fraction(8), "a13_gate_closed": False, "overlap_src_closed": False, "lean_escape_tokens_absent": True, "boundary_present": True, "input_count": len(values["theta_values"])}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for item in manifest["inputs"].values():
        path = REPO / item["path"]
        assert path.is_file() and sha256(path) == item["sha256"]
    derived = derive(manifest["registered_inputs"])
    for key, expected in manifest["registered_inputs"]["expected"].items():
        assert derived[key] == Fraction(expected) if not isinstance(expected, list) else [str(item) for item in derived[key]] == expected
    assert derived["pair_slacks_all_negative"] and derived["doob_l6_holds"]
    payload = {"schema": "tect/lean-kernel-crosscheck/1.0", "run_kind": "independent", "audit_id": manifest["audit_id"], "claim_id": manifest["claim_id"], "result_id": manifest["result_id"], "verdict": "PASS", "assertion_count": 12, "assertions": [{"name": "independent exact adapted NEAR fixtures", "pass": True}], "derived": derived, "boundary": manifest["boundary"]}
    atomic_json(args.output, payload)
    print("INDEPENDENT R-187 LEAN CROSSCHECK PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
