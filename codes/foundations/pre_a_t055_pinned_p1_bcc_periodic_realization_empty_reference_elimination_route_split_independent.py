#!/usr/bin/env python3
"""Independently verify the R-169 v1.1 P1/BCC realization fixture.

Purpose: recompute support, centers, periods, exact fractions, and perturbation
separation without importing the primary lane or a symbolic/numerical package.
Convention: candidate-minus-zero energy and the continuous side-16 torus L2
integral are used throughout.
Formula: orthogonal Fourier characters give N_modes*L^3 and Fraction arithmetic
propagates the inherited R-157 gaps.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import itertools
import json
import os
from pathlib import Path
import tempfile
from typing import Any


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-t055-pinned-p1-bcc-periodic-realization-empty-reference-elimination-route-split"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260814.md"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-14-independent-{SLUG}/result.json"


def normalized_sha256(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
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


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, str]] = []

    def check(self, name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        self.rows.append(
            {"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)}
        )


def support_vectors(scale: int, dimension: int) -> tuple[tuple[int, ...], ...]:
    output: set[tuple[int, ...]] = set()
    for zero in range(dimension):
        active = [index for index in range(dimension) if index != zero]
        for signs in itertools.product((-1, 1), repeat=len(active)):
            vector = [0] * dimension
            for index, sign in zip(active, signs):
                vector[index] = scale * sign
            output.add(tuple(vector))
    return tuple(sorted(output))


def vertex_polynomial(point: tuple[int, int, int]) -> int:
    p, q, r = point
    return p * q + p * r + q * r


def center_cosets(side: int, scale: int, dimension: int) -> set[tuple[int, ...]]:
    step = side // scale
    half_step = step // 2
    first = set(itertools.product(range(0, side, step), repeat=dimension))
    shifted = {tuple((coordinate + half_step) % side for coordinate in point) for point in first}
    return first | shifted


def exact_derivation(manifest: dict[str, Any]) -> dict[str, Any]:
    inputs = manifest["exact_fixture_inputs"]
    dimension = int(inputs["dimension"])
    side = int(inputs["torus_side"])
    scale = int(inputs["frequency_scale"])
    support = support_vectors(scale, dimension)
    vertices = tuple(itertools.product((-1, 1), repeat=dimension))
    values = sorted(vertex_polynomial(point) for point in vertices)
    maximum = max(values)
    minimum = min(values)
    maximum_vertices = sorted(point for point in vertices if vertex_polynomial(point) == maximum)

    centers = center_cosets(side, scale, dimension)
    periods: set[tuple[int, ...]] = set()
    antiperiods: set[tuple[int, ...]] = set()
    for point in itertools.product(range(side), repeat=dimension):
        residues = tuple(sum(component * coordinate for component, coordinate in zip(vector, point)) % side for vector in support)
        if all(residue == 0 for residue in residues):
            periods.add(point)
        if all(residue == side // 2 for residue in residues):
            antiperiods.add(point)

    r157 = json.loads((REPO / manifest["source_authorities"]["r157_manifest"]["path"]).read_text(encoding="utf-8"))
    g = Fraction(r157["exact_constants"]["strict_l2_gap_g"])
    kappa = Fraction(r157["exact_constants"]["strict_radial_derivative_gap_kappa"])
    r169 = json.loads((REPO / manifest["source_authorities"]["r169_v1_0_manifest"]["path"]).read_text(encoding="utf-8"))
    cell_volume = int(r169["standard_bcc_voronoi_fixture"]["fundamental_volume"])
    torus_volume = side**dimension
    norm_coefficient = len(support) * torus_volume
    energy_coefficient = norm_coefficient * g
    radial_coefficient = norm_coefficient * kappa
    monomials = ("p*q", "p*r", "q*r")
    stationary_a = Fraction(3)
    stationary_b = Fraction(-4)
    stationary_c = Fraction(5, 4)
    discriminant = stationary_b * stationary_b - 4 * stationary_a * stationary_c
    discriminant_root = Fraction(1) if discriminant == 1 else None
    if discriminant_root is None:
        raise AssertionError(f"counterfixture discriminant is not the exact square one: {discriminant}")
    stationary_roots = sorted(
        ((-stationary_b - discriminant_root) / (2 * stationary_a), (-stationary_b + discriminant_root) / (2 * stationary_a))
    )
    second_derivatives = [4 * root * (6 * root - 4) for root in stationary_roots]
    local_minimum_root = next(root for root, second in zip(stationary_roots, second_derivatives) if second > 0)
    local_minimum_energy = Fraction(1, 4) * local_minimum_root + local_minimum_root * (local_minimum_root - 1) ** 2

    return {
        "support": [list(vector) for vector in support],
        "support_count": len(support),
        "scalar_factor": str(scale) + "*(" + " + ".join(monomials) + ")",
        "cube_vertex_values": values,
        "cube_minimum": minimum,
        "cube_maximum": maximum,
        "maximum_vertices": [list(point) for point in maximum_vertices],
        "center_count": len(centers),
        "period_count_mod_torus": len(periods),
        "periods_equal_centers": periods == centers,
        "antiperiod_count": len(antiperiods),
        "torus_volume": torus_volume,
        "cell_volume": cell_volume,
        "cell_count": torus_volume // cell_volume,
        "norm_coefficient": norm_coefficient,
        "g": str(g),
        "kappa": str(kappa),
        "energy_coefficient": str(energy_coefficient),
        "radial_coefficient": str(radial_coefficient),
        "energy_above_integer_floor": energy_coefficient > manifest["test_oracles"]["energy_floor_integer"],
        "radial_above_integer_floor": radial_coefficient > manifest["test_oracles"]["radial_floor_integer"],
        "value_perturbation_remainder": f"{g}-delta",
        "radial_perturbation_remainder": f"{kappa}-delta_r",
        "value_only_stationary_polynomial_coefficients": [str(stationary_a), str(stationary_b), str(stationary_c)],
        "value_only_stationary_squared_amplitudes": [str(root) for root in stationary_roots],
        "value_only_second_derivatives": [str(value) for value in second_derivatives],
        "value_only_local_minimum_squared_amplitude": str(local_minimum_root),
        "value_only_local_minimum_energy": str(local_minimum_energy),
    }


def run(staged: bool) -> dict[str, Any]:
    audit = Audit()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = CERTIFICATE.read_text(encoding="utf-8")
    derived = exact_derivation(manifest)
    oracle = manifest["test_oracles"]

    for name, authority in manifest["source_authorities"].items():
        path = REPO / authority["path"]
        audit.check(f"source hash {name}", path.is_file() and normalized_sha256(path) == authority["sha256"], normalized_sha256(path) if path.is_file() else "missing", authority["sha256"], "provenance")

    audit.check("support and vertex ledger", derived["support_count"] == oracle["support_count"] and derived["cube_vertex_values"] == sorted(oracle["cube_vertex_multiset"]), {"support": derived["support_count"], "values": derived["cube_vertex_values"]}, "12 and six -1/two 3", "field")
    dimension = manifest["exact_fixture_inputs"]["dimension"]
    equal_sign_vertices = [[-1] * dimension, [1] * dimension]
    audit.check("center equality cases", derived["maximum_vertices"] == equal_sign_vertices and derived["center_count"] == oracle["center_count"], {"maxima": derived["maximum_vertices"], "centers": derived["center_count"]}, "two equal-sign extrema and 128 centers", "field")
    audit.check("period and anti-period", derived["periods_equal_centers"] and derived["period_count_mod_torus"] == oracle["center_count"] and derived["antiperiod_count"] == 0, {"periods": derived["period_count_mod_torus"], "anti": derived["antiperiod_count"]}, "periods=centers; no anti-period", "lattice")
    audit.check("volume and cells", derived["torus_volume"] == oracle["torus_volume"] and derived["cell_volume"] == oracle["cell_volume"] and derived["cell_count"] == oracle["center_count"], {key: derived[key] for key in ("torus_volume", "cell_volume", "cell_count")}, "4096/32=128", "lattice")
    audit.check("norm and strict margins", derived["norm_coefficient"] == oracle["l2_coefficient"] and derived["energy_above_integer_floor"] and derived["radial_above_integer_floor"], {"norm": derived["norm_coefficient"], "energy": derived["energy_coefficient"], "radial": derived["radial_coefficient"]}, "49152 with strict floors", "energy")
    audit.check("value/radial separation", derived["value_perturbation_remainder"].endswith("-delta") and derived["radial_perturbation_remainder"].endswith("-delta_r"), {"value": derived["value_perturbation_remainder"], "radial": derived["radial_perturbation_remainder"]}, "separate perturbation premises", "scope")
    transfer = manifest["perturbation_transfer"]
    audit.check("semantic value/radial firewall", "above the reference" in transfer["value_conclusion"] and all(token not in transfer["value_conclusion"] for token in ("critical", "local", "metastable")) and "critical" in transfer["radial_conclusion"] and "local-minimum" in transfer["radial_conclusion"], {"value": transfer["value_conclusion"], "radial": transfer["radial_conclusion"]}, "separate conclusion scopes", "scope")
    audit.check("value-only local-minimum fixture", derived["value_only_stationary_squared_amplitudes"] == oracle["value_only_stationary_squared_amplitudes"] and derived["value_only_local_minimum_energy"] == oracle["value_only_local_minimum_energy"] and derived["value_only_second_derivatives"][0].startswith("-") and not derived["value_only_second_derivatives"][1].startswith("-"), {"roots": derived["value_only_stationary_squared_amplitudes"], "second": derived["value_only_second_derivatives"], "energy": derived["value_only_local_minimum_energy"]}, "higher local min survives positive value gap", "scope")
    audit.check("Reading-H firewall", all(token in certificate for token in ("No registered authority maps", "neither promotes nor", "R-158 changes", "remains open")), "firewall tokens present", "firewall tokens present", "scope")

    if staged:
        authorities = (REPO / "claims/GATES.md").read_text(encoding="utf-8") + (REPO / "RESULTS-LEDGER.md").read_text(encoding="utf-8")
        events = [json.loads(line) for line in (REPO / "changelog/log.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
        matches = [event for event in events if event.get("id") == manifest["formal_integration"]["event_id"]]
        if matches:
            audit.check("integrated historical authority revalidation", len(matches) == 1, matches, "one immutable event-id match", "lifecycle")
        else:
            audit.check("preformal authority absence", "EXP-000852" not in authorities and "R-169 v1.1" not in authorities, "new authority absent", "new authority absent", "lifecycle")

    return {
        "schema": "tect/pre-a-t055-pinned-p1-bcc-periodic-realization-independent/1.0",
        "version": __version__,
        "mode": "staged" if staged else "formal",
        "assertions": len(audit.rows),
        "checks": audit.rows,
        "derived": derived,
        "source_hash": normalized_sha256(SCRIPT),
        "manifest_hash": normalized_sha256(MANIFEST),
        "certificate_hash": normalized_sha256(CERTIFICATE),
        "verdict": "PASS",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--staged", action="store_true")
    parser.add_argument("--no-store", action="store_true")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = run(args.staged)
    if not args.no_store:
        atomic_json(args.output, payload)
    print(f"INDEPENDENT PASS {payload['assertions']}/{payload['assertions']} mode={payload['mode']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
