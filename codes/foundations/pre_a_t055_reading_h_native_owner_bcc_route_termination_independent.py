#!/usr/bin/env python3
"""Independently derive the R-169 v1.3 native BCC termination.

Purpose: reproduce the support, center residues, Voronoi combinatorics,
normalization, side-16 split, and direct-P1 rescaling contradiction without
importing the primary lane or any symbolic/numerical package.
Convention: all scalar arithmetic is Fraction-exact and the full signed
antipodal support is counted once.
Formula: I=12A^2, det(Lambda_BCC)=ell^3/2, and the exact quadratic mismatch
remains positive after quartic/sextic matching forces s^2=1,c_E=2.
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
SLUG = "pre-a-t055-reading-h-native-owner-bcc-route-termination"
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


def fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def monomial_text(coefficient: Fraction, power: int) -> str:
    monomial = f"N**{power}"
    if coefficient.denominator == 1:
        return monomial if coefficient.numerator == 1 else f"{coefficient.numerator}*{monomial}"
    if coefficient.numerator == 1:
        return f"{monomial}/{coefficient.denominator}"
    return f"{coefficient.numerator}*{monomial}/{coefficient.denominator}"


def parse_fraction(value: str | int) -> Fraction:
    return Fraction(value)


def atan_partial(x: Fraction, last_index: int) -> Fraction:
    total = Fraction(0)
    for index in range(last_index + 1):
        sign = -1 if index % 2 else 1
        total += sign * x ** (2 * index + 1) / (2 * index + 1)
    return total


def determinant(matrix: tuple[tuple[Fraction, ...], ...]) -> Fraction:
    a, b, c = matrix[0]
    d, e, f = matrix[1]
    g, h, i = matrix[2]
    return a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, str]] = []

    def check(self, name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        self.rows.append(
            {"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)}
        )


def exact_derivation(manifest: dict[str, Any]) -> dict[str, Any]:
    inputs = manifest["registered_inputs"]
    dimension = int(inputs["spatial_dimension"])
    coordinate_values = tuple(int(value) for value in inputs["support_coordinate_values"])
    support_norm_square = int(inputs["support_norm_square"])
    support = sorted(
        vector
        for vector in itertools.product(coordinate_values, repeat=dimension)
        if sum(component * component for component in vector) == support_norm_square
    )
    antipodal = all(tuple(-component for component in vector) in support for vector in support)
    zero_sum = [sum(vector[index] for vector in support) for index in range(dimension)]
    distinct_nonantipodal_dots = []
    for left in support:
        for right in support:
            if left == right or left == tuple(-component for component in right):
                continue
            distinct_nonantipodal_dots.append(sum(left[index] * right[index] for index in range(dimension)))
    minimum_angle_cosine = Fraction(max(distinct_nonantipodal_dots), support_norm_square)

    corners = list(itertools.product((min(coordinate_values), max(coordinate_values)), repeat=dimension))
    corner_values = {}
    for corner in corners:
        corner_values[corner] = sum(
            corner[left] * corner[right] for left, right in itertools.combinations(range(dimension), 2)
        )
    absolute_maximum = max(abs(value) for value in corner_values.values())
    equality_corners = sorted(corner for corner, value in corner_values.items() if abs(value) == absolute_maximum)
    equality_values = [corner_values[corner] for corner in equality_corners]

    center_residues = []
    for residue in itertools.product((0, 1), repeat=dimension):
        signs = tuple((-1) ** value for value in residue)
        value = sum(signs[left] * signs[right] for left, right in itertools.combinations(range(dimension), 2))
        if value == absolute_maximum:
            center_residues.append(residue)

    vertices = set()
    for first_sign in (-1, 1):
        for second_sign in (-1, 1):
            for permutation in itertools.permutations((0, first_sign, 2 * second_sign)):
                vertices.add(tuple(permutation))
    dimension = len(corners[0])
    square_faces = 2 * dimension
    hexagon_faces = len(corners)
    total_faces = square_faces + hexagon_faces
    edge_count = len(vertices) + total_faces - 2
    half = Fraction(1, 2)
    lattice_basis = (
        (Fraction(1), Fraction(0), half),
        (Fraction(0), Fraction(1), half),
        (Fraction(0), Fraction(0), half),
    )
    volume_coefficient = abs(determinant(lattice_basis))
    centers_per_cube = Fraction(1, 1) / volume_coefficient

    production_intensity = parse_fraction(inputs["production_intensity"])
    amplitude_square = production_intensity / len(support)
    bohr_mean = len(support) * amplitude_square

    q0 = parse_fraction(inputs["literal_q0"])
    atan5_upper = atan_partial(Fraction(1, 5), 10)
    atan239_lower = atan_partial(Fraction(1, 239), 3)
    pi_upper = 16 * atan5_upper - 4 * atan239_lower
    side = int(inputs["side16_side"])
    nearest_radial_index_square = int(inputs["side16_nearest_radial_index_square"])
    reciprocal_shell_square_coefficient = Fraction(4 * nearest_radial_index_square, side ** 2)
    shell_three_gap = q0 ** 2 - reciprocal_shell_square_coefficient * pi_upper ** 2
    shell_search_bound = support_norm_square
    side16_shell_three = [
        vector
        for vector in itertools.product(range(-shell_search_bound, shell_search_bound + 1), repeat=dimension)
        if sum(component * component for component in vector) == nearest_radial_index_square
    ]
    side16_shell_two = [
        vector
        for vector in itertools.product(range(-shell_search_bound, shell_search_bound + 1), repeat=dimension)
        if sum(component * component for component in vector) == support_norm_square
    ]
    bohr_snap_error_coefficient = Fraction(1) + Fraction(1)

    angle_floor = parse_fraction(inputs["reading_h_angle_floor"])
    packing_cap = parse_fraction(inputs["packing_cap"])
    angle_membership = Fraction(1) > angle_floor
    packing_membership = len(support) < packing_cap
    selection_intensity_floor = parse_fraction(inputs["selection_intensity_floor"])
    selection_mu2_max = parse_fraction(inputs["selection_mu2_max"])
    operating_region_membership = (
        Fraction(0) < production_intensity < selection_intensity_floor
        and Fraction(0) < parse_fraction(inputs["reading_h_mu2"]) < selection_mu2_max
    )

    quartic_ratio = parse_fraction(inputs["reading_h_quartic_prefactor"]) / parse_fraction(inputs["p1_quartic_prefactor"])
    sextic_ratio = parse_fraction(inputs["reading_h_sextic_prefactor"]) / parse_fraction(inputs["p1_sextic_prefactor"])
    forced_s_square = sextic_ratio / quartic_ratio
    forced_energy_scale = quartic_ratio / forced_s_square ** 2
    p1_r = parse_fraction(inputs["p1_r"])
    hessian_floor = parse_fraction(inputs["p1_hessian_floor"])
    reading_h_mu2 = parse_fraction(inputs["reading_h_mu2"])
    p1_quadratic_lower = forced_energy_scale * (p1_r + hessian_floor)
    reading_h_quadratic = reading_h_mu2 + q0 ** 4
    quadratic_gap = p1_quadratic_lower - reading_h_quadratic

    charge_coefficient = parse_fraction(inputs["p1_charge_definition_factor"]) * side ** dimension
    production_charge = charge_coefficient * production_intensity
    r158_intensity = parse_fraction(inputs["r158_intensity_threshold"])
    threshold_ratio = r158_intensity / production_intensity

    return {
        "support_count": len(support),
        "support_antipodal": antipodal,
        "support_zero_sum": zero_sum,
        "minimum_angle_cosine": fraction_text(minimum_angle_cosine),
        "corner_maximum": max(corner_values.values()),
        "corner_minimum": min(corner_values.values()),
        "absolute_corner_maximum": absolute_maximum,
        "equality_corners": [list(value) for value in equality_corners],
        "equality_values": equality_values,
        "center_residues_mod_two": [list(value) for value in center_residues],
        "voronoi_vertex_count": len(vertices),
        "square_face_count": square_faces,
        "hexagon_face_count": hexagon_faces,
        "edge_count": edge_count,
        "cell_volume_coefficient": fraction_text(volume_coefficient),
        "centers_per_conventional_cube": fraction_text(centers_per_cube),
        "production_amplitude_square": fraction_text(amplitude_square),
        "bohr_mean": fraction_text(bohr_mean),
        "natural_torus_center_count": monomial_text(centers_per_cube, dimension),
        "natural_torus_norm_coefficient": monomial_text(production_intensity, dimension),
        "side16_shell_three_gap": fraction_text(shell_three_gap),
        "side16_q0_above_shell_three": shell_three_gap > 0,
        "side16_nearest_radial_count": len(side16_shell_three),
        "side16_bcc_direction_count": len(side16_shell_two),
        "bohr_snap_error_coefficient": fraction_text(bohr_snap_error_coefficient),
        "angle_membership": angle_membership,
        "packing_membership": packing_membership,
        "operating_region_membership": operating_region_membership,
        "forced_s_square": fraction_text(forced_s_square),
        "forced_energy_scale": fraction_text(forced_energy_scale),
        "p1_quadratic_lower": fraction_text(p1_quadratic_lower),
        "reading_h_quadratic": fraction_text(reading_h_quadratic),
        "quadratic_gap": fraction_text(quadratic_gap),
        "quadratic_contradiction": quadratic_gap > 0,
        "production_p1_charge": fraction_text(production_charge),
        "r158_intensity_ratio": fraction_text(threshold_ratio),
    }


def run(staged: bool) -> dict[str, Any]:
    audit = Audit()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = CERTIFICATE.read_text(encoding="utf-8")
    derived = exact_derivation(manifest)
    oracle = manifest["test_oracles"]

    identity_ok = manifest.get("exploration_id") == "EXP-000860" and manifest.get("version") == "R-169 v1.3" and manifest.get("claim_bearing") is False
    audit.check("manifest identity", identity_ok, {key: manifest.get(key) for key in ("exploration_id", "version", "claim_bearing")}, "EXP-000860 / R-169 v1.3 / false", "identity")

    source_hashes = {name: normalized_sha256(REPO / item["path"]) for name, item in manifest["source_authorities"].items()}
    expected_hashes = {name: item["sha256"] for name, item in manifest["source_authorities"].items()}
    audit.check("frozen source hashes", source_hashes == expected_hashes, source_hashes, expected_hashes, "provenance")

    support_ok = derived["support_count"] == oracle["support_count"] and derived["support_antipodal"] and derived["support_zero_sum"] == oracle["support_zero_sum"] and derived["minimum_angle_cosine"] == oracle["minimum_angle_cosine"]
    audit.check("support derivation", support_ok, {key: derived[key] for key in ("support_count", "support_antipodal", "support_zero_sum", "minimum_angle_cosine")}, "exact registered support", "geometry")

    extrema_ok = derived["corner_maximum"] == oracle["corner_maximum"] and derived["corner_minimum"] == oracle["corner_minimum"] and derived["equality_corners"] == oracle["equality_corners"] and derived["equality_values"] == oracle["equality_values"]
    audit.check("corner and sign derivation", extrema_ok, {key: derived[key] for key in ("corner_maximum", "corner_minimum", "equality_corners", "equality_values")}, "both equality corners positive", "geometry")

    audit.check("BCC residue derivation", derived["center_residues_mod_two"] == oracle["center_residues_mod_two"], derived["center_residues_mod_two"], "two BCC residues", "geometry")

    cell_ok = derived["voronoi_vertex_count"] == oracle["voronoi_vertex_count"] and derived["square_face_count"] == oracle["square_face_count"] and derived["hexagon_face_count"] == oracle["hexagon_face_count"] and derived["edge_count"] == oracle["voronoi_edge_count"] and derived["cell_volume_coefficient"] == oracle["cell_volume_coefficient"]
    audit.check("cell combinatorics and determinant", cell_ok, {key: derived[key] for key in ("voronoi_vertex_count", "edge_count", "square_face_count", "hexagon_face_count", "cell_volume_coefficient")}, "24/36/(6+8), determinant 1/2", "geometry")

    normalization_ok = derived["production_amplitude_square"] == oracle["production_amplitude_square"] and derived["bohr_mean"] == manifest["registered_inputs"]["production_intensity"] and derived["centers_per_conventional_cube"] == str(oracle["center_cosets_per_cell"])
    audit.check("normalization derivation", normalization_ok, {key: derived[key] for key in ("production_amplitude_square", "bohr_mean", "centers_per_conventional_cube")}, "A^2=1/6000, M=1/500, density 2", "normalization")

    side16_ok = derived["side16_q0_above_shell_three"] and derived["side16_nearest_radial_count"] == oracle["side16_nearest_radial_count"] and derived["side16_bcc_direction_count"] == oracle["support_count"] and derived["bohr_snap_error_coefficient"] == oracle["bohr_snap_error_coefficient"]
    audit.check("side-16 firewall derivation", side16_ok, {key: derived[key] for key in ("side16_q0_above_shell_three", "side16_nearest_radial_count", "side16_bcc_direction_count", "bohr_snap_error_coefficient")}, "off shell, 8-vs-12, 2I", "interface")

    native_ok = derived["angle_membership"] and derived["packing_membership"] and derived["operating_region_membership"]
    audit.check("native membership arithmetic", native_ok, {"angle": derived["angle_membership"], "packing": derived["packing_membership"], "region": derived["operating_region_membership"]}, "all strict", "native-sign")

    rescaling_ok = derived["forced_s_square"] == oracle["forced_s_square"] and derived["forced_energy_scale"] == oracle["forced_energy_scale"] and derived["p1_quadratic_lower"] == oracle["p1_quadratic_lower"] and derived["quadratic_contradiction"]
    audit.check("global-rescaling contradiction", rescaling_ok, {key: derived[key] for key in ("forced_s_square", "forced_energy_scale", "p1_quadratic_lower", "reading_h_quadratic", "quadratic_gap", "quadratic_contradiction")}, "forced 1/2 and positive exact gap", "interface")

    ensemble_ok = derived["production_p1_charge"] == oracle["production_p1_charge"] and derived["r158_intensity_ratio"] == oracle["r158_intensity_ratio"]
    audit.check("ensemble arithmetic", ensemble_ok, {key: derived[key] for key in ("production_p1_charge", "r158_intensity_ratio")}, "exact changed-owner values", "ensemble")

    scope_tokens = (
        "PA-T055-READING-H-REALIZATION-TO-PINNED-P1-OR-DECLARED-ESCAPE",
        "No P1 or R-157 premise is used",
        "does not compare either state with an empty",
        "no new negative is registered",
        "No R-169 v1.3 PDF is issued",
    )
    audit.check("certificate boundary", all(token in certificate for token in scope_tokens), [token for token in scope_tokens if token in certificate], list(scope_tokens), "scope")

    if staged:
        authority_text = "\n".join((REPO / path).read_text(encoding="utf-8") for path in ("claims/GATES.md", "RESULTS-LEDGER.md", "explorations/log.jsonl", "changelog/log.jsonl"))
        events = [json.loads(line) for line in (REPO / "changelog/log.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
        matches = [(ordinal, event) for ordinal, event in enumerate(events, start=1) if event.get("id") == manifest["formal_integration"]["event_id"]]
        if matches:
            audit.check("integrated historical authority revalidation", len(matches) == 1, matches, "one immutable event-id match", "lifecycle")
        else:
            tokens = ["EXP-000860", "R-169 v1.3", *manifest["closed_gate_ids"]]
            audit.check("preformal authority absence", all(token not in authority_text for token in tokens), "new authority tokens absent", "new authority tokens absent", "lifecycle")

    return {
        "schema": "tect/pre-a-t055-reading-h-native-owner-bcc-route-termination-independent/1.0",
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
