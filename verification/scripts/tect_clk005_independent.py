"""Independent TEST_ONLY Fraction normal-equation replay; no primary imports.

Preserved from the separately prompted reviewer; only the root locator and
this documentation were adapted for portable replay. Numeric asserted outputs
are clearly test oracles, not inputs or observed scientific constants.
"""
import json, hashlib
from fractions import Fraction as F
from pathlib import Path
p=Path(__file__).resolve().parents[2]/'strategy/clock/TECT-CLK-005-calibration-contract-v1.json'
assert hashlib.sha256(p.read_bytes()).hexdigest()=='da8cfda072cae9768b79f0302617fdbae3e8aefa35652a3a1638ad9f4ecc28a6'
d=json.loads(p.read_text(encoding='utf-8'))['test_only_inputs']
t,u,w=[list(map(F,d[k])) for k in ('t','u','weights')]
X=[[F(1),ti,ui] for ti,ui in zip(t,u)]
A=[[sum(wi*xi[j]*xi[k] for wi,xi in zip(w,X)) for k in range(3)] for j in range(3)]
def solve(A,b):
    m=[list(row)+[rhs] for row,rhs in zip(A,b)]
    n=len(b)
    for j in range(n):
        pivot=next(i for i in range(j,n) if m[i][j])
        m[j],m[pivot]=m[pivot],m[j]
        v=m[j][j];m[j]=[a/v for a in m[j]]
        for i in range(n):
            if i!=j:
                v=m[i][j];m[i]=[a-v*b for a,b in zip(m[i],m[j])]
    return [row[-1] for row in m]
def dot(a,b):return sum(x*y for x,y in zip(a,b))
a=solve(A,[F(0),F(0),F(1)])
ell=[wi*dot(xi,a) for wi,xi in zip(w,X)]
assert dot(ell,u)==1 and sum(ell)==0 and dot(ell,t)==0
nuisance=list(map(F,d['nuisance']))
gamma=F(d['gamma']); dist=list(map(F,d['template_distortion']))
v=[gamma*ui+nuisance[0]+nuisance[1]*ti+ei for ui,ti,ei in zip(u,t,dist)]
ge=dot(ell,v)
assert ge==gamma+dot(ell,dist)
def residual(y):
    c=solve(A,[sum(wi*xi[j]*yi for wi,xi,yi in zip(w,X,y)) for j in range(3)])
    return [yi-dot(xi,c) for xi,yi in zip(X,y)],c
base,bc=residual(v)
B=F(d['annual_bias'])
bias,xc=residual([yi+B*ui for yi,ui in zip(v,u)])
assert bias==base and xc[-1]-bc[-1]==B
nres,nc=residual([yi+nuisance[0]+nuisance[1]*ti for yi,ti in zip(v,t)])
assert nres==base and nc[-1]==bc[-1]
variances={'I':dot(ell,ell),'ones_outer':sum(ell)**2,'u_outer':dot(ell,u)**2}
assert len(set(variances.values()))==3
vals=list(map(F,d['standardized_error_values']));probs=list(map(F,d['standardized_error_probabilities']))
mean=dot(vals,probs); var=sum(p*(x-mean)**2 for x,p in zip(vals,probs));coverage=sum(p for x,p in zip(vals,probs) if abs(x)<=F(d['quoted_interval_multiple']))
assert sum(probs)==1 and mean==0 and var==1 and coverage==F(8,9)
print(json.dumps({'method':'independent Fraction Gauss-Jordan normal-equation solve, no SymPy or root verifier','A':A,'normal_inverse_last_column':a,'ell':ell,'ell_u':dot(ell,u),'ell_ones':sum(ell),'ell_t':dot(ell,t),'gamma_eff':ge,'nominal_gamma':gamma,'gamma_eff_minus_gamma':ge-gamma,'base_fit_coefficients':bc,'annual_bias_fit_coefficients':xc,'base_and_biased_residual':base,'coefficient_variances':variances,'pointwise_remainder_bound':sum(abs(li)*F(r) for li,r in zip(ell,d['remainder_caps'])),'discrete_error':{'mean':mean,'variance':var,'interval_coverage':coverage},'scope':'TEST_ONLY; not physical or observational evidence'},default=str,sort_keys=True,indent=2))
