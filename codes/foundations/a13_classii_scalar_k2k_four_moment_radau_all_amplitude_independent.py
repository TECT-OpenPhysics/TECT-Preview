#!/usr/bin/env python3
"""Independent exact-algebraic audit of the R-115 Radau skew condition.

The variable real power in the sufficient condition is removed analytically;
the remaining radical inequality is reduced to three rational polynomials and
certified by exact tensor Bernstein subdivision.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from math import comb
import os
from pathlib import Path
import tempfile

from flint import arb, ctx
import sympy as sp


VERSION = "1.0.0"
SCHEMA = "tect/a13-scalar-k2k-four-moment-radau-all-amplitude-independent/1.0"
REPO = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = REPO / "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/runs/2026-07-28-independent-scalar-k2k-four-moment-radau-all-amplitude/result.json"


b,c,T,U=sp.symbols("b c T U", positive=True)

# TEST_ORACLE closed forms.  They are not inputs to the certificate: the live
# moments are reconstructed below directly from the scalar packet definition.
mu2_oracle=sp.expand((
    16*b**2*c**2-16*b**2*c+8*b**2-12*b*c**3+20*b*c**2+4*b*c+4*b
    +30*c**4-30*c**3+15*c**2+1
)/32)
mu3_oracle=sp.expand((
    192*b**3*c**2-192*b**3*c+64*b**3+48*b**2*c**4-240*b**2*c**3
    +672*b**2*c**2-192*b**2*c+96*b**2+1404*b*c**5-1860*b*c**4
    +912*b*c**3+552*b*c**2-108*b*c+60*b+990*c**6+108*c**5-375*c**4
    +66*c**3+186*c**2-30*c+15
)/256)
mu4_oracle=sp.expand(
    b**4*sp.Rational(3,16)*(8*c**4-16*c**3+20*c**2-12*c+3)
    -b**3*sp.Rational(3,16)*(18*c**5-62*c**4+61*c**3-61*c**2+23*c-7)
    +b**2*sp.Rational(3,64)*(480*c**6-558*c**5+262*c**4+10*c**3+373*c**2-102*c+31)
    +b*sp.Rational(3,128)*(99*c**7+4041*c**6-4248*c**5+2068*c**4-107*c**3+543*c**2-128*c+36)
    +sp.Rational(3,512)*(12474*c**8-9486*c**7+9213*c**6-4788*c**5+1768*c**4-518*c**3+661*c**2-144*c+36)
)

# Packet reconstruction.  T,U are independent unit exponentials, rho=cT/2,
# sigma=(1-c)U/8, and the phase is uniform.  `phase_squared` is the square of
# the cosine amplitude.  Exact exponential expectations replace T^i U^j by
# i!j!, while E cos^(2j)=binomial(2j,j)/4^j.
rho=c*T/2
sigma=(1-c)*U/8
packet_center=sp.expand(
    b*(rho+4*sigma-sp.Rational(1,2))
    +rho**2+10*rho*sigma+4*sigma**2-rho-sigma
)
phase_squared=sp.expand(36*b*rho**2*sigma)


def exponential_expectation(expr):
    result=sp.S.Zero
    for (i,j),coefficient in sp.Poly(sp.expand(expr),T,U).terms():
        result += coefficient*sp.factorial(i)*sp.factorial(j)
    return sp.expand(result)


def reconstructed_moment(order):
    result=sp.S.Zero
    for twice_j in range(0,order+1,2):
        j=twice_j//2
        phase_moment=sp.binomial(2*j,j)/4**j
        result += (sp.binomial(order,twice_j)*phase_moment
                   *exponential_expectation(packet_center**(order-twice_j)*phase_squared**j))
    return sp.expand(result)


mu2=reconstructed_moment(2)
mu3=reconstructed_moment(3)
mu4=reconstructed_moment(4)
assert sp.Poly(mu2-mu2_oracle,b,c).is_zero
assert sp.Poly(mu3-mu3_oracle,b,c).is_zero
assert sp.Poly(mu4-mu4_oracle,b,c).is_zero

r=b/2
H=sp.expand(r*r*mu2+r*mu3-mu2*mu2)
NA=sp.expand(r*r*mu3-r*mu2*mu2+r*mu4-mu2*mu3)
NB=sp.expand(-r*r*mu2*mu2-r*mu2*mu3+mu2*mu4-mu3*mu3)
D=sp.expand(NA*NA-4*H*NB)
J=sp.expand(2*H*r+NA)
E=sp.expand(H*r*r+NA*r+NB)
C=sp.expand(mu2*H+NB)
W=sp.expand(E-C)
Z=sp.expand(2*H*r*E-W*J)

L=sp.expand(J-H*b/2)
M=sp.expand(100*W-E)
N=sp.expand(16*C-E)
R9=sp.expand(9*C*J+Z)
R0=sp.expand(3*C-E)
P_weight=sp.expand(Z**2-D*(E-3*C)**2)

structural_expressions={
    "H":H,
    "D":D,
    "J":J,
    "J2_minus_D":sp.expand(J**2-D),
    "E":E,
    "W":W,
    "minus_Z":sp.expand(-Z),
    "weight_product":sp.expand(D*W**2-Z**2),
    "nine_D_minus_J2":sp.expand(9*D-J**2),
    "v_side_L":L,
    "v_ge_b_over_4":sp.expand(L**2-D),
    "u_ge_b_over_2":sp.expand(4*D-H**2*b**2),
    "a_ge_1_over_6":sp.expand(6*C-E),
    "p_side_M":M,
    "p_ge_1_over_200":sp.expand(D*M**2-10000*Z**2),
    "q_side_N":N,
    "q_ge_15_over_32":sp.expand(256*Z**2-D*N**2),
    "k_ge_2":sp.expand(4*D-J**2),
    "k_le_6":sp.expand(9*J**2-16*D),
    "kq_le_9a_side":R9,
    "kq_le_9a":sp.expand(R9**2-D*(E+8*C)**2),
}
structural_polys={name:sp.Poly(expr,b,c,domain=sp.QQ) for name,expr in structural_expressions.items()}

# After substituting s^2=D into the cleared numerator of
#   T+k^3(q-p)/q+(k+1)^3(a-p)/q-(25/8)q/p,
# and reversing the known-negative original denominator, the numerator is
# A+B*s.  These formulas are a second derivation, independent of the Arb cover.
def radical_coefficients(CC,DD,JJ,EE,ZZ):
    AA=-(
        3*CC**2*DD**2*JJ+65*CC**2*DD*JJ**3+42*CC*DD**2*EE*JJ-210*CC*DD**2*ZZ
        -114*CC*DD*EE*JJ**3-246*CC*DD*JJ**2*ZZ-45*DD**2*EE**2*JJ+194*DD**2*EE*ZZ
        +49*DD*EE**2*JJ**3+198*DD*EE*JJ**2*ZZ+243*DD*JJ*ZZ**2+17*JJ**3*ZZ**2
    )
    BB=-(
        -CC**2*DD**2-3*CC**2*DD*JJ**2+18*CC*DD**2*EE+54*CC*DD*EE*JJ**2
        +54*CC*DD*JJ*ZZ+18*CC*JJ**3*ZZ-17*DD**2*EE**2-51*DD*EE**2*JJ**2
        -102*DD*EE*JJ*ZZ+111*DD*ZZ**2-34*EE*JJ**3*ZZ-51*JJ**2*ZZ**2
    )
    return AA,BB


# Direct abstract self-test: derive the rational expression afresh, reduce its
# numerator modulo s^2-D, and compare both coefficients with the transcription.
ss,DD,JJ,EE,CC,ZZ=sp.symbols("ss DD JJ EE CC ZZ")
WW=EE-CC
kk=2*ss/(JJ-ss)
aa=CC/EE
pp=(WW*ss+ZZ)/(2*EE*ss)
qq=(WW*ss-ZZ)/(2*EE*ss)
TT=(kk-1)*(kk+2)*(2*kk+1)
phi_abstract=TT+kk**3*(qq-pp)/qq+(kk+1)**3*(aa-pp)/qq-sp.Rational(25,8)*qq/pp
raw_numerator,raw_denominator=sp.together(phi_abstract).as_numer_denom()
remainder=sp.rem(sp.Poly(sp.expand(raw_numerator),ss),sp.Poly(ss**2-DD,ss)).as_expr()
A_template,B_template=radical_coefficients(CC,DD,JJ,EE,ZZ)
_constant_difference=sp.expand(sp.Poly(remainder,ss).coeff_monomial(1)-A_template)
_linear_difference=sp.expand(sp.Poly(remainder,ss).coeff_monomial(ss)-B_template)
assert _constant_difference==0
assert _linear_difference==0
assert sp.factor(raw_denominator-8*(JJ-ss)**3*(WW**2*ss**2-ZZ**2))==0

A,B=(sp.expand(value) for value in radical_coefficients(C,D,J,E,Z))

A_poly=sp.Poly(A,b,c,domain=sp.QQ)
minus_B_poly=sp.Poly(-B,b,c,domain=sp.QQ)
square_poly=A_poly*A_poly-sp.Poly(D,b,c,domain=sp.QQ)*sp.Poly(B,b,c,domain=sp.QQ)**2

x,y=sp.symbols("x y")
B0=sp.Rational(643,200)


def reciprocal_power(poly:sp.Poly)->sp.Poly:
    degree=poly.degree(b)
    expr=sp.cancel(x**degree*poly.as_expr().subs({b:B0/x,c:y}))
    return sp.Poly(expr,x,y,domain=sp.QQ)


def bernstein_table(poly:sp.Poly):
    power=reciprocal_power(poly)
    dx,dy=power.degree_list()
    coeff=[[sp.S.Zero]*(dy+1) for _ in range(dx+1)]
    for (i,j),value in power.terms():
        coeff[i][j]=value
    # Separable power-to-Bernstein transform, exact over QQ.
    first=[[sp.S.Zero]*(dy+1) for _ in range(dx+1)]
    for i in range(dx+1):
        for ell in range(dy+1):
            first[i][ell]=sum(coeff[k][ell]*sp.Rational(comb(i,k),comb(dx,k)) for k in range(i+1))
    out=[[sp.S.Zero]*(dy+1) for _ in range(dx+1)]
    for i in range(dx+1):
        for j in range(dy+1):
            out[i][j]=sum(first[i][ell]*sp.Rational(comb(j,ell),comb(dy,ell)) for ell in range(j+1))
    return out


def split_line(line):
    levels=[line]
    for _ in range(len(line)-1):
        levels.append([(a+b)/2 for a,b in zip(levels[-1],levels[-1][1:])])
    degree=len(line)-1
    return ([levels[k][0] for k in range(degree+1)],
            [levels[degree-k][k] for k in range(degree+1)])


def split_axis(table,axis):
    rows,cols=len(table),len(table[0])
    left=[[sp.S.Zero]*cols for _ in range(rows)]
    right=[[sp.S.Zero]*cols for _ in range(rows)]
    if axis==0:
        for j in range(cols):
            lo,hi=split_line([table[i][j] for i in range(rows)])
            for i in range(rows): left[i][j],right[i][j]=lo[i],hi[i]
    else:
        for i,row in enumerate(table): left[i],right[i]=split_line(row)
    return left,right


def cover(poly):
    root=bernstein_table(poly)
    stack=[(root,0,sp.Rational(0),sp.Rational(1),sp.Rational(0),sp.Rational(1))]
    leaves=[]
    while stack:
        table,depth,x0,x1,y0,y1=stack.pop()
        minimum=min(value for row in table for value in row)
        if minimum>=0:
            values=[value for row in table for value in row]
            positive_count=sum(1 if value>0 else 0 for value in values)
            zero_count=sum(1 if value==0 else 0 for value in values)
            negative_count=sum(1 if value<0 else 0 for value in values)
            assert positive_count+zero_count+negative_count==len(values)
            assert negative_count==0
            raw="\n".join(str(value) for row in table for value in row).encode("ascii")
            leaves.append({
                "depth":depth,"x_interval":[str(x0),str(x1)],"c_interval":[str(y0),str(y1)],
                "minimum":str(minimum),"coefficient_count":len(values),
                "positive_count":positive_count,"zero_count":zero_count,"negative_count":negative_count,
                "sha256":hashlib.sha256(raw).hexdigest(),
            })
            continue
        assert depth<20,(depth,x0,x1,y0,y1,minimum)
        axis=0 if depth%3==2 else 1
        lo,hi=split_axis(table,axis)
        if axis==0:
            mid=(x0+x1)/2
            stack.extend([(hi,depth+1,mid,x1,y0,y1),(lo,depth+1,x0,mid,y0,y1)])
        else:
            mid=(y0+y1)/2
            stack.extend([(hi,depth+1,x0,x1,mid,y1),(lo,depth+1,x0,x1,y0,mid)])
    return leaves


def joint_weight_cover():
    """Certify p<=a by the exact disjunction R0>=0 or P_weight>=0."""
    root_r=bernstein_table(sp.Poly(R0,b,c,domain=sp.QQ))
    root_p=bernstein_table(sp.Poly(P_weight,b,c,domain=sp.QQ))
    stack=[(root_r,root_p,0,sp.Rational(0),sp.Rational(1),sp.Rational(0),sp.Rational(1))]
    leaves=[]
    while stack:
        r_table,p_table,depth,x0,x1,y0,y1=stack.pop()
        r_min=min(value for row in r_table for value in row)
        p_min=min(value for row in p_table for value in row)
        if r_min>=0 or p_min>=0:
            certificate="R0" if r_min>=0 else "P_weight"
            chosen=r_table if r_min>=0 else p_table
            minimum=r_min if r_min>=0 else p_min
            values=[value for row in chosen for value in row]
            positive_count=sum(1 if value>0 else 0 for value in values)
            zero_count=sum(1 if value==0 else 0 for value in values)
            negative_count=sum(1 if value<0 else 0 for value in values)
            assert negative_count==0 and positive_count+zero_count==len(values)
            raw="\n".join(str(value) for value in values).encode("ascii")
            leaves.append({
                "certificate":certificate,"depth":depth,
                "x_interval":[str(x0),str(x1)],"c_interval":[str(y0),str(y1)],
                "minimum":str(minimum),"coefficient_count":len(values),
                "positive_count":positive_count,"zero_count":zero_count,"negative_count":negative_count,
                "sha256":hashlib.sha256(raw).hexdigest(),
            })
            continue
        assert depth<20,(depth,x0,x1,y0,y1,r_min,p_min)
        axis=0 if depth%3==2 else 1
        r_lo,r_hi=split_axis(r_table,axis)
        p_lo,p_hi=split_axis(p_table,axis)
        if axis==0:
            mid=(x0+x1)/2
            stack.extend([
                (r_hi,p_hi,depth+1,mid,x1,y0,y1),
                (r_lo,p_lo,depth+1,x0,mid,y0,y1),
            ])
        else:
            mid=(y0+y1)/2
            stack.extend([
                (r_hi,p_hi,depth+1,x0,x1,mid,y1),
                (r_lo,p_lo,depth+1,x0,x1,y0,mid),
            ])
    return leaves


def polynomial_hash(poly):
    raw="\n".join(f"{monomial}:{coefficient}" for monomial,coefficient in poly.terms()).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


def atomic_json(path,payload):
    path.parent.mkdir(parents=True,exist_ok=True)
    descriptor,temporary=tempfile.mkstemp(prefix=path.name+".",suffix=".tmp",dir=str(path.parent))
    try:
        with os.fdopen(descriptor,"w",encoding="utf-8",newline="\n") as handle:
            json.dump(payload,handle,indent=2,sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary,path)
    except BaseException:
        try: os.unlink(temporary)
        except FileNotFoundError: pass
        raise


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args=parser.parse_args()

    # Rigorous outward-rounded evaluation of the one universal calculus
    # constant.  For g(k)=(9/(k+1))^k/(k+1),
    # d(log g)/dk=log(9/(k+1))-1; hence the unique maximum is at 9/e-1.
    ctx.dps=80
    ee=arb(1).exp()
    assert ee.lower()>arb(9)/7 and ee.upper()<arb(3)  # puts 9/e-1 in (2,6)
    gstar=(arb(9)/ee).exp()/9
    assert gstar.lower()>arb(3)       # adverse oracle: the tempting bound 3 fails
    assert gstar.upper()<arb(25)/8    # certified safe rational upper bound

    structural_certificates={}
    for name,poly in structural_polys.items():
        print("building structural",name,poly.degree_list(),len(poly.terms()),flush=True)
        leaves=cover(poly)
        structural_certificates[name]={
            "leaves":leaves,"leaf_count":len(leaves),
            "max_depth":max(item["depth"] for item in leaves),
        }
        print("structural",name,"PASS",len(leaves),"leaves",flush=True)

    weight_order_leaves=joint_weight_cover()
    weight_order_certificate={
        "claim":"p<=a from R0=3C-E>=0 or P_weight=Z^2-D(E-3C)^2>=0, given Z<0",
        "leaves":weight_order_leaves,"leaf_count":len(weight_order_leaves),
        "max_depth":max(item["depth"] for item in weight_order_leaves),
    }
    print("structural p<=a PASS",len(weight_order_leaves),"leaves",flush=True)

    phi_certificates={}
    for name,poly in (("A",A_poly),("minus_B",minus_B_poly),("A2_minus_DB2",square_poly)):
        print("building",name,poly.degree_list(),len(poly.terms()),flush=True)
        leaves=cover(poly)
        phi_certificates[name]={"leaves":leaves,"leaf_count":len(leaves),"max_depth":max(item["depth"] for item in leaves)}
        print(name,"PASS",len(leaves),"leaves",phi_certificates[name]["max_depth"],flush=True)

    # Adversarial control: node/weight ordering alone is insufficient.  The
    # normalized gap law (a,q,p)=(1/10,89/100,1/100), k=1 has negative third
    # centered-moment numerator at tilt zero.
    bad_a,bad_q,bad_p=sp.Rational(1,10),sp.Rational(89,100),sp.Rational(1,100)
    bad_third=(bad_a*bad_q*(bad_a-bad_q)
               +8*bad_a*bad_p*(bad_a-bad_p)
               +bad_q*bad_p*(bad_q-bad_p))
    assert bad_a+bad_q+bad_p==1 and bad_p<bad_a and bad_p<bad_q
    assert bad_third==sp.Rational(-30879,500000)<0

    source_path=Path(__file__).resolve()
    payload={
        "schema":SCHEMA,
        "version":VERSION,
        "status":"PASS",
        "source":{"path":str(source_path),"sha256":hashlib.sha256(source_path.read_bytes()).hexdigest()},
        "domain":"b>=643/200, c in [0,1]",
        "coordinate":"x=(643/200)/b",
        "moment_reconstruction":{
            "algorithm":"factorial exponential moments plus exact even uniform-phase moments",
            "oracle_equalities":{"mu2":True,"mu3":True,"mu4":True},
            "degrees":{"mu2":sp.Poly(mu2,b,c).degree_list(),"mu3":sp.Poly(mu3,b,c).degree_list(),"mu4":sp.Poly(mu4,b,c).degree_list()},
            "hashes":{"mu2":polynomial_hash(sp.Poly(mu2,b,c)),"mu3":polynomial_hash(sp.Poly(mu3,b,c)),"mu4":polynomial_hash(sp.Poly(mu4,b,c))},
        },
        "calculus_bound":{
            "function":"g(k)=(9/(k+1))^k/(k+1)",
            "derivative":"d(log g)/dk=log(9/(k+1))-1",
            "maximizer":"k=9/e-1 in (2,6)",
            "arb_value":str(gstar),
            "unsafe_bound_3_rejected":True,
            "safe_bound":"25/8",
        },
        "abstract_identity_assertions":{
            "constant_radical_coefficient":True,
            "linear_radical_coefficient":True,
            "positive_denominator_formula":True,
        },
        "structural_implications":{
            "positive_denominator":"H,D,J,J^2-D,E,W,DW^2-Z^2 are positive",
            "positive_weights":"a>=1/6, p>=1/200, q>=15/32",
            "weight_order":"-Z>0 gives p<q; the joint cover gives p<=a",
            "node_geometry":"v>=b/4, u>=b/2, 2<=k=u/v<=6",
            "power_guard":"kq<=9a, hence h=kq/((k+1)a)<=9/(k+1)",
        },
        "structural_polynomial_degrees":{name:poly.degree_list() for name,poly in structural_polys.items()},
        "structural_polynomial_hashes":{name:polynomial_hash(poly) for name,poly in structural_polys.items()},
        "structural_certificates":structural_certificates,
        "weight_order_joint_certificate":weight_order_certificate,
        "polynomial_degrees":{"A":A_poly.degree_list(),"minus_B":minus_B_poly.degree_list(),"A2_minus_DB2":square_poly.degree_list()},
        "polynomial_hashes":{"A":polynomial_hash(A_poly),"minus_B":polynomial_hash(minus_B_poly),"A2_minus_DB2":polynomial_hash(square_poly)},
        "phi_certificates":phi_certificates,
        "adversarial_counterexample":{
            "purpose":"shows p<=min(a,q) and k>=1 alone do not force nonnegative skew",
            "a":"1/10","q":"89/100","p":"1/100","k":"1",
            "tilt_zero_third_numerator":str(bad_third),
        },
        "assertion_groups":{
            "moment_oracle_equalities":3,"abstract_radical_identity":3,
            "calculus_outward_bounds":3,"structural_polynomial_sign_tables":len(structural_polys),
            "joint_weight_cover":1,"phi_polynomial_sign_tables":3,"adversarial_controls":2,
        },
        "implication":"all Radau prerequisites hold; F<=25q/(8p); A>0, -B>0, A^2-D B^2>0 imply Phi_bar>0 and hence Phi>0",
    }
    output=Path(args.output).resolve()
    atomic_json(output,payload)
    print("R-115 algebraic Phi audit PASS ->",output,flush=True)


if __name__=="__main__":
    main()
