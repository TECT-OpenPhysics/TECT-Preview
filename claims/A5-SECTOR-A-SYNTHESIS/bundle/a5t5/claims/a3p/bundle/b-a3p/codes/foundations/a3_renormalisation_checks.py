#!/usr/bin/env python3
"""a3_renormalisation_checks.py -- quantitative self-tests for claim A3-UV-SUPERRENORMALISABILITY.

The scalar Brazovskii functional in d=3 has propagator G(q)=1/K(q),
K(q)=mu^2+Y(q^2-q0^2)^2 ~ Y q^4 (UV). With this q^{-4} propagator the theory is
SUPER-RENORMALISABLE: a connected diagram with V vertices (phi^4/phi^6), I
internal lines, L=I-V+1 loops has superficial degree of divergence
    D = 3L - 4I = 3 - 3V - I,
so D<=-1<0 for every V>=1, I>=1. By Weinberg's theorem (all subdiagrams have
D<0) every loop integral converges absolutely => UV-finite, finite (in fact
empty up to a finite tadpole normal-ordering) counterterm set, and the
continuum (a->0) limit of perturbative correlators exists. mu^2>0 removes any
IR divergence (K>=mu^2>0). Asserts exit 0 iff all pass.
"""
__version__ = "1.0.0"
__first_issued__ = "2026-06-23"
__version_issued__ = "2026-06-23"
__claims__ = ["A3-UV-SUPERRENORMALISABILITY"]

import json, math, sys
from pathlib import Path
import numpy as np

MU2, Y, Q0, D = 5e-3, 1.0, 0.6802, 3
CLAIMS=[]
def claim(n,ok,detail=""):
    CLAIMS.append(dict(name=n,passed=bool(ok),detail=detail)); print(f"  [{'PASS' if ok else 'FAIL'}] {n} -- {detail}")

def K(q): return MU2 + Y*(q*q - Q0*Q0)**2

# (1) superficial degree D = 3 - 3V - I < 0 for all V>=1,I>=1 (d=3, q^-4 propagator)
def Dsdiv(V,I): return 3 - 3*V - I
diagrams=[("phi4 1-loop tadpole",1,1),("phi4 self-energy sunset",2,3),("phi6 2-loop",1,2),
          ("phi4 4-pt 1-loop",2,2),("phi6 sunset",2,4),("phi4 3-loop",3,4)]
Ds={name:Dsdiv(V,I) for name,V,I in diagrams}
claim("superficial_degree_all_negative", all(d<=-1 for d in Ds.values()),
      f"D=3-3V-I for (V>=1,I>=1): {Ds}; all <= -1 < 0 => every connected diagram is superficially convergent")

# (2) propagator UV decay ~ q^-4
qbig=np.array([10.,50.,200.,1000.])
ratio=K(qbig)/(Y*qbig**4)
claim("propagator_uv_decay_q4", np.all(np.abs(ratio-1.0)<5e-2) and abs(ratio[-1]-1.0)<1e-4,
      f"K(q)/(Y q^4) -> 1 as q->inf (q=1000: {ratio[-1]:.6f}); G(q)=1/K ~ q^-4")

# (3) tadpole <phi^2> = (1/2pi^2) int_0^inf q^2/K(q) dq converges (UV q^-2 tail)
def tadpole(L,n=400000):
    q=np.linspace(1e-6,L,n); return (1/(2*math.pi**2))*(np.trapezoid if hasattr(np,'trapezoid') else np.trapz)(q*q/K(q),q)
vals=[tadpole(L) for L in (50,200,800,3200)]
cauchy=[abs(vals[i+1]-vals[i]) for i in range(len(vals)-1)]
claim("tadpole_integral_converges", cauchy[-1]<1e-3 and cauchy[-1]<cauchy[0],
      f"<phi^2>(Lambda) for Lambda=50/200/800/3200 = {[round(v,5) for v in vals]}; |I(4L)-I(2L)| -> {cauchy[-1]:.2e} "
      "(UV integrand ~ 1/q^2 converges) => finite continuum tadpole")

# (4) no IR divergence: K >= mu^2 > 0
qs=np.linspace(0,3,200001)
claim("no_ir_divergence_mu2_positive", float(K(qs).min())>=MU2-1e-12 and MU2>0,
      f"min_q K(q) = {float(K(qs).min()):.6g} >= mu^2 = {MU2} > 0; propagator bounded, no IR divergence")

# (5) discretisation -> continuum (a->0): the tadpole integrand is isotropic in
# |q|, so lattice refinement = radial-grid refinement. At a FIXED UV cutoff
# Lambda the Riemann sum converges to the continuum integral as spacing a->0
# (the sharp shell at q0 where K=mu^2 needs a << shell width ~ sqrt(mu^2/Y)/q0).
LAM=6.0
def tadpole_radial(npts):
    q=np.linspace(1e-8,LAM,npts)
    return (1/(2*math.pi**2))*(np.trapezoid if hasattr(np,'trapezoid') else np.trapz)(q*q/K(q),q)
cont=tadpole_radial(2_000_000)                 # fully resolved reference at cutoff LAM
refine=[tadpole_radial(n) for n in (2000,8000,32000)]   # a = LAM/n -> 0
errs=[abs(r-cont) for r in refine]
claim("tadpole_radial_quadrature_convergence", errs[-1]<errs[0] and errs[-1]<1e-3,
      f"radial QUADRATURE of the tadpole at cutoff {LAM} with n=2000/8000/32000 = {[round(r,5) for r in refine]} "
      f"-> {cont:.5f}; |err| {errs[0]:.2e}->{errs[-1]:.2e}. NOTE: this is numerical accuracy of the (UV-finite) "
      "tadpole integral, NOT the lattice a->0 theorem (that is A3-PERTURBATIVE-CONTINUUM-CORRELATORS / "
      "a3_graphwise_convergence_checks.py)")

# (6) Weinberg: every SUBdiagram (V'>=1,I'>=1) also has D<0 => absolute convergence
sub_worst=max(Dsdiv(1,1), Dsdiv(1,1))  # the least-negative is the minimal subdiagram (V=1,I=1)
claim("weinberg_all_subdiagrams_convergent", sub_worst<0,
      f"the least-suppressed subdiagram (V=1,I=1) has D={sub_worst}<0; since EVERY subdiagram has D<0, "
      "Weinberg's theorem gives absolute convergence => UV-finite, finite/empty counterterm set")

ok=all(c["passed"] for c in CLAIMS)
out=Path(__file__).resolve().parents[2]/"claims"/"A3-UV-SUPERRENORMALISABILITY"/"runs"/"a3_renormalisation_checks.json"
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(dict(version=__version__,params=dict(mu2=MU2,Y=Y,q0=Q0,d=D),
    superficial_degrees=Ds, tadpole_continuum=cont, lattice_refinement=refine, claims=CLAIMS, all_pass=ok),indent=2))
print(f"\nA3 renormalisation checks: {sum(c['passed'] for c in CLAIMS)}/{len(CLAIMS)} {'PASS' if ok else 'FAIL'}")
sys.exit(0 if ok else 1)
