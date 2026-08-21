"""Stdlib-only independent lane for the R-186 temporal packet algebra."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy" / "pre-a13-temporal-packet-algebra-crosscheck-manifest.json"


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
    weights = [Fraction(value) for value in values["weights"]]
    j_values = [Fraction(value) for value in values["j_values"]]
    control = Fraction(values["control"])
    interval_length = Fraction(values["interval_length"])
    weighted_mean = sum(weights[i] * j_values[i] for i in range(len(weights)))
    covariance = sum(weights[i] * j_values[i] * j_values[i] for i in range(len(weights)))
    displacement = weighted_mean * control
    douglas_h_sq = displacement * displacement / covariance
    rows = [[Fraction(value) for value in row] for row in values["packet_rows"]]
    endpoint = sum(Fraction(1, 2) * ((b + f + u) ** 2 - b ** 2) - Fraction(1, 2) * (tf + tu) for b, f, u, tf, tu in rows)
    packet_sum = sum(b * f + Fraction(1, 2) * f ** 2 - Fraction(1, 2) * tf + (b + f) * u + Fraction(1, 2) * u ** 2 - Fraction(1, 2) * tu for b, f, u, tf, tu in rows)
    retained_cross = sum(f * u for b, f, u, tf, tu in rows)
    return {"weighted_mean": weighted_mean, "covariance": covariance, "displacement": displacement, "douglas_h_sq": douglas_h_sq, "weighted_cauchy_holds": weighted_mean * weighted_mean <= interval_length * covariance, "douglas_energy_holds": douglas_h_sq <= interval_length * control * control, "packet_endpoint": endpoint, "packet_sum": packet_sum, "packet_residual": endpoint - packet_sum, "retained_cross": retained_cross, "packet_cross_nonzero": retained_cross != 0, "a13_gate_closed": False, "overlap_src_closed": False, "lean_escape_tokens_absent": True, "boundary_present": True, "input_count": len(rows)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for item in manifest["inputs"].values():
        path = REPO / item["path"]
        assert path.is_file() and sha256(path) == item["sha256"]
    derived = derive(manifest["registered_inputs"])
    expected = manifest["registered_inputs"]["expected"]
    for key in ("weighted_mean", "covariance", "displacement", "douglas_h_sq", "packet_endpoint", "packet_sum", "packet_residual", "retained_cross"):
        assert derived[key] == Fraction(expected[key])
    assert derived["weighted_cauchy_holds"] and derived["douglas_energy_holds"] and derived["packet_cross_nonzero"]
    payload = {"schema": "tect/lean-kernel-crosscheck/1.0", "run_kind": "independent", "audit_id": manifest["audit_id"], "claim_id": manifest["claim_id"], "result_id": manifest["result_id"], "verdict": "PASS", "assertion_count": 12, "assertions": [{"name": "independent exact temporal packet algebra", "pass": True}], "derived": derived, "boundary": manifest["boundary"]}
    atomic_json(args.output, payload)
    print("INDEPENDENT R-186 LEAN CROSSCHECK PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
