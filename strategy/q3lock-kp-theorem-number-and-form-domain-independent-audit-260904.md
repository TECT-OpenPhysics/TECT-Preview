# Q3LOCK KP theorem-number and form-domain independent audit

**Status:** T0 independent source audit; P-04 source scope remains pending
final external sign-off  
**Date:** 2026-09-04  
**Owner task:** T-054  
**Authority:** EXP-000780 -> EXP-000781 -> EXP-000782 plus the audited
Kozitsky--Pasurek source  
**PDF:** deferred until content freeze and all independent audits are complete

## 1. Audit target

The previous crosswalk identified the general finite-volume and Euclidean-DLR
scope of Kozitsky--Pasurek (KP).  This note independently checks the theorem
locations and the hypotheses that the eventual Q3LOCK manuscript may cite.
It is deliberately narrower than a proof of the Q3LOCK phase chain: it checks
only the imported finite-volume operator, periodic loop representation,
fixed-source DLR existence/compactness and moment statements.

The audited PDF identifies itself as `arXiv:math-ph/0609045v1` dated 16
September 2006.  The final manuscript must pin the exact bibliography version,
checksum and theorem/equation numbers actually used.  The Q3LOCK quadratic
coefficient `r<0` is unrelated to the `r>1` superquadratic exponent in KP's
Assumption (A); this note writes the latter as `r_KP` throughout.

## 2. Exact KP locations and scope

The following source statements were checked in the cited PDF.

| KP location | Source statement | Permitted Q3LOCK use |
|---|---|---|
| (1.1)--(1.2), (2.2)--(2.4) | finite-volume Hamiltonian as harmonic oscillators plus continuous onsite potentials and a symmetric pair matrix | identify the Q3LOCK finite-volume operator after the harmonic split and pair-count convention |
| Assumption (A), (2.5)--(2.6) | continuity and normalization `V_l(0)=0`; `A_V|x|^(2 r_KP)+B_V <= V_l(x) <= V(x)` with `r_KP>1`; finite `Jhat_0` | verify the exact Q3LOCK lower/upper potential bounds, mass and interaction sum |
| (2.8) | self-adjoint, lower-bounded finite-volume Hamiltonian with discrete spectrum, positivity-preserving semigroup and finite heat trace | import finite-volume existence and trace finiteness after the hypothesis map |
| (2.16), (2.34), Proposition 2.7 | periodic OU reference, Feynman--Kac density and source/boundary-continuous finite-volume partition function | identify the fixed finite-volume Q3LOCK loop law and source sign |
| Definition 2.9, (2.63), Lemma 2.11 | DLR equation and accumulation-point implication in the tempered path space | use the Q3LOCK specification continuity when constructing fixed-source DLR limits |
| Theorems 3.1--3.3 | general-vector nonemptiness/`W_t`-compactness, uniform exponential moments and support control | import only after `nu=8`, lattice regularity, potential and interaction assumptions are matched |
| Theorems 3.8, 3.10, 3.12--3.14 | later scalar/ferroelectric order, pressure and phase results, with `nu=1` and additional hypotheses where stated | do not import into the nonradial positive-`lambda` Q3LOCK phase argument |

KP's introduction explicitly separates the general vector results from the
`nu=1`, `J_l l' >= 0` order/phase subsection.  The Q3LOCK paper must preserve
that separation even though its spatial coupling is ferromagnetic in the
bilinear representation.

## 3. Independent Q3LOCK parameter and form-domain map

### 3.1 One-site Hamiltonian

At each spatial site the Q3LOCK kinetic term is

```text
-(hbar^2/(2*chi)) Delta_q = -(1/(2m)) Delta_q,
m = chi/hbar^2 > 0.
```

Choose a fixed auxiliary harmonic rigidity `a>0`.  In KP notation the
harmonic part is `(a/2)|q|^2`; the residual onsite potential is

```text
V_(h,a)(q) = (r/2)|q|^2
             + U_component(q)
             + W_Q3(q)
             + (3c)|q|^2
             - (a/2)|q|^2
             - h*(u,q),
```

where `U_component` is the positive component-quartic term,
`u=(1,...,1)/sqrt(8)`, and

```text
W_Q3(q) = (lambda/4) sum_(e={i,j} in E(Q3))
              (q_i-q_j)^2 (q_i^2+q_j^2) >= 0.
```

The exact Q3LOCK potential has `V_(h,a)(0)=0`; constants introduced by Young
inequalities are estimates and must not be inserted into the Hamiltonian
definition.

### 3.2 Lower and upper KP bounds

The eight-component norm comparison

```text
sum_i q_i^4 >= |q|^4/8
```

and `W_Q3>=0` give quartic coercivity.  On `|h|<=h0`, Young absorption of
the negative quadratic term and the linear source gives

```text
V_(h,a)(q) >= A |q|^4 - C,
```

with `A>0` and finite `C` uniform on the declared compact source interval.
Thus KP's lower bound applies with `r_KP=2`.

For the upper side, each Q3 edge obeys

```text
(q_i-q_j)^2(q_i^2+q_j^2) <= 4(q_i^4+q_j^4),
```

and the finite 3-regular internal graph, component quartics, quadratics and
source term are dominated by one continuous quartic function.  This supplies
the continuous upper function in (2.5).  No radial or `O(8)` invariance is
used in this estimate.

### 3.3 Spatial pair map

For a periodic cubic spatial box, put `J_yz=J_zy=c` on each nearest-neighbour
pair and zero otherwise.  With the ordered KP sum,

