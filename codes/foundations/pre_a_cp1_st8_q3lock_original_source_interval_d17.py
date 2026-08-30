#!/usr/bin/env python3
"""Finite d=17 original-source interval enclosure for the Q3LOCK route.

This is a bounded continuation of R-433.  It reuses only the validated
interval primitives from the R-433 implementation and changes the declared
finite cutoff and row contract through the new manifest.  The row is the
unconditional one-site marginal (emission ordinal zero); all choices are
manifest-pinned and no uniform or physical promotion is made.
"""

from __future__ import annotations

import argparse
import gc
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-original-source-interval-d17-manifest.json"
R419_MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-growing-volume-lyapunov-core-tail-stress-manifest.json"
R433_SCRIPT = REPO / "codes/foundations/pre_a_cp1_st8_q3lock_original_source_interval_enclosure.py"
POINT_CACHE = REPO / ".tmp/r435-d17-point-cache.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-primary-original_source_interval_d17/primary.json"

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_original_source_interval_enclosure as base  # noqa: E402

mp = base.mp


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=str)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def lower(value: Any) -> Any:
    return mp.mpf(value.a)


def upper(value: Any) -> Any:
    return mp.mpf(value.b)


def interval_sum(values: Any) -> Any:
    return sum(values, mp.iv.mpf(0))


