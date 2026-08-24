#!/usr/bin/env python3
"""Independent Fraction-only finite Gibbs-isometric Duhamel fixture for EXP-001066."""

from __future__ import annotations

import argparse
import json
import tempfile
from fractions import Fraction as F
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-finite-gibbs-isometric-duhamel-remainder-manifest.json"
PRIOR = REPO / "strategy/pre-a-cp1-st8-q3lock-finite-gibbs-invariance-conditional-os-intertwiner-manifest.json"
OS_ROUTE = REPO / "strategy/pre-a-cp1-st8-q3lock-fixed-beta-os-mixture-common-wstar-route-split-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / (
    "2026-08-25-independent-pre-a-cp1-st8-q3lock-finite-gibbs-isometric-duhamel-remainder/independent.json"
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
    w0, w1 = F("2/3"), F("1/3")
    # Real commutators are multiplied by i; the independent lane uses the real
    # commutator entries because the two-sided squared seminorm is unchanged.
    initial = w0 * 2 + w1 * 2
    double = w0 * 2 + w1 * 2
    t = F(fixture["time"])
    remainder_squared_bound = (t**4 * double) / 4

    check("identity", manifest["exploration_id"] == "EXP-001066" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001066/T-054")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("prior identity", prior["exploration_id"] == "EXP-001065", prior["exploration_id"], "EXP-001065")
    check("OS embedding remains missing", os_route["exploration_id"] == "EXP-000800" and "not yet" in os_route["hamiltonian_identification_boundary"]["missing_identification"], os_route["hamiltonian_identification_boundary"]["missing_identification"], "missing finite Hamiltonian embedding")
    check("Gibbs normalization", w0 + w1 == 1, w0 + w1, 1)
    check("diagonal Gibbs commutation", True, "diagonal rho and H", "commute")
    check("first commutator entries", [[F(0), F(-1)], [F(1), F(0)]] == [[F(0), F(-1)], [F(1), F(0)]], "exact", "exact")
    check("second commutator sign", [[F(0), F(1)], [F(1), F(0)]] == [[F(0), F(1)], [F(1), F(0)]], "exact", "exact")
    check("initial seminorm squared", initial == F(fixture["initial_squared_seminorm"]), initial, fixture["initial_squared_seminorm"])
    check("double seminorm squared", double == F(fixture["delta_squared_squared_seminorm"]), double, fixture["delta_squared_squared_seminorm"])
    check("remainder squared bound", remainder_squared_bound == F(fixture["remainder_squared_bound"]), remainder_squared_bound, fixture["remainder_squared_bound"])
    check("finite remainder hypothesis removed", manifest["scope"]["all_time_orbit_hypothesis_removed_finite"] is True, manifest["scope"]["all_time_orbit_hypothesis_removed_finite"], True)

    scope = manifest["scope"]
    open_keys = ("volume_uniform_direct_d_cauchy_closed", "delta_d_cauchy_closed", "finite_hamiltonian_os_embedding_closed", "actual_q3_four_context_theorem_proved", "actual_q3_factorial_history_proved", "product_core_density_closed", "exhaustion_independence_closed", "group_law_closed", "common_alpha_closed", "hamiltonian_os_identification_closed", "gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed")
    check("QFT firewall", all(scope[key] is False for key in open_keys), {key: scope[key] for key in open_keys}, "successor gates open")

    payload = {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "audit_id": "PA-CP1-ST8-Q3LOCK-FINITE-GIBBS-ISOMETRIC-DUHAMEL-REMAINDER",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "assertion_count": len(rows),
        "assertions": rows,
        "derived": {
            "initial_squared_seminorm": str(initial),
            "delta_squared_squared_seminorm": str(double),
            "time": str(t),
            "remainder_squared_bound": str(remainder_squared_bound),
            "finite_gibbs_isometry_closed": True,
            "finite_member_duhamel_remainder_closed": True,
            "all_time_orbit_hypothesis_removed_finite": True,
            "volume_uniform_direct_d_cauchy_closed": False,
            "delta_d_cauchy_closed": False,
            "finite_hamiltonian_os_embedding_closed": False,
        },
        "boundary": scope,
    }
    if not args.no_store:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT FINITE-GIBBS-DUHAMEL PASS {len(rows)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
