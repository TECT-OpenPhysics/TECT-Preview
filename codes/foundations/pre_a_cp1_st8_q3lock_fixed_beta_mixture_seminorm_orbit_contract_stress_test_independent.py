#!/usr/bin/env python3
"""Independent Fraction-only stress test for EXP-001064."""

from __future__ import annotations

import argparse
import json
import tempfile
from fractions import Fraction as F
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-fixed-beta-mixture-seminorm-orbit-contract-stress-test-manifest.json"
PRIOR = REPO / "strategy/pre-a-cp1-st8-q3lock-conditional-orbit-egf-remainder-composition-manifest.json"
OS_ROUTE = REPO / "strategy/pre-a-cp1-st8-q3lock-fixed-beta-os-mixture-common-wstar-route-split-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / (
    "2026-08-25-independent-pre-a-cp1-st8-q3lock-fixed-beta-mixture-seminorm-orbit-contract-stress-test/independent.json"
)


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with open(descriptor, "w", encoding="utf-8", newline="\n", closefd=True) as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
        Path(temporary).replace(path)
    finally:
        if Path(temporary).exists():
            Path(temporary).unlink()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    prior = json.loads(PRIOR.read_text(encoding="utf-8"))
    os_route = json.loads(OS_ROUTE.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(condition), "actual": str(actual), "expected": str(expected)})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    fixture = manifest["fixture"]
    p = F(fixture["polarization"])
    c = F(3, 5)
    s = F(4, 5)
    rho_11 = (1 + p) / 2
    rho_22 = (1 - p) / 2
    evolved_11 = s**2
    evolved_22 = c**2
    initial = 2 * rho_22
    evolved = 2 * (rho_11 * evolved_11 + rho_22 * evolved_22)
    gap = evolved - initial

    check("identity", manifest["exploration_id"] == "EXP-001064" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001064/T-054")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("prior identity", prior["exploration_id"] == "EXP-001063", prior["exploration_id"], "EXP-001063")
    check("OS route authority", os_route["exploration_id"] == "EXP-000800" and "Finite-volume Hamiltonian-evolved characters" in os_route["hamiltonian_identification_boundary"]["missing_identification"], os_route["exploration_id"], "fixed-beta route with missing embedding")
    check("polarization", p == F(fixture["polarization"]), p, fixture["polarization"])
    check("unitarity", c**2 + s**2 == 1, c**2 + s**2, 1)
    check("rotation diagonal", [evolved_11, evolved_22] == [F(value) for value in fixture["rotation_diagonal"]], [evolved_11, evolved_22], fixture["rotation_diagonal"])
    check("initial norm", initial == F(fixture["initial_squared_norm"]), initial, fixture["initial_squared_norm"])
    check("evolved norm", evolved == F(fixture["evolved_squared_norm"]), evolved, fixture["evolved_squared_norm"])
    check("growth gap", gap == F(fixture["growth_gap"]), gap, fixture["growth_gap"])
    check("noncontractive", evolved > initial, evolved, f">{initial}")

    scope = manifest["scope"]
    check("finite witness scope", scope["finite_counterexample_closed"] is True and scope["automatic_mixture_contractivity_closed"] is False, scope, "finite witness with automatic shortcut open")
    open_keys = ("finite_hamiltonian_os_embedding_closed", "actual_q3_four_context_theorem_proved", "actual_q3_factorial_history_proved", "all_time_orbit_bound_proved", "volume_uniform_direct_d_cauchy_closed", "delta_d_cauchy_closed", "product_core_density_closed", "exhaustion_independence_closed", "group_law_closed", "common_alpha_closed", "hamiltonian_os_identification_closed", "gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed")
    check("QFT firewall", all(scope[key] is False for key in open_keys), {key: scope[key] for key in open_keys}, "successor gates open")

    payload = {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "audit_id": "PA-CP1-ST8-Q3LOCK-FIXED-BETA-MIXTURE-SEMINORM-ORBIT-CONTRACT-STRESS-TEST",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "assertion_count": len(rows),
        "assertions": rows,
        "derived": {
            "polarization": str(p),
            "unitary_verified": True,
            "initial_squared_norm": str(initial),
            "evolved_squared_norm": str(evolved),
            "growth_gap": str(gap),
            "finite_counterexample_closed": True,
            "automatic_mixture_contractivity_closed": False,
            "finite_hamiltonian_os_embedding_closed": False,
            "all_time_orbit_bound_proved": False,
            "volume_uniform_direct_d_cauchy_closed": False,
            "delta_d_cauchy_closed": False,
        },
        "boundary": scope,
    }
    if not args.no_store:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT MIXTURE-SEMINORM-ORBIT-STRESS PASS {len(rows)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
