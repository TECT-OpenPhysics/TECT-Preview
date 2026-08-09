#!/usr/bin/env python3
"""Independent stdlib audit for the ordered-Q3 Gaussian tangent split."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import tempfile
from collections import Counter
from fractions import Fraction
from pathlib import Path
from typing import Any


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
CANDIDATE_ID = "PA-CP1-CL8-ORDERED-Q3-GAUSSIAN-TANGENT-REGULATOR-ROUTE-SPLIT-v0"
RESULT_ID = "PA-CP1-CL8-SPECTRAL-GAUSSIAN-PROJECTIVE-FAMILY-HADAMARD-COMPARATOR-BARE-CRITICAL-SPEED-CENTERED-PROJECTIVITY-AND-CRITICAL-ZERO-MODE-NOGOS"
NEGATIVE_IDS = (
    "NG-2026-08-04-PRE-A-CP1-CL8-CENTERED-GAUSSIAN-LOW-MODE-EXACT-PROJECTIVITY",
    "NG-2026-08-04-PRE-A-CP1-CL8-CRITICAL-COMPACT-GAUSSIAN-NORMAL-GROUND",
)
PARENT_FILES = (
    "strategy/pre-a-cp1-st8-q3lock-manifest.json",
    "strategy/pre-a-c0a-gaussian-ccr-pah1-embedding-manifest.json",
    "strategy/pre-a-cp1-cl8-semidiscrete-cauchy-oa2-manifest.json",
    "strategy/pre-a-cp1-cl8-finite-quantum-state-boundary-fork-manifest.json",
    "strategy/pre-a-cp1-cl8-quantum-boundary-algebra-intertwiner-route-split-manifest.json",
    "strategy/pre-a-cp1-cl8-history-cut-quantum-algebra-state-compatibility-route-split-manifest.json",
)
SLUG = "pre-a-cp1-cl8-ordered-q3-gaussian-tangent-regulator-route-split"
SCHEMA = f"tect/{SLUG}-independent/0.1"
SCRIPT = Path(__file__).resolve()
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-04-independent-{SLUG}/result.json"


def serial(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value).replace("\\", "/")
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    return value


def sha256(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(serial(payload), stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(self, name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={serial(actual)!r}, expected={serial(expected)!r}")
        self.rows.append({"name": name, "group": group, "status": "PASS", "actual": serial(actual), "expected": serial(expected)})


def matvec(matrix: list[list[int]], vector: list[int]) -> list[int]:
    return [sum(row[j] * vector[j] for j in range(len(vector))) for row in matrix]


def cube_data() -> tuple[list[tuple[int, int, int]], list[list[int]]]:
    nodes = [(a, b, c) for a in (0, 1) for b in (0, 1) for c in (0, 1)]
    index = {node: i for i, node in enumerate(nodes)}
    matrix = [[0 for _ in nodes] for _ in nodes]
    for node in nodes:
        i = index[node]
        for axis in range(3):
            neighbor = list(node)
            neighbor[axis] ^= 1
            j = index[tuple(neighbor)]
            matrix[i][i] += 1
            matrix[i][j] -= 1
    return nodes, matrix


def convolve(left: list[Fraction], right: list[Fraction], order: int) -> list[Fraction]:
    result = [Fraction(0) for _ in range(order + 1)]
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            if i + j <= order:
                result[i + j] += a * b
    return result


def build_payload() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    parents = [json.loads((REPO / path).read_text(encoding="utf-8")) for path in PARENT_FILES]
    audit = Audit()

    audit.check("candidate id", manifest.get("candidate_id") == CANDIDATE_ID, manifest.get("candidate_id"), CANDIDATE_ID, "identity")
    audit.check("result id", manifest.get("result_id") == RESULT_ID, manifest.get("result_id"), RESULT_ID, "identity")
    audit.check("negative ids", tuple(manifest.get("negative_ids", [])) == NEGATIVE_IDS, manifest.get("negative_ids"), NEGATIVE_IDS, "identity")
    audit.check("parent ids", tuple(parent.get("candidate_id") for parent in parents) == tuple(manifest.get("parent_ids", [])), [parent.get("candidate_id") for parent in parents], manifest.get("parent_ids"), "identity")
    audit.check("claim nonbearing", manifest.get("claim_bearing") is False, manifest.get("claim_bearing"), False, "identity")

    nodes, laplacian = cube_data()
    spectrum: Counter[int] = Counter()
    for alpha in nodes:
        level = sum(alpha)
        vector = [(-1) ** sum(a * e for a, e in zip(alpha, node)) for node in nodes]
        actual = matvec(laplacian, vector)
        expected = [2 * level * value for value in vector]
        audit.check(f"independent Walsh eigenvector {alpha}", actual == expected, actual, expected, "Q3")
        spectrum[2 * level] += 1
    audit.check("independent Q3 spectrum", spectrum == Counter({0: 1, 2: 3, 4: 3, 6: 1}), dict(spectrum), {0: 1, 2: 3, 4: 3, 6: 1}, "Q3")
    audit.check("independent Q3 row sums", [sum(row) for row in laplacian] == [0] * 8, [sum(row) for row in laplacian], [0] * 8, "Q3")

    # Ordered fixture r=-1/2, g=1, lambda=3 gives v^2=1/2 and
    # nu_s=-2r+2s*lambda*v^2=1+3s.
    r = Fraction(-1, 2)
    g = Fraction(1)
    locking = Fraction(3)
    v2 = -r / g
    species = [-2 * r + 2 * s * locking * v2 for s in range(4)]
    audit.check("independent ordered fixture", species == [1, 4, 7, 10], species, [1, 4, 7, 10], "Hessian")
    expanded = [-2 * r * (1 + Fraction(s) * locking / g) for s in range(4)]
    audit.check("two stiffness derivations agree", species == expanded, species, expanded, "Hessian")
    audit.check("ordered branches positive", all(value > 0 for value in species), species, "all positive", "Hessian")
    zero_locking_species = [-2 * r + 2 * s * Fraction(0) * v2 for s in range(4)]
    audit.check("independent lambda-zero boundary", zero_locking_species == [-2 * r] * 4, zero_locking_species, [-2 * r] * 4, "Hessian")
    audit.check("ordered multiplicities sum eight", sum((1, 3, 3, 1)) == 8, sum((1, 3, 3, 1)), 8, "Hessian")

    spacing = Fraction(3, 5)
    field_scale_squared = spacing / 8
    momentum_scale_squared = 8 / spacing
    audit.check("canonical scale squares", field_scale_squared * momentum_scale_squared == 1, field_scale_squared * momentum_scale_squared, 1, "normalization")
    raw_p2_coefficient = Fraction(4, 1) / spacing
    transformed_p2_coefficient = raw_p2_coefficient * field_scale_squared
    audit.check("oscillator kinetic coefficient", transformed_p2_coefficient == Fraction(1, 2), transformed_p2_coefficient, Fraction(1, 2), "normalization")
    raw_q2_coefficient = spacing / 16
    transformed_q2_coefficient = raw_q2_coefficient * momentum_scale_squared
    audit.check("oscillator potential coefficient", transformed_q2_coefficient == Fraction(1, 2), transformed_q2_coefficient, Fraction(1, 2), "normalization")

    # Direct-product spectral restriction, reconstructed without the primary.
    def spectral_covariance(cutoff: int) -> dict[tuple[int, int, str], float]:
        result: dict[tuple[int, int, str], float] = {}
        for mode in range(cutoff + 1):
            frequency = math.sqrt(1.0 + mode * mode)
            for quadrature in range(1 if mode == 0 else 2):
                result[(mode, quadrature, "q")] = 1.0 / frequency
                result[(mode, quadrature, "p")] = frequency
        return result
    spectral_small = spectral_covariance(2)
    spectral_large = spectral_covariance(5)
    audit.check("independent spectral restriction", all(spectral_large[key] == value for key, value in spectral_small.items()), {str(key): spectral_large[key] for key in spectral_small}, spectral_small, "projective")
    audit.check("independent spectral nesting", set(spectral_small) < set(spectral_large), len(spectral_large), "strict superset", "projective")
    uncertainty = [(spectral_small[key], spectral_small[(key[0], key[1], "p")]) for key in spectral_small if key[2] == "q"]
    audit.check("independent covariance products", all(abs(qvar * pvar - 1.0) < 1e-15 for qvar, pvar in uncertainty), uncertainty, "all one in hbar=2 fixture", "projective")

    # Algebraic refinement identity.  Put u=sin^2(k a/4).  Then the fine
    # symbol is 16u/a^2 and the coarse symbol is 16u(1-u)/a^2.
    identity_samples = []
    for u in (Fraction(1, 16), Fraction(1, 4), Fraction(9, 16)):
        a2 = Fraction(25, 9)
        fine = 16 * u / a2
        coarse = 16 * u * (1 - u) / a2
        witness = 16 * u * u / a2
        identity_samples.append((u, fine, coarse, witness))
    audit.check("independent refinement identity", all(fine - coarse == witness for _, fine, coarse, witness in identity_samples), identity_samples, "fine-coarse=witness", "centered-no-go")
    audit.check("independent refinement strictness", all(fine > coarse for _, fine, coarse, _ in identity_samples), identity_samples, "fine>coarse", "centered-no-go")
    # Exact non-Nyquist fixture: L=6, M=6, n=2, sin^2(pi/3)=3/4;
    # after refinement sin^2(pi/6)=1/4.
    coarse_symbol = 4 * Fraction(3, 4)
    fine_symbol = 16 * Fraction(1, 4)
    audit.check("independent coarse fixture", coarse_symbol == 3, coarse_symbol, 3, "centered-no-go")
    audit.check("independent fine fixture", fine_symbol == 4, fine_symbol, 4, "centered-no-go")
    coarse_frequency = math.sqrt(1.0 + float(coarse_symbol))
    fine_frequency = math.sqrt(1.0 + float(fine_symbol))
    audit.check("independent field covariance mismatch", 1 / fine_frequency < 1 / coarse_frequency, [1 / coarse_frequency, 1 / fine_frequency], "fine<coarse", "centered-no-go")
    audit.check("independent momentum covariance mismatch", fine_frequency > coarse_frequency, [coarse_frequency, fine_frequency], "fine>coarse", "centered-no-go")

    # Derive the centered-symbol series by squaring the sine Taylor series.
    sine = [Fraction(0) for _ in range(10)]
    sine[1] = Fraction(1)
    sine[3] = Fraction(-1, 6)
    sine[5] = Fraction(1, 120)
    sine[7] = Fraction(-1, 5040)
    sine[9] = Fraction(1, 362880)
    sine_squared = convolve(sine, sine, 10)
    # 4 sin^2(k a/2)/a^2: coefficient at a^(2j-2) is
    # 4*sine_squared[2j]*k^(2j)/2^(2j).
    centered_coefficients = {
        power - 2: Fraction(4) * sine_squared[power] / (2**power)
        for power in (2, 4, 6, 8)
    }
    expected_coefficients = {0: Fraction(1), 2: Fraction(-1, 12), 4: Fraction(1, 360), 6: Fraction(-1, 20160)}
    audit.check("independent centered series", centered_coefficients == expected_coefficients, centered_coefficients, expected_coefficients, "convergence")

    errors_q: list[float] = []
    errors_t: list[float] = []
    for M in (30, 60, 120, 240):
        a = 2 * math.pi / M
        k = 4.0
        khat = 2.0 * math.sin(k * a / 2.0) / a
        continuum = math.sqrt(3.0 + k * k)
        lattice = math.sqrt(3.0 + khat * khat)
        cq0 = 1.0 / (2.0 * continuum)
        cqa = 1.0 / (2.0 * lattice)
        errors_q.append(abs(cqa - cq0))
        t = 0.43
        w0 = cq0 * complex(math.cos(continuum * t), -math.sin(continuum * t))
        wa = cqa * complex(math.cos(lattice * t), -math.sin(lattice * t))
        errors_t.append(abs(wa - w0))
    ratios_q = [errors_q[i + 1] / errors_q[i] for i in range(3)]
    ratios_t = [errors_t[i + 1] / errors_t[i] for i in range(3)]
    audit.check("independent fixed-mode convergence", all(errors_q[i + 1] < errors_q[i] for i in range(3)), errors_q, "strict decrease", "convergence")
    audit.check("independent covariance a2 rate", all(0.20 < ratio < 0.28 for ratio in ratios_q), ratios_q, "near one quarter", "convergence")
    audit.check("independent finite-time convergence", all(errors_t[i + 1] < errors_t[i] for i in range(3)), errors_t, "strict decrease", "convergence")
    audit.check("independent finite-time a2 rate", all(0.20 < ratio < 0.28 for ratio in ratios_t), ratios_t, "near one quarter", "convergence")

    # Critical scaling from exact rational parameter ratios: rho -> rho/4
    # doubles xi, halves the gap, and leaves gap*xi fixed.
    branch = Fraction(5, 2)
    speed_squared = Fraction(7, 3)
    critical_rows = []
    critical_exact_rows = []
    for rho in (Fraction(1), Fraction(1, 4), Fraction(1, 16)):
        nu = 2 * rho * branch
        xi_squared = speed_squared / nu
        gap_squared = nu
        xi = math.sqrt(float(speed_squared / nu))
        gap = math.sqrt(float(nu))
        covariance = 1.0 / (2.0 * math.sqrt(float(nu)))
        critical_rows.append((rho, xi, gap, covariance))
        critical_exact_rows.append((rho, xi_squared, gap_squared))
    audit.check("independent xi exponent half", all(abs(critical_rows[i + 1][1] / critical_rows[i][1] - 2.0) < 1e-14 for i in range(2)), critical_rows, "xi doubles", "critical")
    audit.check("independent gap exponent half", all(abs(critical_rows[i + 1][2] / critical_rows[i][2] - 0.5) < 1e-14 for i in range(2)), critical_rows, "gap halves", "critical")
    audit.check("independent z one", all(abs(critical_rows[i][1] * critical_rows[i][2] - math.sqrt(float(speed_squared))) < 1e-14 for i in range(3)), critical_rows, "gap*xi=speed", "critical")
    rho_ratio = critical_exact_rows[1][0] / critical_exact_rows[0][0]
    xi_squared_ratio = critical_exact_rows[1][1] / critical_exact_rows[0][1]
    gap_squared_ratio = critical_exact_rows[1][2] / critical_exact_rows[0][2]

    def integer_scaling_exponent(base: Fraction, value: Fraction) -> int:
        matches = [power for power in range(-4, 5) if base**power == value]
        if len(matches) != 1:
            raise AssertionError(f"non-unique scaling exponent: base={base}, value={value}, matches={matches}")
        return matches[0]

    xi_power = Fraction(integer_scaling_exponent(rho_ratio, xi_squared_ratio), 2)
    gap_power = Fraction(integer_scaling_exponent(rho_ratio, gap_squared_ratio), 2)
    nu_mf = -xi_power
    z_value = -gap_power / xi_power
    common_speed_squared = critical_exact_rows[0][1] * critical_exact_rows[0][2]
    audit.check("independent derived nu half", nu_mf == Fraction(1, 2), nu_mf, Fraction(1, 2), "critical")
    audit.check("independent derived z one", z_value == 1, z_value, 1, "critical")
    audit.check("independent common speed squared", common_speed_squared == speed_squared, common_speed_squared, speed_squared, "critical")
    audit.check("independent zero covariance diverges", critical_rows[0][3] < critical_rows[1][3] < critical_rows[2][3], [row[3] for row in critical_rows], "strict growth", "zero-mode")
    characteristic = [math.exp(-0.5 * row[3]) for row in critical_rows]
    audit.check("independent zero characteristic collapses", characteristic[0] > characteristic[1] > characteristic[2] > 0, characteristic, "strict decrease", "zero-mode")
    no_normal_ground = "no normalizable ground vector" in manifest["critical_zero_mode_no_go"]["conclusion"]
    audit.check("free particle obstruction recorded", no_normal_ground, manifest["critical_zero_mode_no_go"]["conclusion"], "contains no normalizable ground", "zero-mode")

    audit.check("Hadamard prior theorem named", "Fulling, Narcowich and Wald" in manifest["Hadamard_comparator"]["theorem_owner"], manifest["Hadamard_comparator"]["theorem_owner"], "contains theorem owners", "Hadamard")
    audit.check("Hadamard ordered tangent only", "free massive ordered-tangent comparator only" in manifest["Hadamard_comparator"]["scope_boundary"], manifest["Hadamard_comparator"]["scope_boundary"], "contains ordered tangent only", "Hadamard")
    audit.check("spectral regulator differs from centered", "not the inherited centered nodal CL8 regulator" in manifest["spectral_projective_state_family"]["regulator_boundary"], manifest["spectral_projective_state_family"]["regulator_boundary"], "contains regulator distinction", "Hadamard")
    # Independent exact rational-square fixture for the effective metric map:
    # chi=9,c=4 gives sqrt(chi/c)=3/2 and (chi*c)^(1/2)=6.
    sqrt_spatial_metric = Fraction(3, 2)
    field_rescaling_squared = Fraction(6)
    fixture_chi = Fraction(9)
    fixture_c = Fraction(4)
    fixture_nu = Fraction(5)
    audit.check("independent effective metric time coefficient", sqrt_spatial_metric * field_rescaling_squared == fixture_chi, sqrt_spatial_metric * field_rescaling_squared, fixture_chi, "Hadamard")
    audit.check("independent effective metric spatial coefficient", field_rescaling_squared / sqrt_spatial_metric == fixture_c, field_rescaling_squared / sqrt_spatial_metric, fixture_c, "Hadamard")
    audit.check("independent effective metric mass coefficient", sqrt_spatial_metric * field_rescaling_squared * fixture_nu / fixture_chi == fixture_nu, sqrt_spatial_metric * field_rescaling_squared * fixture_nu / fixture_chi, fixture_nu, "Hadamard")
    audit.check("independent smooth extension metadata", "extend continuously" in manifest["Hadamard_comparator"]["full_Cauchy_extension"], manifest["Hadamard_comparator"]["full_Cauchy_extension"], "contains continuous extension", "Hadamard")
    audit.check("independent exact spacetime restriction metadata", "exact finite-mode restriction" in manifest["Hadamard_comparator"]["spacetime_two_point"], manifest["Hadamard_comparator"]["spacetime_two_point"], "contains exact restriction", "Hadamard")

    true_scope = (
        "ordered_Q3_Hessian_spectrum",
        "canonical_a_over_8_mode_normalization",
        "massive_spectral_projective_Gaussian_family",
        "massive_ordered_tangent_Hadamard_comparator",
        "centered_fixed_mode_O_a2_convergence",
        "centered_finite_time_two_point_convergence",
        "bare_mean_field_nu_half_and_z_one",
        "bare_common_tangent_speed",
    )
    false_scope = (
        "natural_centered_exact_projectivity",
        "critical_compact_full_Gaussian_normal_ground",
        "loop_or_RG_speed_protection",
        "interacting_history_cut_state_family",
        "interacting_continuum_Hadamard_state",
        "original_3D_Q3LOCK_parent",
        "physical_light_speed_derived",
        "physical_phase_transition",
        "physical_state_or_vacuum",
        "below_empty_space_comparison",
        "hbar_origin_derived",
        "C0_closed",
        "N1_through_N5_closed",
        "C6_advanced",
        "CP1_complete",
        "Pre_A_complete",
    )
    for key in true_scope:
        audit.check(f"scope true: {key}", manifest["scope"].get(key) is True, manifest["scope"].get(key), True, "scope")
    for key in false_scope:
        audit.check(f"scope false: {key}", manifest["scope"].get(key) is False, manifest["scope"].get(key), False, "scope")
    audit.check("interacting next gate", manifest["gate_resolution"]["next_gate"] == "PA-CP1-CL8-INTERACTING-REGULATOR-COMPATIBLE-HISTORY-CUT-STATE-FAMILY", manifest["gate_resolution"]["next_gate"], "PA-CP1-CL8-INTERACTING-REGULATOR-COMPATIBLE-HISTORY-CUT-STATE-FAMILY", "scope")

    derived = {
        "Q3_spectrum": {"eigenvalues": sorted(spectrum), "multiplicities": [spectrum[value] for value in sorted(spectrum)]},
        "ordered_fixture": species,
        "canonical_scale_squared_product": field_scale_squared * momentum_scale_squared,
        "spectral_restriction": True,
        "centered_fixture": {"L": 6, "coarse_M": 6, "fine_M": 12, "n": 2, "coarse_symbol_squared": coarse_symbol, "fine_symbol_squared": fine_symbol},
        "centered_series_coefficients": centered_coefficients,
        "convergence_errors": {"field": errors_q, "finite_time": errors_t, "field_ratios": ratios_q, "finite_time_ratios": ratios_t},
        "bare_critical": {
            "nu_MF": nu_mf,
            "z": z_value,
            "common_speed_squared_fixture_c7_chi3": common_speed_squared,
            "full_compact_Gaussian_ground": not no_normal_ground,
        },
        "negative_ids": list(NEGATIVE_IDS),
    }
    source_hashes = {"script": sha256(SCRIPT), "manifest": sha256(MANIFEST)}
    for path in PARENT_FILES:
        source_hashes[path] = sha256(REPO / path)
    return {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "parent_ids": manifest["parent_ids"],
        "result_id": RESULT_ID,
        "negative_ids": list(NEGATIVE_IDS),
        "task_id": "T-054",
        "claim_context": "C6-SPACETIME-SIGNATURE",
        "claim_bearing": False,
        "verdict": manifest["verdict"],
        "derived": derived,
        "source_sha256": source_hashes,
        "scope": manifest["scope"],
        "assertions": audit.rows,
        "assertion_summary": {"passed": len(audit.rows), "total": len(audit.rows)},
        "next_gate": manifest["gate_resolution"]["next_gate"],
        "no_overclaim": manifest["no_overclaim"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = build_payload()
    if not args.self_test:
        atomic_json(args.output, payload)
    summary = payload["assertion_summary"]
    print(f"{CANDIDATE_ID} independent: {summary['passed']}/{summary['total']} PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
