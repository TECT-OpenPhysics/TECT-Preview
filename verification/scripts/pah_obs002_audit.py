"""PAH-OBS-002 source crosswalk replay; not a physical instrument verifier.

Exact symbolic controls rederive rotating-frame/harmonic/loop conventions and
reject coherent-rate, time-ordering and encoded-readout shortcuts. Tiny matrices
are diagnostic INPUTS, never PAH carriers or experimental data. The finite-
exposure bound stays conditional on unknown physical couplings and residuals.
--write emits the deterministic receipt only after final hash-bound reviews.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path

import sympy as s

ROOT = Path(__file__).resolve().parents[2]
BASE = "strategy/pa-hyp/PAH-OBS-002-"
ADMISSION = BASE + "admission-v1.json"
ASSESSMENT = BASE + "assessment-v1.json"
EXTENSION = BASE + "extension-review-v0.2.json"
REVIEW = BASE + "review-v1.json"
SCRIPT = "verification/scripts/pah_obs002_audit.py"
OUTPUT = "claims/C6-SPACETIME-SIGNATURE/runs/2026-10-14-pah-obs002/audit.json"


def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def zero(value):
    if isinstance(value, s.MatrixBase):
        assert all(s.simplify(x) == 0 for x in value)
    else:
        assert s.simplify(value) == 0, value


def algebra_controls():
    controls = []
    tau, phi, kxa, C, m = s.symbols("tau phi kxa C m", real=True)
    hb, omega, Delta = s.symbols("hbar omega Delta", positive=True)
    theta = omega * tau - phi
    lam = m * omega * tau - C * s.cos(theta + kxa / 2) / (hb * omega)
    onsite = -m * Delta - C * s.sin(theta + kxa / 2)
    transformed = s.simplify(onsite + hb * s.diff(lam, tau))
    zero(transformed - m * (hb * omega - Delta))
    zero(transformed.subs(Delta, hb * omega))
    assert s.simplify(onsite - hb * s.diff(lam, tau)) != 0
    controls.append("rotating_diagonal_cancellation_and_sign")

    # Generic Fourier index: constant harmonic requires r+1-1=0 or r-1-1=0.
    # This is not a truncation of an evolving system or a Bessel series.
    r = s.symbols("r", integer=True)
    modes = [s.solve(r + power - 1, r)[0] for power in (1, -1)]
    assert modes == [0, 2]  # Independent Fourier-index oracle.
    z = s.symbols("z", nonzero=True)
    A, py, px, pxp, j0, j2 = s.symbols("A py px pxp j0 j2", real=True)
    trig = px * (z + 1/z) / 2 - pxp * (z - 1/z) / (2*s.I)
    raw = s.expand(trig * (j0 + j2*z**2) / z)
    avg = raw.coeff(z, 0)
    expected = (px*(j0+j2) + s.I*pxp*(j0-j2))/2
    zero(avg - expected)
    zero(A*py*s.exp(-s.I*phi)*avg - A*py*s.exp(-s.I*phi)*expected)
    assert s.simplify(avg - (px*(j0+j2)-s.I*pxp*(j0-j2))/2) != 0
    controls.append("resonant_constant_harmonics_half_factor_imaginary_sign")
    kya = s.symbols("kya", real=True)
    angle = theta+kxa/2
    # Re-derive the y rotating-phase argument from Lambda(n+1)-Lambda(n).
    y_phase=C*(s.cos(angle-kya)-s.cos(angle))/(hb*omega)
    gamma_y=2*C*s.sin(kya/2)/(hb*omega)
    zero(s.trigsimp(s.expand_trig(y_phase-gamma_y*s.sin(angle-kya/2))))
    gamma_x=2*C*s.sin(kxa/2)/(hb*omega)
    assert s.simplify(gamma_y-gamma_x) != 0
    assert s.solve(r, r) == [0]
    controls.append("y_rotating_argument_and_zero_harmonic_selection")
    x = s.symbols("x", real=True)
    j0s = s.besselj(0, x).series(x, 0, 5).removeO()
    j2s = s.besselj(2, x).series(x, 0, 5).removeO()
    j1s = s.besselj(1, x).series(x, 0, 6).removeO()
    zero(s.expand((j0s+j2s)/2 - j1s/x))
    zero(s.expand((j0s-j2s)/2 - s.diff(j1s,x)))
    assert ((j0s+j2s)/2).subs(x, 0) == s.Rational(1, 2)
    controls.append("small_drive_bessel_limit_no_division_at_zero")

    n, phix, phiy = s.symbols("n phix phiy", real=True)
    phase = m*phix+n*phiy
    loop = s.exp(-s.I*phase)*s.exp(s.I*(phase+phiy))
    zero(loop - s.exp(s.I*phiy))
    zero(s.conjugate(loop) - s.exp(-s.I*phiy))
    assert s.im(s.exp(s.I*phiy)).subs(phiy, s.pi/2) == 1
    assert s.im(s.exp(-s.I*phiy)).subs(phiy, s.pi/2) == -1
    controls.append("source_loop_orientation_and_noncosine_sign_control")
    u, gv, gw = s.symbols("u gv gw", real=True)
    J = s.symbols("J", real=True)
    U = s.exp(s.I*u)
    H = -J*s.Matrix([[0, s.conjugate(U)], [U, 0]])
    D = s.diag(s.exp(s.I*gv), s.exp(s.I*gw))
    zero(H.subs(u, u+gw-gv) - D*H*D.conjugate().T)
    zero(H-H.conjugate().T)
    controls.append("conditional_directed_probe_gauge_covariance")
    jr, ji = s.symbols("jr ji", real=True)
    jc = jr+s.I*ji
    full=-s.Matrix([[0,s.conjugate(jc*U)],[jc*U,0]])
    zero(full-full.conjugate().T)
    zero(full.subs(u,u+gw-gv)-D*full*D.conjugate().T)
    wrong=-jc*s.Matrix([[0,s.conjugate(U)],[U,0]])
    assert s.simplify(wrong[0,1]-s.conjugate(wrong[1,0])) != 0
    controls.append("complex_control_requires_full_reverse_conjugation")

    # Coherent probe need not be a CTMC; this tests only the naive direct import.
    kappa, c, speed = s.symbols("kappa c speed", positive=True)
    coherent = s.sin(kappa*tau/hb)**2
    jump = (1-s.exp(-2*c*speed*tau))/2
    assert s.diff(coherent,tau).subs(tau,0) == 0
    zero(s.diff(jump,tau).subs(tau,0)-c*speed)
    zero(s.diff(coherent,tau,2).subs(tau,0)-2*kappa**2/hb**2)
    controls.append("coherent_hopping_is_not_direct_markov_hazard")

    sx=s.Matrix([[0,1],[1,0]])
    sz=s.diag(1,-1)
    eye=s.eye(2)
    dt=s.symbols("dt", real=True)
    # Two equal-duration pulses vs an average with the same integrated H.
    ordered=(eye-s.I*sz*dt-sz**2*dt**2/2)*(eye-s.I*sx*dt-sx**2*dt**2/2)
    averaged=eye-s.I*(sx+sz)*dt-(sx+sz)**2*dt**2/2
    second=(ordered-averaged).applyfunc(lambda e:s.expand(e).coeff(dt,2))
    zero(second-(sx*sz-sz*sx)/2)
    assert second != s.zeros(2)
    controls.append("period_average_not_exact_time_ordered_propagator")

    # One edge's Hermitian difference has norm |J| |delta U|, not twice it.
    aa, bb = s.symbols("aa bb", real=True)
    edge=-J*s.Matrix([[0,aa-s.I*bb],[aa+s.I*bb,0]])
    zero(edge.conjugate().T*edge-J**2*(aa**2+bb**2)*eye)
    dc=aa+s.I*bb
    edgec=-s.Matrix([[0,s.conjugate(jc*dc)],[jc*dc,0]])
    zero(edgec.conjugate().T*edgec-(jr**2+ji**2)*(aa**2+bb**2)*eye)
    controls.append("conditional_exposure_edge_norm_factor")

    # These are symbolic response-kernel inputs, not data or a physical PAH map.
    a0, a1, U0, U1, v, bias = s.symbols("a0 a1 U0 U1 v bias", real=True)
    encoded=(1+bias+v*s.cos(a0))/2
    assert s.diff(encoded,U0) == 0
    assert s.diff(encoded,U1) == 0
    naive_correlation=encoded.subs(a0,U0)
    assert s.diff(naive_correlation,U0) != 0
    # A nonzero correlation after encoding is not fixed-controls sensitivity.
    signal1=(1+bias+v*U1)/2
    signal0=(1+bias+v*U0)/2
    zero(signal1-signal0-v*(U1-U0)/2)
    controls.append("encoder_correlation_not_background_causal_response")
    return controls


def firewall(a, e):
    assert a["verdict"] == "HOLD_FOR_EVIDENCE"
    assert a["classification"] == "auxiliary_support"
    assert a["new_result_id"] is None
    for key in ("claim_bearing","active_gate_change","physical_promotion"):
        assert a[key] is False
    assert a["missing_input"]["status"] == "NOT_SUPPLIED"
    assert a["follow_on"]["attempts_remaining"] == 0
    assert a["follow_on"]["automatic_successor"] is False
    assert e["status"] == "REVIEWED_NOT_ADMITTED"
    assert e["adopted"] is False
    assert e["parent_model_changed"] is False
    assert e["proposed_identification"]["status"] == "NOT_JUSTIFIED"
    assert all(x is None for x in e["unfilled_inputs"].values())


def mutation_controls(a,e):
    rejected=[]
    cases=[("verdict","ADMISSIBLE_FOR_TEST"),("classification","mainline_advance"),
           ("new_result_id","FORBIDDEN"),("claim_bearing",True),
           ("active_gate_change",True),("physical_promotion",True)]
    for key,value in cases:
        bad=copy.deepcopy(a)
        bad[key]=value
        try:
            firewall(bad,e)
        except AssertionError:
            rejected.append(key)
        else:
            raise AssertionError("undetected metadata mutation: "+key)
    for key in ("adopted","parent_model_changed"):
        bad=copy.deepcopy(e)
        bad[key]=True
        try:
            firewall(a,bad)
        except AssertionError:
            rejected.append(key)
        else:
            raise AssertionError("undetected extension mutation: "+key)
    for key in e["unfilled_inputs"]:
        bad=copy.deepcopy(e)
        bad["unfilled_inputs"][key]="ASSUMED_TO_PASS"
        try:
            firewall(a,bad)
        except AssertionError:
            rejected.append("invented_"+key)
        else:
            raise AssertionError("invented physical input accepted: "+key)
    return rejected


def audit(with_review=True):
    if not __debug__:
        raise RuntimeError("Assertions must be enabled")
    pre,a,e=read(ADMISSION),read(ASSESSMENT),read(EXTENSION)
    firewall(a,e)
    assert a["admission"]["sha256"] == sha(ADMISSION)
    assert pre["attempt_budget"] == 1  # Tooling attempt budget.
    assert {r["id"] for r in a["source_crosswalk"]} == set(pre["required_fields"])
    assert a["extension"] == EXTENSION
    for path,expected in pre["source_pins"].items():
        assert sha(path) == expected, path
    assert sha(e["parent"]) == e["parent_sha256"]
    assert sha(e["predecessor"]["path"]) == e["predecessor"]["sha256"]
    artifacts=(ADMISSION,ASSESSMENT,EXTENSION,SCRIPT)
    if with_review:
        review=read(REVIEW)
        for path in artifacts:
            assert review["artifact_hashes"][path] == sha(path), path
        assert {r["role"] for r in review["reviews"]} == {"independent","hostile"}
        assert all(r["verdict"] == "ACCEPT_SCOPED_AUDIT" for r in review["reviews"])
        artifacts+=(REVIEW,)
    return {"schema":"tect/pah-physical-coupling-replay/1.0",
            "status":"PASS_PROVENANCE_AND_CONDITIONAL_ALGEBRA_ONLY",
            "scientific_verdict":a["verdict"],
            "source_hashes":pre["source_pins"],
            "artifact_hashes":{path:sha(path) for path in artifacts},
            "algebra_controls":algebra_controls(),
            "metadata_mutations_rejected":mutation_controls(a,e),
            "external_source_expected_sha256":pre["external_source"]["sha256"],
            "boundary":"Source applicability reviewed separately. No physical PAH carrier, clock map, rate realization, measured error, new PAH dynamics, general no-go or Lean theorem verified."}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group()
    group.add_argument("--write",action="store_true")
    group.add_argument("--check",action="store_true")
    group.add_argument("--selftest",action="store_true")
    parser.add_argument("--source-cache",type=Path)
    args=parser.parse_args()
    result=audit(with_review=not args.selftest)
    if args.source_cache:
        data=(args.source_cache/"1308.1431v3.pdf").read_bytes()
        assert data.startswith(b"%PDF")
        assert hashlib.sha256(data).hexdigest() == result["external_source_expected_sha256"]
        print("OBS-002 PRIMARY PDF BYTES: PASS")
    if args.write:
        out=ROOT/OUTPUT
        out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8",newline="\n")
    elif not args.selftest:
        assert read(OUTPUT) == result, "deterministic receipt drift"
    print("OBS-002 AUDIT: PASS (scope/hash/conditional algebra only);",
          len(result["algebra_controls"]),"algebra controls;",
          len(result["metadata_mutations_rejected"]),"metadata controls;",
          result["scientific_verdict"])


if __name__ == "__main__":
    main()
