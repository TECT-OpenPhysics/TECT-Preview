# Q3LOCK thermodynamic pressure: open boxes and periodic cubes

Status: T0 internal manuscript-content proof; independent signed review pending.  
Date: 2026-09-05. Owner: T-054.  
Research authority: EXP-000780 -> EXP-000781 -> EXP-000782.  
Finite-volume prerequisite: EXP-001588, using the EXP-001587 residual correction.  
PDF: deferred to final content review and organization.

## 1. Statement and scope

Use the physical Hamiltonian of EXP-000782 equation (2.1), defined explicitly
in `q3lock-finite-volume-pressure-content-260905.md` Section 1. At fixed
beta>0, hbar,chi,c,g,lambda>0 and r in R, the proposed pressure limit is

    p_beta(h)=lim_(R growing) |R|^(-1)log Tr exp(-beta H_R^op(h))
            =lim_(L even -> infinity) L^(-3)log Tr exp(-beta H_L^per(h)).

R ranges over rectangles with positive even side lengths, each tending to
infinity independently. The open Hamiltonian retains only positive-direction
spatial bonds with both endpoints in R. The periodic Hamiltonian retains
the full positive-direction bond multiset, including L=2 multiplicities.
The onsite polynomial and source are identical in both models.

The limit is finite, even and convex in h; convergence is locally uniform
in (beta,h) on (0,infinity) x R. Set P_beta(h)=p_beta(h)/(8beta). At any
differentiability point of P_beta in h, finite-volume source derivatives
converge to P_beta'(h). No differentiability at h=0 is asserted for the
limit. The eventual cusp argument will use this distinction.

The proof below fills the actual-model hypotheses left explicit in the
earlier seam and Fekete audits. Its internal analytic status does not replace
external mathematical acceptance or establish the later phase/DLR theorem.

## 2. Common physical forms and a retained quartic bound

Write r_-=max(-r,0), J_i=h/sqrt(8), and

    Q_R=(g/8)sum_(y,i)q_(y,i)^4,
    b(h0)=8r_-^2/g+(3/2)(4/g)^(1/3)h0^(4/3).

For a scalar x, direct minimization gives

    (g/16)x^4-(r_-/2)x^2>=-r_-^2/g,
    (g/16)x^4-|J_i||x|>=-(3/4)(4/g)^(1/3)|J_i|^(4/3).

Retaining g x^4/8 and summing these two inequalities over coordinates proves

    H_R^op(h)>=Q_R-b(h0)|R|,  |h|<=h0.                    (2.1)

Here sum_i |h/sqrt(8)|^(4/3)=2|h|^(4/3). The kinetic form, Q3 locking term
and spatial differences are nonnegative. Thus (2.1) uses the physical onsite
r/2 coefficient, with no auxiliary harmonic term or extra 3c allocation.

All finite Hamiltonians on the same site set have common closed form domain
H^1(R^(8|R|)) intersect L^2((sum_y|q_y|^4)dq). Adding or removing finitely
many quadratic bonds preserves this domain, since |x|^2<=delta |x|^4+C_delta.
The polynomial upper and lower bounds make the corresponding form norms
equivalent. Smooth compactly supported functions form a core by cutoff and
mollification. This supplies the common domain needed below.

## 3. Explicit volume-uniform absolute pressure bounds

Choose any a>0 and set m=chi/hbar^2, omega=sqrt(a/m). For |h|<=h0 let C be
the corrected residual lower-bound constant of EXP-001587:

    C=16(|r-a|/2)^2/g+(3/4)h0^(4/3)(32/g)^(1/3).

For beta in [beta_-,beta_+] with beta_->0, set

    K_*=1/(beta_- a)+beta_+/(12m),
    C_J=4|r-a|K_*+24cK_*+(6g+24lambda)K_*^2.

The product harmonic reference has coordinate variance at most K_*.
Every open box has at most 3|R| spatial bond occurrences; periodic cubes
have exactly 3|R|. Centered Gaussian averaging of the corrected residual
therefore gives E_gamma R_(a,h)<=beta |R| C_J for either boundary condition.
The source average is zero. Jensen and residual coercivity, with the absolute
harmonic factor restored as in EXP-001588, yield

    -8log[2sinh(beta omega/2)]-beta C_J
       <= |R|^(-1)log Z_R(beta,h)
       <= -8log[2sinh(beta omega/2)]+beta C.                (3.1)

Both bounds hold for every finite box. In particular, if

    M=8 max_{beta in {beta_-,beta_+}} |log[2sinh(beta omega/2)]|
                                         +beta_+ max(C,C_J),

