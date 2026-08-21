"""Stdlib-only independent arithmetic lane for the R-163 Lean bridge."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy" / "pre-a-a13-r163-dyadic-forest-lean-crosscheck-manifest.json"


def sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() != ".pdf":
        payload = payload.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(payload).hexdigest()


def fraction(value: str) -> Fraction:
    return Fraction(value)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for item in manifest["inputs"].values():
        path = REPO / item["path"]
        assert path.is_file()
        assert sha256(path) == item["sha256"]
    constants = manifest["registered_constants"]
    r163 = json.loads((REPO / manifest["inputs"]["r163_primary_result"]["path"]).read_text(encoding="utf-8"))
    independent = json.loads((REPO / manifest["inputs"]["r163_independent_result"]["path"]).read_text(encoding="utf-8"))
    pd = r163["diagnostics"]
    idg = independent["diagnostics"]
    for key in ("origin_gap", "retained_gap", "reduced_action_hessian_floor", "owner_adverse_floor", "CM_D3_bound_at_r0"):
        assert pd[key] == idg[key]
    origin = fraction(pd["origin_gap"])
    loss = fraction(constants["origin_gap_loss"])
    retained = origin - loss
    headroom = fraction(constants["epsilon_v_limit"]) - fraction(constants["explicit_source_coefficient"])
    owner_floor = -2 * headroom - 2 * fraction(constants["explicit_source_coefficient"])
    assert retained == fraction(constants["retained_gap"]) > fraction(constants["target_gap"])
    assert headroom == fraction(constants["coefficient_headroom"])
    assert owner_floor == fraction(constants["owner_adverse_floor"])
    assert fraction(pd["epsilon_6"]) < fraction(constants["epsilon_6_limit"])
    recursive_guard = Fraction(100, 97) ** 4
    assert recursive_guard < Fraction(13, 10)
    assert Fraction(27, 5) * Fraction(3, 2) / Fraction(1, 2) ** 5 == Fraction(1296, 5)
    derived = {
        "origin_gap": str(origin),
        "retained_gap": str(retained),
        "source_headroom": str(headroom),
        "owner_adverse_floor": str(owner_floor),
        "epsilon_6": pd["epsilon_6"],
        "recursive_guard": str(recursive_guard),
        "source_third_derivative": "1296/5",
    }
    payload = {
        "schema": "tect/lean-kernel-crosscheck/1.0",
        "run_kind": "independent",
        "audit_id": manifest["audit_id"],
        "claim_id": manifest["claim_id"],
        "result_id": manifest["result_id"],
        "verdict": "PASS",
        "derived": derived,
        "source_hashes": {key: item["sha256"] for key, item in manifest["inputs"].items()},
        "boundary": manifest["boundary"],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print("INDEPENDENT R-163 LEAN CROSSCHECK PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
