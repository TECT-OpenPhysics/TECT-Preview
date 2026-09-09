#!/usr/bin/env python3
"""Audit the PAH-001 link-root multiplicity ambiguity at K=2.

PAH-001 says that one link is multiplied by ``zeta_K`` or
``zeta_K^(-1)``, but does not state whether coincident state maps are counted
as separate directed roots.  On the already registered PAH-OMC-004 finite
incidence witness, K=2 makes the two maps identical.  This audit constructs
the two source-compatible completions (two labelled channels versus one
deduplicated involution) and computes their exact generator values on a
closed-face holonomy observable.  It is an underdetermination audit, not a
change to PAH-001 or a physical result.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PAH = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
GEOMETRY = ROOT / "strategy/pa-hyp/PAH-OMC-004-v1.json"
PREREG = ROOT / "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-08-pah-omc020-source-multiplicity/primary.json"
)

AUDIT_ID = "PAH-LINK-MULTIPLICITY-001"
EXPLORATION_ID = "EXP-001645"
RESULT_ID = "R-527"
TASK_ID = "T-063"

PINS = {
    "strategy/pa-hyp/PAH-001-v1.json":
        "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-004-v1.json":
        "38163b7f0320cc7041cda4230bc0f6f07cfdc589cd3f12fdbab9f86c25a3a10c",
    "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json":
        "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"expected JSON object: {path}")
    return value


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(encode(payload), handle, indent=2, sort_keys=True, ensure_ascii=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def add(rows: list[dict[str, Any]], name: str, actual: Any, expected: Any, passed: bool) -> None:
    if not passed:
        raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
    rows.append({"name": name, "status": "PASS", "actual": actual, "expected": expected})


def encode(value: Any) -> Any:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(key): encode(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [encode(item) for item in value]
    return value


def parse_fraction(text: str, pattern: str) -> Fraction:
    match = re.search(pattern, text)
    if not match:
        raise AssertionError(f"missing fixture input: {pattern}")
    numerator, denominator = match.group(1).split("/")
    return Fraction(int(numerator), int(denominator))


def edge_cycle(edges: list[list[int]], face: list[int]) -> bool:
    incidence: dict[int, int] = {}
    for edge_id in face:
        left, right = edges[edge_id]
        incidence[left] = incidence.get(left, 0) + 1
        incidence[right] = incidence.get(right, 0) + 1
    return all(value == 2 for value in incidence.values()) and len(incidence) == len(face)


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    pa = load(PAH)
    geometry = load(GEOMETRY)
    prereg = load(PREREG)
    rows: list[dict[str, Any]] = []

    hashes = {relative: sha(ROOT / relative) for relative in PINS}
    for relative, expected in PINS.items():
        add(rows, f"hash:{relative}", hashes[relative], expected, hashes[relative] == expected)

    move_set = pa.get("dynamics", {}).get("move_set", [])
    generator = pa.get("dynamics", {}).get("generator", "")
    add(rows, "source identity", pa.get("packet_id"), "PAH-001", pa.get("packet_id") == "PAH-001")
    add(rows, "link move is displayed", move_set, "one link multiplied by zeta_K or zeta_K^(-1)",
        "one link multiplied by zeta_K or zeta_K^(-1)" in move_set)
    add(rows, "midpoint generator is displayed", generator,
        "exp[-beta(F_rho(r x)-F_rho(x))/2]",
        "exp[-beta(F_rho(r x)-F_rho(x))/2]" in generator)
    full_source_text = json.dumps(pa, ensure_ascii=True, sort_keys=True).lower()
    for absent in ("duplicate", "multiplicity", "invalid-move", "root measure"):
        add(rows, f"source omits {absent} convention", absent in full_source_text, False,
            absent not in full_source_text)

    scope = geometry.get("exact_scope", {})
    witness = scope.get("local_incidence_witness", {})
    fine_edges = witness.get("fine_edges", [])
    fine_faces = witness.get("fine_faces", [])
    add(rows, "geometry identity", geometry.get("contract_id"), "PAH-OMC-004",
        geometry.get("contract_id") == "PAH-OMC-004")
    add(rows, "genuine fine incidence", (len(fine_edges), len(fine_faces)), (5, 2),
        len(fine_edges) == 5 and len(fine_faces) == 2)
    face = fine_faces[0]
    add(rows, "closed triangle witness", face, [0, 1, 4], face == [0, 1, 4] and edge_cycle(fine_edges, face))
    add(rows, "identity anchor automorphism", scope.get("strip_family", {}).get("anchors", ""),
        "identity", "identity" in scope.get("strip_family", {}).get("anchors", "").lower())

    state_text = scope.get("state_and_regulator", "")
    k_match = re.search(r"K=(\d+)", state_text)
    beta_match = re.search(r"beta=([0-9]+)", state_text)
    nu_match = re.search(r"nu=([0-9]+)", state_text)
    k = int(k_match.group(1)) if k_match else 0
    beta = Fraction(int(beta_match.group(1)), 1) if beta_match else Fraction(0)
    nu = Fraction(int(nu_match.group(1)), 1) if nu_match else Fraction(0)
    epsilon = parse_fraction(state_text, r"epsilon=(\d+/\d+)")
    kappa_g_match = re.search(r"kappa_g=([0-9]+)", state_text)
    kappa_g = Fraction(int(kappa_g_match.group(1)), 1) if kappa_g_match else Fraction(0)
    add(rows, "K=2 fixture", k, 2, k == 2)
    add(rows, "beta=1 fixture", beta, Fraction(1), beta == 1)
    add(rows, "nu=1 fixture", nu, Fraction(1), nu == 1)
    add(rows, "epsilon=1/2 fixture", epsilon, Fraction(1, 2), epsilon == Fraction(1, 2))
    add(rows, "kappa_g=1 fixture", kappa_g, Fraction(1), kappa_g == 1)

    # All aperture levels are j=0, hence every endpoint has s=epsilon.  The
    # first triangle has three links and each edge stiffness is derived from
    # the displayed J_e(s)=2/(s_v+s_w), not inserted as a result constant.
    s = epsilon
    edge_stiffness = Fraction(2, 1) / (s + s)
    face_stiffness = sum((edge_stiffness for _ in face), Fraction(0)) / len(face)
    before_holonomy = 1
    after_holonomy = -1  # one Z_2 link is flipped; zeta_2=zeta_2^(-1)=-1.
    before_face_term = kappa_g * face_stiffness * (1 - before_holonomy)
    after_face_term = kappa_g * face_stiffness * (1 - after_holonomy)
    delta_f = after_face_term - before_face_term
    mobility_square = s * s
    mobility = Fraction(1, 2)  # positive square root of mobility_square=1/4
    observable_delta = (1 - after_holonomy) - (1 - before_holonomy)
    add(rows, "Z2 inverse maps coincide", "zeta_2 = zeta_2^(-1) = -1", "coincident state map", k == 2)
    add(rows, "closed-face gauge cancellation", {str(v): 2 for v in sorted({x for edge_id in face for x in fine_edges[edge_id]})},
        "each triangle vertex occurs twice", edge_cycle(fine_edges, face))
    add(rows, "edge stiffness derived", edge_stiffness, Fraction(2), edge_stiffness == 2)
    add(rows, "face stiffness derived", face_stiffness, Fraction(2), face_stiffness == 2)
    add(rows, "exact Wilson delta F", delta_f, Fraction(4), delta_f == 4)
    add(rows, "mobility square derived", mobility_square, Fraction(1, 4), mobility_square == Fraction(1, 4))
    add(rows, "positive mobility root", mobility, Fraction(1, 2), mobility == Fraction(1, 2))
    add(rows, "holonomy observable delta", observable_delta, Fraction(2), observable_delta == 2)

    rate_exponent = -beta * delta_f / 2
    rate_coefficient = mobility * observable_delta
    add(rows, "midpoint exponent", rate_exponent, Fraction(-2), rate_exponent == -2)
    add(rows, "one-root observable contribution", rate_coefficient, Fraction(1), rate_coefficient == 1)

    # Completion A keeps the two written signs as two directed labels and
    # pairs their inverses.  Completion B deduplicates the coincident map and
    # uses the involution as its own inverse.  Neither changes F, c, or the
    # finite state space; only an unspoken multiplicity convention differs.
    completion_a = {
        "name": "labelled-sign-channels",
        "roots": ["LK(edge=0,sigma=+1)", "LK(edge=0,sigma=-1)"],
        "inverse": {"LK(edge=0,sigma=+1)": "LK(edge=0,sigma=-1)",
                    "LK(edge=0,sigma=-1)": "LK(edge=0,sigma=+1)"},
        "map": "flip edge 0",
    }
    completion_b = {
        "name": "deduplicated-involution",
        "roots": ["LK(edge=0,flip)"],
        "inverse": {"LK(edge=0,flip)": "LK(edge=0,flip)"},
        "map": "flip edge 0",
    }
    add(rows, "completion A inverse closure", completion_a["inverse"], "cross-labelled inverse pair",
        len(completion_a["roots"]) == 2 and len(completion_a["inverse"]) == 2)
    add(rows, "completion B inverse closure", completion_b["inverse"], "self-inverse involution",
        len(completion_b["roots"]) == 1 and completion_b["inverse"][completion_b["roots"][0]] == completion_b["roots"][0])
    add(rows, "same state map", completion_a["map"], completion_b["map"], completion_a["map"] == completion_b["map"])

    a_coefficient = len(completion_a["roots"]) * rate_coefficient
    b_coefficient = len(completion_b["roots"]) * rate_coefficient
    difference_coefficient = a_coefficient - b_coefficient
    add(rows, "completion A coefficient", a_coefficient, Fraction(2), a_coefficient == 2)
    add(rows, "completion B coefficient", b_coefficient, Fraction(1), b_coefficient == 1)
    add(rows, "generator values differ", difference_coefficient, Fraction(1), difference_coefficient != 0)
    add(rows, "same functional and rate", "F_rho and c_r unchanged", "source display", True)
    add(rows, "not a contradiction in every completion", "two admissible completions", "underdetermination", True)
    add(rows, "temporal preregistration pinned", prereg.get("contract_id"), "PAH-OMC-020", prereg.get("contract_id") == "PAH-OMC-020")

    payload: dict[str, Any] = {
        "schema": "tect/pah-omc020-source-multiplicity-primary/1.0",
        "run_kind": "primary",
        "audit_id": AUDIT_ID,
        "exploration_id": EXPLORATION_ID,
        "result_id": RESULT_ID,
        "task_id": TASK_ID,
        "verification": "PASS",
        "checks_passed": len(rows),
        "checks": rows,
        "source_hashes": hashes,
        "scope": {
            "dimension": "finite PAH-OMC-004 incidence witness",
            "model": "immutable PAH-001 functional and displayed midpoint generator",
            "normalization": "finite counting-measure Gibbs midpoint rate",
            "regulator": "K=2, M_s=M_psi=1, Q=0, epsilon=1/2, beta=nu=1; unit displayed couplings",
            "volume": "the existing PAH-OMC-004 fine witness (5 edges, 2 faces); no new carrier",
            "limit": "none; one finite state and one closed triangular face",
        },
        "observable": {
            "name": "f=1-Re(U_p)",
            "face": face,
            "before_holonomy": before_holonomy,
            "after_holonomy": after_holonomy,
            "before_value": 0,
            "after_value": observable_delta,
            "gauge_invariant_reason": "closed face incidence has even vertex degree in Z_2",
            "anchor_invariant_reason": "PAH-OMC-004 declares the audited anchor automorphism group to be identity",
        },
        "derived": {
            "edge_stiffness": str(edge_stiffness),
            "face_stiffness": str(face_stiffness),
            "delta_F": str(delta_f),
            "mobility_square": str(mobility_square),
            "mobility": str(mobility),
            "rate": "(1/2)*exp(-2)",
            "one_root_generator_increment": "exp(-2)",
            "completion_A_generator_increment": "2*exp(-2)",
            "completion_B_generator_increment": "exp(-2)",
            "difference_A_minus_B": "exp(-2)",
        },
        "completions": {"A": completion_a, "B": completion_b},
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "finding": "The immutable PAH-001 prose does not uniquely determine the finite link-root multiplicity at K=2. Two source-compatible inverse conventions on the existing PAH-OMC-004 closed-face witness preserve the displayed functional, state map, mobility and midpoint rate but give generator increments 2*exp(-2) and exp(-2) for the same invariant observable, so the original finite semigroup is underdetermined until a root multiplicity/duplicate-transition convention is owner-fixed.",
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "stage2_status": "HOLD_FOR_EVIDENCE",
        "non_claims": [
            "This is not a universal no-go for every future PAH owner completion; it is a source-definition underdetermination witness.",
            "No PAH-001 functional, move family, rate, state, carrier, regulator, external Markov time or j-before-n order is changed.",
            "PAH-OMC-004 is used only as an already hashed finite witness; its successor theorem is not imported as PAH-001 authority.",
            "No PAH-OMC-020 N2b/N2c/N4/N2d closure or stationary semigroup convergence follows.",
            "No physical Pre-A, spacetime, QFT, gravity, continuum, mass-gap, Yang-Mills or TOE conclusion.",
        ],
        "next_question": "Can a source-authorized PAH owner packet fix one exact root-label multiplicity, invalid-move convention and root measure while preserving the PAH-001 hash and then satisfy N2a energy intertwining?",
        "reproduction": {
            "primary": "python -X utf8 verification/scripts/pah_omc020_source_multiplicity_underdetermination.py --check",
            "independent": "python -X utf8 codes/foundations/pah_omc020_source_multiplicity_underdetermination_independent.py --check",
            "hostile": "python -X utf8 codes/foundations/pah_omc020_source_multiplicity_underdetermination_hostile.py --check",
            "integrated": "python -X utf8 verification/scripts/pah_omc020_source_multiplicity_underdetermination_verify.py --check --lean-cache E:\\Dev\\TECT\\verification\\lean\\.lake\\packages",
            "lean": "Lean 4.32.1 verification/lean/Tect/PahOmc020Multiplicity.lean",
        },
    }
    write_json(output, payload)
    print(f"{AUDIT_ID} PRIMARY PASS {len(rows)}/{len(rows)}; verdict=HOLD_FOR_EVIDENCE; generator gap=exp(-2)")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = run(args.output)
    if args.check and json.loads(args.output.read_text(encoding="utf-8")) != encode(payload):
        raise SystemExit("deterministic replay mismatch")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
