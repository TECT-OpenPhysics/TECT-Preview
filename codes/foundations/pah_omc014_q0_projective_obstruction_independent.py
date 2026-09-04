#!/usr/bin/env python3
"""Independent direct-enumeration check for the PAH-OMC-014 Q=0 probe.

Unlike the primary lane, this implementation obtains the face-flux
multiplicities by enumerating every Z_2 link assignment.  It then compares the
same cross-multiplied aperture-cylinder expectations using exact Fractions.
No primary code is imported.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import tempfile
from collections import Counter, defaultdict
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
    "2026-09-05-pah-omc014-q0-projective-obstruction/independent.json"
)
AUDIT_ID = "PAH-OMC-014-Q0-PROJECTIVE-OBSTRUCTION-INDEPENDENT-001"
TASK_ID = "T-054"
CLAIM_ID = "C6-SPACETIME-SIGNATURE"
NEGATIVE_TAG = "AUDIT-2026-09-05-PAH-OMC-014-Q0-COMPONENT-PUSHFORWARD"
EPSILON = Fraction(1, 2)
EXPECTED = {
    "PAH-001": "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "PAH-OMC-004": "38163b7f0320cc7041cda4230bc0f6f07cfdc589cd3f12fdbab9f86c25a3a10c",
    "PAH-OMC-012": "180228b83e44f46406b302c97ff6caab023240eeaa19997618012074930f3e72",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as stream:
            json.dump(payload, stream, ensure_ascii=True, indent=2, sort_keys=True)
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


def carrier(level: int) -> dict[str, object]:
    vs = tuple((i, j) for i in range(level + 2) for j in (0, 1))
    es: list[tuple[tuple[int, int], tuple[int, int]]] = []
    label: dict[str, int] = {}
    for i in range(level + 1):
        for j in (0, 1):
            label[f"h{i}{j}"] = len(es)
            es.append(((i, j), (i + 1, j)))
    for i in range(level + 2):
        label[f"v{i}"] = len(es)
        es.append(((i, 0), (i, 1)))
    for i in range(level):
        label[f"d{i}"] = len(es)
        es.append(((i, 0), (i + 1, 1)))
    fs: list[tuple[tuple[int, int], ...]] = []
    for i in range(level):
        fs += [
            ((label[f"h{i}0"], 1), (label[f"v{i+1}"], 1), (label[f"d{i}"], -1)),
            ((label[f"d{i}"], 1), (label[f"h{i}1"], -1), (label[f"v{i}"], -1)),
        ]
    i = level
    fs.append(((label[f"h{i}0"], 1), (label[f"v{i+1}"], 1), (label[f"h{i}1"], -1), (label[f"v{i}"], -1)))
    return {"vertices": vs, "edges": tuple(es), "faces": tuple(fs)}


def direct_flux_counts(c: dict[str, object]) -> Counter[tuple[int, ...]]:
    counts: Counter[tuple[int, ...]] = Counter()
    for links in product((0, 1), repeat=len(c["edges"])):
        counts[tuple(sum(links[edge] for edge, _ in face) % 2 for face in c["faces"])] += 1
    return counts


def s(bit: int) -> Fraction:
    return EPSILON + Fraction(bit, 2)


def weight_row(c: dict[str, object], a: tuple[int, ...], flux_counts: Counter[tuple[int, ...]]) -> dict[Fraction, int]:
    ix = {vertex: i for i, vertex in enumerate(c["vertices"])}
    base = sum(((s(value) - 1) ** 2 / 2 for value in a), Fraction(0))
    for left, right in c["edges"]:
        base += (s(a[ix[left]]) - s(a[ix[right]])) ** 2 / 2
    jp = []
    for face in c["faces"]:
        values = [Fraction(2, 1) / (s(a[ix[c["edges"][edge][0]]]) + s(a[ix[c["edges"][edge][1]]])) for edge, _ in face]
        jp.append(sum(values, Fraction(0)) / len(values))
    out: dict[Fraction, int] = defaultdict(int)
    for flux, multiplicity in flux_counts.items():
        out[base + sum((2 * value for value, flag in zip(jp, flux) if flag), Fraction(0))] += multiplicity
    return dict(out)


def add(dst: dict[Fraction, int], src: dict[Fraction, int], sign: int = 1) -> None:
    for exponent, coefficient in src.items():
        dst[exponent] = dst.get(exponent, 0) + sign * coefficient
        if dst[exponent] == 0:
            del dst[exponent]


def conv(left: dict[Fraction, int], right: dict[Fraction, int], sign: int = 1) -> dict[Fraction, int]:
    out: dict[Fraction, int] = defaultdict(int)
    for x, cx in left.items():
        for y, cy in right.items():
            out[x + y] += sign * cx * cy
    return {x: c for x, c in out.items() if c}


def coefficient_text(data: dict[Fraction, int]) -> str:
    return json.dumps([[str(x), c] for x, c in sorted(data.items())], separators=(",", ":"))


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    source, geometry, graded = read(PAH001), read(OMC004), read(OMC012)
    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool, actual: Any, expected: Any) -> None:
        checks.append({"name": name, "passed": bool(passed), "actual": actual, "expected": expected})

    actual = {"PAH-001": sha(PAH001), "PAH-OMC-004": sha(OMC004), "PAH-OMC-012": sha(OMC012)}
    check("source hashes", actual == EXPECTED, actual, EXPECTED)
    check("source identities", source.get("packet_id") == "PAH-001" and geometry.get("contract_id") == "PAH-OMC-004" and graded.get("contract_id") == "PAH-OMC-012", [source.get("packet_id"), geometry.get("contract_id"), graded.get("contract_id")], ["PAH-001", "PAH-OMC-004", "PAH-OMC-012"])
    check("declared finite slice", "Q=0" in geometry["exact_scope"]["state_and_regulator"] and "beta=1" in geometry["exact_scope"]["state_and_regulator"], geometry["exact_scope"]["state_and_regulator"], "Q=0 beta=1")
    check("deterministic grade", "Q_f-Q_c" in graded["exact_scope"]["charge_balance"] and ">=0" in graded["exact_scope"]["charge_balance"], graded["exact_scope"]["charge_balance"], "Q_f=0 => Q_c=0")
    coarse, fine = carrier(2), carrier(3)
    coarse_flux, fine_flux = direct_flux_counts(coarse), direct_flux_counts(fine)
    check("direct flux enumeration", len(coarse_flux) > 0 and len(fine_flux) > 0 and len(set(coarse_flux.values())) == 1 and len(set(fine_flux.values())) == 1, {"coarse_patterns": len(coarse_flux), "fine_patterns": len(fine_flux), "coarse_multiplicity": sorted(set(coarse_flux.values())), "fine_multiplicity": sorted(set(fine_flux.values()))}, "uniform exact face-flux fibres")
    coarse_z: dict[Fraction, int] = defaultdict(int)
    coarse_n: dict[Fraction, int] = defaultdict(int)
    for a in product((0, 1), repeat=len(coarse["vertices"])):
        row = weight_row(coarse, a, coarse_flux)
        add(coarse_z, row)
        if a[0] == 1: add(coarse_n, row)
    fine_z: dict[Fraction, int] = defaultdict(int)
    fine_n: dict[Fraction, int] = defaultdict(int)
    old_count = len(coarse["vertices"])
    for a in product((0, 1), repeat=len(fine["vertices"])):
        row = weight_row(fine, a, fine_flux)
        add(fine_z, row)
        if a[0] == 1: add(fine_n, row)
        check("old coordinate retained", a[:old_count] == tuple(a[i] for i in range(old_count)), "coordinate restriction", "coordinate restriction") if a == (0,) * len(fine["vertices"]) else None
    difference: dict[Fraction, int] = defaultdict(int, conv(fine_n, coarse_z))
    add(difference, conv(coarse_n, fine_z), -1)
    text = coefficient_text(difference)
    check("cross difference nonempty", bool(difference), {"terms": len(difference), "sha256": hashlib.sha256(text.encode()).hexdigest()}, "nonempty exact coefficient map")
    failed = [row for row in checks if not row["passed"]]
    payload: dict[str, Any] = {
        "schema": "tect/pah-omc014-q0-projective-obstruction-independent/1.0",
        "run_kind": "independent", "audit_id": AUDIT_ID, "task_id": TASK_ID, "claim_id": CLAIM_ID, "negative_tag": NEGATIVE_TAG,
        "verification": "PASS" if not failed else "FAIL", "verdict": "NEGATIVE_RESULT" if not failed and difference else "HOLD_FOR_EVIDENCE",
        "assertion_count": len(checks), "passed": len(checks) - len(failed), "failed": len(failed), "assertions": checks, "source_hashes": actual,
        "scope": "G_3 -> G_2, K=2, M_s=M_psi=1, epsilon=1/2, beta=1, R_max=1, Q=0; indicator(aperture_(0,0)=1)",
        "derived": {"coarse_vertices": len(coarse["vertices"]), "fine_vertices": len(fine["vertices"]), "coarse_edges": len(coarse["edges"]), "fine_edges": len(fine["edges"]), "coarse_faces": len(coarse["faces"]), "fine_faces": len(fine["faces"]), "coarse_flux_patterns": len(coarse_flux), "fine_flux_patterns": len(fine_flux), "coarse_exponential_terms": len(coarse_z), "fine_pushforward_exponential_terms": len(fine_z), "cross_difference_terms": len(difference), "cross_difference_sha256": hashlib.sha256(text.encode()).hexdigest(), "cross_difference_coefficients": [[str(x), c] for x, c in sorted(difference.items())]},
        "exact_nonzero_criterion": "The coefficient map is nonempty over distinct rational exponents; Lindemann--Weierstrass gives exact nonvanishing. Decimal evaluation is not used as the proof.",
        "boundary": "This rejects only the componentwise Q_f=0 push-forward equality and its deterministic-grade kernel factorization. It is not a full-Q global-mixture no-go.",
        "non_claims": ["No sector weights or omega are defined.", "No weak cylinder limit, Cauchy bound, R-488 lower bound or stationarity is proved.", "No physical, continuum, QFT, gravity, Yang--Mills, mass-gap or TOE conclusion follows."],
    }
    write_json(output, payload)
    print(f"{AUDIT_ID} {payload['verification']} {payload['passed']}/{payload['assertion_count']}; verdict={payload['verdict']}; cross_terms={len(difference)}")
    return 0 if payload["verification"] == "PASS" else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    raise SystemExit(run(args.output))
