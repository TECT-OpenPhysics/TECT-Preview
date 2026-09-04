# Q3LOCK independent proof audit — round 1

**Status:** T0 research audit; not a claim card and not a manuscript  
**Date:** 2026-09-04  
**Owner task:** T-054  
**Authority:** EXP-000780 -> EXP-000781 -> EXP-000782 only  
**PDF:** deliberately deferred until all mathematical review and release gates close

## 1. Audit purpose and scope

This document is an adversarial review of the proposed bounded paper on the
positive-`lambda`, fixed-spacing, three-dimensional, eight-component Q3LOCK
quantum anharmonic crystal. It does not promote `C6-SPACETIME-SIGNATURE`,
create a P2 manuscript, or assert a final theorem. The only proposed
conclusion under review is the conditional regime

```text
r<0, hbar>0, chi>0, c>0, g>0, lambda>0,
A0 = 8*c*chi*theta_Q^2/hbar^2 > I3,
beta > beta_star,
```

with a strict cusp of the limiting collective-source pressure and at least two
distinct parity-related tempered Euclidean DLR states. The audit excludes
real-time dynamics, algebraic KMS, ground-state or gap statements, continuum
limits, physical-vacuum interpretation, and any conclusion about C6, CP1,
Sector A, or Pre-A.

The working standard is stronger than an executable PASS: every load-bearing
limit must have a paper-level statement, every imported theorem must have its
hypotheses matched, and every remaining gap must be named rather than hidden
inside a certificate or numerical script.

## 2. Source-hypothesis crosswalk

