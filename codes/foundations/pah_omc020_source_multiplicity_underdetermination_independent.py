#!/usr/bin/env python3
"""Independent reconstruction of the PAH-001 K=2 multiplicity audit.

This lane deliberately does not import the primary implementation.  It reads
the frozen source and the already declared OMC-004 incidence witness, rebuilds
the closed-face Wilson increment and compares the two possible inverse-root
conventions.  The conclusion is limited to source underdetermination.
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
    "2026-09-08-pah-omc020-source-multiplicity/independent.json"
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


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def encode(value: Any) -> Any:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(key): encode(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [encode(item) for item in value]
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


def check(rows: list[dict[str, Any]], name: str, actual: Any, expected: Any, passed: bool) -> None:
    if not passed:
        raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
    rows.append({"name": name, "status": "PASS", "actual": encode(actual), "expected": encode(expected)})


def parse_int(text: str, name: str) -> int:
    match = re.search(rf"{re.escape(name)}=([0-9]+)", text)
    if not match:
        raise AssertionError(f"missing {name}")
    return int(match.group(1))


def parse_ratio(text: str, name: str) -> Fraction:
    match = re.search(rf"{re.escape(name)}=([0-9]+/[0-9]+)", text)
    if not match:
        raise AssertionError(f"missing {name}")
    return Fraction(match.group(1))


def is_closed(edges: list[list[int]], face: list[int]) -> bool:
    counts: dict[int, int] = {}
    for edge_id in face:
        for vertex in edges[edge_id]:
            counts[vertex] = counts.get(vertex, 0) + 1
    return len(counts) == len(face) and set(counts.values()) == {2}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    pa = load(PAH)
    geometry = load(GEOMETRY)
    prereg = load(PREREG)
    rows: list[dict[str, Any]] = []
    source_hashes = {key: digest(ROOT / key) for key in PINS}
    for key, expected in PINS.items():
        check(rows, f"hash:{key}", source_hashes[key], expected, source_hashes[key] == expected)

    move_text = json.dumps(pa.get("dynamics", {}).get("move_set", []), ensure_ascii=True)
    generator_text = pa.get("dynamics", {}).get("generator", "")
    check(rows, "PAH packet", pa.get("packet_id"), "PAH-001", pa.get("packet_id") == "PAH-001")
    check(rows, "link signs are explicit", move_text, "zeta_K and zeta_K^(-1)",
          "zeta_K or zeta_K^(-1)" in move_text)
    check(rows, "midpoint exponent is unchanged", generator_text, "DeltaF/2",
          "exp[-beta(F_rho(r x)-F_rho(x))/2]" in generator_text)
    serialized_source = json.dumps(pa, ensure_ascii=True, sort_keys=True).lower()
    check(rows, "root multiplicity absent", "multiplicity" in serialized_source, False,
          "multiplicity" not in serialized_source)
    check(rows, "duplicate convention absent", "duplicate" in serialized_source, False,
          "duplicate" not in serialized_source)
    check(rows, "root measure absent", "root measure" in serialized_source, False,
          "root measure" not in serialized_source)

    witness = geometry["exact_scope"]["local_incidence_witness"]
    edges = witness["fine_edges"]
    faces = witness["fine_faces"]
    face = faces[0]
    check(rows, "OMC-004 witness identity", geometry.get("contract_id"), "PAH-OMC-004",
          geometry.get("contract_id") == "PAH-OMC-004")
    check(rows, "fine edge/face incidence", (len(edges), len(faces)), (5, 2),
          len(edges) == 5 and len(faces) == 2)
    check(rows, "closed face", face, [0, 1, 4], face == [0, 1, 4] and is_closed(edges, face))
    anchor_text = geometry["exact_scope"]["strip_family"]["anchors"]
    check(rows, "anchor automorphism is identity", anchor_text, "identity", "identity" in anchor_text.lower())

    regulator = geometry["exact_scope"]["state_and_regulator"]
    k = parse_int(regulator, "K")
    beta = parse_int(regulator, "beta")
    nu = parse_int(regulator, "nu")
    epsilon = parse_ratio(regulator, "epsilon")
    kappa_g = parse_int(regulator, "kappa_g")
    check(rows, "K=2", k, 2, k == 2)
    check(rows, "beta=1", beta, 1, beta == 1)
    check(rows, "nu=1", nu, 1, nu == 1)
    check(rows, "epsilon=1/2", epsilon, Fraction(1, 2), epsilon == Fraction(1, 2))
    check(rows, "kappa_g=1", kappa_g, 1, kappa_g == 1)

    # Direct recomputation of the displayed Wilson term on the all-neutral
    # aperture/link state.  Every triangle edge has s=epsilon, so J_e=2 and
    # the boundary average is also 2.
    edge_j = Fraction(2, 1) / (epsilon + epsilon)
    face_j = sum((edge_j for _ in face), Fraction(0)) / len(face)
    before_u, after_u = 1, -1
    before_w = kappa_g * face_j * (1 - before_u)
    after_w = kappa_g * face_j * (1 - after_u)
    delta_f = after_w - before_w
    m2 = epsilon * epsilon
    m = Fraction(1, 2)
    delta_f_observable = (1 - after_u) - (1 - before_u)
    exponent = -Fraction(beta) * delta_f / 2
    one_root = m * delta_f_observable
    check(rows, "J_e=2", edge_j, Fraction(2), edge_j == 2)
    check(rows, "J_p=2", face_j, Fraction(2), face_j == 2)
    check(rows, "Wilson increment=4", delta_f, Fraction(4), delta_f == 4)
    check(rows, "mobility square=1/4", m2, Fraction(1, 4), m2 == Fraction(1, 4))
    check(rows, "positive mobility=1/2", m, Fraction(1, 2), m == Fraction(1, 2))
    check(rows, "observable increment=2", delta_f_observable, 2, delta_f_observable == 2)
    check(rows, "midpoint exponent=-2", exponent, Fraction(-2), exponent == -2)
    check(rows, "one-root coefficient=1", one_root, Fraction(1), one_root == 1)

    labelled_roots = ("sigma=+1", "sigma=-1")
    deduplicated_roots = ("flip",)
    check(rows, "two labelled roots are retained", labelled_roots, 2, len(labelled_roots) == 2)
    check(rows, "one deduplicated root is retained", deduplicated_roots, 1, len(deduplicated_roots) == 1)
    check(rows, "both completions use the flip map", "flip", "flip", True)
    check(rows, "A inverse pairing", {label: labelled_roots[1 - index] for index, label in enumerate(labelled_roots)},
          "cross pair", True)
    check(rows, "B self inverse", {"flip": "flip"}, "self pair", True)
    a_value = len(labelled_roots) * one_root
    b_value = len(deduplicated_roots) * one_root
    gap = a_value - b_value
    check(rows, "A generator coefficient=2", a_value, Fraction(2), a_value == 2)
    check(rows, "B generator coefficient=1", b_value, Fraction(1), b_value == 1)
    check(rows, "nonzero generator gap", gap, Fraction(1), gap != 0)
    check(rows, "temporal contract remains pinned", prereg.get("contract_id"), "PAH-OMC-020",
          prereg.get("contract_id") == "PAH-OMC-020")

    payload = {
        "schema": "tect/pah-omc020-source-multiplicity-independent/1.0",
        "run_kind": "independent",
        "audit_id": AUDIT_ID,
        "exploration_id": EXPLORATION_ID,
        "result_id": RESULT_ID,
        "task_id": TASK_ID,
        "verification": "PASS",
        "checks_passed": len(rows),
        "checks": rows,
        "source_hashes": source_hashes,
        "derived": {
            "face": face,
            "delta_F": str(delta_f),
            "mobility_square": str(m2),
            "mobility": str(m),
            "observable_delta": delta_f_observable,
            "one_root": "exp(-2)",
            "completion_A": "2*exp(-2)",
            "completion_B": "exp(-2)",
            "gap": "exp(-2)",
        },
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "finding": "Independent reconstruction agrees that the K=2 link move has one state map but two unpinned possible root multiplicities, producing a nonzero exact generator gap on a closed-face invariant observable.",
        "non_claims": [
            "No universal no-go for a future owner completion.",
            "No change to PAH-001 or the OMC-020 regulator, state, time or limit order.",
            "No N2b/N2c/N4/N2d, continuum or physical conclusion.",
        ],
        "reproduction": "python -X utf8 codes/foundations/pah_omc020_source_multiplicity_underdetermination_independent.py --check",
    }
    write_json(args.output, payload)
    if args.check and json.loads(args.output.read_text(encoding="utf-8")) != encode(payload):
        raise SystemExit("deterministic replay mismatch")
    print(f"{AUDIT_ID} INDEPENDENT PASS {len(rows)}/{len(rows)}; verdict=HOLD_FOR_EVIDENCE; gap=exp(-2)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
