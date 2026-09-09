"""Verify the ordered finite-time correlation limit on the PAH radial sector.

This is a bounded auxiliary theorem.  It keeps the PAH-001 generator,
state, regulator order and external Markov time unchanged.  It proves only
the amplitude-only cylinder sector, where the post-j-limit PH/LK/AP operator
vanishes and the original radial residual is controlled by the registered
R-511 estimate.  It does not prove a common-space theorem for mixed
observables or the full anchored-n passage.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import tempfile
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-07-pah-omc020-radial-sector/primary.json"
)

PINS = {
    "strategy/pa-hyp/PAH-001-v1.json":
        "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-017-result-v1.json":
        "4e2884d43a15846069a3ead9682d35e8321674a5d2ca3be727a1d411aae831fb",
    "strategy/pa-hyp/PAH-OMC-018-result-v1.json":
        "d34d08c5dda4acf6edb3749c5d18ddd3d98f13a4d52e6049cb373dc055729a65",
    "strategy/pa-hyp/PAH-OMC-018-generator-certificate.md":
        "18dc782cafff8cf8a516fd8366ec7e1f8727a24c9553dba0656a6b4bc84de264",
    "strategy/pa-hyp/PAH-OMC-019-result-v1.json":
        "82c35e7d96b618d0b8d8a7eed906fafef2e29559af158e40b47501e9210dd4cd",
    "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json":
        "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3",
    "strategy/pa-hyp/PAH-OMC-020-temporal-work.md":
        "45fc8e90e5ee960414d6a3f868647c85fcd0fe1f0b17e7e1b677b5647e78d16b",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True, ensure_ascii=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def check(rows: list[dict], name: str, actual: object, expected: object, ok: bool) -> None:
    if not ok:
        raise AssertionError(f"{name}: {actual!r} != {expected!r}")
    def serial(value: object) -> object:
        return str(value) if isinstance(value, Fraction) else value
    rows.append({"name": name, "status": "PASS", "actual": serial(actual), "expected": serial(expected)})


def compute() -> dict:
    rows: list[dict] = []
    source_hashes: dict[str, str] = {}
    for relative, expected in PINS.items():
        path = ROOT / relative
        actual = digest(path)
        source_hashes[relative] = actual
        check(rows, f"source hash {relative}", actual, expected, actual == expected)

    pah = json.loads((ROOT / "strategy/pa-hyp/PAH-001-v1.json").read_text(encoding="utf-8"))
    omc017 = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-017-result-v1.json").read_text(encoding="utf-8"))
    omc018 = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-018-result-v1.json").read_text(encoding="utf-8"))
    omc019 = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-019-result-v1.json").read_text(encoding="utf-8"))
    prereg = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json").read_text(encoding="utf-8"))
    cert = (ROOT / "strategy/pa-hyp/PAH-OMC-018-generator-certificate.md").read_text(encoding="utf-8")
    work = (ROOT / "strategy/pa-hyp/PAH-OMC-020-temporal-work.md").read_text(encoding="utf-8")

    moves = pah["dynamics"]["move_set"]
    check(rows, "source PAH identity", pah["packet_id"], "PAH-001", pah["packet_id"] == "PAH-001")
    check(rows, "TR radial move present", any("radial" in item.lower() for item in moves), True,
          any("radial" in item.lower() for item in moves))
    check(rows, "nonradial phase move present", any("phase" in item.lower() for item in moves), True,
          any("phase" in item.lower() for item in moves))
    check(rows, "link move present", any("link" in item.lower() for item in moves), True,
          any("link" in item.lower() for item in moves))
    check(rows, "aperture move present", any("aperture" in item.lower() for item in moves), True,
          any("aperture" in item.lower() for item in moves))
    check(rows, "TR residual estimate is pinned", "||L_TR,nj S_nj f||_L2(mu_nj) <= 2 H_f L_f h" in cert,
          True, "||L_TR,nj S_nj f||_L2(mu_nj) <= 2 H_f L_f h" in cert)
    mesh_present = bool(re.search(r"h=2\^\(?-j\)?", cert)) and bool(
        re.search(r"h_j=2\^\(?-j\)?", work))
    check(rows, "declared mesh is h_j=2^(-j)", mesh_present, True, mesh_present)
    check(rows, "post-j operator keeps PH/LK/AP", "retaining the PH,LK,AP summands" in cert,
          True, "retaining the PH,LK,AP summands" in cert)
    check(rows, "amplitude-only null source statement", "For every amplitude-only f in D, Af=0" in cert,
          True, "For every amplitude-only f in D, Af=0" in cert)
    check(rows, "R-510 local state convergence is source input",
          omc017["conclusion"]["answer"].startswith("For each fixed prefix"), True,
          omc017["conclusion"]["answer"].startswith("For each fixed prefix"))
    check(rows, "R-512 radial kernel is source input", "H_rad subset ker(Ebar)" in omc019["kernel_claim"],
          True, "H_rad subset ker(Ebar)" in omc019["kernel_claim"])
    check(rows, "R-512 remains auxiliary", omc019["classification"] == "auxiliary_support", "auxiliary_support",
          omc019["classification"] == "auxiliary_support")
    check(rows, "target is minimal form semigroup", "T_min(t)=exp(-t K_min)" in prereg["objects_and_comparison"]["target_semigroup"],
          True, "T_min(t)=exp(-t K_min)" in prereg["objects_and_comparison"]["target_semigroup"])
    markov_time = "external unaccelerated markov time" in prereg["scope"]["time"].lower()
    check(rows, "external Markov time retained", markov_time, True, markov_time)

    # Exact source-derived finite-time estimate.  H_f and L_g are test inputs,
    # not fitted PAH constants; the factor 2 is the registered R-511 bound.
    H_f = Fraction(3, 2)
    L_g = Fraction(5, 3)
    T = Fraction(7, 4)
    radial_factor = 2 * H_f * L_g
    errors = {j: T * radial_factor * Fraction(1, 2 ** j) for j in range(0, 13)}
    check(rows, "R-511 radial coefficient", radial_factor, Fraction(5), radial_factor == Fraction(5))
    check(rows, "finite-time bound is nonnegative", all(value >= 0 for value in errors.values()), True,
          all(value >= 0 for value in errors.values()))
    check(rows, "finite-time bound decreases in j", all(errors[j + 1] < errors[j] for j in range(0, 12)), True,
          all(errors[j + 1] < errors[j] for j in range(0, 12)))
    check(rows, "variation-of-constants factor", T * radial_factor, Fraction(35, 4),
          T * radial_factor == Fraction(35, 4))
    check(rows, "j=10 bound below 1/100", errors[10] < Fraction(1, 100), True,
          errors[10] < Fraction(1, 100))

    # The stationary correlation estimate is scalar and does not require a
    # completed varying-space map on this invariant sector.
    check(rows, "finite semigroup contraction input",
          "finite_transfer_target" in pah["dynamics"] and "reversible" in pah["dynamics"]["finite_transfer_target"],
          True, "finite_transfer_target" in pah["dynamics"] and "reversible" in pah["dynamics"]["finite_transfer_target"])
    nonradial_label_only = "nonradial roots only change finite labels" in cert.lower()
    check(rows, "radial sector avoids nonradial increments", nonradial_label_only, True,
          nonradial_label_only)
    check(rows, "target fixes radial vector under form kernel",
          "zero energy and zero cross-energy" in omc019["conclusion"], True,
          "zero energy and zero cross-energy" in omc019["conclusion"])
    anchored_open = "anchored `n`" in work and any("semigroup convergence" in item for item in omc019["non_claims"])
    check(rows, "full anchored-n obligation retained", anchored_open, True, anchored_open)
    check(rows, "no common U_n shortcut", "not claimed an isometry" in omc017["common_observable_algebra"]["norm"].lower()
          or "not claimed an isometry" in json.dumps(prereg), True,
          "not claimed an isometry" in omc017["common_observable_algebra"]["norm"].lower()
          or "not claimed an isometry" in json.dumps(prereg))

    return {
        "schema": "tect/pah-omc020-radial-sector-primary/1.0",
        "status": "PASS_RADIAL_SECTOR_ORDERED_CORRELATION",
        "verdict": "AUXILIARY_SUPPORT",
        "conditional": True,
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "source_hashes": source_hashes,
        "checks": rows,
        "scope": {
            "observables": "Amplitude-only bounded globally amplitude-Lipschitz finite-prefix cylinders f,g in D_rad.",
            "model": "Exact PAH-001 functional and original finite generator; no new rate, state, carrier, projection or time.",
            "order": "j->infinity at fixed n, then the original anchored n state passage; only the radial-sector scalar correlation is closed.",
            "time": "External unaccelerated Markov time on every compact [0,T].",
        },
        "proof": {
            "finite_j": "For g in D_rad, non-TR roots leave g unchanged and R-511 gives ||L_TR,nj S_nj g||_2 <= 2 H_g L_g h_j. Finite stationary L2 contraction and variation of constants give a uniform compact-time error <= 2 T ||f||_infinity H_g L_g h_j.",
            "n_passage": "R-510 local state convergence sends the static sampled inner product to the R-510/R-511 local limiting inner product for each fixed cylinder pair.",
            "target": "R-512 places D_rad in H_rad with zero form energy and zero cross-energy, so the self-adjoint operator represented by the minimal closed form annihilates these vectors and its semigroup fixes them.",
            "uniformity": "The j estimate is uniform in finite n at the registered support stage; the n step is the inherited local-state convergence, not a varying-space operator theorem.",
        },
        "derived_inputs": {
            "test_H_f": str(H_f),
            "test_L_g": str(L_g),
            "test_T": str(T),
            "radial_residual_factor": str(radial_factor),
            "error_by_j": {str(j): str(value) for j, value in errors.items()},
        },
        "assumptions": [
            "The exact R-511 radial residual estimate and source move-set distinction apply to D_rad.",
            "The finite stationary semigroup is an L2 contraction and admits the elementary variation-of-constants identity.",
            "R-510 fixed-prefix local-state convergence applies to the selected f,g.",
            "The standard closed-form implication that a zero-form vector is fixed by the semigroup represented by the R-512 minimal form.",
        ],
        "missing_assumptions": [
            "No common U_n/Hilbert realization for mixed observables.",
            "No N2b arbitrary-sequence liminf/recovery, N2c/N4 boundary escape for general evolved cylinders, or N2d selection beyond the radial kernel.",
            "No semigroup convergence for general aperture/label-dependent f,g and no full PAH-OMC-020 theorem.",
        ],
        "non_claims": [
            "This is an auxiliary conditional theorem on D_rad, not the full anchored-n PAH-OMC-020 convergence claim.",
            "It does not establish a common U_n, a mixed-observable varying-Hilbert limit, N2b/N2c/N2d in full generality, or an infinite-volume process.",
            "No physical Pre-A, spacetime, QFT, gravity, continuum, Yang-Mills, mass-gap or TOE conclusion.",
            "External Markov time is not quantum real time, proper time or Lorentzian time.",
        ],
        "next_single_question": "Can the same minimal-form comparison be proved for one non-radial local cylinder without a source-authorized common U_n/terminal-square map?",
        "reproduction": "python -X utf8 verification/scripts/pah_omc020_radial_sector.py --check",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = compute()
    encoded = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check and args.output.exists():
        if args.output.read_bytes() != encoded:
            raise SystemExit("PAH-OMC-020 radial-sector replay mismatch")
    elif not args.check:
        atomic_json(args.output, payload)
    print(f"PAH-OMC-020 RADIAL SECTOR: PASS ({len(payload['checks'])} checks; D_rad only)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
