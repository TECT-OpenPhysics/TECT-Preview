"""Exact PAH-OMC-016 source-to-energy and nondegeneracy-bound audit.

The certificate proves the universal analytic assertions. This executable
differentiates the source local polynomial and derives all proof constants
from the immutable input parameters and the declared degree bound. Finite
regression samples are not a proof of a limit. No Gibbs weights are fitted.
"""
from __future__ import annotations
import argparse
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import sympy as s

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "GOVERNANCE.md").exists())
PREREG = "strategy/pa-hyp/PAH-OMC-016-resolved-radial-prereg-v1.json"
PIN = "1cebe3acff477175125c7abf2ebdfa2cd5b65089530ae3581bbaa69b23c161b7"
__version__ = "1.0.0"
OUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-06-pah-omc016-uniform/primary.json"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main(output):
    checks = []
    def check(name, ok):
        assert bool(ok), name
        checks.append({"name": name, "pass": True})
    check("prereg_hash", sha(ROOT/PREREG) == PIN)
    c = json.loads((ROOT/PREREG).read_text(encoding="utf-8"))
    for path, pin in c["sources"].items():
        check("source:"+path, sha(ROOT/path) == pin)
    p = {k: Q(str(v)) for k,v in c["scope"]["fixed_parameters"].items()}
    check("unit_positive_source_scope", all(p[k] == 1 for k in
        ("beta","nu","lambda_s","lambda_4","eta_6","g","kappa_s","kappa_D","kappa_g"))
        and p["m2"] == 0 and p["epsilon"] == Q(1,2) and p["K"] == 2 and p["M_s"] == 1)
    geometry = json.loads((ROOT/"strategy/pa-hyp/PAH-OMC-004-v1.json").read_text())["exact_scope"]["strip_family"]
    d = geometry["degree_bound"]
    check("incidence_degree_upper_bound", d >= 2+1+2)
    r,w,J,sv = s.symbols("r w J sv", real=True)
    onsite = p["eta_6"]*r**6/6+p["lambda_4"]*r**4/4+(p["m2"]+p["g"]*sv**2)*r**2/2
    virial = r*s.diff(onsite,r)
    check("onsite_virial_exact", s.expand(virial-(r**6+r**4+sv**2*r**2)) == 0)
    for sign in (-1,1):
        edge = p["kappa_D"]*J*(r-sign*w)**2/2
        check(f"signed_edge_derivative_{sign}", s.expand(r*s.diff(edge,r)-J*(r**2-sign*r*w)) == 0)
        check(f"conditional_edge_polynomial_{sign}", s.expand(edge-edge.subs(r,0)-(J*r**2/2-sign*J*w*r)) == 0)
    y = s.symbols("y", nonnegative=True)
    # Universal tail polynomial certificates: nonnegative coefficients on y>=0.
    majorant_tail_start = 4  # Auxiliary analytic split chosen in certificate.
    check("shifted_sextic_majorant_tail", all(a>=0 for a in s.Poly(((y+majorant_tail_start)-1)**6/6-(y+majorant_tail_start),y).all_coeffs()))

    jmax = Q(1)/p["epsilon"]
    drift = d*p["kappa_D"]*jmax
    m = 1
    while not (m*m>drift and m*(m*m-drift)>1):
        m += 1
    check("maximum_moment_barrier", m*m>drift and m*(m*m-drift)>1)
    radius = 1
    while Q(d*m,radius**2) > Q(1,2):
        radius *= 2
    good = 1-Q(d*m,radius**2)
    hcap = drift*radius
    acap = p["g"]+drift
    a6,a4 = p["eta_6"]/6,p["lambda_4"]/4
    split = 1
    while a6*Q(split**5,2) < max(hcap,1):
        split += 1
    # [1,2] is an auxiliary proof interval on which preregistered b^2=1.
    left,right = Q(1),Q(2)
    numerator_cost = a6*right**6+a4*right**4+acap*right**2/2+hcap*right
    denominator_cost = hcap*split
    denominator_pref = split+1
    exponent = numerator_cost+denominator_cost
    pref = good*(right-left)/denominator_pref
    check("neighbor_event_uniform_positive", 0<good<=1 and good>=Q(1,2))
    check("conditional_tail_absorbs_linear", a6*Q(split**5,2)>=hcap)
    check("conditional_tail_integrable", a6*Q(split**5,2)>=1)
    check("strict_lower_bound_parameters", pref>0 and exponent>0)
    check("conditional_tail_polynomial", all(a>=0 for a in s.Poly(a6*(y+split)**6/2-hcap*(y+split),y).all_coeffs()))
    check("conditional_tail_ge_t_polynomial", all(a>=0 for a in s.Poly(a6*(y+split)**6/2-(y+split),y).all_coeffs()))

    vertex = p["lambda_s"]*(1-p["epsilon"])**2/2+a6+a4+p["g"]/2
    edge = p["kappa_s"]*(1-p["epsilon"])**2/2+p["kappa_D"]*jmax*4/2
    face = p["kappa_g"]*jmax*2
    geometry_checks=[]
    for n in (2,3,5):  # Tooling incidence audit; all-n bound is in certificate.
        vs=[(i,k) for i in range(n+2) for k in range(2)]
        es=[((i,k),(i+1,k)) for i in range(n+1) for k in range(2)]
        es += [((i,0),(i,1)) for i in range(n+2)]
        es += [((i,0),(i+1,1)) for i in range(n)]
        max_degree=max(sum(v in e for e in es) for v in vs)
        check(f"strip_counts_degree_{n}", len(vs)==2*(n+2) and len(es)==4*n+4 and max_degree<=d)
        geometry_checks.append({"n":n,"vertices":len(vs),"edges":len(es),"faces":2*n+1,"max_degree":max_degree})
    # Endpoint-cell identity includes all ell=0,...,M, not just ell<M.
    for j in range(5):
        R,M=2**j,2**(2*j)
        h=Q(R,M)
        check(f"endpoint_cell_{j}", h*(M+1)==R+h and h<=1 and R>=1)
    constants={
        "degree":d,"J_max":str(jmax),"drift_coefficient":str(drift),
        "second_moment_bound":str(m),"neighbor_radius":str(radius),"good_event_lower":str(good),
        "H_cap":str(hcap),"A_cap":str(acap),"tail_split":str(split),
        "numerator_cost":str(numerator_cost),"denominator_cost":str(denominator_cost),
        "denominator_prefactor":str(denominator_pref),"lower_prefactor":str(pref),"lower_exponent":str(exponent),
        "unit_cube_vertex":str(vertex),"unit_cube_edge":str(edge),"unit_cube_face":str(face),
        "scalar_majorant_integral_upper":str(majorant_tail_start+1)
    }
    result={"lane":"primary","status":"PASS","checks":checks,"source_sha256":PIN,
        "code_sha256":sha(Path(__file__)),"code_version":__version__,"constants":constants,"geometry_checks":geometry_checks,
        "analytic_scope":"Certificate proves all j at fixed n and a common positive lower bound after that limit for every n. Diagnostics audit algebra, not limit extrapolation."}
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8",newline="\n")
    print(f"PAH-OMC-016 PRIMARY: PASS ({len(checks)} checks)")


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,default=OUT)
    main(parser.parse_args().output)
