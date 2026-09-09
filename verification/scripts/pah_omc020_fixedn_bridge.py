#!/usr/bin/env python3
"""Scoped PAH-OMC-020 fixed-n bridge audit.

This executable checks the algebraic and provenance spine of the proposed
fixed-n radial-mesh argument.  It does not claim a semigroup convergence
theorem: the compact rate/Lipschitz propagation and a common-space
Mosco/strong-resolvent bridge remain explicit analytic obligations.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
PREREG = ROOT / "strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json"
PAH = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
OMC016 = ROOT / "strategy/pa-hyp/PAH-OMC-016-uniform-result-v1.json"
OMC018_CERT = ROOT / "strategy/pa-hyp/PAH-OMC-018-generator-certificate.md"
LEAN = ROOT / "verification/lean/Tect/PahOmc020.lean"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-07-pah-omc020-fixedn-bridge/bridge.json"
)

PREREG_SHA = "906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3"
SOURCE_PINS = {
    "strategy/pa-hyp/PAH-001-v1.json":
        "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-OMC-016-uniform-result-v1.json":
        "6ba124f6b102022c0e4995c005d9275ce51aaa51a52a6f274ef73254d444bf97",
    "strategy/pa-hyp/PAH-OMC-018-generator-certificate.md":
        "18dc782cafff8cf8a516fd8366ec7e1f8727a24c9553dba0656a6b4bc84de264",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(rows: list[dict], name: str, condition: bool, actual: object, expected: object) -> None:
    if not condition:
        raise AssertionError(name)
    rows.append({"name": name, "status": "PASS", "actual": actual, "expected": expected})


def source_and_scope_checks(rows: list[dict]) -> dict:
    check(rows, "OMC-020 preregistration pin", sha256(PREREG) == PREREG_SHA,
          sha256(PREREG), PREREG_SHA)
    for relative, pin in SOURCE_PINS.items():
        path = ROOT / relative
        check(rows, f"source pin:{relative}", sha256(path) == pin, sha256(path), pin)
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    pah = json.loads(PAH.read_text(encoding="utf-8"))
    state = json.loads(OMC016.read_text(encoding="utf-8"))
    check(rows, "fixed-n comparison is declared",
          prereg["objects_and_comparison"]["finite_semigroup"].startswith("P_nj"),
          prereg["objects_and_comparison"]["finite_semigroup"], "P_nj=exp(t L_nj)")
    check(rows, "j-before-n order is declared",
          "First j" in prereg["scope"]["regulator_order"] and
          "then" in prereg["scope"]["regulator_order"],
          prereg["scope"]["regulator_order"], "j then anchored n")
    check(rows, "same external time is declared",
          "unaccelerated Markov time" in prereg["scope"]["time"],
          prereg["scope"]["time"], "external unaccelerated Markov time")
    fixed = state["exact_scope"]["parameters"]
    check(rows, "source parameter crosswalk",
          all(token in fixed for token in ("K=2", "M_s=1", "epsilon=1/2", "beta=nu=1")),
          fixed, "OMC-016 fixed parameters")
    generator = pah["dynamics"]["generator"]
    check(rows, "PAH generator remains original",
          "exp[-beta(F_rho(r x)-F_rho(x))/2]" in generator,
          generator, "original midpoint Gibbs rate")
    cert = OMC018_CERT.read_text(encoding="utf-8")
    for marker in ("(2)", "(3)", "(4)", "(5)", "not a temporal path-law construction"):
        check(rows, f"OMC-018 bridge marker:{marker}", marker in cert, marker, "present")
    return prereg


def primary_algebra(rows: list[dict]) -> None:
    # The following identities are the source midpoint convention, written
    # symbolically.  They are not a numerical fit or a finite PAH simulation.
    fx, fy, fz, mobility, normalizer = sp.symbols(
        "fx fy fz mobility normalizer", real=True
    )
    rate_xy = mobility * sp.exp(-(fy - fx) / 2)
    pi_x = sp.exp(-fx) / normalizer
    check(rows, "square-weight transport",
          sp.simplify(pi_x * rate_xy**2 - mobility**2 * sp.exp(-fy) / normalizer) == 0,
          "pi_x c_xy^2", "mobility^2 exp(-fy)/normalizer")
    rate_yx = mobility * sp.exp(-(fx - fy) / 2)
    check(rows, "directed conductance balance",
          sp.simplify(pi_x * rate_xy - sp.exp(-fy) / normalizer * rate_yx) == 0,
          "pi_x c_xy", "pi_y c_yx")
    f, ft, g, gt, conductance = sp.symbols("f ft g gt conductance", real=True)
    form_difference = -conductance * (f * (gt - g) + ft * (g - gt))
    check(rows, "inverse-pair form sign",
          sp.expand(form_difference - conductance * (ft - f) * (gt - g)) == 0,
          "-<f,Lg> pair", "conductance*(ft-f)*(gt-g)")
    H, lipschitz, mesh = sp.symbols("H lipschitz mesh", nonnegative=True)
    check(rows, "radial half-form coefficient",
          sp.expand(H * (2 * lipschitz * mesh) ** 2 / 2
                    - 2 * H * lipschitz**2 * mesh**2) == 0,
          "H*(2 L h)^2/2", "2 H L^2 h^2")


def independent_reconstruction(rows: list[dict]) -> None:
    """Rebuild a two-state reversible oracle without importing primary code."""
    # This is a generic exact oracle for the finite label fibre, not a new PAH
    # carrier.  At zero energy difference and unit mobility, the generator is
    # the reversible two-state block forced by the source rate convention.
    t = sp.symbols("t", nonnegative=True)
    generator = sp.Matrix([[-1, 1], [1, -1]])
    semigroup = sp.exp(t * generator)
    ones = sp.Matrix([1, 1])
    check(rows, "independent fibre conservativity",
          sp.simplify(semigroup * ones - ones) == sp.zeros(2, 1),
          "exp(t L) 1", "1")
    check(rows, "independent fibre reversibility",
          sp.simplify(semigroup - semigroup.T) == sp.zeros(2),
          "exp(t L)", "transpose")
    check(rows, "independent fibre nonnegative form",
          sp.expand(-(sp.Matrix([[sp.Symbol("a")], [sp.Symbol("b")]]).T
                       * generator
                       * sp.Matrix([[sp.Symbol("a")], [sp.Symbol("b")]]))[0])
          == sp.expand((sp.Symbol("a") - sp.Symbol("b")) ** 2),
          "-v^T L v", "(a-b)^2")


def hostile_controls(rows: list[dict]) -> None:
    with tempfile.TemporaryDirectory(prefix="pah020-bridge-hostile-") as directory:
        altered = Path(directory) / "altered-prereg.json"
        altered.write_bytes(PREREG.read_bytes() + b"\n")
        check(rows, "hostile preregistration mutation rejected",
              sha256(altered) != PREREG_SHA, sha256(altered), "different from pinned hash")
    fx, fy, mobility, normalizer = sp.symbols("fx fy mobility normalizer", real=True)
    wrong_rate = mobility * sp.exp(-(fy - fx))
    pi_x = sp.exp(-fx) / normalizer
    check(rows, "hostile missing half exponent rejected",
          sp.simplify(pi_x * wrong_rate**2
                      - mobility**2 * sp.exp(-fy) / normalizer) != 0,
          "full exponent square", "not source midpoint identity")


def lean_check() -> dict:
    compiler = Path.home() / ".elan/toolchains/leanprover--lean4---v4.32.1/bin/lean.exe"
    if not compiler.is_file():
        return {"status": "NOT_AVAILABLE", "command": "lean Tect/PahOmc020.lean"}
    package_root = Path("E:/Dev/TECT/verification/lean/.lake/packages")
    env = os.environ.copy()
    if package_root.is_dir():
        paths = []
        for package in package_root.iterdir():
            candidate = package / ".lake/build/lib/lean"
            if candidate.is_dir():
                paths.append(str(candidate))
        env["LEAN_PATH"] = ";".join(paths)
    process = subprocess.run(
        [str(compiler), str(LEAN)], cwd=LEAN.parent.parent.parent,
        env=env, capture_output=True, text=True, encoding="utf-8", errors="replace",
        check=False, timeout=180,
    )
    output = (process.stdout + "\n" + process.stderr).strip()
    return {
        "status": "PASS" if process.returncode == 0 and "error:" not in output.lower() else "FAIL",
        "command": "lean verification/lean/Tect/PahOmc020.lean",
        "returncode": process.returncode,
        "output": output[-2000:],
        "compiler": str(compiler),
    }


def run(output: Path) -> dict:
    rows: list[dict] = []
    prereg = source_and_scope_checks(rows)
    primary_algebra(rows)
    independent_reconstruction(rows)
    hostile_controls(rows)
    lean = lean_check()
    if lean["status"] != "PASS":
        raise AssertionError("Lean cross-check did not pass")
    payload = {
        "schema": "tect/pah-omc020-fixedn-bridge/1.0",
        "status": "PASS_SCOPED_BRIDGE_AUDIT",
        "temporal_verdict": "IN_PROGRESS",
        "preregistration_sha256": sha256(PREREG),
        "code_sha256": sha256(Path(__file__)),
        "checks": rows,
        "lean": lean,
        "scope": prereg["scope"],
        "proved_scope": [
            "source midpoint Gibbs square and detailed-balance algebra",
            "inverse-pair form sign and radial half-form coefficient",
            "generic finite reversible fibre oracle and hostile mutation rejection",
            "provenance and fixed-n/j-before-n contract pins",
        ],
        "conditional_bridge": [
            "compact amplitude rate Lipschitzness plus finite-fibre semigroup stability",
            "Duhamel control of the radial residual after compact truncation",
            "common-space form Mosco or equivalent strong-resolvent identification",
        ],
        "missing_for_temporal_completion": [
            "a PAH-specific proof of the compact semigroup Lipschitz propagation constant",
            "a PAH-specific common-space weak-liminf/recovery or equivalent theorem",
            "identification of the anchored n limit with R-512 minimal closure",
        ],
        "non_claims": [
            "This is not a finite-semigroup convergence theorem or a full PAH result.",
            "No graph-core, operator-core, minimal/maximal-domain equality or infinite-volume process is claimed.",
            "No physical Pre-A, spacetime, quantum real time, QFT, gravity, continuum, mass gap or TOE conclusion.",
        ],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        expected = args.output.read_bytes()
        payload = run(Path(tempfile.mktemp(prefix="pah020-bridge-replay-", suffix=".json")))
        actual = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
        if expected != actual:
            raise SystemExit("PAH-OMC-020 fixed-n bridge replay mismatch")
    else:
        run(args.output)
    print("PAH-OMC-020 FIXED-N BRIDGE: PASS (scoped algebraic audit; temporal proof IN_PROGRESS)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
