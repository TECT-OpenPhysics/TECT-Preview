"""Non-importing Fraction lane for the finite mobility counterpair."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pre-a13-fref-mobility-heat-root-nonidentifiability-manifest.json"
DEFAULT_OUTPUT = ROOT / "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/runs/2026-08-23-independent-fref-mobility-heat-root-nonidentifiability/result.json"


def sha(path: Path) -> str:
    raw = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(raw).hexdigest()


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


def derive(manifest: dict) -> dict:
    inputs = manifest["registered_inputs"]
    hessian = [Fraction(str(v)) for v in inputs["hessian_diagonal"]]
    mobility_a = [Fraction(str(v)) for v in inputs["mobility_a"]]
    mobility_b = [Fraction(str(v)) for v in inputs["mobility_b"]]
    beta = Fraction(str(inputs["beta"]))
    rates_a = [m * h for m, h in zip(mobility_a, hessian)]
    rates_b = [m * h for m, h in zip(mobility_b, hessian)]
    cancel = lambda m, h: m * (h + beta**-1 * (-beta * h))
    return {
        "hessian": [str(x) for x in hessian],
        "gibbs_covariance": [str(x**-1) for x in hessian],
        "mobility_a_rates": [str(x) for x in rates_a],
        "mobility_b_rates": [str(x) for x in rates_b],
        "stationary_current_a": [str(cancel(m, h)) for m, h in zip(mobility_a, hessian)],
        "stationary_current_b": [str(cancel(m, h)) for m, h in zip(mobility_b, hessian)],
        "same_stationary_density": all(cancel(m, h) == 0 for m, h in zip(mobility_a + mobility_b, hessian + hessian)),
        "different_heat_rates": rates_a != rates_b,
        "root_labels": list(inputs["root_labels"]),
        "root_rate_pairs": {
            "A": dict(zip(inputs["root_labels"], [str(x) for x in rates_a])),
            "B": dict(zip(inputs["root_labels"], [str(x) for x in rates_b])),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows = []

    def check(name: str, ok: bool, actual, expected) -> None:
        rows.append({"name": name, "pass": bool(ok), "actual": str(actual), "expected": str(expected)})
        if not ok:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("manifest identity", manifest["audit_id"] == "A13-FREF-MOBILITY-HEAT-ROOT-NONIDENTIFIABILITY", manifest["audit_id"], "A13-FREF-MOBILITY-HEAT-ROOT-NONIDENTIFIABILITY")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("no new negative", manifest["formal_integration"]["no_new_negative_ids"] == [], manifest["formal_integration"]["no_new_negative_ids"], [])
    for label, item in manifest["source_authorities"].items():
        path = ROOT / item["path"]
        check(f"source {label}", path.is_file() and sha(path) == item["sha256"], sha(path) if path.is_file() else None, item["sha256"])
    for label, item in manifest["files"].items():
        path = ROOT / item["path"]
        check(f"file {label}", path.is_file() and item["sha256"] != "TO_BE_FILLED" and sha(path) == item["sha256"], sha(path) if path.is_file() else None, item["sha256"])
    derived = derive(manifest)
    check("stationary currents vanish", derived["same_stationary_density"], derived["stationary_current_a"], ["0", "0"])
    check("rates A", derived["mobility_a_rates"] == ["1", "1"], derived["mobility_a_rates"], ["1", "1"])
    check("rates B", derived["mobility_b_rates"] == ["2", "3"], derived["mobility_b_rates"], ["2", "3"])
    check("rates differ", derived["different_heat_rates"], True, True)
    check("covariance unchanged", derived["gibbs_covariance"] == ["1", "1"], derived["gibbs_covariance"], ["1", "1"])
    payload = {"schema": "tect/a13-fref-mobility-heat-root-nonidentifiability-independent/1.0", "run_kind": "independent", "audit_id": manifest["audit_id"], "exploration_id": manifest["exploration_id"], "claim_id": manifest["claim_id"], "verdict": "PASS", "assertion_count": len(rows), "assertions": rows, "derived": derived, "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"), "boundary": manifest["boundary"]}
    if not args.no_store:
        atomic_json(args.output if args.output.is_absolute() else ROOT / args.output, payload)
    print(f"A13 FREF MOBILITY HEAT ROOT NONIDENTIFIABILITY INDEPENDENT PASS {len(rows)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
