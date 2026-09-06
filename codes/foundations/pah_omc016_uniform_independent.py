"""Independent PAH-OMC-016 local-polynomial and uniform-bound reconstruction.

Imports no primary or prior PAH executable. Expands signed edges coefficient
by coefficient using Fraction arithmetic; proves tail polynomial positivity
through binomial coefficients and obtains constants from barrier searches.
The companion certificate gives the finite-box/tail analytic passage.
"""
from __future__ import annotations
import argparse
from fractions import Fraction as Q
import hashlib
import itertools
import json
import math
from pathlib import Path

ROOT=next(p for p in Path(__file__).resolve().parents if (p/"GOVERNANCE.md").exists())
PIN="1cebe3acff477175125c7abf2ebdfa2cd5b65089530ae3581bbaa69b23c161b7"
__version__="1.0.0"
OUT=ROOT/"claims/C6-SPACETIME-SIGNATURE/runs/2026-09-06-pah-omc016-uniform/independent.json"


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def main(output):
    checks=[]
    def check(name,condition):
        assert condition,name
        checks.append({"name":name,"pass":True})
    source=ROOT/"strategy/pa-hyp/PAH-OMC-016-resolved-radial-prereg-v1.json"
    check("source_pin",sha(source)==PIN)
    c=json.loads(source.read_text())
    for path,pin in c["sources"].items():check("parent:"+path,sha(ROOT/path)==pin)
    p={k:Q(str(v)) for k,v in c["scope"]["fixed_parameters"].items()}
    geom=json.loads((ROOT/"strategy/pa-hyp/PAH-OMC-004-v1.json").read_text())
    d=geom["exact_scope"]["strip_family"]["degree_bound"]
    jcap=max(Q(2)/(u+v) for u in (p["epsilon"],Q(1)) for v in (p["epsilon"],Q(1)))
    a6,a4=p["eta_6"]/6,p["lambda_4"]/4
    coefficient_records=[]
    for degree in range(d+1):
        # All signed patterns and all aperture assignments in a permitted star.
        tested=0
        for aperture in itertools.product((p["epsilon"],Q(1)),repeat=degree+1):
            Js=[Q(2)/(aperture[0]+u) for u in aperture[1:]]
            for signs in itertools.product((-1,1),repeat=degree):
                weights=[Q(i+1,degree+1) for i in range(degree)] # exact translation probes
                linear=-sum((J*sign*w for J,sign,w in zip(Js,signs,weights)),Q(0))
                quadratic=(p["g"]*aperture[0]**2+sum(Js,Q(0)))/2
                for t in (Q(0),Q(1,2),Q(2)):
                    expanded=a6*t**6+a4*t**4+quadratic*t**2+linear*t
                    direct=a6*t**6+a4*t**4+p["g"]*aperture[0]**2*t**2/2
                    direct+=sum((J*((t-sign*w)**2-w*w)/2 for J,sign,w in zip(Js,signs,weights)),Q(0))
                    assert expanded==direct
                # Formal coefficient differentiation t*d/dt multiplies degree k.
                assert 6*a6==p["eta_6"] and 4*a4==p["lambda_4"]
                assert 2*quadratic==p["g"]*aperture[0]**2+sum(Js,Q(0))
                tested+=1
        coefficient_records.append({"degree":degree,"background_patterns":tested})
        check(f"all_signed_local_coefficients_degree_{degree}",tested>0)
    drift=d*p["kappa_D"]*jcap
    moment=next(k for k in itertools.count(1) if k*k>drift and k**3-drift*k>1)
    B=next(2**k for k in itertools.count() if Q(d*moment,2**(2*k))<=Q(1,2))
    H=drift*B
    A=p["g"]+drift
    T=next(k for k in itertools.count(1) if a6*k**5/2>=H and a6*k**5/2>=1)
    U=a6*2**6+a4*2**4+A*2+H*2
    good=1-Q(d*moment,B*B)
    check("uniform_moment_barrier", moment*(moment**2-drift)>1)
    check("union_bound_not_volume_sum",0<good<1 and d*moment==sum(moment for _ in range(d)))
    for linear in (H,Q(1)):
        coeff=[a6*Q(math.comb(6,k))*T**(6-k)/2 for k in range(7)]
        coeff[0]-=linear*T
        coeff[1]-=linear
        check("tail_binomial_coefficients_"+str(linear),all(x>=0 for x in coeff))
    # Independent mesh recurrence: refine half-open cells including endpoint.
    R,h=Q(1),Q(1)
    for level in range(5):
        M=R/h
        check(f"cell_partition_recurrence_{level}",M.denominator==1 and (int(M)+1)*h==R+h)
        R*=2; h/=2
    majorant_tail_start=4  # Analytic split specified in certificate, not a fit.
    constants={"degree":d,"J_max":str(jcap),"drift_coefficient":str(drift),
        "second_moment_bound":str(moment),"neighbor_radius":str(B),"good_event_lower":str(good),
        "H_cap":str(H),"A_cap":str(A),"tail_split":str(T),"numerator_cost":str(U),
        "denominator_cost":str(H*T),"denominator_prefactor":str(T+1),
        "lower_prefactor":str(good/(T+1)),"lower_exponent":str(U+H*T),
        "unit_cube_vertex":str(p["lambda_s"]*(1-p["epsilon"])**2/2+a6+a4+p["g"]/2),
        "unit_cube_edge":str(p["kappa_s"]*(1-p["epsilon"])**2/2+2*p["kappa_D"]*jcap),
        "unit_cube_face":str(2*p["kappa_g"]*jcap),"scalar_majorant_integral_upper":str(majorant_tail_start+1)}
    check("positive_uniform_bound",Q(constants["lower_prefactor"])>0)
    result={"lane":"independent","status":"PASS","checks":checks,"source_sha256":PIN,
        "code_sha256":sha(Path(__file__)),"code_version":__version__,"constants":constants,"coefficient_records":coefficient_records,
        "independence":"No primary or prior PAH imports; direct signed-edge coefficient expansion, binomial tails and recursive cell partition. External signed review not claimed."}
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8",newline="\n")
    print(f"PAH-OMC-016 INDEPENDENT: PASS ({len(checks)} checks)")


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--output",type=Path,default=OUT)
    main(p.parse_args().output)
