#!/usr/bin/env python3
"""Audit the source-compatible terminal square-to-split fibre boundary.

This diagnostic keeps the PAH-001 functional and the PAH-OMC-017 transfer
convention fixed.  It retains the old terminal labels h0=h1=+1 and compares
the original unsplit square weight with the sum over the newly retained
diagonal label on an allowed continuous-amplitude state.  The source
plaquette coefficient is the boundary average of the source edge stiffnesses;
on the s=1 witness every edge stiffness is therefore recomputed as one.

The result is deliberately narrower than PAH-OMC-020: it proves that the
coordinate-preserving terminal lift has a density ratio whose inverse grows
along an explicit amplitude ray.  It does not prove that no abstract
varying-space comparison or no local temporal limit exists.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import os
import tempfile
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PAH001 = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
OMC017_CERT = ROOT / "strategy/pa-hyp/PAH-OMC-017-transfer-certificate.md"
OMC020 = ROOT / "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json"
LEAN = ROOT / "verification/lean/Tect/PahOmc020.lean"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-07-pah-omc020-boundary-kernel-obstruction/result.json"
)

PINS = {
    "strategy/pa-hyp/PAH-001-v1.json":
        "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json":
        "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3",
}

# These are witness inputs, not derived constants.  They are all allowed by
# the source domain: r>=0, s in {1/2,1}, and Z_2 link/phase signs.
S_WITNESS = 1.0
R_ZERO = 0.0
OLD_LINK = 1
VERTICAL_LINK = 1
PHASE = 1
AMPLITUDE_GRID = (0.0, 1.0, 2.0, 4.0, 8.0)
CHALLENGE_LEVELS = (1.0, 10.0, 100.0)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True, ensure_ascii=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def check(rows: list[dict], name: str, ok: bool, actual: object, expected: object) -> None:
    if not ok:
        raise AssertionError(name)
    rows.append({"name": name, "status": "PASS", "actual": actual, "expected": expected})


def source_checks(rows: list[dict]) -> None:
    for relative, pin in PINS.items():
        path = ROOT / relative
        actual = digest(path)
        check(rows, f"source pin:{relative}", actual == pin, actual, pin)
    source = json.loads(PAH001.read_text(encoding="utf-8"))
    check(
        rows,
        "source edge stiffness",
        source["functional_or_action"]["edge_stiffness"] == "J_e(s)=2/(s_v+s_w) for e=(v,w)",
        source["functional_or_action"]["edge_stiffness"],
        "J_e(s)=2/(s_v+s_w) for e=(v,w)",
    )
    check(
        rows,
        "source plaquette boundary average",
        source["functional_or_action"]["plaquette_stiffness"]
        == "J_p(s)=|boundary p|^(-1) sum_(e in boundary p) J_e(s)",
        source["functional_or_action"]["plaquette_stiffness"],
        "boundary average of source edge stiffnesses",
    )
    certificate = OMC017_CERT.read_text(encoding="utf-8")
    compact_certificate = " ".join(certificate.split())
    required = (
        "B_triangle",
        "B_square",
        "(J_h0+J_vy+J_d)/3",
        "(J_d+J_h1+J_vx)/3",
        "There is no diagonal in this",
        "not finite Gibbs projectivity",
        "does not drop a boundary interaction",
    )
    check(rows, "source transfer boundary formula", all(item in compact_certificate for item in required),
          [item for item in required if item in compact_certificate], list(required))


def source_edge_stiffness(s_left: float, s_right: float) -> float:
    return 2.0 / (s_left + s_right)


def source_edge_energy(r_left: float, s_left: float, r_right: float,
                       s_right: float, link: int) -> float:
    stiffness = source_edge_stiffness(s_left, s_right)
    return (s_left - s_right) ** 2 / 2.0 + stiffness * (
        PHASE * r_right - link * PHASE * r_left
    ) ** 2 / 2.0


def primary_boundary_terms(amplitude: float, diagonal: int) -> tuple[float, float]:
    """Return (B_square, B_triangle) from the displayed source definitions."""
    h0 = OLD_LINK
    h1 = OLD_LINK
    vx = VERTICAL_LINK
    vy = VERTICAL_LINK
    j_h0 = source_edge_stiffness(S_WITNESS, S_WITNESS)
    j_h1 = source_edge_stiffness(S_WITNESS, S_WITNESS)
    j_vx = source_edge_stiffness(S_WITNESS, S_WITNESS)
    j_vy = source_edge_stiffness(S_WITNESS, S_WITNESS)
    j_d = source_edge_stiffness(S_WITNESS, S_WITNESS)
    square = (
        source_edge_energy(R_ZERO, S_WITNESS, R_ZERO, S_WITNESS, h0)
        + source_edge_energy(amplitude, S_WITNESS, amplitude, S_WITNESS, h1)
        + (j_h0 + j_vy + j_h1 + j_vx) / 4.0
        * (1 - h0 * vy * h1 * vx)
    )
    triangle = (
        source_edge_energy(R_ZERO, S_WITNESS, R_ZERO, S_WITNESS, h0)
        + source_edge_energy(amplitude, S_WITNESS, amplitude, S_WITNESS, h1)
        + source_edge_energy(R_ZERO, S_WITNESS, amplitude, S_WITNESS, diagonal)
        + (j_h0 + j_vy + j_d) / 3.0 * (1 - h0 * vy * diagonal)
        + (j_d + j_h1 + j_vx) / 3.0 * (1 - diagonal * h1 * vx)
    )
    return square, triangle


def independent_boundary_terms(amplitude: float, diagonal: int) -> tuple[Fraction, Fraction]:
    """Rebuild the same witness with rational sign arithmetic, independently."""
    square = Fraction(0)
    cross = Fraction(amplitude).limit_denominator() ** 2 / 2
    face_one = Fraction(1 - OLD_LINK * VERTICAL_LINK * diagonal)
    face_two = Fraction(1 - diagonal * OLD_LINK * VERTICAL_LINK)
    triangle = cross + face_one + face_two
    return square, triangle


def ratio(amplitude: float) -> float:
    square, _ = primary_boundary_terms(amplitude, OLD_LINK)
    split = sum(
        math.exp(-primary_boundary_terms(amplitude, diagonal)[1])
        for diagonal in (-1, 1)
    )
    return split / math.exp(-square)


def arithmetic_checks(rows: list[dict]) -> dict:
    primary_rows = []
    for amplitude in AMPLITUDE_GRID:
        primary = {
            str(diagonal): primary_boundary_terms(amplitude, diagonal)
            for diagonal in (-1, 1)
        }
        independent = {
            str(diagonal): independent_boundary_terms(amplitude, diagonal)
            for diagonal in (-1, 1)
        }
        for diagonal in (-1, 1):
            square, triangle = primary[str(diagonal)]
            i_square, i_triangle = independent[str(diagonal)]
            check(rows, f"primary/independent square A={amplitude} d={diagonal}",
                  abs(square - float(i_square)) < 1e-12, square, float(i_square))
            check(rows, f"primary/independent triangle A={amplitude} d={diagonal}",
                  abs(triangle - float(i_triangle)) < 1e-12, triangle, float(i_triangle))
        primary_rows.append({
            "A": amplitude,
            "B_square": primary["1"][0],
            "B_triangle_d_plus": primary["1"][1],
            "B_triangle_d_minus": primary["-1"][1],
            "split_over_square": ratio(amplitude),
        })
    first_square, first_triangle = primary_boundary_terms(AMPLITUDE_GRID[0], OLD_LINK)
    check(rows, "fixed old-label square energy", abs(first_square) < 1e-12,
          first_square, 0.0)
    check(rows, "diagonal plus triangle energy", abs(first_triangle) < 1e-12,
          first_triangle, 0.0)
    minus_square, minus_triangle = primary_boundary_terms(AMPLITUDE_GRID[0], -1)
    check(rows, "diagonal minus face penalty", abs(minus_triangle - 4.0) < 1e-12,
          minus_triangle, 4.0)
    elementary = math.exp(-4.0)
    prefactor = 1.0 + elementary
    check(rows, "exact split/square ratio formula",
          all(abs(row["split_over_square"] - prefactor * math.exp(-(row["A"] ** 2) / 2.0)) < 1e-12
              for row in primary_rows),
          primary_rows, "(1+exp(-4))*exp(-A^2/2)")
    ratios = [row["split_over_square"] for row in primary_rows]
    check(rows, "ratio strictly decreases on positive witness grid",
          all(right < left for left, right in zip(ratios[1:], ratios[2:])),
          ratios, "strict decrease after A=1")
    check(rows, "ratio is positive on witness grid", all(value > 0 for value in ratios),
          ratios, ">0")
    witnesses = []
    for challenge in CHALLENGE_LEVELS:
        amplitude = math.sqrt(2.0 * math.log(4.0 * challenge))
        inverse_ratio = 1.0 / ratio(amplitude)
        check(rows, f"inverse ratio exceeds challenge {challenge}", inverse_ratio > challenge,
              inverse_ratio, f">{challenge}")
        witnesses.append({"challenge": challenge, "A": amplitude, "inverse_ratio": inverse_ratio})
    return {
        "fixed_old_labels": {"h0": 1, "h1": 1, "vx": 1, "vy": 1},
        "amplitude_grid": primary_rows,
        "prefactor": prefactor,
        "ratio_formula": "(1+exp(-4))*exp(-A^2/2)",
        "inverse_ratio_witnesses": witnesses,
        "scope": "coordinate-preserving terminal fibre only",
    }


def hostile_checks(rows: list[dict]) -> None:
    for amplitude in (1.0, 2.0, 4.0):
        correct = ratio(amplitude)
        omitted_diagonal_edge = 1.0 + math.exp(-4.0)
        check(rows, f"hostile omission of diagonal E rejected A={amplitude}",
              abs(omitted_diagonal_edge - correct) > 1e-6,
              omitted_diagonal_edge, "different from source ratio")
    wrong_face_average = 2.0 * (1.0 + math.exp(-2.0 / 3.0)) ** 2
    corrected_zero = ratio(0.0)
    check(rows, "hostile one-third face-average mutation rejected",
          abs(wrong_face_average - corrected_zero) > 1e-6,
          wrong_face_average, "different from source-stiffness result")
    check(rows, "no semigroup conclusion is encoded",
          "No physical Pre-A" in OMC020.read_text(encoding="utf-8")
          and "finite stationary semigroups" in OMC020.read_text(encoding="utf-8"),
          "OMC-020 non-claims retained", "present")


def run(output: Path) -> dict:
    rows: list[dict] = []
    source_checks(rows)
    arithmetic = arithmetic_checks(rows)
    hostile_checks(rows)
    payload = {
        "schema": "tect/pah-omc020-boundary-kernel-obstruction/1.0",
        "status": "PASS_COORDINATE_BOUNDARY_OBSTRUCTION",
        "source_pins": PINS,
        "script_sha256": digest(Path(__file__)),
        "lean_entrypoint": "verification/lean/Tect/PahOmc020.lean",
        "lean_source_sha256": digest(LEAN),
        "checks": rows,
        "arithmetic": arithmetic,
        "finding": "For the retained old-label fibre h0=h1=vx=vy=+1, the source square weight is exp(-B_square)=1 while the diagonal-summed split weight is (1+exp(-4))*exp(-A^2/2). Its inverse exceeds every tested challenge and grows along the allowed A>=0 ray.",
        "scope": "This is an exact obstruction to a uniformly bounded coordinate-preserving density-ratio lift for the terminal fibre. It is not a no-go theorem for every abstract U_n and not a counterexample to local temporal semigroup convergence.",
        "non_claims": [
            "No full PAH semigroup negative result, no Mosco liminf failure, and no statement that every possible varying-Hilbert-space comparison map is impossible.",
            "No change to the PAH-001 functional, rates, state, carrier, regulator order or external Markov time.",
            "No physical Pre-A, spacetime, QFT, gravity, continuum, mass gap, Yang-Mills or TOE conclusion."
        ],
    }
    atomic_json(output, payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        expected = args.output.read_bytes()
        with tempfile.TemporaryDirectory(prefix="pah020-boundary-replay-") as directory:
            payload = run(Path(directory) / "replay.json")
        actual = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
        if expected != actual:
            raise SystemExit("PAH-OMC-020 boundary-kernel replay mismatch")
    else:
        run(args.output)
    print("PAH-OMC-020 BOUNDARY KERNEL: PASS (coordinate-fibre obstruction; temporal proof IN_PROGRESS)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
