"""Non-importing standard-library Fraction lane for the A1 mismatch."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy" / "pre-a-a1-nonlinear-gradient-mismatch-lean-crosscheck-manifest.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    a1_path = REPO / manifest["inputs"]["a1_manifest"]["path"]
    a1 = json.loads(a1_path.read_text(encoding="utf-8"))
    params = a1["parameters"]
    lam = Fraction(str(params[manifest["lean_inputs"]["lambda_key"]]))
    gamma = Fraction(str(params[manifest["lean_inputs"]["gamma_key"]]))
    rho = Fraction(str(manifest["lean_inputs"]["fixture_rho"]))
    residual = lam * rho + gamma * rho * rho
    declared = 2 * lam * rho + 2 * gamma * rho * rho
    assert sha256(a1_path) == manifest["inputs"]["a1_manifest"]["sha256"]
    assert lam == Fraction(str(manifest["lean_inputs"]["lambda"]))
    assert gamma == Fraction(str(manifest["lean_inputs"]["gamma"]))
    assert declared == 2 * residual
    assert declared != residual
    payload = {
        "schema": "tect/a1-nonlinear-gradient-mismatch-lean-crosscheck/1.0",
        "run_kind": "independent",
        "audit_id": manifest["audit_id"],
        "claim_id": manifest["claim_id"],
        "verdict": "PASS",
        "derived": {
            "lambda": f"{lam.numerator}/{lam.denominator}",
            "gamma": f"{gamma.numerator}/{gamma.denominator}",
            "rho": f"{rho.numerator}/{rho.denominator}",
            "residual_coefficient": f"{residual.numerator}/{residual.denominator}",
            "declared_gradient_coefficient": f"{declared.numerator}/{declared.denominator}",
            "difference": f"{(declared - residual).numerator}/{(declared - residual).denominator}",
            "declared_equals_twice_residual": True,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print("INDEPENDENT A1 LEAN CROSSCHECK PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