then the absolute value of every log-partition density is at most M on the
chosen rectangle of beta and source values. The endpoint maximum suffices
because log[2sinh(beta omega/2)] is increasing. Although the normalized
weighted-density bound depends exponentially on volume, its logarithm
divided by volume gives exactly the uniform bound (3.1).

## 4. Open-box pressure by an explicit rectangular tiling

For fixed beta,h put F(R)=log Z_R^op(beta,h). Cutting an open rectangle into
two rectangles deletes only nonnegative crossing spatial differences:

    H_R^op=H_(R1)^op tensor 1+1 tensor H_(R2)^op+B_12,
    B_12>=0.

The common form domain from Section 2 and min--max eigenvalue comparison
give Z_R^op<=Z_(R1)^op Z_(R2)^op, hence F(R)<=F(R1)+F(R2).
This is a trace comparison through ordered eigenvalues, not operator
monotonicity of the exponential. Tensor-product trace factorization is valid
because both finite factors have finite positive heat trace by EXP-001588.

Fix an even block B with sides b_i. Tile an even rectangle R with sides l_i
by floor(l_i/b_i) full intervals along each axis and one remainder interval
when nonzero. Remainders l_i mod b_i are even. The full blocks occupy
V_tile=prod_i b_i floor(l_i/b_i); the remaining rectangles occupy V_rem.
Their exact volume satisfies

    0<=V_rem/|R|=1-prod_i(1-(l_i mod b_i)/l_i)
                         <=sum_i (l_i mod b_i)/l_i ->0.

Subadditivity and (3.1) on each remainder rectangle imply

    F(R)/|R| <= (V_tile/|R|) F(B)/|B|+M V_rem/|R|.

Thus limsup_R F(R)/|R|<=F(B)/|B| for every B. Every finite normalized value
is at least inf_B F(B)/|B|, which is finite by (3.1). Hence

    p_beta^op(h)=inf_(B even rectangle) F(B)/|B|.           (4.1)

This proves the limit along arbitrary even rectangular exhaustion with all
three sides tending to infinity. No ground-state limit is needed.

## 5. Periodic seam and correction of a displayed coefficient

On a cube, write H_L^per=H_L^op+B_L. The seam contains 3L^2 spatial bonds
and, with eight components, 48L^2 scalar endpoint occurrences. A scalar
coordinate is incident to at most three seam occurrences. For eta>0,

    (c/2)(x-y)^2<=c(x^2+y^2),
    cx^2<=(eta g/24)x^4+6c^2/(eta g).

The latter constant follows by maximizing ct-(eta g/24)t^2 for t>=0.
Summing the endpoint budgets gives the correct bound

    0<=B_L<=eta Q_L+288c^2 L^2/(eta g).                    (5.1)

The factor is 48 times 6. Section 4 of
`q3lock-pressure-seam-minmax-independent-audit-260905.md` displays 48
instead of 288 once, although its following prose, later sections and script
use 288. The displayed 48 bound is false and is superseded by (5.1).
For L=2, c=g=eta=1 and all eight components equal to 2(-1)^(y1+y2+y3),
exact evaluation gives B_L=768 and Q_L=128. The incorrect right side is
128+48*4=320; the corrected bound is 128+288*4=1280.
The original EXP-000780 comparison and the existing R-498 verifier use the
correct larger constant; this correction targets the later prose only.

Use (2.1) to deduce, on the common physical form domain,

    H_L^op<=H_L^per<=(1+eta)H_L^op+D_L,
    D_L=eta b(h0)L^3+288c^2 L^2/(eta g).

Min--max therefore gives

    exp(-beta D_L) Z_L^op(beta(1+eta),h)
                              <=Z_L^per(beta,h)<=Z_L^op(beta,h).        (5.2)

## 6. Moving beta and equality of the two limits

Let f_L(beta,h)=L^(-3)log Z_L^op(beta,h). At fixed h this function is convex
in beta, since its second derivative is the energy variance divided by L^3.
Finite heat traces at every positive beta justify differentiation on compact
positive-beta intervals. At fixed beta it is convex in h by EXP-001588.

Fix a target compact set beta in [beta0,beta1], |h|<=H. Apply (3.1) on the
larger set [beta0/2,2beta1] x [-H-1,H+1], obtaining a volume-independent M.
For any convex function bounded in absolute value by M on an interval, its
slopes on points at distance at least delta from the interval boundary lie
between -2M/delta and 2M/delta, by the two endpoint secants.

If eta<=1/2, both beta and beta(1+eta) lie in [beta0,3beta1/2]. Their distance
from the enlarged interval boundary is at least beta0/2. Consequently

    |f_L(beta(1+eta),h)-f_L(beta,h)|
                                  <=(4M beta1/beta0)eta.                (6.1)

