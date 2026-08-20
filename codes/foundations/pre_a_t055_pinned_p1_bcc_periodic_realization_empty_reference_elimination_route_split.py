#!/usr/bin/env python3
"""Derive the exact R-169 v1.1 P1/BCC realization fixture.

Purpose: construct the twelve-mode side-16 field, derive its modulus-max
centers, period lattice, Voronoi-cell count, and inherited R-157 margins.
Convention: energies are candidate minus zero reference and the L2 norm is the
continuous side-16 torus integral.
Formula: ||Psi_A||_2^2=12*16^3|A|^2 and R-157 supplies the exact g and kappa.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
from pathlib import Path
import tempfile
from typing import Any

import sympy as sp


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-t055-pinned-p1-bcc-periodic-realization-empty-reference-elimination-route-split"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260814.md"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-14-primary-{SLUG}/result.json"


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


def exact_support(scale: int) -> tuple[tuple[int, int, int], ...]:
    support: set[tuple[int, int, int]] = set()
    for zero in range(3):
        active = [index for index in range(3) if index != zero]
        for signs in itertools.product((-1, 1), repeat=2):
            vector = [0, 0, 0]
            vector[active[0]] = scale * signs[0]
            vector[active[1]] = scale * signs[1]
            support.add(tuple(vector))
    return tuple(sorted(support))


def bcc_cosets(side: int, scale: int) -> set[tuple[int, int, int]]:
    step = side // scale
    half = step // 2
    first = set(itertools.product(range(0, side, step), repeat=3))
    second = {
        tuple((coordinate + half) % side for coordinate in point)
        for point in first
    }
    return first | second


def exact_derivation(manifest: dict[str, Any]) -> dict[str, Any]:
    inputs = manifest["exact_fixture_inputs"]
    scale = sp.Integer(inputs["frequency_scale"])
    side = sp.Integer(inputs["torus_side"])
    dimension = sp.Integer(inputs["dimension"])
    support = exact_support(int(scale))

    p, q, r = sp.symbols("p q r", real=True)
    polynomial = p * q + p * r + q * r
    vertex_values = sorted(
        sp.Integer(polynomial.subs({p: pv, q: qv, r: rv}))
        for pv, qv, rv in itertools.product((-1, 1), repeat=3)
    )
    maximum = max(vertex_values)
    minimum = min(vertex_values)
    maximum_vertices = sorted(
        point
        for point in itertools.product((-1, 1), repeat=3)
        if polynomial.subs({p: point[0], q: point[1], r: point[2]}) == maximum
    )

    centers = bcc_cosets(int(side), int(scale))
    periods: set[tuple[int, int, int]] = set()
    antiperiods: set[tuple[int, int, int]] = set()
    for point in itertools.product(range(int(side)), repeat=int(dimension)):
        residues = [sum(n_i * x_i for n_i, x_i in zip(vector, point)) % int(side) for vector in support]
        if all(value == 0 for value in residues):
            periods.add(point)
        if all(value == int(side // 2) for value in residues):
            antiperiods.add(point)

    torus_volume = side**dimension
    support_count = sp.Integer(len(support))
    norm_coefficient = sp.factor(support_count * torus_volume)
    r157_path = REPO / manifest["source_authorities"]["r157_manifest"]["path"]
    r157 = json.loads(r157_path.read_text(encoding="utf-8"))
    g = sp.Rational(r157["exact_constants"]["strict_l2_gap_g"])
    kappa = sp.Rational(r157["exact_constants"]["strict_radial_derivative_gap_kappa"])
    energy_coefficient = sp.factor(norm_coefficient * g)
    radial_coefficient = sp.factor(norm_coefficient * kappa)

    r169_path = REPO / manifest["source_authorities"]["r169_v1_0_manifest"]["path"]
    r169 = json.loads(r169_path.read_text(encoding="utf-8"))
    cell_volume = sp.Integer(r169["standard_bcc_voronoi_fixture"]["fundamental_volume"])
    cell_count = sp.factor(torus_volume / cell_volume)

    delta = sp.symbols("delta", nonnegative=True)
    delta_r = sp.symbols("delta_r", nonnegative=True)
    value_remainder = sp.factor(g - delta)
    radial_remainder = sp.factor(kappa - delta_r)

    y = sp.symbols("y", nonnegative=True)
    value_only_total = sp.Rational(1, 4) * y + y * (y - 1) ** 2
    stationary_polynomial = sp.factor(sp.diff(value_only_total, y))
    stationary_roots = sorted(sp.solve(stationary_polynomial, y))
    second_derivatives = [sp.factor(4 * root * sp.diff(stationary_polynomial, y).subs(y, root)) for root in stationary_roots]
    local_minimum_root = stationary_roots[second_derivatives.index(next(value for value in second_derivatives if value > 0))]
    local_minimum_energy = sp.factor(value_only_total.subs(y, local_minimum_root))

    return {
        "support": [list(vector) for vector in support],
        "support_count": int(support_count),
        "scalar_factor": str(sp.factor(4 * polynomial)),
        "cube_vertex_values": [int(value) for value in vertex_values],
        "cube_minimum": int(minimum),
        "cube_maximum": int(maximum),
        "maximum_vertices": [list(point) for point in maximum_vertices],
        "center_count": len(centers),
        "period_count_mod_torus": len(periods),
        "periods_equal_centers": periods == centers,
        "antiperiod_count": len(antiperiods),
        "torus_volume": int(torus_volume),
        "cell_volume": int(cell_volume),
        "cell_count": int(cell_count),
        "norm_coefficient": int(norm_coefficient),
        "g": str(g),
        "kappa": str(kappa),
        "energy_coefficient": str(energy_coefficient),
        "radial_coefficient": str(radial_coefficient),
        "energy_above_integer_floor": bool(energy_coefficient > manifest["test_oracles"]["energy_floor_integer"]),
        "radial_above_integer_floor": bool(radial_coefficient > manifest["test_oracles"]["radial_floor_integer"]),
        "value_perturbation_remainder": f"{g}-delta",
        "radial_perturbation_remainder": f"{kappa}-delta_r",
        "value_only_stationary_polynomial_coefficients": [str(value) for value in sp.Poly(stationary_polynomial, y).all_coeffs()],
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

    for name, authority in manifest["source_authorities"].items():
        path = REPO / authority["path"]
        audit.check(f"source hash {name}", path.is_file() and normalized_sha256(path) == authority["sha256"], normalized_sha256(path) if path.is_file() else "missing", authority["sha256"], "provenance")

    oracle = manifest["test_oracles"]
    audit.check("twelve-mode support", derived["support_count"] == oracle["support_count"], derived["support_count"], oracle["support_count"], "field")
    dimension = manifest["exact_fixture_inputs"]["dimension"]
    equal_sign_vertices = [[-1] * dimension, [1] * dimension]
    audit.check("multiaffine extrema", derived["cube_vertex_values"] == sorted(oracle["cube_vertex_multiset"]) and derived["maximum_vertices"] == equal_sign_vertices, {"values": derived["cube_vertex_values"], "maxima": derived["maximum_vertices"]}, "two equal-sign maxima", "field")
    audit.check("centers and exact periods", derived["center_count"] == oracle["center_count"] and derived["periods_equal_centers"] and derived["antiperiod_count"] == 0, {key: derived[key] for key in ("center_count", "period_count_mod_torus", "antiperiod_count")}, "128 centers=periods and no anti-period", "lattice")
    audit.check("cell-volume quotient", derived["torus_volume"] == oracle["torus_volume"] and derived["cell_volume"] == oracle["cell_volume"] and derived["cell_count"] == oracle["center_count"], {key: derived[key] for key in ("torus_volume", "cell_volume", "cell_count")}, "4096/32=128", "lattice")
    audit.check("Fourier norm", derived["norm_coefficient"] == oracle["l2_coefficient"], derived["norm_coefficient"], oracle["l2_coefficient"], "energy")
    audit.check("strict inherited margins", derived["energy_above_integer_floor"] and derived["radial_above_integer_floor"], {"energy": derived["energy_coefficient"], "radial": derived["radial_coefficient"]}, "energy>6144 and radial>12288", "energy")
    audit.check("separate perturbation conclusions", "delta" in derived["value_perturbation_remainder"] and "delta_r" not in derived["value_perturbation_remainder"] and "delta_r" in derived["radial_perturbation_remainder"], {"value": derived["value_perturbation_remainder"], "radial": derived["radial_perturbation_remainder"]}, "separate g/delta and kappa/delta_r", "scope")
    transfer = manifest["perturbation_transfer"]
    audit.check("semantic value/radial firewall", "above the reference" in transfer["value_conclusion"] and all(token not in transfer["value_conclusion"] for token in ("critical", "local", "metastable")) and "critical" in transfer["radial_conclusion"] and "local-minimum" in transfer["radial_conclusion"], {"value": transfer["value_conclusion"], "radial": transfer["radial_conclusion"]}, "value only reference sign; radial only critical/local exclusion", "scope")
    audit.check("value-only counterfixture", derived["value_only_stationary_squared_amplitudes"] == oracle["value_only_stationary_squared_amplitudes"] and derived["value_only_local_minimum_energy"] == oracle["value_only_local_minimum_energy"] and derived["value_only_second_derivatives"][0].startswith("-") and not derived["value_only_second_derivatives"][1].startswith("-"), {"roots": derived["value_only_stationary_squared_amplitudes"], "second": derived["value_only_second_derivatives"], "energy": derived["value_only_local_minimum_energy"]}, "nonzero higher local minimum despite value gap", "scope")
    audit.check("certificate scope", all(token in certificate for token in ("neither promotes nor", "refutes the current B1/B3", "does not by itself exclude", "remains open", "No R-169 v1.1 PDF")), "scope tokens present", "scope tokens present", "scope")

    if staged:
        gates = (REPO / "claims/GATES.md").read_text(encoding="utf-8")
        results = (REPO / "RESULTS-LEDGER.md").read_text(encoding="utf-8")
        events = [json.loads(line) for line in (REPO / "changelog/log.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
        matches = [event for event in events if event.get("id") == manifest["formal_integration"]["event_id"]]
        if matches:
            audit.check("integrated historical authority revalidation", len(matches) == 1, matches, "one immutable event-id match", "lifecycle")
        else:
            audit.check("preformal authority absence", "EXP-000852" not in gates and "R-169 v1.1" not in results, "new authority absent", "new authority absent", "lifecycle")

    return {
        "schema": "tect/pre-a-t055-pinned-p1-bcc-periodic-realization-primary/1.0",
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
    print(f"PRIMARY PASS {payload['assertions']}/{payload['assertions']} mode={payload['mode']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
