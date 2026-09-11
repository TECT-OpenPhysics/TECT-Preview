#!/usr/bin/env python3
"""Exact coordinate/energy comparison of two UNADOPTED v2 cutoff proposals.

Uses the pinned coordinate enumerator, not an old comparison implementation.
The only numerical fixture is the issued R-570 triangle. Fraction arithmetic
and Gaussian rational pairs evaluate the unchanged functional exactly.
Rates are stored as positive rational coefficient times exp(rational), never
floated or fitted. No full fine Gibbs sum, semigroup or limit is computed.
"""
import argparse
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
PREREG = ROOT / "strategy/pa-hyp/PAH-v2-charge-AB-prereg.json"
PREREG_HASH = "33fe50af87c588715b18fed5415cdad5dc5b17f0b9c3d3a25edd6e2874c06457"  # INPUT, preregistered bytes.
OUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-11-pah-v2-charge-ab/primary.json"
sys.path.insert(0, str(ROOT / "codes/foundations"))
import pah_v2_root_enumerator as enum


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cmul(a, b):
    return (a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0])


def csub(a, b):
    return (a[0]-b[0], a[1]-b[1])


def cconj(a):
    return (a[0], -a[1])


def norm2(a):
    return a[0]*a[0]+a[1]*a[1]


def root(n, k):
    assert (4*n) % k == 0, "fixture must use exact Gaussian roots"
    return ((F(1),F(0)),(F(0),F(1)),(F(-1),F(0)),(F(0),F(-1)))[(4*n//k)%4]


def fields(reg, x, epsilon, rmax):
    ap = [epsilon + F(v, reg.M_s)*(1-epsilon) for v in x.aperture]
    matter = [tuple(rmax*F(l,reg.M_psi)*z for z in root(n,reg.K)) for l,n in zip(x.occupation,x.phase)]
    links = [root(u,reg.K) for u in x.link]
    return ap, matter, links


def energy(reg, x, epsilon, rmax, inp):
    ap, matter, links = fields(reg,x,epsilon,rmax)
    p = {k:F(inp[k]) for k in ("lambda_s","m2","lambda_4","eta_6","g","kappa_s","kappa_D","kappa_g")}
    value = F(0)
    for s,z in zip(ap,matter):
        r2=norm2(z)
        value += p["lambda_s"]*(s-1)**2/2 + p["m2"]*r2/2 + p["lambda_4"]*r2**2/4 + p["eta_6"]*r2**3/6 + p["g"]*s*s*r2/2
    stiffness=[]
    for idx,(v,w) in enumerate(reg.edges):
        je=2/(ap[v]+ap[w]); stiffness.append(je)
        value += p["kappa_s"]*(ap[v]-ap[w])**2/2
        value += p["kappa_D"]*je*norm2(csub(matter[w],cmul(links[idx],matter[v])))/2
    for face in inp["faces"]:
        hol=(F(1),F(0))
        for edge,sign in face:
            hol=cmul(hol,links[edge] if sign==1 else cconj(links[edge]))
        jp=sum(stiffness[e] for e,_ in face)/len(face)
        value += p["kappa_g"]*jp*(1-hol[0])
    return value


def inject(x, branch):
    return enum.State(tuple(2*v for v in x.aperture),
                      tuple((2 if branch=="B" else 1)*v for v in x.occupation),
                      tuple(2*v for v in x.phase),tuple(2*v for v in x.link))


def requested_steps(family, branch):
    return 1 if family=="TR" and branch=="A" else 2


def run():
    assert sha(PREREG)==PREREG_HASH
    spec=json.loads(PREREG.read_text(encoding="utf-8"))
    for path,h in spec["source_pins"].items():
        assert sha(ROOT/path)==h,path
    audit=json.loads((ROOT/"strategy/pa-hyp/PAH-v2-finite-audit-v1.json").read_text(encoding="utf-8"))
    inp=audit["primary_fixture_inputs"]
    assert F(inp["nu"])==2, "rational aperture-mobility fixture"
    co=enum.Regulator(inp["vertices"],tuple(tuple(e) for e in inp["edges"]),inp["K"],inp["M_s"],inp["M_psi"],inp["Q"])
    eps,r0=F(inp["epsilon"]),F(inp["R_max"])
    xs=tuple(enum.states(co)); report={}
    for branch in ("A","B"):
        fi=enum.Regulator(co.vertices,co.edges,2*co.K,2*co.M_s,4*co.M_psi,(2 if branch=="B" else 1)*co.Q)
        images=set(); root_counts={k:{"valid":0,"one_step_equal":0,"path_equal":0} for k in enum.FAMILIES}
        energy_matches=0
        for x in xs:
            z=inject(x,branch)
            assert enum.valid_state(fi,z)
            images.add(z)
            a0,p0,u0=fields(co,x,eps,r0)
            a1,p1,u1=fields(fi,z,eps,2*r0)
            assert a0==a1 and u0==u1
            ratio=F(1,2) if branch=="A" else F(1)
            assert p1==[tuple(ratio*t for t in p) for p in p0]
            # The displayed value does not erase any coordinate label.
            assert z.phase==tuple(2*n for n in x.phase)
            assert z.aperture==tuple(2*j for j in x.aperture)
            e0,e1=energy(co,x,eps,r0,inp),energy(fi,z,eps,2*r0,inp)
            energy_matches += (e0==e1)
            if branch=="B": assert e0==e1
            for move,y in enum.incidences(co,x):
                expected=inject(y,branch); one=enum.apply_move(fi,z,move)
                assert one is not None
                row=root_counts[move.family];row["valid"]+=1
                row["one_step_equal"] += one==expected
                path=z
                for _ in range(requested_steps(move.family,branch)):
                    path=enum.apply_move(fi,path,move);assert path is not None
                assert path==expected
                row["path_equal"]+=1
        assert len(images)==len(xs)
        seed=enum.State((0,)*co.vertices,(co.Q,)+(0,)*(co.vertices-1),(0,)*co.vertices,(0,)*len(co.edges))
        z=inject(seed,branch)
        odd=lambda state:int(any(j%2 for j in state.aperture))
        assert all(odd(image)==0 for image in images)
        flux=[]
        for move,y in enum.incidences(fi,z):
            dh=odd(y)-odd(z)
            if dh:
                assert move.family=="AP" and dh==1 and y not in images
                s0=eps+F(z.aperture[move.cell],fi.M_s)*(1-eps)
                s1=eps+F(y.aperture[move.cell],fi.M_s)*(1-eps)
                coefficient=s0*s1  # nu=2, exactly the inherited AP mobility.
                exponent=-F(inp["beta"])*(energy(fi,y,eps,2*r0,inp)-energy(fi,z,eps,2*r0,inp))/2
                assert coefficient>0
                flux.append({"family":move.family,"cell":move.cell,"sign":move.sign,"coefficient":str(coefficient),"exponent":str(exponent)})
        assert flux
        report[branch]={"coarse_states":len(xs),"images_distinct":len(images),"fine_Q":fi.Q,
                        "displayed_total_coarse":str(r0*co.Q/co.M_psi),
                        "displayed_total_image":str(2*r0*fi.Q/fi.M_psi),
                        "image_energy_equal_states":energy_matches,"root_checks":root_counts,
                        "trace_witness": {"h":"indicator(any aperture index odd)","coarse_generator_of_trace":"0","fine_generator_at_image_terms":flux,"strictly_positive":True},
                        "seed_energy_coarse":str(energy(co,seed,eps,r0,inp)),"seed_energy_image":str(energy(fi,z,eps,2*r0,inp))}
        if branch=="A": assert energy_matches<len(xs)
        else:
            off=enum.State((0,)*fi.vertices,(1,fi.Q-1)+(0,)*(fi.vertices-2),(0,)*fi.vertices,(0,)*len(fi.edges))
            assert enum.valid_state(fi,off) and off not in images
            half=tuple(F(l,2) for l in off.occupation)
            assert any(l.denominator!=1 for l in half)
            report[branch]["odd_inverse_witness"]={"fine_occupation":off.occupation,"required_coarse_occupation":tuple(map(str,half)),"integer_state_inverse":False}
    # INPUT levels test the proposed formula only; no asymptotic inference.
    schedule=[]
    for j in range(4):
        ms=co.M_s*2**j;mp=co.M_psi*4**j;rm=r0*2**j;k=co.K*2**j
        qa=co.Q;qb=co.Q*2**j
        assert qa<=co.vertices*mp and qb<=co.vertices*mp
        schedule.append({"j":j,"K":k,"M_s":ms,"M_psi":mp,"R_max":str(rm),"A_Q":qa,"B_Q":qb,"A_total":str(rm*qa/mp),"B_total":str(rm*qb/mp)})
    return {"schema":"tect/pah-v2-charge-ab-primary/1.0","status":"PASS_SCOPED_COMPARISON_CHECKS", "prereg_sha256":sha(PREREG),"script_sha256":sha(Path(__file__)),"source_pins":spec["source_pins"],"branches":report,"schedule_fixture":schedule,
            "non_claims":"Neither branch adopted; no full p/I, full fine Gibbs sum, eventual intertwining, weak limit, physical or external-person review claim."}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("--check",action="store_true");args=parser.parse_args()
    result=json.loads(json.dumps(run()))
    if args.check: assert json.loads(OUT.read_text(encoding="utf-8"))==result
    else:
        OUT.parent.mkdir(parents=True,exist_ok=True)
        with OUT.open("w",encoding="utf-8",newline="\n") as stream:json.dump(result,stream,indent=2,sort_keys=True);stream.write("\n")
    print("PAH-V2-CHARGE-AB PRIMARY: PASS (both proposals; exact fixture roots, energies and trace witnesses; neither adopted)")


if __name__=="__main__":main()