The general Euclidean DLR framework of
[Kozitsky--Pasurek](https://arxiv.org/abs/math-ph/0609045) supplies fixed-source
existence, tempered compactness, periodic accumulation, and uniform local
moments once the finite vector dimension, positive mass, confining potential,
and summable interaction hypotheses are checked. The proposed Q3LOCK
potential is continuous, radially quartically confined after Young absorption,
and has finite-range scalar interaction. The source-to-zero tangent extension
is therefore paper-local; it cannot be cited as an automatic consequence of
fixed-source existence.

The pressure, Griffiths, and Bruch--Falk tools are taken from
[Kargol--Kondratiev--Kozitsky](https://arxiv.org/abs/0710.2303). Their
rotation-invariant infrared corollary is explicitly excluded. In particular,
the paper must use the exact Euclidean source variable
`X_L=sum_y integral_0^beta Q_y(tau)d tau` and retain the factor-eight relation
between the fine energy pressure and the collective slope.

The finite-dimensional Gaussian-domination input is the transfer argument of
[Froehlich--Simon--Spencer](https://math.caltech.edu/SimonPapers/65.pdf). The
source paper allows arbitrary single-spin measures with the required
quadratic exponential moments and does not require internal `O(8)` symmetry.
The Q3LOCK time coordinate is infinite-dimensional only after the time-grid
limit, so a finite `8N`-component transfer followed by a separate
Feynman--Kac/Trotter limit is the permitted route.

## 3. Obligation matrix

| Obligation | Audit disposition | Reason and required evidence |
|---|---|---|
| P-01 finite-volume lower bound, compact resolvent, heat trace | Pre-registration consistent; independent operator audit open | Quartic comparison gives a confining tensor oscillator. The manuscript must state the closed form, min--max comparison, and trace-finiteness argument. |
| P-02 open pressure limit and periodic/open equality | Pre-registration consistent; seam/min--max audit open | The `24 L^2` seam count and `eta=L^(-1/2)` absorption give the advertised density scale, but the moving-temperature trace comparison must be checked line by line. |
| P-03 local-uniform pressure convergence and parity | Pre-registration consistent; convex-analysis audit open | Pointwise limits, compact-source bounds, convexity, and global inversion are present; the manuscript must prove the interior equicontinuity step. |
| P-04 DLR hypothesis crosswalk and periodic compactness | Pre-registration crosswalk complete; source-removal audit open | Fixed-source hypotheses match the vector model. The varying-source kernel estimate and Feller passage must be written explicitly. |
| P-05 tangent selection and factor-eight slope | Pre-registration algebra consistent; DLR/convex audit open | The source derivative is an energy-pressure derivative, while the Griffiths variable is Euclidean-time integrated. The two normalizations must be kept separate and recomputed. |
| P-06 continuous-loop FKG for nonradial Q3 | **Open** | Finite time-grid mixed derivatives have the attractive sign. Closure requires a mesh-uniform Gaussian tightness estimate, a normalizer lower bound, uniform integrability, and a cited or proved Feynman--Kac/Trotter identification. The finite-grid edge convention, order-preserving interpolation, nonnegative product shifts, and clipped-coordinate passage are written in `q3lock-fkg-continuous-loop-limit-audit-260904.md` (EXP-001500). Only bounded-continuous association is claimed; path-space MTP2 and total variation are not available shortcuts. |
| P-07 collective moment lower bound | Pre-registration algebra consistent; domain/FKG audit open | The uniform translation cancels every spatial bond and gives the exact Hessian coefficients. The common form domain, cutoff removal, and cross-component FKG moments still require an independent check. |
| P-08 Bruch--Falk local Duhamel bound | Pre-registration normalization consistent; manuscript transcription required | The smooth truncation `Q_R=R tanh(Q/R)` controls the unbounded observable and has the stated double commutator. The limit in the Duhamel norm must be displayed. |
| P-09 reflection positivity and Gaussian domination | **Open** | The finite-grid crossing kernel is positive definite for arbitrary anisotropic onsite weight. The transfer theorem, edge orientation, zero-sum Poisson solution, constant-source loop limit, and differentiation under the limit remain paper-local proof obligations. The `8N` spin scaling, `beta`/factor-two ledger, and quartic uniform-integrability passage are isolated in `q3lock-fss-source-differentiation-audit-260904.md` (EXP-001499) but still need an independent theorem-level audit. |
| P-10 three-dimensional infrared sum | Analytic estimate closed at pre-registration level; numerical enclosure open | The `|p|^{-2}` singularity is integrable in three dimensions and the shell estimate proves `I_(3,L)->I3`. Any decimal is only a recomputed enclosure. |
| P-11 threshold equivalence | Algebra closed at pre-registration level; independent transcription open | Strict monotonicity of `x tanh(x)` gives the equivalence of `delta_beta>0`, `A0>I3`, and `beta>beta_star`; the boundary case must remain explicit. |
| P-12 cusp and two DLR states | Conditional only | The factor-eight Griffiths bridge and parity construction are valid only after P-06 and P-09 supply the positive infrared lower bound and after the source-tangent audit closes. |

## 4. Detailed adversarial findings

### 4.1 Continuous-loop FKG (P-06)

At mesh `epsilon=beta/N`, a positive harmonic split produces a cyclic
M-matrix precision. The spatial bond contributes a positive mixed derivative
to the log density, and for a Q3 edge

```text
-epsilon*d^2/dxdy [(lambda/4)(x-y)^2(x^2+y^2)]
  = (epsilon*lambda/4)[(x+y)^2+5(x-y)^2] >= 0.
```

This establishes finite-grid association. It does not by itself establish
association for the exact continuous loop law. The load-bearing passage must
use piecewise-linear interpolation, a mesh-uniform tightness estimate for the
harmonic Gaussian reference, a positive lower bound on the weighted normalizer
on a sup-norm ball, and uniform integrability from quartic confinement. The
order of limits is fixed: time-grid limit at fixed finite spatial volume and
source first, spatial thermodynamic limit second. Bounded continuous
increasing functionals pass through weak convergence; coordinate products are
then recovered by clipping. An independent reviewer must check that the
chosen interpolation preserves the coordinate order and that the stated
Feynman--Kac/Trotter theorem has exactly the required source and potential
hypotheses.

### 4.2 Hilbert-valued reflection positivity (P-09)

At mesh `N`, collect the eight components and all time slices into one spin in
`R^(8N)` with weighted inner product `epsilon*sum_k`. A crossing spatial bond
has kernel

```text
exp[-c*||a-b||^2/2]
  = exp[-c*||a||^2/2] exp[-c*||b||^2/2] exp[c*<a,b>].
```

The last factor is positive definite by its nonnegative symmetric-tensor
series, so the finite-dimensional FSS transfer does not require radial or
`O(8)` symmetry. The infrared source is time-constant,
`j_y(tau)=t*a_y*u`, with `sum_y a_y=0`; its Poisson edge field is also
time-constant and is represented exactly on every grid. Expanding the shifted
square gives

```text
log E_0 exp(<j,omega>) <= (2c)^(-1)<j,L_sp^(-1)j>,
```

and the spatial eigenvalue `2 E(p)` yields
`(Q_hat_p,Q_hat_-p)_D <= 1/(2 beta c E(p))`. The independent audit must still
verify the FSS hypotheses for the anisotropic onsite measure, the orientation
and normalization of `D`, the quartic majorant used in the shifted loop limit,
and differentiation at the constant source.

### 4.3 Collective projection (P-07)

The normalized global momentum shift leaves all spatial differences unchanged.
On the polynomial core, the exact second derivative is

```text
[Pi_0,[H,Pi_0]]
 = hbar^2 [r + (3g/(8V))*sum_y S_y
              + (lambda/(8V))*sum_y D_y].
```

Zero-source association gives nonnegative cross-component products. Since
the Q3 graph is 3-regular, `E[D_0]<=3 E[S_0]` and
`E[Q_0^2]>=E[S_0]/8`, hence
`E[Q_0^2]>=-r/[3(g+lambda)]`. The algebra is internally consistent, but an
independent reviewer must audit the common polynomial form domain, trace
differentiation, and the use of the clipped FKG moments before this is used
inside the infrared chain.

### 4.4 Griffiths composition (P-12)

With `f_L(h)=V^(-1)log E_0 exp(h X_L)`, the exact Feynman--Kac identity is
`f_L(h)=8 beta[P_(beta,L)(h)-P_(beta,L)(0)]`. Applying the general
Griffiths subgradient bound to `X_L/V` gives

```text
beta^2 limsup Pi_L <= [8 beta D_+P_beta(0)]^2.
```

Thus a positive infrared limsup implies `D_+P_beta(0)>=sqrt(delta_beta)/8`.
The compact-source tangent lemma then yields a zero-source DLR state with
collective expectation `8 D_+P_beta(0)`, and parity supplies the opposite
state. This is a one-way sufficient implication: failure of `delta_beta>0`
does not imply uniqueness or absence of order, and parity images are not
asserted to be pure, extremal, clustering, or KMS states.

## 5. Reproducibility and release audit

The primary and independent mathematical payloads have deterministic
assertion values, but the current integrated verifier captures child stdout
verbatim while using a random `TemporaryDirectory` suffix. Consequently two
identical reruns can differ in `result.json` bytes and hash even when all
assertions and numerical values agree. This is a release-serialization defect
and is recorded separately as EXP-001482. Before any claim registration or
PDF creation, the final clean checkpoint must:

1. canonicalize or omit environment-specific scratch paths;
2. rerun the EXP-000780, EXP-000781, and EXP-000782 integrated verifiers;
3. compare canonical bytes and hashes across two reruns;
4. run the independent mathematical and novelty audits on the same clean
   snapshot; and
5. pass the repository release gate with no concurrent staged work.

The current repository has unrelated staged/generated PAH work, so a broad
regeneration, commit, or release run is intentionally postponed. No PDF is
created during this content-review stage. PDF compilation, rendering, and
visual QA are final-stage actions only after the mathematical and artifact
gates close.

## 6. Decision

The Q3LOCK route is a credible bounded-paper candidate, but it is not yet at
claim-registration or submission quality. P-06 and P-09 are the two
load-bearing open proof sections. P-01--P-05, P-07--P-08, and P-10--P-12 are
paper-local or conditional components whose wording, domains, and normalizing
factors still require independent audit. The correct next gate is therefore
not PDF production; it is completion and audit of the two limit passages,
followed by a clean deterministic reproduction package. Only then may a
bounded independent claim and P2 manuscript be registered, after which the
content review must finish before the final PDF is built and visually checked.
