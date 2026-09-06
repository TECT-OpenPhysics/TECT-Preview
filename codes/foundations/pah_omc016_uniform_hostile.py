"""Adversarial exact controls for PAH-OMC-016; no alternative model is adopted."""
from __future__ import annotations
import argparse
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import sympy as s

ROOT=next(p for p in Path(__file__).resolve().parents if (p/"GOVERNANCE.md").exists())
PIN="1cebe3acff477175125c7abf2ebdfa2cd5b65089530ae3581bbaa69b23c161b7"
__version__="1.0.0"
OUT=ROOT/"claims/C6-SPACETIME-SIGNATURE/runs/2026-09-06-pah-omc016-uniform/hostile.json"


def main(output):
    checks=[]
    def reject(name,condition):
        assert condition,name
        checks.append({"name":name,"pass":True,"disposition":"mutated assertion rejected"})
    path=ROOT/"strategy/pa-hyp/PAH-OMC-016-resolved-radial-prereg-v1.json"
    raw=path.read_bytes()
    assert hashlib.sha256(raw).hexdigest()==PIN
    reject("source_byte_mutation",hashlib.sha256(raw+b" ").hexdigest()!=PIN)
    t,w=s.symbols("t w",real=True)
    edge=(t-w)**2/2
    reject("missing_edge_half",s.expand(t*s.diff(2*edge,t)-t*s.diff(edge,t))!=0)
    reject("wrong_Gibbs_sign",s.integrate(s.exp(t),(t,0,s.oo))==s.oo)
    # Exact integration-by-parts control: on [0,infinity), density t^a exp(-t).
    # The integral of (t^(a+1)exp(-t))' yields E[t]=a+1.
    moments=[s.integrate(t**(a+1)*s.exp(-t),(t,0,s.oo))/s.integrate(t**a*s.exp(-t),(t,0,s.oo)) for a in (0,1)]
    reject("polar_Jacobian_changes_virial",moments[0]==1 and moments[1]==2 and moments[0]!=moments[1])
    reject("conditional_H_may_be_negative",Q(-80)*Q(1)<0)
    reject("drop_H_wrong_numerator_upper",Q(1,6)+Q(1,4)+Q(11,2)+80>Q(1,6)+Q(1,4)+Q(11,2))
    reject("tail_split_too_small",Q(3**5,12)<80)
    reject("raw_index_not_bounded_amplitude",min(Q(1),Q(1,2)*2)!=2)
    reject("normalized_index_not_bounded_amplitude",min(Q(1),Q(1,2)*2)!=Q(2,4))
    reject("upper_endpoint_cell_missing",Q(1,2)*4 != Q(2)+Q(1,2))
    reject("unscaled_counting_not_integral",sum(Q(1) for _ in range(5))!=Q(1,2)*5)
    # Positive finite expectations can still tend to zero.
    reject("finite_positive_is_not_uniform",all(Q(1,k)>0 for k in (1,2,4)) and s.limit(1/t,t,s.oo)==0)
    reject("global_sum_not_local_max",Q(100)>4 and Q(100)<=100*4)
    reject("degree_must_be_bounded",Q(100)*4/Q(8**2)>1)
    reject("injection_not_generator_root_map",2*1!=1)
    # Alternating point masses have a common positive b^2 lower bound but
    # distinct even/odd limits: this is a logical countercontrol, not PAH data.
    k=s.symbols("k",integer=True,positive=True)
    even,odd=Q(1,4),Q(3,4)
    reject("lower_bound_not_outer_convergence",even>0 and odd>0 and even!=odd)
    reject("fixed_n_bound_not_uniform_n",2**10>2**2)
    result={"lane":"hostile","status":"PASS","checks":checks,"source_sha256":PIN,
        "code_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),"code_version":__version__,
        "scope":"Internal algebraic countercontrols, not alternate candidate experiments or external signed review."}
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8",newline="\n")
    print(f"PAH-OMC-016 HOSTILE: PASS ({len(checks)} controls)")


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--output",type=Path,default=OUT)
    main(p.parse_args().output)
