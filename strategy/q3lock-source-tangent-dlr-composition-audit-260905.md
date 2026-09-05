# Q3LOCK source-tangent and zero-source DLR composition audit

**Status:** T0 proof-text audit; independent mathematical review remains required  
**Date:** 2026-09-05  
**Owner task:** T-054  
**Authority:** EXP-000780 -> EXP-000781 -> EXP-000782  
**Primary source:** Y. Kozitsky and T. Pasurek, *Euclidean Gibbs States of
Interacting Quantum Anharmonic Oscillators*, arXiv:math-ph/0609045v1  
**PDF:** deferred until the complete mathematical content is reviewed and frozen

## 1. Purpose and strict boundary

EXP-000781 supplies the positive-source tangent construction used after a
pressure cusp is established.  This audit isolates the only composition that
is needed: periodic finite-volume states at a sequence of positive source
values, their DLR accumulation points, and a further source-to-zero limit.  It
checks the pressure normalization, the topology used at each limit, and the
continuity of the local specification.

The audit does not prove a positive source slope.  It does not promote
EXP-000781 or EXP-000782, and it does not construct a common infinite-volume
real-time dynamics, a KMS state, an extremal state, a pure state, clustering,
or a ground-state phase.

## 2. Frozen model and source convention

Let `Lambda_L=(Z/LZ)^3`, `V_L=L^3`, and let `q_y in R^8` with
`u=(1,...,1)/sqrt(8)`.  The energy source is

```text
H_L(h) = H_L(0) - h * sum_y (u,q_y),
```

and the physical energy pressure is

```text
P_(beta,L)(h) = (1/(8*beta*V_L)) * log Tr exp(-beta*H_L(h)).
```

The Euclidean source factor is therefore `exp(+h*X_L)` with

```text
X_L = sum_y integral_0^beta (u,omega_y(tau)) d tau.
```

At finite volume, Duhamel differentiation and coarse translation invariance
give

```text
d/dh P_(beta,L)(h) = (1/8) * <(u,q_0)>_(L,h)
                     = (1/(8*beta*V_L)) * E_(L,h)[X_L].
```

The factor `1/8` is the fine-oscillator normalization.  The dimensionless
log-density `p_(beta,L)=V_L^(-1) log Z_L` instead satisfies

```text
d/dh p_(beta,L)(h) = beta * E_(L,h)[X_L]/V_L
                     = 8*beta*d/dh P_(beta,L)(h).
```

These two derivatives must not be interchanged in the source-tangent proof.

## 3. Uniform source window for the KP hypotheses

Fix `h_0>0` and restrict to `|h|<=h_0`.  After the periodic spatial split and
an auxiliary harmonic term `a|q|^2/2`, the Q3LOCK one-site potential is

```text
V_(h,a)(q) = ((r+6c-a)/2)*|q|^2
             + (g/4)*sum_e q_e^4
             + W_Q3(q) - h*(u,q),
```

with `W_Q3>=0`.  The norm inequality `sum_e q_e^4>=|q|^4/8` and quartic
Young bounds give constants `A>0` and `C<infinity`, independent of `h` in
this window, such that

```text
V_(h,a)(q) >= A*|q|^4 - C.
```

An upper function for the same window is obtained by replacing the source by
`h_0*|q|`; it is continuous and finite on `R^8`.  The interaction norm is
`Jhat_0=6c`, and the reduced mass is `m=chi/hbar^2`.  Thus the general KP
Assumption (A) and finite-range interaction bound hold with common stability
data throughout the source window.

The source-uniform conclusion needed below is not a new phase theorem.  It is
the following bounded-window reuse of the KP estimates: re-run the constants
in Theorems 3.1--3.3 with the common lower/upper data above.  This gives a
common one-site exponential estimate and a common tempered-support bound for
all source-DLR measures with `|h|<=h_0`.  The estimate is used only for
tightness and uniform integrability; its constants must be written explicitly
in the final manuscript and checked independently.

## 4. From pressure differentiability points to source-DLR states

Let `P_beta` be the locally uniform thermodynamic pressure from EXP-000780.
For a convex function, choose differentiability points `h_n>0` with
`h_n downarrow 0` and

```text
P_beta'(h_n) -> D_+P_beta(0).
```

For each fixed `h_n`, the convex-derivative lemma recorded in
`q3lock-pressure-derivative-subsequence-audit-260905.md` applies: finite
periodic pressures are convex `C^1`, and EXP-000780 supplies locally uniform
convergence, so `P_(beta,L)'(h_n) -> P_beta'(h_n)` along the full periodic
sequence and hence along the subsequence selected for DLR compactness.  Apply
KKK Proposition 2.21 to that periodic-volume subsequence.  It supplies a
translation-invariant tempered Euclidean DLR accumulation point `mu_n` for
the source `h_n`.  The finite-volume derivative identity and the common
exponential estimate imply uniform integrability of `(u,omega_0(0))`.
Consequently,

```text
(1/8) * integral (u,omega_0(0)) dmu_n
    = P_beta'(h_n).
```

The common source-window tightness permits a subsequence, still denoted
`mu_n`, converging locally in a fixed `W_alpha` topology to a probability
measure `mu_plus`.  The common support estimate places the limit on the
tempered configuration space.  Translation invariance passes to the limit.

No assertion that the different `mu_n` are a single cofinal-volume sequence
is needed: each fixed-source DLR accumulation is taken first, and the source
limit is then a separate compactness step.  The derivative identification is
not supplied by DLR compactness alone; it uses local uniform pressure
convergence, finite-volume trace differentiability, and local-observable
uniform integrability as isolated in EXP-001560.

