#!/usr/bin/env python3
"""Independent interval cross-check for the R-431 rounded graph snapshot.

This lane does not import R-431.  It reconstructs the R-429 snapshot, uses the
reverse block/anchor order, permutes the compressed matrix before interval
Cholesky, and recomputes the Rayleigh upper bound independently.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pre-a-cp1-st8-q3lock-rounded-snapshot-interval-enclosure-manifest.json"
R429_MANIFEST = ROOT / "strategy/pre-a-cp1-st8-q3lock-residual-precision-uplift-manifest.json"
R429_SCRIPT = ROOT / "codes/foundations/pre_a_cp1_st8_q3lock_residual_precision_uplift.py"
OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-independent-rounded_snapshot_interval_enclosure/independent.json"


def load_mp():
    try:
        import mpmath as module
        return module
    except ModuleNotFoundError:
        runtime = ROOT / ".tmp/verification-runtime"
        sys.path.insert(0, str(runtime))
        import mpmath as module
        return module


mp = load_mp()
mp.iv.dps = 80
mp.mp.dps = 120


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
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


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def lo(value: Any) -> Any:
    return mp.mpf(value.a)


def hi(value: Any) -> Any:
    return mp.mpf(value.b)


def interval_from_float(value: float) -> Any:
    rational = Fraction.from_float(float(value))
    return mp.iv.mpf(rational.numerator) / mp.iv.mpf(rational.denominator)


def interval_hull(left: Any, right: Any) -> Any:
    return mp.iv.mpf([min(lo(left), lo(right)), max(hi(left), hi(right))])


def isum(values: list[Any]) -> Any:
    return sum(values, mp.iv.mpf(0))


def contains(value: Any, target: Any) -> bool:
    target_mp = mp.mpf(target)
    return lo(value) <= target_mp <= hi(value)


def reconstruct() -> tuple[list[Any], list[list[Any]], list[np.ndarray]]:
    sys.path.insert(0, str(R429_SCRIPT.parent))
    import pre_a_cp1_st8_q3lock_residual_precision_uplift as r429  # noqa: PLC0415

    pi_float, conductance_float, blocks = r429.row_inputs()
    return (
        [interval_from_float(float(value)) for value in pi_float],
        [[interval_from_float(float(value)) for value in row] for row in conductance_float],
        blocks,
    )


def residual_matrix(pi: list[Any], conductance: list[list[Any]], blocks: list[np.ndarray]) -> list[list[Any]]:
    n = len(pi)
    c = [[mp.iv.mpf(0) for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for j in range(n):
            c[i][j] = interval_hull(conductance[i][j], conductance[j][i])
    op = [[mp.iv.mpf(0) for _ in range(n)] for _ in range(n)]
    for i in range(n):
        diagonal = isum(c[i])
        for j in range(n):
            op[i][j] = (diagonal if i == j else -c[i][j]) / mp.iv.sqrt(pi[i] * pi[j])

    # Reverse both block order and anchor choice from the primary lane.
    raw: list[list[Any]] = []
    for array in reversed(blocks):
        block = [int(index) for index in array]
        anchor = block[-1]
        for index in reversed(block[:-1]):
            vector = [mp.iv.mpf(0) for _ in range(n)]
            vector[anchor] = mp.iv.sqrt(pi[index])
            vector[index] = -mp.iv.sqrt(pi[anchor])
            raw.append(vector)
    basis: list[list[Any]] = []
    for vector in raw:
        work = list(vector)
        for previous in basis:
            coefficient = isum([a * b for a, b in zip(previous, work)])
            work = [value - coefficient * base for value, base in zip(work, previous)]
        norm_square = isum([value * value for value in work])
        if hi(norm_square) <= 0:
            raise AssertionError("independent interval vector lost positivity")
        norm = mp.iv.sqrt(norm_square)
        basis.append([value / norm for value in work])
    q = [list(column) for column in zip(*basis)]
    k = len(q[0])
    compressed = [[mp.iv.mpf(0) for _ in range(k)] for _ in range(k)]
    for i in range(k):
        for j in range(k):
            total = mp.iv.mpf(0)
            for a in range(n):
                total += q[a][i] * isum([op[a][b] * q[b][j] for b in range(n)])
            compressed[i][j] = total
    return [[interval_hull(compressed[i][j], compressed[j][i]) for j in range(k)] for i in range(k)]


def permute(matrix: list[list[Any]]) -> list[list[Any]]:
    order = list(reversed(range(len(matrix))))
    return [[matrix[i][j] for j in order] for i in order]


def interval_cholesky(matrix: list[list[Any]], probe: Any) -> tuple[bool, list[Any]]:
    n = len(matrix)
    factor = [[mp.iv.mpf(0) for _ in range(n)] for _ in range(n)]
    pivots: list[Any] = []
    for i in range(n):
        pivot = matrix[i][i] - probe - isum([factor[i][k] * factor[i][k] for k in range(i)])
        pivots.append(pivot)
        if lo(pivot) <= 0:
            return False, pivots
        factor[i][i] = mp.iv.sqrt(pivot)
        for j in range(i + 1, n):
            factor[j][i] = (matrix[j][i] - isum([factor[j][k] * factor[i][k] for k in range(i)])) / factor[i][i]
    return True, pivots


def rayleigh(matrix: list[list[Any]]) -> Any:
    center = np.asarray([[(float(lo(value)) + float(hi(value))) / 2 for value in row] for row in matrix], dtype=float)
    _values, vectors = np.linalg.eigh(center)
    vector = [interval_from_float(float(value)) for value in vectors[:, 0]]
    numerator = mp.iv.mpf(0)
    for i in range(len(matrix)):
        numerator += vector[i] * isum([matrix[i][j] * vector[j] for j in range(len(matrix))])
    denominator = isum([value * value for value in vector])
    if lo(denominator) <= 0:
        raise AssertionError("independent Rayleigh denominator is not positive")
    return numerator / denominator


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    contract = manifest["interval_contract"]
    oracle = manifest["test_oracles"]
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("manifest identity", manifest["result_id"] == "R-431" and manifest["exploration_id"] == "EXP-001276" and manifest["claim_bearing"] is False, [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"]], "R-431/EXP-001276/false", "provenance")
    check("upstream hashes", sha256(R429_MANIFEST) == manifest["upstream_authority"]["r429_sha256"] and sha256(R429_SCRIPT) == manifest["upstream_authority"]["r429_script_sha256"], "R429 manifest and producer hash", "declared SHA-256", "authority")
    pi, conductance, blocks = reconstruct()
    pi_sum = isum(pi)
    normalization_error = max(abs(lo(pi_sum) - 1), abs(hi(pi_sum) - 1))
    check("positive weights", all(lo(value) > 0 for value in pi), "all lower endpoints positive", ">0", "snapshot")
    check("normalization", normalization_error <= mp.mpf(str(contract["snapshot_normalization_tolerance"])), normalization_error, f"<={contract['snapshot_normalization_tolerance']}", "snapshot")
    check("reverse block sizes", [len(block) for block in blocks] == [int(contract["fixed_row"]["core_size"]), int(contract["fixed_row"]["tail_size"])], [len(block) for block in blocks], "7/9", "fixture")
    matrix = permute(residual_matrix(pi, conductance, blocks))
    lower = interval_from_decimal = mp.iv.mpf(str(contract["lower_probe"]))
    upper_probe = mp.iv.mpf(str(contract["cholesky_failure_probe"]))
    lower_ok, lower_pivots = interval_cholesky(matrix, lower)
    check("permuted interval Cholesky lower", lower_ok and all(lo(value) > 0 for value in lower_pivots), min(lo(value) for value in lower_pivots), ">0", "eigenvalue enclosure")
    failure_ok, failure_pivots = interval_cholesky(matrix, upper_probe)
    check("permuted upper probe rejected", failure_ok is False and any(hi(value) <= 0 for value in failure_pivots), [failure_ok, len(failure_pivots)], "rejected", "eigenvalue enclosure")
    quotient = rayleigh(matrix)
    check("independent Rayleigh upper", hi(quotient) <= mp.mpf(str(contract["upper_probe"])), [str(lo(quotient)), str(hi(quotient))], f"<={contract['upper_probe']}", "eigenvalue enclosure")
    check("R-422 separation", mp.mpf(str(contract["lower_probe"])) > mp.mpf(str(oracle["r422_lower_separation_threshold"])), str(mp.mpf(str(contract["lower_probe"])) - mp.mpf(str(oracle["r422_reference"]))), f">{contract['comparison_tolerance']}", "reference separation")
    check("R-426 direct separation", hi(quotient) < mp.mpf(str(oracle["r426_upper_separation_threshold"])), str(mp.mpf(str(oracle["r426_direct_reference"])) - hi(quotient)), f">{contract['comparison_tolerance']}", "reference separation")
    bracket_width = hi(quotient) - mp.mpf(str(contract["lower_probe"]))
    check("bracket width", bracket_width <= mp.mpf(str(contract["maximum_bracket_width"])), bracket_width, f"<={contract['maximum_bracket_width']}", "eigenvalue enclosure")
    scope = manifest["scope"]
    check("scope firewall", scope["rounded_snapshot_interval_certified"] is True and scope["original_source_interval_certified"] is False and scope["residual_reuse_closed_for_original_source"] is False and scope["no_tier_change"] is True, scope, "snapshot only", "scope")
    payload = {
        "schema": "tect/pre-a-r431-independent/1.0",
        "result_id": "R-431",
        "exploration_id": "EXP-001276",
        "claim_id": manifest["claim_ids"][0],
        "manifest": MANIFEST.relative_to(ROOT).as_posix(),
        "run_kind": "independent",
        "verdict": "INDEPENDENT_ROUNDED_SNAPSHOT_INTERVAL",
        "assertion_count": len(checks),
        "assertions": checks,
        "derived": {
            "lower_probe": contract["lower_probe"],
            "upper_endpoint": str(hi(quotient)),
            "bracket_width": str(bracket_width),
            "rayleigh_interval": [str(lo(quotient)), str(hi(quotient))],
            "lower_min_pivot": str(min(lo(value) for value in lower_pivots)),
            "snapshot_normalization_error": str(normalization_error),
            "rounded_snapshot_interval_certified": True,
            "original_source_interval_certified": False,
            "r426_route_failure_preserved": True,
        },
        "source_hashes": {"manifest": sha256(MANIFEST), "r429_manifest": sha256(R429_MANIFEST), "r429_script": sha256(R429_SCRIPT)},
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "evidence_level": manifest["evidence_level"],
        "non_claims": manifest["non_claims"],
        "boundary": manifest["boundary"],
    }
    atomic_json(OUTPUT, payload)
    print(f"R-431 INDEPENDENT {len(checks)}/{len(checks)} interval PASS bracket=[{contract['lower_probe']},{hi(quotient)}]")
    return payload


if __name__ == "__main__":
    run()