def interval_from_point(value: Any, digits: int) -> Any:
    return base.interval_from_point(value, digits)


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    source = manifest["source_contract"]
    contract = manifest["interval_contract"]
    fixture = json.loads(R419_MANIFEST.read_text(encoding="utf-8"))["finite_fixture"]
    dimension = int(source["cutoff_dimension"])
    volume = int(source["volume"])
    size = dimension * dimension
    point_digits = int(contract["point_decimal_digits"])
    source_digits = int(contract["source_decimal_digits_in_intervals"])
    mp.mp.dps = point_digits
    mp.iv.dps = int(contract["interval_decimal_digits"])
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check(
        "manifest identity",
        manifest["result_id"] == "R-435" and manifest["exploration_id"] == "EXP-001280" and manifest["claim_bearing"] is False,
        [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"]],
        "R-435/EXP-001280/false",
        "provenance",
    )
    check("source dimension", size == int(contract["expected_hamiltonian_dimension"]), size, contract["expected_hamiltonian_dimension"], "source")
    check("source row kind", source["row_kind"] == "unconditional_one_site_marginal" and source["target_emission_ordinal"] == 0, source["row_kind"], "unconditional ordinal 0", "row")
    check("R-419 authority", sha256(R419_MANIFEST) == manifest["upstream_authority"]["r419_manifest_sha256"], sha256(R419_MANIFEST), manifest["upstream_authority"]["r419_manifest_sha256"], "authority")
    check("R-433 primitive authority", sha256(R433_SCRIPT) == manifest["upstream_authority"]["r433_script_sha256"], sha256(R433_SCRIPT), manifest["upstream_authority"]["r433_script_sha256"], "authority")

    q_point, skew_point, h_point = base.source_sparse(dimension, fixture, interval=False)
    q_interval, skew_interval, h_interval = base.source_sparse(dimension, fixture, interval=True)
    cache_key = {
        "point_digits": point_digits,
        "source_digits": source_digits,
        "dimension": dimension,
        "volume": volume,
        "r419_manifest_sha256": sha256(R419_MANIFEST),
        "r433_script_sha256": sha256(R433_SCRIPT),
    }
    cached: dict[str, Any] | None = None
    if POINT_CACHE.is_file():
        try:
            candidate = json.loads(POINT_CACHE.read_text(encoding="utf-8"))
            if candidate.get("cache_key") == cache_key:
                cached = candidate
        except (OSError, ValueError, TypeError):
            cached = None
    if cached is None:
        energies, h_columns, block_sizes = base.source_eigenpairs(h_point, dimension, mp)
    else:
        energies = [mp.mpf(value) for value in cached["energies"]]
        h_columns = [[mp.mpf(value) for value in row] for row in cached["h_columns"]]
        block_sizes = [int(value) for value in cached["block_sizes"]]
    check("exchange/parity blocks", block_sizes == manifest["expected_block_sizes"], block_sizes, manifest["expected_block_sizes"], "symmetry")
    check("source eigenvalue ordering", all(energies[index] < energies[index + 1] for index in range(size - 1)), "strictly increasing", "strictly increasing", "source")

    if cached is None:
        h_bounds = base.source_residual_bounds(h_interval, energies, h_columns, dimension, source_digits)
    else:
        h_bounds = {key: mp.mpf(value) for key, value in cached["h_bounds"].items()}
        h_bounds["columns_interval"] = []
        h_bounds["energies_interval"] = []
    check("Hamiltonian residual enclosure", h_bounds["residual_upper"] < mp.mpf(contract["hamiltonian_residual_threshold"]), h_bounds["residual_upper"], f"<{contract['hamiltonian_residual_threshold']}", "source interval")
    check("Hamiltonian Gram enclosure", h_bounds["gram_upper"] < mp.mpf(contract["hamiltonian_gram_threshold"]), h_bounds["gram_upper"], f"<{contract['hamiltonian_gram_threshold']}", "source interval")
    check("Hamiltonian polar regime", h_bounds["polar_delta_upper"] < mp.mpf("0.5"), h_bounds["polar_delta_upper"], "<0.5", "source interval")

    if cached is None:
        q_point_dense = base.dense_from_sparse(q_point, dimension)
        q_values, q_vectors = mp.eigsy(q_point_dense)
        q_bounds = base.coordinate_residual_bounds(q_interval, [q_values[index] for index in range(dimension)], q_vectors, dimension, source_digits)
        cache_payload = {
            "cache_key": cache_key,
            "energies": [mp.nstr(value, 60) for value in energies],
            "h_columns": base.jsonable_matrix(h_columns),
            "block_sizes": block_sizes,
            "h_bounds": {key: mp.nstr(value, 60) for key, value in h_bounds.items() if key not in {"columns_interval", "energies_interval"}},
            "q_values": [mp.nstr(value, 60) for value in q_values],
            "q_vectors": base.jsonable_matrix([[q_vectors[row, column] for column in range(dimension)] for row in range(dimension)]),
            "q_bounds": {key: mp.nstr(value, 60) for key, value in q_bounds.items() if key not in {"vectors_interval", "values_interval"}},
        }
        atomic_json(POINT_CACHE, cache_payload)
    else:
        q_values = [mp.mpf(value) for value in cached["q_values"]]
        q_vectors = mp.matrix([[mp.mpf(value) for value in row] for row in cached["q_vectors"]])
        q_bounds = {key: mp.mpf(value) for key, value in cached["q_bounds"].items()}
        q_bounds["vectors_interval"] = [[interval_from_point(q_vectors[row, column], source_digits) for column in range(dimension)] for row in range(dimension)]
        q_bounds["values_interval"] = [interval_from_point(value, source_digits) for value in q_values]
    check("coordinate residual enclosure", q_bounds["residual_upper"] < mp.mpf(contract["coordinate_residual_threshold"]), q_bounds["residual_upper"], f"<{contract['coordinate_residual_threshold']}", "coordinate interval")
    check("coordinate Gram enclosure", q_bounds["gram_upper"] < mp.mpf(contract["coordinate_gram_threshold"]), q_bounds["gram_upper"], f"<{contract['coordinate_gram_threshold']}", "coordinate interval")

    h_error = h_bounds["spectral_approximation_error_upper"]
    q_error = q_bounds["spectral_approximation_error_upper"]
    h_delta = h_bounds["polar_delta_upper"]
    q_delta = q_bounds["polar_delta_upper"]
    lambda_hat = [mp.mpf(mp.nstr(value, source_digits)) for value in energies]
    qvec_hat = [[mp.mpf(mp.nstr(q_vectors[row, column], source_digits)) for column in range(dimension)] for row in range(dimension)]
    hvec_hat = [[mp.mpf(mp.nstr(h_columns[row][column], source_digits)) for column in range(size)] for row in range(size)]
    shift_safety = base.rational(mp, contract["shift_safety"])
    lower_shift = lambda_hat[0] - h_error - shift_safety
    lower_shift_interval = mp.iv.mpf(mp.nstr(lower_shift, source_digits))
    energy_intervals = [interval_from_point(value, source_digits) for value in lambda_hat]
    beta = mp.iv.mpf(str(source["beta"]))
    d_intervals = [mp.iv.exp(-beta * (value - lower_shift_interval)) for value in energy_intervals]
    d_max = max(upper(value) for value in d_intervals)
    h_basis_delta = h_delta * (1 + mp.sqrt(1 + h_bounds["gram_upper"]))
    exponential_error = beta * h_error
    kernel_error = exponential_error + h_basis_delta * d_max
    q_basis_delta = q_delta * (1 + mp.sqrt(1 + q_bounds["gram_upper"]))
    coordinate_vector_error = 2 * q_basis_delta + q_basis_delta * q_basis_delta
    total_diagonal_error = kernel_error + coordinate_vector_error
    check("shifted source cone", lower_shift < lambda_hat[0], [lower_shift, lambda_hat[0]], "lower shift below approximate minimum", "Gibbs")
    check("Gibbs kernel error finite", total_diagonal_error < mp.mpf(contract["diagonal_error_threshold"]), total_diagonal_error, f"<{contract['diagonal_error_threshold']}", "Gibbs")

    h_interval = {}
    h_point = {}
    q_point = {}
    h_bounds["columns_interval"] = []
    gc.collect()

    coordinate_matrix = mp.matrix(size, size)
    for left in range(dimension):
        for right in range(dimension):
            coordinate_index = left * dimension + right
            for x in range(dimension):
                for y in range(dimension):
                    coordinate_matrix[x * dimension + y, coordinate_index] = qvec_hat[x][left] * qvec_hat[y][right]
    h_matrix = mp.matrix(size, size)
    d_mid: list[Any] = []
    d_radius = mp.mpf(0)
    for eigen_index in range(size):
        d_mid_value = (lower(d_intervals[eigen_index]) + upper(d_intervals[eigen_index])) / 2
        d_mid.append(d_mid_value)
        d_radius = max(d_radius, (upper(d_intervals[eigen_index]) - lower(d_intervals[eigen_index])) / 2)
        for state in range(size):
            h_matrix[state, eigen_index] = hvec_hat[state][eigen_index]
    weighted_h = mp.matrix(size, size)
    for state in range(size):
        for eigen_index in range(size):
            weighted_h[state, eigen_index] = h_matrix[state, eigen_index] * d_mid[eigen_index]
    kernel_mid = weighted_h * h_matrix.T
    diagonal_mid = coordinate_matrix.T * kernel_mid * coordinate_matrix

    h_radius = mp.mpf(0)
    h_max = mp.mpf(0)
    for row in range(size):
        for column in range(size):
            value = interval_from_point(h_columns[row][column], source_digits)
            h_radius = max(h_radius, (upper(value) - lower(value)) / 2)
            h_max = max(h_max, abs(h_matrix[row, column]))
    q_radius = mp.mpf(0)
    q_max = mp.mpf(0)
    for row in range(dimension):
        for column in range(dimension):
            value = q_bounds["vectors_interval"][row][column]
            q_radius = max(q_radius, (upper(value) - lower(value)) / 2)
            q_max = max(q_max, abs(qvec_hat[row][column]))
    h_matrix_norm = size * (h_max + h_radius)
    h_rounding_norm = size * h_radius
    d_norm = max(abs(value) for value in d_mid) + d_radius
    delta_kernel_rounding = (2 * h_matrix_norm * h_rounding_norm + h_rounding_norm * h_rounding_norm) * d_norm
    delta_kernel_rounding += (h_matrix_norm + h_rounding_norm) ** 2 * d_radius
    kernel_entry_error = kernel_error + delta_kernel_rounding
    coordinate_norm = mp.sqrt(size) * (q_max + q_radius) ** 2
    kernel_norm = h_matrix_norm * h_matrix_norm * d_norm
    diagonal_radius = (2 * coordinate_norm * coordinate_vector_error + coordinate_vector_error * coordinate_vector_error) * kernel_norm
    diagonal_radius += (coordinate_norm + coordinate_vector_error) ** 2 * kernel_entry_error
    h_diagonal_intervals = [mp.iv.mpf([diagonal_mid[index, index] - diagonal_radius, diagonal_mid[index, index] + diagonal_radius]) for index in range(size)]

    total_diagonal = interval_sum(h_diagonal_intervals)
    normalized_diagonal = [value / total_diagonal for value in h_diagonal_intervals]
    row = [interval_sum(normalized_diagonal[left * dimension : (left + 1) * dimension]) for left in range(dimension)]
    check("unconditional row positivity", all(lower(value) > 0 for value in row), [lower(value) for value in row], ">0", "Gibbs row")
    row_sum = interval_sum(row)
    check("unconditional row normalization", lower(row_sum) <= 1 <= upper(row_sum), row_sum, "contains 1", "Gibbs row")
    point_row = [mp.mpf((lower(value) + upper(value)) / 2) for value in row]
    maximum_index = max(range(dimension), key=lambda index: point_row[index])
    phi = [mp.log(point_row[maximum_index]) - mp.log(value) for value in point_row]
    core = [index for index, value in enumerate(phi) if value < base.rational(mp, source["tail_threshold"])]
    tail = [index for index, value in enumerate(phi) if value >= base.rational(mp, source["tail_threshold"])]
    check("tail split identity", core == source["core_indices"] and tail == source["tail_indices"], [core, tail], [source["core_indices"], source["tail_indices"]], "row")
    maximum_interval = row[maximum_index]
    for index in core:
        phi_interval = mp.iv.log(maximum_interval) - mp.iv.log(row[index])
        check(f"core threshold {index}", upper(phi_interval) < base.rational(mp, source["tail_threshold"]), phi_interval, "<4", "row threshold")
    for index in tail:
        phi_interval = mp.iv.log(maximum_interval) - mp.iv.log(row[index])
        check(f"tail threshold {index}", lower(phi_interval) > base.rational(mp, source["tail_threshold"]), phi_interval, ">4", "row threshold")

    q_vector_intervals = q_bounds["vectors_interval"]
    p_squared = [[mp.iv.mpf(0) for _ in range(dimension)] for _ in range(dimension)]
    skew_norm = base.row_abs_upper(skew_interval, dimension)
    p_basis_delta = q_delta * (1 + mp.sqrt(1 + q_bounds["gram_upper"]))
    p_error = 2 * skew_norm * p_basis_delta + skew_norm * p_basis_delta * p_basis_delta
    for left in range(dimension):
        for right in range(dimension):
            total = mp.iv.mpf(0)
            for row_index in range(dimension):
                for column in range(dimension):
                    total += q_vector_intervals[row_index][left] * skew_interval.get((row_index, column), mp.iv.mpf(0)) * q_vector_intervals[column][right]
            projected = base.inflate(total, p_error)
            p_squared[left][right] = projected * projected
    chi = base.rational(mp, fixture["chi"])
    compressed, basis, _conductance = base.build_residual_interval(row, p_squared, [core, tail], chi)
    gram = [[mp.iv.mpf(0) for _ in range(len(basis[0]))] for _ in range(len(basis[0]))]
    for left in range(len(gram)):
        for right in range(len(gram)):
            gram[left][right] = interval_sum(basis[index][left] * basis[index][right] for index in range(dimension))
    gram_ok = all(lower(gram[index][index]) <= 1 <= upper(gram[index][index]) and all(lower(gram[index][other]) <= 0 <= upper(gram[index][other]) for other in range(len(gram)) if other != index) for index in range(len(gram)))
    check("residual basis interval orthogonality", gram_ok, "diagonal contains 1 and off-diagonal contains 0", "orthonormal enclosure", "residual")
    maximum_width = max(upper(value) - lower(value) for residual_row in compressed for value in residual_row)
    check("residual matrix interval width", maximum_width < base.rational(mp, contract["maximum_matrix_interval_width"]), maximum_width, f"<{contract['maximum_matrix_interval_width']}", "residual")
    lower_probe = base.rational(mp, contract["lower_probe"])
    upper_probe = base.rational(mp, contract["upper_probe"])
    failure_probe = base.rational(mp, contract["cholesky_failure_probe"])
    lower_ok, lower_pivots = base.interval_cholesky_lower(compressed, mp.iv.mpf(mp.nstr(lower_probe, source_digits)))
    check("interval Cholesky lower bound", lower_ok and all(lower(pivot) > 0 for pivot in lower_pivots), min(lower(pivot) for pivot in lower_pivots), f">0 at {lower_probe}", "eigenvalue")
    failure_ok, failure_pivots = base.interval_cholesky_lower(compressed, mp.iv.mpf(mp.nstr(failure_probe, source_digits)))
    check("upper-side Cholesky probe rejected", failure_ok is False and any(upper(pivot) <= 0 for pivot in failure_pivots), [failure_ok, len(failure_pivots)], f"rejected at {failure_probe}", "eigenvalue")
    rayleigh, _vector = base.interval_rayleigh_upper(compressed)
    check("interval Rayleigh upper bound", upper(rayleigh) < upper_probe, [lower(rayleigh), upper(rayleigh)], f"<{upper_probe}", "eigenvalue")
    bracket_width = upper(rayleigh) - lower_probe
    check("certified bracket width", bracket_width < base.rational(mp, contract["maximum_bracket_width"]), bracket_width, f"<{contract['maximum_bracket_width']}", "eigenvalue")

    scope = manifest["scope"]
    for key in ("original_source_interval_certified", "exact_original_hamiltonian_certified", "gibbs_kernel_interval_propagated", "unconditional_row_interval_propagated", "residual_interval_certified", "finite_positive_gap_certified"):
        check(f"scope {key}", scope[key] is True, scope[key], True, "scope")
    for key in ("residual_reuse_closed_for_original_source", "cutoff_uniform_coarse_schur_closed", "volume_uniform_coarse_schur_closed", "phase_uniform_coarse_schur_closed", "exhaustion_uniform_coarse_schur_closed", "common_core_closed", "kms_gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed"):
        check(f"scope firewall {key}", scope[key] is False, scope[key], False, "scope")
    derived = {
        "fixed_row": source,
        "symmetry_block_sizes": block_sizes,
        "point_decimal_digits": point_digits,
        "interval_decimal_digits": int(contract["interval_decimal_digits"]),
        "hamiltonian_dimension": size,
        "hamiltonian_ground_energy_point": mp.nstr(lambda_hat[0], 45),
        "hamiltonian_top_energy_point": mp.nstr(lambda_hat[-1], 45),
        "hamiltonian_residual_upper": mp.nstr(h_bounds["residual_upper"], 45),
        "hamiltonian_gram_upper": mp.nstr(h_bounds["gram_upper"], 45),
        "coordinate_residual_upper": mp.nstr(q_bounds["residual_upper"], 45),
        "coordinate_gram_upper": mp.nstr(q_bounds["gram_upper"], 45),
        "kernel_error_upper": mp.nstr(kernel_error, 45),
        "total_diagonal_error_upper": mp.nstr(total_diagonal_error, 45),
        "conditional_row_lower": [mp.nstr(lower(value), 45) for value in row],
        "conditional_row_upper": [mp.nstr(upper(value), 45) for value in row],
        "tail_split": {"core": core, "tail": tail},
        "maximum_residual_matrix_interval_width": mp.nstr(maximum_width, 45),
        "rayleigh_interval": [mp.nstr(lower(rayleigh), 45), mp.nstr(upper(rayleigh), 45)],
        "lower_probe": mp.nstr(lower_probe, 45),
        "upper_rayleigh_endpoint": mp.nstr(upper(rayleigh), 45),
        "bracket_width": mp.nstr(bracket_width, 45),
        "finite_positive_gap_certified": True,
        "residual_reuse_closed_for_original_source": False,
    }
    payload = {
        "schema": "tect/pre-a-r435-primary/1.0",
        "manifest": MANIFEST.relative_to(REPO).as_posix(),
        "result_id": "R-435",
        "exploration_id": "EXP-001280",
        "claim_id": manifest["claim_ids"][0],
        "run_kind": "primary",
        "verdict": "ORIGINAL_SOURCE_INTERVAL_CERTIFIED",
        "assertion_count": len(checks),
        "assertions": checks,
        "derived": derived,
        "source_hashes": {"primary": sha256(Path(__file__)), "manifest": sha256(MANIFEST), "r419_manifest": sha256(R419_MANIFEST), "r433_script": sha256(R433_SCRIPT)},
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "evidence_level": manifest["evidence_level"],
        "non_claims": manifest["non_claims"],
        "boundary": manifest["boundary"],
    }
    atomic_json(output, payload)
    print(f"R-435 PRIMARY ORIGINAL_SOURCE_INTERVAL_CERTIFIED {len(checks)}/{len(checks)} d={dimension} row=unconditional bracket=[{derived['rayleigh_interval'][0]},{derived['rayleigh_interval'][1]}]", flush=True)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    destination = args.output if args.output.is_absolute() else REPO / args.output
    payload = run(destination)
    if args.self_test:
        assert payload["verdict"] == "ORIGINAL_SOURCE_INTERVAL_CERTIFIED"
        assert payload["derived"]["finite_positive_gap_certified"] is True
        print("R-435 PRIMARY SELFTEST: PASS", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
