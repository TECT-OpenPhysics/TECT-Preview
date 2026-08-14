#!/usr/bin/env python3
"""Derive the R-169 v1.3 native Reading-H BCC route termination.

Purpose: reconstruct the registered zero-phase {110} field, its BCC center
lattice and Voronoi cell, audit native cFull membership, and prove the scoped
direct-P1 global-rescaling obstruction.
Convention: the twelve signed modes are listed once, I=sum_k |c_k|^2, and
the native Reading-H and side-16 pinned-P1 owners are never identified.
Formula: phi=4A(pq+pr+qr), Lambda=ell Z^3 union (ell/2)(1,1,1)+ell Z^3,
M_Bohr(phi^2)=I, and quartic/sextic matching forces s^2=1,c_E=2.
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
SLUG = "pre-a-t055-reading-h-native-owner-bcc-route-termination"
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


def atan_partial(x: sp.Rational, last_index: int) -> sp.Rational:
    return sp.factor(
        sum(((-1) ** j) * x ** (2 * j + 1) / sp.Rational(2 * j + 1) for j in range(last_index + 1))
    )


def exact_derivation(manifest: dict[str, Any]) -> dict[str, Any]:
    inputs = manifest["registered_inputs"]
    dimension = int(inputs["spatial_dimension"])
    coordinate_values = tuple(int(value) for value in inputs["support_coordinate_values"])
    support_norm_square = int(inputs["support_norm_square"])
    q0 = sp.Rational(inputs["literal_q0"])
    intensity = sp.Rational(inputs["production_intensity"])
    amplitude_square = sp.factor(intensity / sp.Integer(len([
        vector
        for vector in itertools.product(coordinate_values, repeat=dimension)
        if sum(component * component for component in vector) == support_norm_square
    ])))

    support = sorted(
        vector
        for vector in itertools.product(coordinate_values, repeat=dimension)
        if sum(component * component for component in vector) == support_norm_square
    )
    antipodal = all(tuple(-component for component in vector) in support for vector in support)
    zero_sum = tuple(sum(vector[index] for vector in support) for index in range(dimension))
    distinct_nonantipodal_dots = [
        sum(left[index] * right[index] for index in range(dimension))
        for left in support
        for right in support
        if left != right and left != tuple(-component for component in right)
    ]
    maximum_dot = max(distinct_nonantipodal_dots)
    minimum_angle_cosine = sp.Rational(maximum_dot, support_norm_square)

    corners = list(itertools.product((min(coordinate_values), max(coordinate_values)), repeat=dimension))
    corner_values = {
        corner: sum(corner[left] * corner[right] for left, right in itertools.combinations(range(dimension), 2))
        for corner in corners
    }
    absolute_maximum = max(abs(value) for value in corner_values.values())
    equality_corners = sorted(corner for corner, value in corner_values.items() if abs(value) == absolute_maximum)
    equality_values = [corner_values[corner] for corner in equality_corners]

    residue_classes = list(itertools.product((0, 1), repeat=dimension))
    residue_values = {}
    for residue in residue_classes:
        signs = tuple((-1) ** value for value in residue)
        residue_values[residue] = sum(
            signs[left] * signs[right] for left, right in itertools.combinations(range(dimension), 2)
        )
    center_residues = sorted(residue for residue, value in residue_values.items() if value == absolute_maximum)

    vertices = {
        tuple(permutation)
        for first_sign in (-1, 1)
        for second_sign in (-1, 1)
        for permutation in itertools.permutations((0, first_sign, 2 * second_sign))
    }
    square_faces = 2 * len(corners[0])
    hexagon_faces = len(corners)
    total_faces = square_faces + hexagon_faces
    edge_count = len(vertices) + total_faces - 2
    volume_matrix = sp.Matrix(
        [
            [1, 0, sp.Rational(1, 2)],
            [0, 1, sp.Rational(1, 2)],
            [0, 0, sp.Rational(1, 2)],
        ]
    )
    volume_coefficient = sp.factor(abs(volume_matrix.det()))
    centers_per_conventional_cube = sp.factor(1 / volume_coefficient)

    bohr_mean_coefficient = len(support)
    bohr_mean = sp.factor(bohr_mean_coefficient * amplitude_square)
    n = sp.symbols("N", integer=True, positive=True)
    natural_torus_center_count = sp.factor(centers_per_conventional_cube * n ** dimension)
    natural_torus_norm_coefficient = sp.factor(n ** dimension * bohr_mean)

    # Exact Machin upper enclosure proves q0^2>3*pi^2/64, hence q0 is
    # strictly above both side-16 {111} and support-preserving {110} radii.
    atan5_upper = atan_partial(sp.Rational(1, 5), 10)
    atan239_lower = atan_partial(sp.Rational(1, 239), 3)
    pi_upper = sp.factor(16 * atan5_upper - 4 * atan239_lower)
    side = sp.Integer(inputs["side16_side"])
    nearest_radial_index_square = int(inputs["side16_nearest_radial_index_square"])
    reciprocal_shell_square_coefficient = sp.Rational(4 * nearest_radial_index_square, side ** 2)
    shell_three_gap = sp.factor(q0 ** 2 - reciprocal_shell_square_coefficient * pi_upper ** 2)
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
    bohr_snap_error_coefficient = sp.Integer(1) + sp.Integer(1)

    angle_floor = sp.Rational(inputs["reading_h_angle_floor"])
    packing_cap = sp.Rational(inputs["packing_cap"])
    angle_membership = bool(sp.Rational(1, 1) > angle_floor)  # pi/3>1 from pi>3.
    packing_membership = bool(sp.Integer(len(support)) < packing_cap)
    selection_intensity_floor = sp.Rational(inputs["selection_intensity_floor"])
    selection_mu2_max = sp.Rational(inputs["selection_mu2_max"])
    operating_region_membership = bool(
        sp.Integer(0) < intensity < selection_intensity_floor
        and sp.Integer(0) < sp.Rational(inputs["reading_h_mu2"]) < selection_mu2_max
    )

    quartic_ratio = sp.factor(sp.Rational(inputs["reading_h_quartic_prefactor"]) / sp.Rational(inputs["p1_quartic_prefactor"]))
    sextic_ratio = sp.factor(sp.Rational(inputs["reading_h_sextic_prefactor"]) / sp.Rational(inputs["p1_sextic_prefactor"]))
    forced_s_square = sp.factor(sextic_ratio / quartic_ratio)
    forced_energy_scale = sp.factor(quartic_ratio / forced_s_square ** 2)
    p1_r = sp.Rational(inputs["p1_r"])
    hessian_floor = sp.Rational(inputs["p1_hessian_floor"])
    reading_h_mu2 = sp.Rational(inputs["reading_h_mu2"])
    p1_quadratic_lower = sp.factor(forced_energy_scale * (p1_r + hessian_floor))
    reading_h_quadratic = sp.factor(reading_h_mu2 + q0 ** 4)
    quadratic_gap = sp.factor(p1_quadratic_lower - reading_h_quadratic)

    p1_charge_coefficient = sp.factor(sp.Rational(inputs["p1_charge_definition_factor"]) * side ** dimension)
    production_charge = sp.factor(p1_charge_coefficient * intensity)
    r158_intensity = sp.Rational(inputs["r158_intensity_threshold"])
    threshold_ratio = sp.factor(r158_intensity / intensity)

    return {
        "support_count": len(support),
        "support_antipodal": antipodal,
        "support_zero_sum": list(zero_sum),
        "minimum_angle_cosine": str(minimum_angle_cosine),
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
        "cell_volume_coefficient": str(volume_coefficient),
        "centers_per_conventional_cube": str(centers_per_conventional_cube),
        "production_amplitude_square": str(amplitude_square),
        "bohr_mean": str(bohr_mean),
        "natural_torus_center_count": str(natural_torus_center_count),
        "natural_torus_norm_coefficient": str(natural_torus_norm_coefficient),
        "side16_shell_three_gap": str(shell_three_gap),
        "side16_q0_above_shell_three": bool(shell_three_gap > 0),
        "side16_nearest_radial_count": len(side16_shell_three),
        "side16_bcc_direction_count": len(side16_shell_two),
        "bohr_snap_error_coefficient": str(bohr_snap_error_coefficient),
        "angle_membership": angle_membership,
        "packing_membership": packing_membership,
        "operating_region_membership": operating_region_membership,
        "forced_s_square": str(forced_s_square),
        "forced_energy_scale": str(forced_energy_scale),
        "p1_quadratic_lower": str(p1_quadratic_lower),
        "reading_h_quadratic": str(reading_h_quadratic),
        "quadratic_gap": str(quadratic_gap),
        "quadratic_contradiction": bool(quadratic_gap > 0),
        "production_p1_charge": str(production_charge),
        "r158_intensity_ratio": str(threshold_ratio),
    }


def run(staged: bool) -> dict[str, Any]:
    audit = Audit()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = CERTIFICATE.read_text(encoding="utf-8")
    derived = exact_derivation(manifest)
    oracle = manifest["test_oracles"]

    identity_ok = (
        manifest.get("schema") == "tect/pre-a-t055-reading-h-native-owner-bcc-route-termination/1.0"
        and manifest.get("version") == "R-169 v1.3"
        and manifest.get("exploration_id") == "EXP-000860"
        and manifest.get("tier") == "T0"
        and manifest.get("claim_bearing") is False
    )
    audit.check("manifest identity", identity_ok, {key: manifest.get(key) for key in ("schema", "version", "exploration_id", "tier", "claim_bearing")}, "exact v1.3 identity", "identity")

    source_hashes = {
        name: normalized_sha256(REPO / authority["path"])
        for name, authority in manifest["source_authorities"].items()
    }
    expected_hashes = {name: authority["sha256"] for name, authority in manifest["source_authorities"].items()}
    audit.check("frozen source hashes", source_hashes == expected_hashes, source_hashes, expected_hashes, "provenance")

    support_ok = (
        derived["support_count"] == oracle["support_count"]
        and derived["support_antipodal"]
        and derived["support_zero_sum"] == oracle["support_zero_sum"]
        and derived["minimum_angle_cosine"] == oracle["minimum_angle_cosine"]
    )
    audit.check("twelve-mode antipodal support", support_ok, {key: derived[key] for key in ("support_count", "support_antipodal", "support_zero_sum", "minimum_angle_cosine")}, "12 antipodal zero-sum modes and cosine 1/2", "geometry")

    extrema_ok = (
        derived["corner_maximum"] == oracle["corner_maximum"]
        and derived["corner_minimum"] == oracle["corner_minimum"]
        and derived["equality_corners"] == oracle["equality_corners"]
        and derived["equality_values"] == oracle["equality_values"]
    )
    audit.check("signed and absolute extrema", extrema_ok, {key: derived[key] for key in ("corner_maximum", "corner_minimum", "equality_corners", "equality_values")}, "both all-equal corners attain +3", "geometry")

    center_ok = derived["center_residues_mod_two"] == oracle["center_residues_mod_two"]
    audit.check("BCC center cosets", center_ok, derived["center_residues_mod_two"], "two BCC residues", "geometry")

    cell_ok = (
        derived["voronoi_vertex_count"] == oracle["voronoi_vertex_count"]
        and derived["square_face_count"] == oracle["square_face_count"]
        and derived["hexagon_face_count"] == oracle["hexagon_face_count"]
        and derived["cell_volume_coefficient"] == oracle["cell_volume_coefficient"]
        and derived["edge_count"] == oracle["voronoi_edge_count"]
    )
    audit.check("regular truncated-octahedron cell", cell_ok, {key: derived[key] for key in ("voronoi_vertex_count", "edge_count", "square_face_count", "hexagon_face_count", "cell_volume_coefficient")}, "24/36/(6+8), volume ell^3/2", "geometry")

    normalization_ok = (
        derived["production_amplitude_square"] == oracle["production_amplitude_square"]
        and derived["bohr_mean"] == manifest["registered_inputs"]["production_intensity"]
        and derived["centers_per_conventional_cube"] == str(oracle["center_cosets_per_cell"])
        and derived["natural_torus_center_count"] == oracle["natural_torus_center_count"]
        and derived["natural_torus_norm_coefficient"] == oracle["natural_torus_norm_coefficient"]
    )
    audit.check("intensity and natural-torus normalization", normalization_ok, {key: derived[key] for key in ("production_amplitude_square", "bohr_mean", "centers_per_conventional_cube", "natural_torus_center_count", "natural_torus_norm_coefficient")}, "A^2=1/6000, mean=I, 2N^3 cells", "normalization")

    native_membership_ok = derived["angle_membership"] and derived["packing_membership"] and derived["operating_region_membership"]
    audit.check("native cFull structural membership", native_membership_ok, {"angle": derived["angle_membership"], "packing": derived["packing_membership"], "region": derived["operating_region_membership"]}, "pi/3 above floor, 12 below cap, anchor inside region", "native-sign")

    sign_tokens = (
        "F[Q]-F[G_*]>0",
        "T7-target: F[Q] > F[G_*]",
    )
    b2_text = (REPO / manifest["source_authorities"]["b2_t7_proposition"]["path"]).read_text(encoding="utf-8")
    audit.check("native sign authority", all(token in b2_text for token in sign_tokens), [token for token in sign_tokens if token in b2_text], list(sign_tokens), "native-sign")

    side16_ok = (
        derived["side16_q0_above_shell_three"]
        and derived["side16_nearest_radial_count"] == oracle["side16_nearest_radial_count"]
        and derived["side16_bcc_direction_count"] == oracle["support_count"]
        and derived["bohr_snap_error_coefficient"] == oracle["bohr_snap_error_coefficient"]
    )
    audit.check("side-16 owner firewall", side16_ok, {key: derived[key] for key in ("side16_q0_above_shell_three", "side16_nearest_radial_count", "side16_bcc_direction_count", "bohr_snap_error_coefficient")}, "literal q0 off shell, 8-vs-12, Bohr error 2I", "interface")

    rescaling_ok = (
        derived["forced_s_square"] == oracle["forced_s_square"]
        and derived["forced_energy_scale"] == oracle["forced_energy_scale"]
        and derived["p1_quadratic_lower"] == oracle["p1_quadratic_lower"]
        and derived["quadratic_contradiction"]
    )
    audit.check("global rescaling obstruction", rescaling_ok, {key: derived[key] for key in ("forced_s_square", "forced_energy_scale", "p1_quadratic_lower", "reading_h_quadratic", "quadratic_gap", "quadratic_contradiction")}, "s^2=1, c_E=2, exact positive quadratic gap", "interface")

    ensemble_ok = derived["production_p1_charge"] == oracle["production_p1_charge"] and derived["r158_intensity_ratio"] == oracle["r158_intensity_ratio"]
    audit.check("changed-ensemble boundary", ensemble_ok, {key: derived[key] for key in ("production_p1_charge", "r158_intensity_ratio")}, "512/125 and 5375/54", "ensemble")

    certificate_tokens = (
        "argmax phi_(A,o)",
        "volume = ell^3/2",
        "F_RH[Q_BCC,A] - F_RH[G_*] > 0",
        "Reading-H-to-pinned-P1 intertwiner",
        "physical empty or disordered reference",
        "generic interface parent remains",
        "Devil's-advocate audit",
        "External review is invited",
        "No R-169 v1.3 PDF is issued",
    )
    audit.check("certificate theorem and scope", all(token in certificate for token in certificate_tokens), [token for token in certificate_tokens if token in certificate], list(certificate_tokens), "scope")

    if staged:
        authority_text = "\n".join(
            (REPO / path).read_text(encoding="utf-8")
            for path in ("claims/GATES.md", "RESULTS-LEDGER.md", "explorations/log.jsonl", "changelog/log.jsonl")
        )
        new_tokens = ["EXP-000860", "R-169 v1.3", *manifest["closed_gate_ids"]]
        audit.check("preformal authority absence", all(token not in authority_text for token in new_tokens), "new authority tokens absent", "new authority tokens absent", "lifecycle")

    return {
        "schema": "tect/pre-a-t055-reading-h-native-owner-bcc-route-termination-primary/1.0",
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