## 5. Passing the DLR equation through `h_n -> 0`

For a finite region `Delta`, let `pi_Delta^h` denote the KP local
specification at source `h`.  For `f in C_b(Omega_alpha)`, the KP Feller lemma
applies at each fixed source.  The source dependence is only the local factor

```text
exp(+h * sum_(y in Delta) integral_0^beta (u,omega_y(tau)) d tau).
```

The compact-boundary source-window lemma recorded in
`q3lock-kp-source-window-feller-audit-260905.md` makes the needed uniformity
explicit: boundary linear terms are bounded on compact sets, quartic Young
absorption supplies a common exponential majorant, and KP continuity plus a
bounded interior set supplies a uniform normalizer lower bound.  Hence

```text
(h,xi) -> pi_Delta^h(f | xi)
```

is jointly continuous on `[-h_0,h_0] x Omega_alpha` when restricted to a
compact boundary set, and the convergence to `pi_Delta^0(f|xi)` is uniform on
that set.  Tightness of `{mu_n}` then gives

```text
integral [pi_Delta^(h_n)(f|xi) - pi_Delta^0(f|xi)] dmu_n(xi) -> 0.
```

Because `pi_Delta^0(f|.)` is bounded continuous by the KP Feller property,
weak convergence gives

```text
integral pi_Delta^0(f|xi) dmu_n(xi)
    -> integral pi_Delta^0(f|xi) dmu_plus(xi).
```

The DLR identity for `mu_n`, followed by these two limits, therefore yields

```text
mu_plus(f) = integral pi_Delta^0(f|xi) dmu_plus(xi).
```

The bounded-continuous identity extends to all Borel `f` by the usual monotone
class argument.  Thus `mu_plus` is a zero-source tempered Euclidean DLR
measure.  This step is the required source-to-zero composition; it is not an
appeal to uniqueness.

## 6. Passing the tangent expectation and applying parity

The common exponential estimate also gives uniform integrability of the local
unbounded observable `(u,omega_0(0))`.  Therefore

```text
(1/8) * integral (u,omega_0(0)) dmu_plus
    = lim_n P_beta'(h_n)
    = D_+P_beta(0).
```

At zero source the global inversion `Theta(omega)=-omega` preserves the
Hamiltonian and the local specification.  Set

```text
mu_minus = Theta_* mu_plus.
```

Then `mu_minus` is another zero-source tempered Euclidean DLR measure and

```text
(1/8) * integral (u,omega_0(0)) dmu_minus
    = -D_+P_beta(0).
```

The two measures are provably distinct only when the endpoint slope is
strictly positive.  If the slope is zero, this construction does not imply
uniqueness or phase absence.

## 7. Limit-order ledger

The valid order is:

1. Fix a source `h_n` and take a periodic spatial-volume accumulation point;
2. identify its local magnetization with the finite-volume pressure derivative;
3. choose `h_n downarrow 0` through differentiability points of the limiting
   convex pressure;
4. use common source-window tightness to take the source-to-zero DLR limit;
5. only after this composition use a strict pressure slope to infer two
   distinct parity-related states.

Taking `h=0` in a finite periodic volume first gives zero magnetization by
parity and cannot replace this order.  Conversely, a pressure cusp alone does
not produce a DLR state until the specification-continuity and uniform-
integrability steps above are supplied.

## 8. Adversarial checks

| Objection | Disposition | Boundary |
|---|---|---|
| Any DLR state at each source realizes the pressure derivative | **VALID ONLY AFTER PERIODIC BRIDGE** | Choose periodic accumulation points and pass the local observable with UI. |
| Compactness at each fixed source implies compactness as source varies | **NOT AUTOMATIC** | Use common source-window coercivity and re-run the KP moment/support constants. |
| Pointwise Feller continuity in the boundary is enough for the source limit | **NOT AUTOMATIC** | Split the DLR difference and prove uniform-on-compacts source continuity. |
| A zero-source limit of DLR states is automatically zero-source DLR | **CONDITIONAL** | It follows only after the specification passage in Section 5. |
| Parity makes the two states distinct | **FALSE WITHOUT A STRICT SLOPE** | Distinctness follows from opposite nonzero expectations, not parity alone. |
| A Euclidean DLR tangent state is a KMS state for one infinite-volume dynamics | **UPHELD AS A NONCLAIM** | KP explicitly leaves the limiting real-time automorphism problem open. |

## 9. Decision and remaining gate

The source-tangent composition is now explicit: the pressure derivative is
attached to periodic DLR accumulation points, and the source-to-zero step is a
separate specification-continuity argument with common source-window
uniform integrability.  This is a T0 proof-text advance, not a certified
theorem.  The remaining independent review must check the source-uniform
adaptation of KP Theorems 3.1--3.3, the `W_alpha` extraction, the compact-set
specification convergence, and the unbounded-observable truncation.

The strict slope still comes only from the independent Q3LOCK zero-mode,
infrared, and KKK endpoint-interval arguments.  Until all those inputs pass,
the result remains research-only and no claim card or manuscript is issued.

## 10. Explicit nonclaims and final PDF gate

This audit does not assert a strict cusp, positive-lambda phase transition,
DLR multiplicity, extremality, purity, clustering, a common real-time
dynamics, a KMS state, a ground-state phase or gap, a continuum limit, a
physical vacuum, a cosmological interpretation, C6, CP1, Sector A or Pre-A
closure.

No LaTeX or PDF is created here.  Final PDF compilation, rendering,
page-by-page visual inspection and hash capture are permitted only after the
complete proof text, source hypotheses, bibliography, nonclaims, claim/result
lineage and clean replay have been independently reviewed and content-frozen.
