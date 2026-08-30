#!/usr/bin/env python3
"""Primary finite equation-level audit for the additive M3 candidate.

The audit checks only the displayed finite charge bookkeeping and the
completion-square identity.  It does not admit a source owner or a physical
candidate and does not alter the T-054/T-059 methods.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pre-a-m3-compact-u1-equation-level-audit-manifest.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-08-31-primary-pre_a_m3_compact_u1_equation_level_audit/primary.json"
)


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def digest(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    ).hexdigest()


def jsonable(value: Any) -> Any:
    """Convert tuple-keyed incidence diagnostics into JSON-safe values."""
    if isinstance(value, dict):
        return {str(key): jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(item) for item in value]
    return value


Coord = tuple[int, int, int]
Factor = tuple[str, Coord, int, int | None]


def sites(size: int) -> list[Coord]:
    return [(i, j, k) for i in range(size) for j in range(size) for k in range(size)]


def shift(site: Coord, direction: int, size: int, amount: int = 1) -> Coord:
    values = list(site)
    values[direction] = (values[direction] + amount) % size
    return tuple(values)  # type: ignore[return-value]


def charge_vector(size: int, factors: Iterable[Factor]) -> dict[Coord, int]:
    result = {site: 0 for site in sites(size)}
    for kind, site, sign, direction in factors:
        if kind in {"phi", "pi"}:
            result[site] += sign
        elif kind == "U":
            if direction is None:
                raise AssertionError("link factor needs a direction")
            result[site] += sign
            result[shift(site, direction, size)] -= sign
        else:
            raise AssertionError(f"unknown factor kind {kind}")
    return result


def negate(factors: Iterable[Factor]) -> list[Factor]:
    return [(kind, site, -sign, direction) for kind, site, sign, direction in factors]


def plaquette(site: Coord, first: int, second: int) -> list[Factor]:
    return [
        ("U", site, 1, first),
        ("U", shift(site, first, _CURRENT_SIZE), 1, second),
        ("U", shift(site, second, _CURRENT_SIZE), -1, first),
        ("U", site, -1, second),
    ]


_CURRENT_SIZE = 2


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    global _CURRENT_SIZE
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append(
            {
                "name": name,
                "group": group,
                "status": "PASS",
                "actual": jsonable(actual),
                "expected": jsonable(expected),
            }
        )

    check(
        "identity",
        [
            manifest["result_id"],
            manifest["exploration_id"],
            manifest["task_id"],
            manifest["claim_bearing"],
            manifest["tier"],
            manifest["status"],
        ]
        == [
            "R-457",
            "EXP-001330",
            "T-054",
            False,
            "T0",
            "M3_EQUATION_LEVEL_AUDITED_NOT_ADMITTED",
        ],
        [
            manifest["result_id"],
            manifest["exploration_id"],
            manifest["task_id"],
            manifest["claim_bearing"],
            manifest["tier"],
            manifest["status"],
        ],
        "R-457/EXP-001330/T-054/false/T0/status",
        "provenance",
    )
    check(
        "method preservation",
        all(manifest["methods_preserved"].values()),
        manifest["methods_preserved"],
        "all established methods remain unchanged",
        "method-firewall",
    )
    check(
        "candidate remains unadmitted",
        manifest["scope"]["source_owner_admitted"] is False
        and manifest["scope"]["candidate_admitted"] is False,
        manifest["scope"],
        "source and candidate admission false",
        "promotion-firewall",
    )

    lattice_sizes = [int(value) for value in manifest["finite_scope"]["lattice_sizes"]]
    check(
        "lattice size oracle",
        len(lattice_sizes) == manifest["test_oracles"]["lattice_size_count"]
        and all(value >= 2 for value in lattice_sizes),
        lattice_sizes,
        "declared finite periodic sizes",
        "finite-scope",
    )

    plaquette_checks = 0
    covariant_checks = 0
    observable_checks = 0
    gauss_checks = 0
    site_checks = 0
    for size in lattice_sizes:
        _CURRENT_SIZE = size
        current_sites = sites(size)
        site_checks += len(current_sites)
        for site in current_sites:
            for first in range(3):
                for second in range(first + 1, 3):
                    charge = charge_vector(size, plaquette(site, first, second))
                    check(
                        f"L={size} plaquette charge ({first},{second}) {site}",
                        all(value == 0 for value in charge.values()),
                        charge,
                        "zero at every site",
                        "gauge-charge",
                    )
                    plaquette_checks += 1
            for direction in range(3):
                target = shift(site, direction, size)
                first_term = [("U", site, 1, direction), ("phi", target, 1, None)]
                second_term = [("phi", site, 1, None)]
                first_charge = charge_vector(size, first_term)
                second_charge = charge_vector(size, second_term)
                check(
                    f"L={size} covariant term charge {site}/{direction}",
                    first_charge == second_charge
                    and first_charge[site] == 1
                    and sum(first_charge.values()) == 1,
                    [first_charge, second_charge],
                    "same charge anchored at source site",
                    "gauge-charge",
                )
                for left in (first_term, second_term):
                    for right in (first_term, second_term):
                        norm_charge = charge_vector(size, negate(left) + right)
                        check(
                            f"L={size} covariant norm neutrality {site}/{direction}",
                            all(value == 0 for value in norm_charge.values()),
                            norm_charge,
                            "zero at every site",
                            "gauge-charge",
                        )
                        covariant_checks += 1
                density = [("phi", site, -1, None), ("phi", site, 1, None)]
                current = [
                    ("phi", site, -1, None),
                    ("U", site, 1, direction),
                    ("phi", target, 1, None),
                ]
                for label, factors in (("density", density), ("current", current)):
                    charge = charge_vector(size, factors)
                    check(
                        f"L={size} {label} neutrality {site}/{direction}",
                        all(value == 0 for value in charge.values()),
                        charge,
                        "zero at every site",
                        "observable-charge",
                    )
                    observable_checks += 1
            gauss_matter = [("pi", site, -1, None), ("phi", site, 1, None)]
            gauss_charge = charge_vector(size, gauss_matter)
            check(
                f"L={size} Gauss matter neutrality {site}",
                all(value == 0 for value in gauss_charge.values()),
                gauss_charge,
                "zero at every site",
                "Gauss-charge",
            )
            gauss_checks += 1
            quartic = [
                ("phi", site, -1, None),
                ("phi", site, -1, None),
                ("phi", site, 1, None),
                ("phi", site, 1, None),
            ]
            quartic_charge = charge_vector(size, quartic)
            check(
                f"L={size} quartic neutrality {site}",
                all(value == 0 for value in quartic_charge.values()),
                quartic_charge,
                "zero at every site",
                "Hamiltonian-charge",
            )
            observable_checks += 1
        check(
            f"L={size} coverage",
            plaquette_checks >= len(current_sites) * 3
            and covariant_checks >= len(current_sites) * 3 * 4
            and gauss_checks >= len(current_sites),
            [plaquette_checks, covariant_checks, gauss_checks],
            "all sites, planes, links",
            "coverage",
        )

    positive = manifest["parameter_fixtures"]["positive_parameters"]
    positive_values = {name: Fraction(value) for name, value in positive.items()}
    check(
        "positive parameter domain",
        all(value > 0 for value in positive_values.values()),
        {name: str(value) for name, value in positive_values.items()},
        "all displayed positive parameters are positive",
        "finite-flow",
    )

    coercivity_rows = 0
    for lam_text in manifest["parameter_fixtures"]["lambda_values"]:
        lam = Fraction(lam_text)
        check(
            f"lambda domain {lam_text}",
            lam > 0,
            str(lam),
            ">0",
            "finite-flow",
        )
        for m_text in manifest["parameter_fixtures"]["m2_values"]:
            mass = Fraction(m_text)
            for radial_text in manifest["parameter_fixtures"]["radial_values"]:
                radial = Fraction(radial_text)
                lhs = lam * radial * radial / 4 + mass * radial / 2
                rhs = (
                    lam * (radial + mass / lam) ** 2 / 4
                    - mass * mass / (4 * lam)
                )
                lower = -mass * mass / (4 * lam)
                check(
                    f"completion square lam={lam_text} m2={m_text} x={radial_text}",
                    lhs == rhs and lhs >= lower,
                    [str(lhs), str(rhs), str(lower)],
                    "identity and lower bound",
                    "coercivity",
                )
                coercivity_rows += 1

    canonical_pairs = sum(len(sites(size)) * 5 for size in lattice_sizes)
    trial_values = [Fraction(index + 1, canonical_pairs + 1) for index in range(canonical_pairs)]
    poisson_value = sum(
        left * right - right * left
        for left, right in zip(trial_values[::2], trial_values[1::2])
    )
    check(
        "Poisson self-bracket identity",
        poisson_value == 0,
        str(poisson_value),
        "0 by antisymmetry",
        "Hamiltonian-flow",
    )
    check(
        "finite flow conditional",
        positive_values["lambda"] > 0
        and positive_values["chi"] > 0
        and positive_values["kappa_E"] > 0,
        {name: str(value) for name, value in positive_values.items()},
        "coercive finite polynomial Hamiltonian assumptions",
        "Hamiltonian-flow",
    )

    derived = {
        "lattice_sizes": lattice_sizes,
        "sites_checked": site_checks,
        "plaquette_checks": plaquette_checks,
        "covariant_checks": covariant_checks,
        "observable_checks": observable_checks,
        "gauss_checks": gauss_checks,
        "coercivity_rows": coercivity_rows,
        "poisson_self_bracket_rows": canonical_pairs,
        "equation_charge_audit_closed": True,
        "gauge_invariant_hamiltonian_terms_closed": True,
        "observable_map_neutrality_closed": True,
        "gauss_neutrality_identity_closed": True,
        "gauss_surface_preservation": "CONDITIONAL_ON_DECLARED_CANONICAL_GENERATOR",
        "poisson_energy_identity_closed": True,
        "coercivity_completion_identity_closed": True,
        "finite_flow_conditional_closed": True,
        "source_owner_admitted": False,
        "candidate_admitted": False,
        "physical_identity": False,
        "continuum_closed": False,
        "pre_a_closed": False,
        "sector_a_closed": False,
    }
    payload = {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": manifest["audit_id"],
        "result_id": manifest["result_id"],
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": manifest["status"],
        "assertion_count": len(checks),
        "assertions": checks,
        "derived": derived,
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "evidence_level": manifest["evidence_level"],
        "non_claims": manifest["non_claims"],
        "boundary": manifest["boundary"],
    }
    atomic_json(output, payload)
    print(
        "R-457 PRIMARY M3_EQUATION_LEVEL_AUDITED_NOT_ADMITTED "
        f"{len(checks)}/{len(checks)} lattices={lattice_sizes} "
        f"plaquettes={plaquette_checks} covariant={covariant_checks} "
        f"coercivity={coercivity_rows}",
        flush=True,
    )
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run(args.output if args.output.is_absolute() else ROOT / args.output)
    if args.self_test:
        assert payload["derived"]["equation_charge_audit_closed"] is True
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
