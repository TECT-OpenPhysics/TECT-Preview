#!/usr/bin/env python3
"""Recompute the v0.1.41 paper's rational certificates and normalization tests.

Inputs come from the pinned A1 parameter manifest; no primary theorem checker
is imported. Printed root/decimal endpoints are explicitly test oracles, not
derived eigenvalues. The root bracket is checked independently by three sign
changes of the reconstructed characteristic polynomial. This finite audit
does not verify the PDE proof, novelty, or an external review disposition.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction as F
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
PAPER = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json"
DEFAULT_OUTPUT = ROOT / "claims/A2-FULL-PRODUCTION-WELLPOSED/runs/2026-09-09-paper-rereview/result.json"


def det3(a):
    return (a[0][0] * (a[1][1]*a[2][2]-a[1][2]*a[2][1])
            - a[0][1] * (a[1][0]*a[2][2]-a[1][2]*a[2][0])
            + a[0][2] * (a[1][0]*a[2][1]-a[1][1]*a[2][0]))


def atan_bounds(x, terms):
    if not 0 < x < 1 or terms < 1:
        raise ValueError("alternating arctangent needs 0<x<1 and positive terms")
    partial = sum(((-1)**j*x**(2*j+1)/F(2*j+1) for j in range(terms)), F(0))
    remainder = x**(2*terms+1)/F(2*terms+1)
    return (partial, partial+remainder) if terms % 2 == 0 else (partial-remainder, partial)


def machin(n5, n239):
    a, b = atan_bounds(F(1, 5), n5), atan_bounds(F(1, 239), n239)
    return 16*a[0]-4*b[1], 16*a[1]-4*b[0]


def sign(value):
    return (value > 0) - (value < 0)


def shell_certificate(shell, center, alpha_lo, alpha_hi):
    return F(2*shell-1, 2) < center/alpha_hi < center/alpha_lo < F(2*shell+1, 2)


def encode(value):
    if isinstance(value, F):
        return str(value)
    if isinstance(value, dict):
        return {str(k): encode(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [encode(v) for v in value]
    return value


def build():
    params = json.loads(MANIFEST.read_text(encoding="utf-8"))["parameters"]
    get = lambda name: F(str(params[name]))
    lengths = [get(key) for key in ("Lx", "Ly", "Lz")]
    volume = lengths[0]*lengths[1]*lengths[2]
    family = [F(str(x)) for x in params["family_masses"]]
    z0 = [F(str(x)) for x in params["z0"]]
    norm = sum(x*x for x in z0)
    matrix = [[(family[i] if i == j else F(0)) + get("k_lock") *
               (int(i == j)-z0[i]*z0[j]/norm) for j in range(3)] for i in range(3)]
    trace = sum(matrix[i][i] for i in range(3))
    second = sum(matrix[i][i]*matrix[j][j]-matrix[i][j]*matrix[j][i]
                 for i in range(3) for j in range(i+1, 3))
    determinant = det3(matrix)
    chi = lambda t: t**3-trace*t*t+second*t-determinant
    # Printed endpoint oracles: the checker verifies, rather than assumes, them.
    a, b = F(2811617233511, 10**14), F(2811617233512, 10**14)
    brackets = [(a,b), (F(3,20),F(9,50)), (F(19,100),F(11,50))]
    root_signs = [(sign(chi(lo)), sign(chi(hi))) for lo, hi in brackets]
    pi_lo, pi_hi = machin(20, 7)  # finite certificate lengths printed in the paper
    fine_lo, fine_hi = machin(24, 9)  # stricter alternate truncation, not a fitted value
    alpha_lo, alpha_hi = (2*pi_lo/lengths[0])**2, (2*pi_hi/lengths[0])**2
    y, z, r, lam, gamma = [get(key) for key in ("Y","Z","r","lambda","gamma")]
    center = -z/(2*y)
    scalar = lambda x: y*x*x+z*x+r
    lambda_lo, lambda_hi = scalar(3*alpha_lo)+a, scalar(3*alpha_hi)+b
    outward_lo = F("0.28811617234458494031")  # displayed decimal oracles
    outward_hi = F("0.28811617234459494032")
    rho = -3*lam/(4*gamma)
    cstar = 3*lam*lam/(16*gamma)
    charge = volume*rho/2
    nu = r-z*z/(4*y)+F(7,250)
    energy_gap = nu/2-3*lam*lam/(32*gamma)
    radial_gap = nu-lam*lam/(4*gamma)
    rows = []

    def check(name, passed, actual):
        rows.append({"name": name, "passed": bool(passed), "actual": encode(actual)})

    check("fixed_side_16", lengths == [16,16,16], lengths)
    check("internal_characteristic_from_inputs", (trace,second,determinant) ==
          (F(2,5),F(223,5000),F(3,3125)), [trace,second,determinant])
    for index, signs in enumerate(root_signs):
        check(f"root_bracket_{index+1}_sign_change", signs[0]*signs[1] == -1, signs)
    check("three_disjoint_cubic_brackets", all(brackets[i][1] < brackets[i+1][0]
          for i in range(2)), brackets)
    check("printed_sign_order", root_signs == [(-1,1),(1,-1),(-1,1)], root_signs)
    check("machin_positive_interval", 3 < pi_lo < pi_hi < 4, [pi_lo,pi_hi])
    check("machin_refinement_nested", pi_lo < fine_lo < fine_hi < pi_hi, [fine_lo,fine_hi])
    tangent_twice = 2*F(1,5)/(1-F(1,5)**2)
    tangent_four = 2*tangent_twice/(1-tangent_twice**2)
    check("machin_branch_algebra", (tangent_four-F(1,239))/(1+tangent_four*F(1,239)) == 1,
          [tangent_twice,tangent_four])
    check("unique_integer_shell", shell_certificate(3,center,alpha_lo,alpha_hi),
          [center/alpha_hi,center/alpha_lo])
    check("interval_above_scalar_vertex", 3*alpha_lo > center, 3*alpha_lo-center)
    check("outward_lambda_interval", outward_lo < lambda_lo < lambda_hi < outward_hi,
          [lambda_lo,lambda_hi])
    modes = [n for n in product(range(-1,2),repeat=3) if sum(i*i for i in n)==3]
    check("shell_mode_count", len(modes)==8, modes)
    check("charge_normalization", charge == F(11008,27), charge)
    check("polynomial_quartic_match", -gamma*rho/3 == lam/4, -gamma*rho/3)
    check("polynomial_linear_cancellation", gamma*rho*rho/6-cstar/2 == 0,
          gamma*rho*rho/6-cstar/2)
    check("neutral_energy_gap", energy_gap > F(1,8), energy_gap)
    check("neutral_radial_gap", radial_gap > F(1,4), radial_gap)
    check("local_zero_h2_coefficient_positive", 0 < cstar < lambda_lo,
          cstar/(10*lambda_hi))
    check("bregman_threshold", 4*gamma*rho+3*lam == 0, 4*gamma*rho+3*lam)
    # Actual altered alternatives are passed to the same predicates.
    check("hostile_shell_two_rejected", not shell_certificate(2,center,alpha_lo,alpha_hi), 2)
    check("hostile_shell_four_rejected", not shell_certificate(4,center,alpha_lo,alpha_hi), 4)
    check("hostile_root_interval_rejected", chi(b)*chi(F(3,100)) > 0, [b,F(3,100)])
    check("hostile_missing_volume_rejected", rho/2 != charge, rho/2)
    check("hostile_missing_charge_half_rejected", volume*rho != charge, volume*rho)
    check("hostile_wrong_completion_sign_rejected", gamma*rho*rho/6+cstar/2 != 0,
          gamma*rho*rho/6+cstar/2)
    text = (PAPER/"manuscript.tex").read_text(encoding="utf-8")
    for label in ("eq:fourier-normalization", "eq:midpoint-uniform-tail", "eq:strict-local-zero",
                  "eq:root-sign-certificate", "eq:machin-certificate", "eq:lambda-rational-certificate"):
        check("proof_anchor_"+label, text.count("\\label{"+label+"}")==1, label)
    check("energy_operator_notation_separated", r"\mathcal F(u):=Lu+N(u)" not in text
          and r"\mathcal G(u):=Lu+N(u)" in text, "scalar energy F / vector field G")
    return {"schema":"tect/a2-paper-rereview/1.0", "claim_bearing":False,
            "source_sha256":hashlib.sha256(MANIFEST.read_bytes()).hexdigest(),
            "manuscript_sha256":hashlib.sha256((PAPER/"manuscript.tex").read_bytes()).hexdigest(),
            "assertions":rows, "passed_count":sum(row["passed"] for row in rows),
            "assertion_count":len(rows), "verdict":"PASS" if all(row["passed"] for row in rows) else "FAIL",
            "scope":"Finite rational and structural re-review only; no analytic or external review certification."}


def self_test():
    assert det3([[F(1),F(0),F(0)],[F(0),F(2),F(0)],[F(0),F(0),F(3)]]) == 6
    assert atan_bounds(F(1,5),2)[0] < atan_bounds(F(1,5),3)[0]
    for invalid in (F(0), F(1), F(-1)):
        try:
            atan_bounds(invalid,2)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid alternating-series argument was accepted")


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test",action="store_true")
    args=parser.parse_args()
    self_test()
    result=build()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    fd, temp=tempfile.mkstemp(dir=args.output.parent,prefix=".rereview-",suffix=".json")
    try:
        with os.fdopen(fd,"w",encoding="utf-8",newline="\n") as stream:
            json.dump(result,stream,indent=2,sort_keys=True)
            stream.write("\n")
        os.replace(temp,args.output)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)
    print(f"A2-PAPER-REREVIEW-{result['verdict']}: {result['passed_count']}/{result['assertion_count']}")
    for row in result["assertions"]:
        if not row["passed"]:
            print("FAILED:",row["name"])
    print("artifact:",args.output)
    return 0 if result["verdict"]=="PASS" else 1


if __name__=="__main__":
    raise SystemExit(main())
