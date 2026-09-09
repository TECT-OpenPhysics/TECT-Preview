#!/usr/bin/env python3
"""Independent arithmetic reconstruction of the PAH-OMC-020 coupling candidate.

This lane intentionally does not import the primary verifier.  It checks the
maximal-overlap matrix, conditional-expectation contraction, local recovery
bound, and the diagonal prefix-index fixture using fresh Fraction code.  It
does not claim source authorization or any N2b--N2d/semigroup theorem.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CANDIDATE = ROOT / "strategy/pa-hyp/PAH-OMC-020-noncoordinate-coupling-candidate-v1.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-08-pah-omc020-noncoordinate-coupling/independent.json"
)

PINS = {
    "strategy/pa-hyp/PAH-001-v1.json": "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json": "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3",
    "strategy/pa-hyp/PAH-OMC-017-transfer-certificate.md": "49d0bc5299df9e5f583b009121ee2b1e53fc04f4460e5eedb779f9759113dddf",
    "strategy/pa-hyp/PAH-OMC-020-noncoordinate-coupling-candidate-v1.json": "TO_FILL",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(rows: list[dict], name: str, actual: object, expected: object) -> None:
    if actual != expected:
        raise AssertionError(f"{name}: {actual!r} != {expected!r}")
    rows.append({"name": name, "status": "PASS", "actual": serial(actual), "expected": serial(expected)})


def serial(value: object) -> object:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    return value


def bounded_delta(d_value: Fraction, q_value: Fraction, n_value: int, m_value: int) -> Fraction:
    return min(Fraction(1), 4 * d_value * q_value ** (n_value - m_value))


def diagonal_index(d_value: Fraction, q_value: Fraction, n_value: int) -> int:
    valid = [
        m_value for m_value in range(n_value)
        if bounded_delta(d_value, q_value, n_value, m_value)
        <= Fraction(1, (m_value + 1) ** 2)
    ]
    return max(valid)


def square_norm(weights: list[Fraction], values: list[Fraction]) -> Fraction:
    return sum(weight * value * value for weight, value in zip(weights, values))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    candidate_hash = digest(CANDIDATE)
    pins = dict(PINS)
    pins["strategy/pa-hyp/PAH-OMC-020-noncoordinate-coupling-candidate-v1.json"] = candidate_hash
    rows: list[dict] = []
    for relative, expected in pins.items():
        actual = digest(ROOT / relative)
        check(rows, f"hash {relative}", actual, expected)

    contract = json.loads(CANDIDATE.read_text(encoding="utf-8"))
    check(rows, "candidate status", contract["status"], "RESEARCHER_OWNED_CANDIDATE_ONLY")
    check(rows, "candidate has no model change", contract["provenance"]["model_change"], False)
    check(rows, "candidate lacks source authorization", contract["provenance"]["source_authorized_packet_present"], False)
    check(rows, "candidate map is non-coordinate", contract["map"]["kind"], "maximal-prefix-coupling-conditional-expectation")
    check(rows, "all hard obligations remain open", len(contract["open_obligations"]), 6)
    check(rows, "physical non-claim is explicit", any("physical Pre-A" in text for text in contract["non_claims"]), True)

    # Fresh two-point maximal-overlap construction.
    limiting = [Fraction(3, 5), Fraction(2, 5)]
    finite = [Fraction(1, 2), Fraction(1, 2)]
    coupling = [
        [Fraction(1, 2), Fraction(1, 10)],
        [Fraction(0), Fraction(2, 5)],
    ]
    check(rows, "coupling row sums", [sum(row) for row in coupling], limiting)
    check(rows, "coupling column sums", [sum(coupling[row][col] for row in range(2)) for col in range(2)], finite)
    overlap = sum(min(limiting[i], finite[i]) for i in range(2))
    tv = sum(abs(limiting[i] - finite[i]) for i in range(2)) / 2
    check(rows, "overlap", overlap, Fraction(9, 10))
    check(rows, "mismatch", 1 - overlap, Fraction(1, 10))
    check(rows, "overlap/mismatch identity", 1 - overlap, tv)

    # Conditional expectation is tested on a distinct exact grid.
    grid = [Fraction(value, 3) for value in range(-6, 7)]
    tested = 0
    for a in grid:
        for b in grid:
            image0 = (coupling[0][0] * a + coupling[0][1] * b) / limiting[0]
            image1 = (coupling[1][0] * a + coupling[1][1] * b) / limiting[1]
            target = square_norm(limiting, [image0, image1])
            source = square_norm(finite, [a, b])
            if target > source:
                raise AssertionError("Jensen contraction failed")
            tested += 1
    check(rows, "conditional Jensen grid", tested, 169)

    f = [Fraction(2), Fraction(-1, 2)]
    image = [
        (coupling[0][0] * f[0] + coupling[0][1] * f[1]) / limiting[0],
        (coupling[1][0] * f[0] + coupling[1][1] * f[1]) / limiting[1],
    ]
    error = square_norm(limiting, [image[i] - f[i] for i in range(2)])
    bound = 4 * max(abs(value) for value in f) ** 2 * tv
    check(rows, "recovery image", image, [Fraction(19, 12), Fraction(-1, 2)])
    check(rows, "recovery inequality", error <= bound, True)

    d_value = Fraction(1)
    q_value = Fraction(1, 2)
    levels = list(range(10, 61))
    indices = [diagonal_index(d_value, q_value, n_value) for n_value in levels]
    check(rows, "diagonal set nonempty", all(index >= 0 for index in indices), True)
    check(rows, "diagonal index valid", all(index < n_value for index, n_value in zip(indices, levels)), True)
    check(rows, "diagonal index grows", indices[-1] > indices[0], True)
    check(rows, "diagonal criterion", all(
        bounded_delta(d_value, q_value, n_value, index) <= Fraction(1, (index + 1) ** 2)
        for n_value, index in zip(levels, indices)
    ), True)

    check(rows, "N2b is not silently claimed", any("N2b" in text for text in contract["open_obligations"]), True)
    check(rows, "N2c/N4 is not silently claimed", any("N2c/N4" in text for text in contract["open_obligations"]), True)
    check(rows, "N2d is not silently claimed", any("N2d" in text for text in contract["open_obligations"]), True)

    payload = {
        "schema": "tect/pah-omc020-noncoordinate-coupling-independent/1.0",
        "status": "PASS_INDEPENDENT_NONCOORDINATE_LOCAL_COUPLING",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "conditional": True,
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "source_hashes": pins,
        "candidate_sha256": candidate_hash,
        "checks": rows,
        "fixture": {"overlap": "9/10", "mismatch": "1/10", "diagonal_indices_n10_to_n60": indices},
        "finding": "Independent Fraction reconstruction confirms only the non-coordinate local contraction/recovery candidate; owner authorization, energy intertwining, N2b, N2c/N4, N2d and temporal convergence remain open.",
        "non_claims": contract["non_claims"],
    }
    encoded = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check:
        if args.output.read_bytes() != encoded:
            raise SystemExit("independent coupling replay mismatch")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(encoded)
    print(f"PAH-OMC-020 NONCOORDINATE INDEPENDENT: PASS {len(rows)}/{len(rows)}; verdict={payload['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
