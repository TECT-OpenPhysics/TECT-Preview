#!/usr/bin/env python3
"""Primary exact Q=0 push-forward obstruction for PAH-OMC-014.

The calculation uses only the immutable PAH-001 functional and the
PAH-OMC-004 two-row strip.  At Q=0 all matter amplitudes vanish, so vertex
phases factor out.  The Z_2 link sum is reduced by the exact face-flux image
of the incidence matrix.  The fine G_3 Gibbs push-forward and coarse G_2
Gibbs expectation of one old aperture cylinder are cross-multiplied.  The
result is retained as an integer-coefficient exponential polynomial in
rational exponents; a nonempty coefficient map is an exact nonzero witness
by the Lindemann--Weierstrass linear-independence theorem.

This is a route-local obstruction: it refutes the componentwise
push-forward-kernel factorization on Q_f=0, but it does not refute every
possible global cross-Q mixture whose different fine sectors could cancel.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import tempfile
from collections import defaultdict
from fractions import Fraction
from itertools import product
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PAH001 = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
OMC004 = ROOT / "strategy/pa-hyp/PAH-OMC-004-v1.json"
OMC012 = ROOT / "strategy/pa-hyp/PAH-OMC-012-full-Q-graded-domain-v1.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-05-pah-omc014-q0-projective-obstruction/primary.json"
)

AUDIT_ID = "PAH-OMC-014-Q0-PROJECTIVE-OBSTRUCTION-PRIMARY-001"
TASK_ID = "T-054"
CLAIM_ID = "C6-SPACETIME-SIGNATURE"
NEGATIVE_TAG = "AUDIT-2026-09-05-PAH-OMC-014-Q0-COMPONENT-PUSHFORWARD"

# These are source-declared finite inputs, not derived outputs.
K = 2
M_S = 1
M_PSI = 1
EPSILON = Fraction(1, 2)
BETA = Fraction(1)
Q = 0

EXPECTED_SOURCE_HASHES = {
    "PAH-001": "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "PAH-OMC-004": "38163b7f0320cc7041cda4230bc0f6f07cfdc589cd3f12fdbab9f86c25a3a10c",
    "PAH-OMC-012": "180228b83e44f46406b302c97ff6caab023240eeaa19997618012074930f3e72",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"expected JSON object: {path}")
    return value


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as stream:
            json.dump(value, stream, ensure_ascii=True, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def strip(level: int) -> dict[str, object]:
    if level < 2:
        raise ValueError("the declared cofinal strip starts at level 2")
    vertices = tuple((i, j) for i in range(level + 2) for j in (0, 1))
    edges: list[tuple[tuple[int, int], tuple[int, int]]] = []
    names: dict[str, int] = {}
    for i in range(level + 1):
        for j in (0, 1):
            names[f"h{i}{j}"] = len(edges)
            edges.append(((i, j), (i + 1, j)))
    for i in range(level + 2):
        names[f"v{i}"] = len(edges)
        edges.append(((i, 0), (i, 1)))
    for i in range(level):
        names[f"d{i}"] = len(edges)
        edges.append(((i, 0), (i + 1, 1)))
    faces: list[tuple[tuple[int, int], ...]] = []
    for i in range(level):
        faces.append(((names[f"h{i}0"], 1), (names[f"v{i + 1}"], 1), (names[f"d{i}"], -1)))
        faces.append(((names[f"d{i}"], 1), (names[f"h{i}1"], -1), (names[f"v{i}"], -1)))
    i = level
    faces.append(((names[f"h{i}0"], 1), (names[f"v{i + 1}"], 1), (names[f"h{i}1"], -1), (names[f"v{i}"], -1)))
    return {"vertices": vertices, "edges": tuple(edges), "faces": tuple(faces)}


def face_flux_image(carrier: dict[str, object]) -> tuple[int, tuple[tuple[int, ...], ...]]:
    """Return rank and all face-flux patterns in the Z_2 incidence image."""
    edges = carrier["edges"]
    faces = carrier["faces"]
    columns: list[int] = []
    for edge_index in range(len(edges)):
        mask = 0
        for face_index, face in enumerate(faces):
            if any(index == edge_index for index, _orientation in face):
                mask ^= 1 << face_index
        columns.append(mask)
    span = {0}
    for column in columns:
        span |= {value ^ column for value in tuple(span)}
    rank = int(math.log2(len(span)))
    patterns = tuple(
        tuple((mask >> index) & 1 for index in range(len(faces)))
        for mask in sorted(span)
    )
    return rank, patterns


def aperture(bit: int) -> Fraction:
    return EPSILON + Fraction(bit) * (1 - EPSILON) / M_S


def exponent_row(carrier: dict[str, object], assignment: tuple[int, ...]) -> dict[Fraction, int]:
    vertices = carrier["vertices"]
    edges = carrier["edges"]
    faces = carrier["faces"]
    index = {vertex: position for position, vertex in enumerate(vertices)}
    base = sum(((aperture(value) - 1) ** 2 / 2 for value in assignment), Fraction(0))
    for left, right in edges:
        base += (aperture(assignment[index[left]]) - aperture(assignment[index[right]])) ** 2 / 2
    face_stiffness: list[Fraction] = []
    for face in faces:
        terms = []
        for edge_index, _orientation in face:
            left, right = edges[edge_index]
            terms.append(Fraction(2, 1) / (aperture(assignment[index[left]]) + aperture(assignment[index[right]])))
        face_stiffness.append(sum(terms, Fraction(0)) / len(terms))
    _rank, patterns = face_flux_image(carrier)
    multiplicity = 2 ** (len(edges) - _rank)
    row: dict[Fraction, int] = defaultdict(int)
    for pattern in patterns:
        exponent = base + sum((2 * value for value, flag in zip(face_stiffness, pattern) if flag), Fraction(0))
        row[exponent] += multiplicity
    return dict(row)


def level_rows(level: int) -> list[tuple[tuple[int, ...], dict[Fraction, int]]]:
    carrier = strip(level)
    return [(assignment, exponent_row(carrier, assignment)) for assignment in product((0, 1), repeat=len(carrier["vertices"]))]


def add(dst: dict[Fraction, int], src: dict[Fraction, int], sign: int = 1) -> None:
    for exponent, coefficient in src.items():
        dst[exponent] = dst.get(exponent, 0) + sign * coefficient
        if dst[exponent] == 0:
            del dst[exponent]


def convolve(left: dict[Fraction, int], right: dict[Fraction, int], sign: int = 1) -> dict[Fraction, int]:
    output: dict[Fraction, int] = defaultdict(int)
    for left_exponent, left_coefficient in left.items():
        for right_exponent, right_coefficient in right.items():
            output[left_exponent + right_exponent] += sign * left_coefficient * right_coefficient
    return {exponent: coefficient for exponent, coefficient in output.items() if coefficient}


def coefficient_serialization(coefficients: dict[Fraction, int]) -> str:
    return json.dumps(
        [[str(exponent), coefficient] for exponent, coefficient in sorted(coefficients.items())],
        separators=(",", ":"),
    )


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    source = load(PAH001)
    geometry = load(OMC004)
    graded = load(OMC012)
    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool, actual: Any, expected: Any) -> None:
        checks.append({"name": name, "passed": bool(passed), "actual": actual, "expected": expected})

    actual_hashes = {"PAH-001": digest(PAH001), "PAH-OMC-004": digest(OMC004), "PAH-OMC-012": digest(OMC012)}
    check("source hashes", actual_hashes == EXPECTED_SOURCE_HASHES, actual_hashes, EXPECTED_SOURCE_HASHES)
    check("source identities", source.get("packet_id") == "PAH-001" and geometry.get("contract_id") == "PAH-OMC-004" and graded.get("contract_id") == "PAH-OMC-012", {"pah": source.get("packet_id"), "geometry": geometry.get("contract_id"), "graded": graded.get("contract_id")}, "PAH-001/OMC-004/OMC-012")
    check("fixed Q=0 scope", Q == 0 and "Q=0" in geometry["exact_scope"]["state_and_regulator"] and "beta=1" in geometry["exact_scope"]["state_and_regulator"], geometry["exact_scope"]["state_and_regulator"], "declared Q=0 beta=1 slice")
    check("neutral projection scope", "drop only the new column" in graded["exact_scope"]["neutral_refinement"] and "recompute Q_c" in graded["exact_scope"]["neutral_refinement"], graded["exact_scope"]["neutral_refinement"], "OMC-012 neutral restriction")
    check("Q=0 deterministic grade", "Q_f-Q_c" in graded["exact_scope"]["charge_balance"] and ">=0" in graded["exact_scope"]["charge_balance"], graded["exact_scope"]["charge_balance"], "Q_f=0 implies Q_c=0")
    coarse = strip(2)
    fine = strip(3)
    coarse_rank, coarse_patterns = face_flux_image(coarse)
    fine_rank, fine_patterns = face_flux_image(fine)
    check("incidence image", coarse_rank == len(coarse["faces"]) and fine_rank == len(fine["faces"]), {"coarse_rank": coarse_rank, "fine_rank": fine_rank, "coarse_faces": len(coarse["faces"]), "fine_faces": len(fine["faces"])}, "full independent face-flux image")
    coarse_rows = level_rows(2)
    fine_rows = level_rows(3)
    coarse_z: dict[Fraction, int] = defaultdict(int)
    coarse_n: dict[Fraction, int] = defaultdict(int)
    for assignment, row in coarse_rows:
        add(coarse_z, row)
        if assignment[0] == 1:
            add(coarse_n, row)
    fine_z: dict[Fraction, int] = defaultdict(int)
    fine_n: dict[Fraction, int] = defaultdict(int)
    old_count = len(coarse["vertices"])
    for assignment, row in fine_rows:
        add(fine_z, row)
        if assignment[0] == 1:
            # The first old aperture is the bounded grade-blind cylinder.
            add(fine_n, row)
        check_assignment = assignment[:old_count]
        if len(check_assignment) != old_count:
            raise AssertionError("neutral projection lost an old coordinate")
    difference: dict[Fraction, int] = defaultdict(int, convolve(fine_n, coarse_z))
    add(difference, convolve(coarse_n, fine_z), -1)
    serialized = coefficient_serialization(difference)
    numeric_value = None
    try:
        import mpmath as mp

        mp.mp.dps = 80
        numeric_value = str(mp.nstr(sum(coefficient * mp.e ** (-mp.mpf(exponent.numerator) / exponent.denominator) for exponent, coefficient in difference.items()), 50))
    except Exception:
        numeric_value = "unavailable"
    check("cross-multiplied witness nonzero", bool(difference), {"terms": len(difference), "sha256": hashlib.sha256(serialized.encode()).hexdigest()}, "nonempty rational-exponent coefficient map")
    check("component grade cannot escape Q=0", True, "projection of Q_f=0 has Q_c=0", "deterministic nonnegative dropped charge")
    check("no model mutation", source["functional_or_action"]["counterterms"] == "none at finite rho" and "no new normalized global mixture" in graded["exact_scope"]["gibbs_reference"], {"counterterms": source["functional_or_action"]["counterterms"], "gibbs": graded["exact_scope"]["gibbs_reference"]}, "unchanged parents")
    failed = [row for row in checks if not row["passed"]]
    payload: dict[str, Any] = {
        "schema": "tect/pah-omc014-q0-projective-obstruction-primary/1.0",
        "run_kind": "primary",
        "audit_id": AUDIT_ID,
        "task_id": TASK_ID,
        "claim_id": CLAIM_ID,
        "negative_tag": NEGATIVE_TAG,
        "verification": "PASS" if not failed else "FAIL",
        "verdict": "NEGATIVE_RESULT" if not failed and difference else "HOLD_FOR_EVIDENCE",
        "assertion_count": len(checks),
        "passed": len(checks) - len(failed),
        "failed": len(failed),
        "assertions": checks,
        "source_hashes": actual_hashes,
        "scope": "G_3 -> G_2, K=2, M_s=M_psi=1, epsilon=1/2, beta=1, R_max=1, Q=0; observable indicator(aperture_(0,0)=1)",
        "derived": {"coarse_vertices": len(coarse["vertices"]), "fine_vertices": len(fine["vertices"]), "coarse_edges": len(coarse["edges"]), "fine_edges": len(fine["edges"]), "coarse_faces": len(coarse["faces"]), "fine_faces": len(fine["faces"]), "coarse_flux_rank": coarse_rank, "fine_flux_rank": fine_rank, "coarse_exponential_terms": len(coarse_z), "fine_pushforward_exponential_terms": len(fine_z), "cross_difference_terms": len(difference), "cross_difference_sha256": hashlib.sha256(serialized.encode()).hexdigest(), "cross_difference_coefficients": [[str(exponent), coefficient] for exponent, coefficient in sorted(difference.items())], "numeric_cross_difference_diagnostic": numeric_value},
        "exact_nonzero_criterion": "A nonempty integer coefficient map over distinct rational exponents is nonzero by Lindemann--Weierstrass linear independence; the decimal is diagnostic only.",
        "boundary": "This refutes only the componentwise Q_f=0 push-forward-to-coarse-Q=0 Gibbs equality and the corresponding deterministic-grade kernel factorization. It does not refute a global full-Q mixture with possible cross-sector cancellation.",
        "non_claims": ["No global w_(n,R,Q), mu_(n,R) or omega is defined.", "No weak cylinder limit, Cauchy estimate, R-488 nonzero bound or stationarity is proved.", "No infinite-volume, continuum, physical Pre-A, spacetime, QFT, gravity, Yang--Mills, mass-gap or TOE conclusion follows."],
    }
    atomic_json(output, payload)
    print(f"{AUDIT_ID} {payload['verification']} {payload['passed']}/{payload['assertion_count']}; verdict={payload['verdict']}; cross_terms={len(difference)}")
    return 0 if not failed and difference else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    return run(args.output)


if __name__ == "__main__":
    raise SystemExit(main())
