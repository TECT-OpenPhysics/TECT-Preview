#!/usr/bin/env python3
"""PAH-OMC-030 frozen-source compatibility and missing-bridge audit."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PREREG = ROOT / "strategy/pa-hyp/PAH-OMC-030-prereg-v1.json"
RUN_DEFAULT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-09-pah-omc030-bridge/primary.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def run() -> dict:
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    checks: dict[str, bool] = {}
    pin_failures = []
    for rel, expected in prereg["source_files"].items():
        actual = sha256(ROOT / rel)
        if actual != expected:
            pin_failures.append({"path": rel, "expected": expected, "actual": actual})
    checks["source_hashes"] = not pin_failures

    r510 = load("strategy/pa-hyp/PAH-OMC-017-result-v1.json")
    r511 = load("strategy/pa-hyp/PAH-OMC-018-result-v1.json")
    r514 = load("strategy/pa-hyp/PAH-OMC-020-fixedn-temporal-result-v1.json")
    r568 = load("strategy/pa-hyp/PAH-OMC-029-result-v1.json")

    checks["same_model_parameters"] = (
        prereg["exact_scope"]["parameters"]
        == "K=2, M_s=1, epsilon=1/2, beta=nu=1, m2=theta=0 and all remaining displayed OMC-016 couplings one."
    )
    checks["terminal_square_retained"] = "terminal unsplit square" in (
        prereg["exact_scope"]["boundary"] + " " + r514["exact_scope"]["geometry"]
    )
    checks["ordered_regulators"] = "j->infinity" in prereg["exact_scope"]["order"] and "anchored n" in prereg["exact_scope"]["order"]
    checks["common_domain_matches"] = "finite-prefix" in r511["exact_scope"]["domain"] and "finite-prefix" in prereg["exact_scope"]["domain"]
    checks["r514_fixed_n_only"] = "At fixed n" in r514["exact_scope"]["order"] and "anchored n" in " ".join(r514["non_claims"])
    checks["r568_conditional"] = bool(r568["conditional"]) and "original finite-semigroup convergence" in " ".join(r568["non_claims"])
    checks["r510_local_not_full"] = (
        "Original rates and external Markov time are unchanged" in r510["exact_scope"]["dynamics"]
        and "infinite-volume dynamics" in " ".join(r510["non_claims"]).lower()
    )

    missing = prereg["required_bridges"]
    checks["missing_un_n_bridge_is_explicit"] = "U_n" in missing["N2a"]
    checks["missing_liminf_bridge_is_explicit"] = "liminf" in missing["N2b"]
    checks["missing_boundary_bridge_is_explicit"] = "boundary" in missing["N2c_N4"]
    checks["missing_minimal_identification_is_explicit"] = "minimal" in missing["N2d"]
    checks["fixed_n_constants_not_uniform"] = "fixed `n`" in (ROOT / "strategy/pa-hyp/PAH-OMC-030-certificate.md").read_text(encoding="utf-8")

    status = "HOLD_FOR_EVIDENCE"
    all_compatibility = all(checks.values())
    return {
        "schema": "tect/pah-omc030-primary/1.0",
        "status": "PASS" if all_compatibility else "FAIL",
        "verdict": status,
        "result_id": "R-569",
        "exploration_id": "EXP-001721",
        "event_id": "20260909-pah-omc-030-finite-strip-markov-bridge",
        "source_hashes": prereg["source_files"],
        "checks": checks,
        "pin_failures": pin_failures,
        "derived_boundary": {
            "r514_fixed_n_error": "2*T*H_(n,K,g)*L_(n,K,T,g)*h_j",
            "uniformity_status": "not supplied in R-514; H and L retain n and K dependence",
            "target_boundary_status": "R-568 controls the already constructed target H, not the finite nu_n family"
        },
        "missing_bridge": "A source-authorized U_n compatible with the unsplit terminal square, arbitrary-sequence liminf/recovery, and compact-time N2c/N4 boundary escape for the original unbounded rates.",
        "lean_scope": {
            "status": "PARTIAL_ONLY",
            "available": ["R-514 finite algebra declarations", "R-568 fixed-target uniqueness declarations"],
            "not_formalized": ["U_n", "Mosco liminf/recovery", "finite-rate boundary escape", "anchored-n semigroup convergence"]
        },
        "non_claims": [
            "No PAH finite-to-target convergence theorem",
            "No new model, rate, state, carrier, time or limit order",
            "No physical Pre-A, QFT, gravity, continuum, Yang-Mills, mass-gap or TOE conclusion"
        ]
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", type=Path, default=RUN_DEFAULT)
    args = parser.parse_args()
    payload = run()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"PAH-OMC-030 PRIMARY: {payload['status']}; verdict={payload['verdict']}; missing common-space temporal bridge")
    return 0 if args.check and payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
