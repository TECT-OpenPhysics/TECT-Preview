#!/usr/bin/env python3
"""Auxiliary seam/min--max audit for the EXP-000780 Q3LOCK pressure route.

The script recomputes the periodic/open edge counts, the corrected periodic
onsite allocation, the optimized Young constant in the seam estimate, and the
resulting density scale for ``eta=L**(-1/2)``.  It is a finite diagnostic for
the written proof; it is not an operator theorem and it does not certify a
thermodynamic limit, phase transition, or publication claim.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import random
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = REPO / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-05-q3lock-pressure-seam-minmax-audit/result.json"
)


def normalized_sha256(path: Path) -> str:
    """Hash a text file after normalizing line endings for provenance."""

    return hashlib.sha256(
        path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    ).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


@dataclass
class Audit:
    rows: list[dict[str, Any]]

    def __init__(self) -> None:
        self.rows = []

    def check(self, name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{group}: {name}: {actual!r} != {expected!r}")
        self.rows.append(
            {
                "name": name,
                "group": group,
                "status": "PASS",
                "actual": str(actual),
                "expected": str(expected),
            }
        )


def sites(length: int) -> list[tuple[int, int, int]]:
    return [
        (x, y, z)
        for x in range(length)
        for y in range(length)
        for z in range(length)
    ]


def open_edges(length: int) -> list[tuple[tuple[int, int, int], tuple[int, int, int], int]]:
    """Return positive-direction open bonds, retaining direction labels."""

    edges: list[tuple[tuple[int, int, int], tuple[int, int, int], int]] = []
    for site in sites(length):
        for direction in range(3):
            target = list(site)
            target[direction] += 1
            if target[direction] < length:
                edges.append((site, tuple(target), direction))
    return edges


def periodic_edges(
    length: int,
) -> list[tuple[tuple[int, int, int], tuple[int, int, int], int, bool]]:
    """Return positive-direction periodic bonds and mark wrap/seam bonds."""

    edges: list[tuple[tuple[int, int, int], tuple[int, int, int], int, bool]] = []
    for site in sites(length):
        for direction in range(3):
            target = list(site)
            wraps = target[direction] == length - 1
            target[direction] = (target[direction] + 1) % length
            edges.append((site, tuple(target), direction, wraps))
    return edges


def seam_incidence(length: int) -> dict[tuple[int, int, int], int]:
    incidence = {site: 0 for site in sites(length)}
    for left, right, _direction, wraps in periodic_edges(length):
        if wraps:
            incidence[left] += 1
            incidence[right] += 1
    return incidence


def seam_bound_constants(length: int, c: float, g: float, eta: float) -> dict[str, float]:
    """Compute the Young split from graph incidence, not pasted constants."""

    seam_scalar_edges = sum(1 for *_rest, wraps in periodic_edges(length) if wraps)
    endpoint_occurrences = 2 * seam_scalar_edges
    max_incidence = max(seam_incidence(length).values())
    q_coefficient = g / 8.0
    per_endpoint_quartic_coefficient = eta * q_coefficient / max_incidence
    per_endpoint_constant = c * c / (4.0 * per_endpoint_quartic_coefficient)
    return {
        "seam_scalar_edges": float(seam_scalar_edges),
        "endpoint_occurrences_per_component": float(endpoint_occurrences),
        "max_seam_incidence": float(max_incidence),
        "q_coefficient": q_coefficient,
        "per_endpoint_quartic_coefficient": per_endpoint_quartic_coefficient,
        "per_endpoint_constant": per_endpoint_constant,
        "all_component_endpoint_occurrences": float(8 * endpoint_occurrences),
        "all_component_constant": 8.0 * endpoint_occurrences * per_endpoint_constant,
    }


def seam_energy(values: dict[tuple[int, int, int], float], length: int, c: float) -> float:
    total = 0.0
    for left, right, _direction, wraps in periodic_edges(length):
        if wraps:
            total += 0.5 * c * (values[left] - values[right]) ** 2
    return total


def quartic_energy(values: dict[tuple[int, int, int], float], g: float) -> float:
    return (g / 8.0) * sum(value**4 for value in values.values())


def build_payload() -> dict[str, Any]:
    audit = Audit()
    component_count = 8
    dimensions = 3
    parameters = {"c": 1.7, "g": 2.3}
    edge_rows: list[dict[str, Any]] = []

    for length in (2, 4, 6, 8):
        volume = length**dimensions
        open_count = len(open_edges(length))
        periodic_count = len(periodic_edges(length))
        seam_count = sum(1 for *_rest, wraps in periodic_edges(length) if wraps)
        expected_open = dimensions * length ** (dimensions - 1) * (length - 1)
        expected_periodic = dimensions * volume
        expected_seam = dimensions * length ** (dimensions - 1)
        audit.check("open positive-direction edge count", open_count == expected_open, open_count, expected_open, "edge_count")
        audit.check("periodic positive-direction edge count", periodic_count == expected_periodic, periodic_count, expected_periodic, "edge_count")
        audit.check("seam edge count", seam_count == expected_seam, seam_count, expected_seam, "edge_count")
        audit.check("open plus seam equals periodic", open_count + seam_count == periodic_count, open_count + seam_count, periodic_count, "edge_count")
        incidence = seam_incidence(length)
        audit.check("seam endpoint occurrence count", sum(incidence.values()) == 2 * seam_count, sum(incidence.values()), 2 * seam_count, "edge_count")
        audit.check("seam maximum incidence", max(incidence.values()) == dimensions, max(incidence.values()), dimensions, "edge_count")
        edge_rows.append(
            {
                "L": length,
                "V": volume,
                "open_scalar_edges": open_count,
                "periodic_scalar_edges": periodic_count,
                "seam_scalar_edges": seam_count,
                "seam_endpoint_occurrences_all_components": component_count * 2 * seam_count,
            }
        )

    # The corrected spatial expansion is checked on a constant field.  The
    # edge list is explicit, so L=2 retains its periodic multiplicity.
    c = parameters["c"]
    for length in (2, 4, 6):
        volume = length**dimensions
        scalar_field = {site: 1.0 for site in sites(length)}
        original_per_component = seam_energy(scalar_field, length, c)
        full_original = component_count * (0.5 * c) * sum(
            (scalar_field[left] - scalar_field[right]) ** 2
            for left, right, _direction, _wraps in periodic_edges(length)
        )
        # The expanded periodic expression has degree six and one undirected
        # term per positive-direction bond occurrence.
        expanded_per_component = (dimensions * c) * volume - c * len(periodic_edges(length))
        audit.check("constant field original seam energy", original_per_component == 0.0, original_per_component, 0.0, "onsite_allocation")
        audit.check("constant field full difference energy", full_original == 0.0, full_original, 0.0, "onsite_allocation")
        audit.check("corrected onsite/pair expansion", abs(expanded_per_component) < 1e-12, expanded_per_component, 0.0, "onsite_allocation")
        old_expanded = (dimensions * c / 2.0) * volume - c * len(periodic_edges(length))
        audit.check("old half-allocation is rejected", abs(old_expanded) > 0.0, old_expanded, "nonzero", "hostile")

    # Test the optimized seam Young split on deterministic and seeded values.
    g = parameters["g"]
    random_source = random.Random(20260905)
    young_rows: list[dict[str, Any]] = []
    for length in (2, 4, 6, 8):
        eta = length ** (-0.5)
        constants = seam_bound_constants(length, c, g, eta)
        per_component_constant = (
            constants["endpoint_occurrences_per_component"]
            * constants["per_endpoint_constant"]
        )
        for label, scale in (("zero", 0.0), ("unit", 1.0), ("random", 2.0)):
            values = {
                site: (scale * (1.0 if (sum(site) % 2 == 0) else -1.0))
                for site in sites(length)
            }
            if label == "random":
                values = {site: scale * (random_source.random() - 0.5) for site in sites(length)}
            left = seam_energy(values, length, c)
            right = eta * quartic_energy(values, g) + per_component_constant
            # Eight components are represented by the same scalar field in
            # this check, hence both sides are multiplied by eight.  The
            # constant above is deliberately per component; the all-component
            # constant is used only in the density calculation below.
            left *= component_count
            right *= component_count
            audit.check("Young seam bound fixture", left <= right + 1e-12, left, "<= bound", "young")
            young_rows.append({"L": length, "fixture": label, "lhs": left, "rhs": right})

    # With eta=L^(-1/2), the additive seam density tends to zero.  The
    # generic b_J term is kept as an explicit test input, while the derived
    # seam constant comes from the graph above.
    b_j = 0.9
    density_rows: list[dict[str, float]] = []
    previous = math.inf
    for length in (2, 4, 8, 16, 32, 64):
        eta = length ** (-0.5)
        constants = seam_bound_constants(length, c, g, eta)
        d_total = eta * b_j * length**dimensions + constants["all_component_constant"]
        density = d_total / (component_count * length**dimensions)
        audit.check("optimized seam density positive", density > 0.0, density, ">0", "minmax_scale")
        audit.check("optimized seam density decreases", density < previous, density, previous, "minmax_scale")
        previous = density
        density_rows.append({"L": float(length), "eta": eta, "D_total": d_total, "density": density})
    audit.check(
        "seam density scaling diagnostic",
        density_rows[-1]["density"] < density_rows[0]["density"] / 3.0,
        density_rows[-1]["density"],
        "< one third of the L=2 value",
        "minmax_scale",
    )

    # Hostile factor mutations must be observable in the same convention.
    length = 4
    volume = length**dimensions
    correct_constant_field = dimensions * c * volume - c * len(periodic_edges(length))
    half_incidence_field = (dimensions * c / 2.0) * volume - c * len(periodic_edges(length))
    audit.check("correct constant-field cancellation", abs(correct_constant_field) < 1e-12, correct_constant_field, 0.0, "hostile")
    audit.check("half onsite mutation changes constant mode", abs(half_incidence_field) > 1e-12, half_incidence_field, "nonzero", "hostile")
    eta = length ** (-0.5)
    constants = seam_bound_constants(length, c, g, eta)
    wrong_density = (eta * b_j * volume + constants["all_component_constant"]) / volume
    correct_density = (eta * b_j * volume + constants["all_component_constant"]) / (component_count * volume)
    audit.check("component normalization is visible", wrong_density > correct_density, wrong_density, "> correct density", "hostile")

    script_path = Path(__file__).resolve()
    return {
        "schema": "tect/q3lock-pressure-seam-minmax-audit/0.1",
        "script_version": __version__,
        "authority_chain": ["EXP-000780", "EXP-000781", "EXP-000782"],
        "result_id": "R-498",
        "exploration_id": "EXP-001580",
        "claim_bearing": False,
        "diagnostic_fixture_not_proof": True,
        "assertions": {"passed": len(audit.rows), "total": len(audit.rows), "rows": audit.rows},
        "parameters": {**parameters, "component_count": component_count, "dimensions": dimensions},
        "derived": {"edge_rows": edge_rows, "young_rows": young_rows, "density_rows": density_rows},
        "files": {"script": str(script_path.relative_to(REPO)).replace("\\", "/"), "script_sha256": normalized_sha256(script_path)},
        "verdict": "PASS",
        "boundary": "Finite edge-count, corrected onsite-allocation, Young-constant and seam-density diagnostics only. No operator min--max theorem, thermodynamic pressure limit, phase conclusion, claim promotion, manuscript or PDF.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    atomic_json(args.output, payload)
    summary = payload["assertions"]
    print(f"EXP-001580 PASS {summary['passed']}/{summary['total']}")
    print(args.output)


if __name__ == "__main__":
    main()
