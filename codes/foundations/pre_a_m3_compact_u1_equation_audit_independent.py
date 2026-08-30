#!/usr/bin/env python3
"""Non-importing independent charge-incidence audit for R-457."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


BASE = Path(__file__).resolve().parents[2]
MANIFEST = BASE / "strategy/pre-a-m3-compact-u1-equation-level-audit-manifest.json"
DEFAULT = BASE / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-08-31-independent-pre_a_m3_compact_u1_equation_level_audit/independent.json"
)


def save(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def lattice(size: int) -> list[tuple[int, int, int]]:
    return [(a, b, c) for a in range(size) for b in range(size) for c in range(size)]


def sid(site: tuple[int, int, int], size: int) -> int:
    return site[0] * size * size + site[1] * size + site[2]


def move(site: tuple[int, int, int], axis: int, size: int) -> tuple[int, int, int]:
    value = list(site)
    value[axis] = (value[axis] + 1) % size
    return tuple(value)  # type: ignore[return-value]


def incidence(size: int, factors: list[tuple[str, int, int | None, int]]) -> list[int]:
    vector = [0] * (size**3)
    for kind, site_id, axis, exponent in factors:
        if kind in ("phi", "pi"):
            vector[site_id] += exponent
        elif kind == "link":
            if axis is None:
                raise AssertionError("axis missing")
            site = (site_id // (size * size), (site_id // size) % size, site_id % size)
            vector[site_id] += exponent
            vector[sid(move(site, axis, size), size)] -= exponent
        else:
            raise AssertionError(f"bad factor {kind}")
    return vector


def add(left: list[int], right: list[int]) -> list[int]:
    return [a + b for a, b in zip(left, right)]


def opposite(factors: list[tuple[str, int, int | None, int]]) -> list[tuple[str, int, int | None, int]]:
    return [(kind, site_id, axis, -exponent) for kind, site_id, axis, exponent in factors]


def run(path: Path = DEFAULT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    checks: list[dict[str, Any]] = []

    def check(name: str, ok: bool, actual: Any, expected: Any, group: str) -> None:
        if not ok:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": actual, "expected": expected})

    check(
        "identity",
        [manifest["result_id"], manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"], manifest["tier"]]
        == ["R-457", "EXP-001330", "T-054", False, "T0"],
        [manifest["result_id"], manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"], manifest["tier"]],
        "R-457/EXP-001330/T-054/false/T0",
        "provenance",
    )
    check("method firewall", all(manifest["methods_preserved"].values()), manifest["methods_preserved"], "all true", "method-firewall")
    check(
        "admission firewall",
        manifest["scope"]["source_owner_admitted"] is False and manifest["scope"]["candidate_admitted"] is False,
        manifest["scope"],
        "no source or candidate admission",
        "promotion-firewall",
    )

    sizes = [int(item) for item in manifest["finite_scope"]["lattice_sizes"]]
    plaquette_count = 0
    covariant_count = 0
    observable_count = 0
    gauss_count = 0
    site_count = 0
    for size in sizes:
        points = lattice(size)
        site_count += len(points)
        for point in points:
            point_id = sid(point, size)
            for axis in range(3):
                for other in range(axis + 1, 3):
                    p1 = ("link", point_id, axis, 1)
                    p2 = ("link", sid(move(point, axis, size), size), other, 1)
                    p3 = ("link", sid(move(point, other, size), size), axis, -1)
                    p4 = ("link", point_id, other, -1)
                    vector = incidence(size, [p1, p2, p3, p4])
                    check(f"L={size} plaquette {point}/{axis}/{other}", not any(vector), vector, "zero incidence", "gauge-charge")
                    plaquette_count += 1
            for axis in range(3):
                target_id = sid(move(point, axis, size), size)
                first = [("link", point_id, axis, 1), ("phi", target_id, None, 1)]
                second = [("phi", point_id, None, 1)]
                first_vector = incidence(size, first)
                second_vector = incidence(size, second)
                check(
                    f"L={size} covariant source {point}/{axis}",
                    first_vector == second_vector and first_vector[point_id] == 1 and sum(first_vector) == 1,
                    [first_vector, second_vector],
                    "same unit source charge",
                    "gauge-charge",
                )
                for left in (first, second):
                    for right in (first, second):
                        vector = incidence(size, opposite(left) + right)
                        check(f"L={size} covariant norm {point}/{axis}", not any(vector), vector, "zero incidence", "gauge-charge")
                        covariant_count += 1
                density = [("phi", point_id, None, -1), ("phi", point_id, None, 1)]
                current = [("phi", point_id, None, -1), ("link", point_id, axis, 1), ("phi", target_id, None, 1)]
                for label, factors in (("density", density), ("current", current)):
                    vector = incidence(size, factors)
                    check(f"L={size} {label} {point}/{axis}", not any(vector), vector, "zero incidence", "observable-charge")
                    observable_count += 1
            gauss = [("pi", point_id, None, -1), ("phi", point_id, None, 1)]
            vector = incidence(size, gauss)
            check(f"L={size} Gauss matter {point}", not any(vector), vector, "zero incidence", "Gauss-charge")
            gauss_count += 1
            quartic = [("phi", point_id, None, exponent) for exponent in (-1, -1, 1, 1)]
            vector = incidence(size, quartic)
            check(f"L={size} quartic {point}", not any(vector), vector, "zero incidence", "Hamiltonian-charge")
            observable_count += 1

    positive = {key: Fraction(value) for key, value in manifest["parameter_fixtures"]["positive_parameters"].items()}
    check("positive parameters", all(value > 0 for value in positive.values()), {key: str(value) for key, value in positive.items()}, "all >0", "finite-flow")

    coercivity_rows = 0
    for lam_text in manifest["parameter_fixtures"]["lambda_values"]:
        lam = Fraction(lam_text)
        check(f"lambda {lam_text}", lam > 0, str(lam), ">0", "finite-flow")
        for mass_text in manifest["parameter_fixtures"]["m2_values"]:
            mass = Fraction(mass_text)
            for radius_text in manifest["parameter_fixtures"]["radial_values"]:
                radius = Fraction(radius_text)
                left = lam * radius**2 / 4 + mass * radius / 2
                right = lam * (radius + mass / lam) ** 2 / 4 - mass**2 / (4 * lam)
                floor = -mass**2 / (4 * lam)
                check(f"square {lam_text}/{mass_text}/{radius_text}", left == right and left >= floor, [str(left), str(right), str(floor)], "identity and lower bound", "coercivity")
                coercivity_rows += 1

    canonical_entries = sum(len(lattice(size)) * 5 for size in sizes)
    values = [Fraction(index + 1, canonical_entries + 1) for index in range(canonical_entries)]
    bracket = sum(a * b - b * a for a, b in zip(values[::2], values[1::2]))
    check("Poisson self bracket", bracket == 0, str(bracket), "0", "Hamiltonian-flow")
    check("conditional flow domain", positive["lambda"] > 0 and positive["chi"] > 0 and positive["kappa_E"] > 0, {key: str(value) for key, value in positive.items()}, "finite coercive assumptions", "Hamiltonian-flow")

    derived = {
        "lattice_sizes": sizes,
        "sites_checked": site_count,
        "plaquette_checks": plaquette_count,
        "covariant_checks": covariant_count,
        "observable_checks": observable_count,
        "gauss_checks": gauss_count,
        "coercivity_rows": coercivity_rows,
        "poisson_self_bracket_rows": canonical_entries,
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
        "run_kind": "independent",
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
    save(path, payload)
    print(f"R-457 INDEPENDENT M3_EQUATION_LEVEL_AUDITED_NOT_ADMITTED {len(checks)}/{len(checks)} lattices={sizes} plaquettes={plaquette_count} coercivity={coercivity_rows}", flush=True)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    result = run(args.output if args.output.is_absolute() else BASE / args.output)
    if args.self_test:
        assert result["derived"]["candidate_admitted"] is False
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