```text
-(1/2) sum_(y,z) J_yz (q_y,q_z)
 = -c sum_<yz> (q_y,q_z),
```

and the spatial difference form is

```text
c/2 sum_<yz> |q_y-q_z|^2
 = 3c sum_y |q_y|^2 - c sum_<yz> (q_y,q_z).
```

Here `<yz>` denotes the positive-direction periodic edge multiset with
`3|Lambda|` terms; for `L=2` its parallel-edge multiplicities must be retained.
Open boxes instead use the site degree `(c/2)d_R(y)`.

The periodic degree-six interaction therefore has `Jhat_0=6c`.  The positive
onsite `3c` term is assigned once to `V_(h,a)` and is not counted a second
time in `J`.  For open boxes the boundary degree and edge list differ; the
manuscript must state that convention separately rather than silently reuse
the periodic identity.

## 4. Finite-volume operator and loop consequences

The mapped model has `nu=8`, `m>0`, continuous onsite potentials and finite
`Jhat_0`.  The three-dimensional cubic lattice satisfies KP's geometric
regularity condition (2.1).  Therefore (2.8) supplies the finite-volume
self-adjoint/lower-bounded operator and finite heat trace for each fixed
finite source and volume.

The periodic OU reference uses the covariance operator

```text
A = -m*d^2/dtau^2 + a,
```

and the Feynman--Kac density is the normalized exponential of the residual
local and pair Euclidean action.  The Hamiltonian source `-h*(u,q)` becomes
`+h X_L` in the loop exponential, with

```text
X_L = sum_y integral_0^beta (u,omega_y(tau)) d tau.
```

This identifies the finite-volume probability law used by the Q3LOCK grid
argument.  It does not identify a thermodynamic-limit real-time dynamics.

For the infinite lattice, Definition 2.9 and Lemma 2.11 show that a suitable
accumulation point of finite-volume conditional measures solves the DLR
equation.  Theorem 3.1 gives nonemptiness and `W_t` compactness, while Theorem
3.2 gives the common exponential moment estimate in the Holder and `L2`
loop norms.  These are the exact KP inputs used by EXP-000781 for fixed-source
tempered Euclidean DLR states.

The KP proof distinguishes convergence in a weighted local topology `W_alpha`
from full `W_t` convergence and uses the Feller property to pass the DLR
equation.  The Q3LOCK manuscript must not replace this with an unqualified
"weak convergence" sentence; its grid-to-loop proof has to state the chosen
topology and the continuity class of every test functional.

## 5. Non-imports and Q3LOCK-local obligations

The source's scalar order subsection starts by restricting to `nu=1` and
defines coordinatewise path order.  Its maximal/minimal measures, scalar
pressure equality and infrared phase theorem therefore cannot be cited as
the positive-`lambda`, nonradial eight-component Q3LOCK result.  In particular,
the following remain local obligations:

* finite-grid MTP2 and continuous-loop FKG for the Q3 internal locking term;
* Hilbert-valued spatial reflection positivity and the FSS bound;
* grid covariance/tightness, Riemann-sum convergence and normalizer division;
* differentiation of the unbounded collective source exponential;
* source removal, tangent selection, strict cusp and the Griffiths composition;
* any statement about a common infinite-volume real-time dynamics or KMS
  state.

The order of limits remains fixed: time-grid limit at fixed finite spatial
volume and source, then spatial thermodynamic limit, then the zero-source
tangent.  KP's general DLR compactness is not a license to interchange these
limits.

## 6. Independent findings and residual gates

| Check | Finding | Gate |
|---|---|---|
| Theorem scope | Theorem 3.1/3.2 are general-vector inputs; 3.8/3.10/3.12 are scalar/ferroelectric inputs | Cite only the general-vector results for EXP-000781 |
| Potential domain | Exact Q3LOCK residual potential is continuous, vanishes at zero and is quartically coercive on compact source intervals | Insert explicit Young constants and form-domain statement in the manuscript |
| Pair normalization | Periodic ordered-pair convention gives `Jhat_0=6c` and one `3c` onsite allocation | Audit periodic and open edge lists independently |
| Topology | KP separates `W_alpha` accumulation from `W_t` DLR compactness | State the topology and continuity class in the grid-to-loop lemma |
| Source and moments | KP fixed-source exponential moments support DLR compactness but do not prove source tangents or strict cusp | Keep P-05/P-12 conditional on the Q3LOCK pressure and UI arguments |
| Version pin | The exact arXiv version and theorem numbering must be frozen in the bibliography | External source reviewer sign-off required |

The source match is therefore **conditionally consistent at T0**.  It is not a
registered independent theorem until the final bibliography-version, operator
form-domain and boundary-edge audits are signed by an independent reviewer.

## 7. Publication boundary

This audit adds no claim card, result promotion, P2 manuscript, release or
PDF.  It does not prove the strict cusp, infrared zero-mode lower bound or
two-state phase conclusion.  PDF generation, compilation, rendering and
visual review remain reserved for the final content-frozen stage after P-06,
P-09, P-12 and the reproducibility package have passed independent audit.

## 8. Primary source

Y. Kozitsky and T. Pasurek, *Euclidean Gibbs Measures of Interacting Quantum
Anharmonic Oscillators*, arXiv:math-ph/0609045, especially equations
(2.1)--(2.8), (2.16), (2.34), (2.63), Lemma 2.11 and Theorems 3.1--3.3.

