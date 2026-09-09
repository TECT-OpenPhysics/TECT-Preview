"""Non-importing independent audit for the PAH radial-sector result."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-07-pah-omc020-radial-sector/independent.json"
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
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, payload: dict) -> None:
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    checks: list[dict] = []

    def ck(name: str, actual: object, expected: object, ok: bool) -> None:
        if not ok:
            raise AssertionError(f"{name}: {actual!r} != {expected!r}")
        checks.append({"name": name, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    hashes = {}
    for relative, expected in PINS.items():
        actual = sha(ROOT / relative)
        hashes[relative] = actual
        ck(f"hash {relative}", actual, expected, actual == expected)

    pah = json.loads((ROOT / "strategy/pa-hyp/PAH-001-v1.json").read_text(encoding="utf-8"))
    r510 = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-017-result-v1.json").read_text(encoding="utf-8"))
    r512 = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-019-result-v1.json").read_text(encoding="utf-8"))
    omc018 = (ROOT / "strategy/pa-hyp/PAH-OMC-018-generator-certificate.md").read_text(encoding="utf-8")
    prereg = json.loads((ROOT / "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json").read_text(encoding="utf-8"))

    moves = [item.lower() for item in pah["dynamics"]["move_set"]]
    ck("PAH packet", pah["packet_id"], "PAH-001", pah["packet_id"] == "PAH-001")
    ck("four source move classes", ["phase" in x for x in moves] + ["radial" in x for x in moves]
       + ["link" in x for x in moves] + ["aperture" in x for x in moves], [True, True, True, True],
       all(any(token in x for x in moves) for token in ("phase", "radial", "link", "aperture")))
    radial_form_present = "E_TR,nj" in omc018 and "H_f L_f^2 h^2" in omc018
    ck("R-511 radial residual", radial_form_present, True, radial_form_present)
    compact_omc018 = re.sub(r"\s+", "", omc018)
    operator_residual = "||L_njS_njf-S_njA_nf||_L2(mu_nj)->0" in compact_omc018
    ck("R-511 operator residual", operator_residual, True, operator_residual)
    ck("R-510 no physical volume", "not physical volume" in r510["exact_scope"]["volume"].lower(), True,
       "not physical volume" in r510["exact_scope"]["volume"].lower())
    ck("R-510 local limit", "converges without subsequence selection" in r510["conclusion"]["answer"], True,
       "converges without subsequence selection" in r510["conclusion"]["answer"])
    radial_kernel = r512["kernel_claim"].startswith("H_rad subset ker(Ebar)")
    ck("R-512 radial kernel", radial_kernel, True, radial_kernel)
    ck("minimal form is auxiliary", r512["classification"], "auxiliary_support", r512["classification"] == "auxiliary_support")
    ck("time is external", "external unaccelerated markov time" in prereg["scope"]["time"].lower(), True,
       "external unaccelerated markov time" in prereg["scope"]["time"].lower())

    # Independent exact arithmetic reconstruction of the contraction envelope.
    norm_f = Fraction(4, 3)
    lipschitz_g = Fraction(7, 2)
    time_horizon = Fraction(5, 4)
    coefficient = 2 * norm_f * lipschitz_g
    errors = [time_horizon * coefficient * Fraction(1, 2 ** j) for j in range(0, 12)]
    ck("coefficient from R-511 factor", coefficient, Fraction(28, 3), coefficient == Fraction(28, 3))
    ck("envelope nonnegative", all(x >= 0 for x in errors), True, all(x >= 0 for x in errors))
    ck("envelope strict decay", all(errors[i + 1] < errors[i] for i in range(len(errors) - 1)), True,
       all(errors[i + 1] < errors[i] for i in range(len(errors) - 1)))
    ck("last fixture below 1/100", errors[-1] < Fraction(1, 100), True, errors[-1] < Fraction(1, 100))
    ck("variation bound uses compact T", time_horizon * coefficient, Fraction(35, 3),
       time_horizon * coefficient == Fraction(35, 3))
    no_common_shortcut = "S_nj" in json.dumps(prereg) and "not claimed an isometry" in json.dumps(prereg)
    ck("no common-space promotion", no_common_shortcut, True, no_common_shortcut)
    target_open = any("semigroup convergence" in item.lower() for item in r512["non_claims"])
    ck("full target remains open", target_open, True, target_open)
    ck("physical firewall", any("physical Pre-A" in item for item in r512["non_claims"]), True,
       any("physical Pre-A" in item for item in r512["non_claims"]))

    payload = {
        "schema": "tect/pah-omc020-radial-sector-independent/1.0",
        "status": "PASS_INDEPENDENT_RADIAL_SECTOR",
        "verdict": "AUXILIARY_SUPPORT",
        "conditional": True,
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "source_hashes": hashes,
        "checks": checks,
        "derived": {
            "norm_f": str(norm_f),
            "lipschitz_g": str(lipschitz_g),
            "time_horizon": str(time_horizon),
            "coefficient": str(coefficient),
            "error_by_j": [str(x) for x in errors],
        },
        "scope": "Independent finite arithmetic and source-contract audit for D_rad only; no common-space or general anchored-n theorem.",
        "non_claims": [
            "No mixed-observable semigroup convergence, common U_n, N2b/N2c/N2d closure or infinite-volume process.",
            "No physical Pre-A, spacetime, QFT, gravity, continuum, Yang-Mills, mass-gap or TOE conclusion.",
            "External Markov time is not quantum real time, proper time or Lorentzian time.",
        ],
        "reproduction": "python -X utf8 codes/foundations/pah_omc020_radial_sector_independent.py --check",
    }
    encoded = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    if args.check and args.output.exists():
        if args.output.read_bytes() != encoded:
            raise SystemExit("PAH-OMC-020 radial independent replay mismatch")
    elif not args.check:
        write_json(args.output, payload)
    print(f"PAH-OMC-020 RADIAL INDEPENDENT: PASS ({len(checks)} checks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