Combining (5.2)--(6.1), with eta=L^(-1/2), yields for even L>=4

    0<=f_L(beta,h)-L^(-3)log Z_L^per(beta,h)
      <=[4M beta1/beta0+beta1 b(H)+288 beta1 c^2/g] L^(-1/2).           (6.2)

Thus the periodic and open pressure limits agree, uniformly in the target
compact parameter set once open convergence is uniform there. It remains
to justify that uniformity rather than assume it.

## 7. Local uniformity and convergence of source derivatives

Apply the endpoint-secant bound separately to beta and h on the enlarged
rectangle in Section 6. For fixed h the beta slopes are bounded on the target
interval; for fixed beta the h slopes are bounded by 2M on [-H,H]. Comparing
two points one coordinate at a time proves a common Lipschitz bound for
f_R(beta,h) on the target rectangle. Pointwise limits from Section 4 inherit
that bound. A finite net then upgrades pointwise convergence to uniform
convergence there. Equation (6.2) does the same for periodic cubes.

The normalization P=p/(8beta) preserves local uniform convergence because
beta is bounded away from zero. Evenness and convexity in h pass to the
limit. At a differentiability point h of P_beta and any t>0, finite-volume
convexity gives

    [P_L(h)-P_L(h-t)]/t <= P_L'(h)
                                    <=[P_L(h+t)-P_L(h)]/t.

First let L tend to infinity, then t decrease to zero. Both endpoints tend
to P_beta'(h). Therefore P_L'(h)->P_beta'(h); in the periodic model the
finite derivative is E_(L,h) Q_0/8. This supplies the numerical normalization
needed by the later source-tangent DLR argument, without assuming
differentiability at the eventual cusp.

## 8. Source applicability and review boundary

The local model authority is EXP-000780, Sections 3--5 of
`pre-a-cp1-st8-q3lock-fixed-lattice-3d-quantum-pressure-ground-density-effective-reduction-route-split-certificate-260804.md`.
Its physical source family is restricted to J=hu as in EXP-000782. The
finite-volume normalization/Feynman--Kac input is the one crosswalked in
EXP-001588; the residual convention is corrected by EXP-001587. No scalar
KP pressure or phase theorem is used as a vector-model premise here.

| Previously explicit hypothesis | Supplied model-specific argument |
|---|---|
| common form domain | Section 2: physical quartic weighted form and quadratic bond relative bounds |
| linear-volume pressure bounds | Section 3: restored harmonic trace, corrected residual coercivity and Gaussian Jensen bound |
| subadditivity and even remainders | Section 4: positive crossing bonds and exact Cartesian tiling |
| unbounded seam control | Section 5: endpoint Young budgets with corrected coefficient 288 |
| moving-temperature equicontinuity | Section 6: bounded convex functions on an enlarged positive-beta interval |
| compact-source pressure and derivative passage | Section 7: separate convexity, finite net and ordered secant limits |

These are internal analytic dispositions; signed independent mathematical
and literature review is still absent. The next manuscript stages are the
DLR/source-tangent and FKG/FSS/operator/Griffiths composition, with matching
claim scope. No phase theorem is promoted by this pressure block.

## 9. Reproduction and adversarial checks

Run `python -X utf8 verification/scripts/q3lock_thermodynamic_pressure_audit.py`.
The script checks exact rational seam energies and budgets, an explicit
counterexample to the displayed 48 coefficient, even Cartesian remainders,
and crossing-bond energy identities. These are finite diagnostics for the
analytic proof; neither finite samples nor test counts prove an infinite limit.

* Factor: the 288 coefficient is derived from component count, endpoint count
  and the per-endpoint Young maximum; the bad 48 constant is a hostile oracle.
* Sign: positive crossing bonds make log Z subadditive and periodic pressure
  no greater than open pressure. Trace order uses eigenvalues.
* Source: the bound is for J=hu, with sum_i|J_i|^(4/3)=2|h|^(4/3).
* Domain: the seam inequality is relative to the actual physical H_op,
  not the allocated residual plus a second spatial diagonal.
* Limits: time mesh is removed first at fixed spatial volume; beta is bounded
  away from zero; even spatial sides then diverge. No beta=infinity claim.
* Local uniformity: beta and h convexity are used separately; joint convexity
  in the pair (beta,h) is not assumed.
* Review: external reviewers should attack the Gaussian linear-volume bound,
  tensor form comparison, remainder control and moving-beta estimate.

PDF, submission and remote upload remain deferred. No DLR multiplicity,
extremality, purity, KMS, ground-state gap, continuum or cosmological result
is supplied by this block.
