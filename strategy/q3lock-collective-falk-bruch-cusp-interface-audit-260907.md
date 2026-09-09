# Q3LOCK collective, Falk--Bruch, and cusp interface audit

Date: 2026-09-07  
Result line: R-497  
Exploration: EXP-001628  
Paper package: `publish/papers/q3lock-phase-coexistence/`  
Status: `T0 / INTERNAL_REVIEW_ONLY / claim_bearing=false`

## Scope and disposition

This is a bounded content audit of the manuscript's collective lower-bound,
Falk--Bruch, endpoint-tail, and source-selected DLR interfaces.  It checks the
normalizations, order of limits, and the logical joins in Sections
`collective`, `cusp`, and the adjacent FKG/Duhamel sections.  It does not sign
an unbounded operator-domain argument, an infinite-volume analytic passage, or
the conditional theorem.

Disposition: **conditionally internally consistent; independent review remains
open**.  No claim tier, publication status, or PDF status changes.  Audit rows
A14--A18 and A22 in `proof-audit.md` remain `OPEN` because the checks below are
an internal reading, not an external mathematical acceptance.

## A14: translated forms and scalar Jensen

For fixed volume, the common displacement
`v_{y,e}=u_e/sqrt(V)` has unit norm.  Spatial and internal differences are
unchanged, and translation preserves both the `H^1` and quartic weighted form
domains.  The finite heat trace supplies a discrete eigenbasis and the shifted
coercive form supplies the required first moments.

The manuscript applies scalar Jensen to the spectral measure of `H(t)` in each
`H(0)` eigenvector, sums with Gibbs weights, and applies scalar Jensen again to
the numbers `d_i`.  This yields
`rho(U(q+tv)-U(q)) >= 0` without differentiating a heat trace through an
unbounded cubic perturbation.  The subsequent second derivative is only the
derivative of a finite polynomial whose coefficients are Gibbs-integrable.
The displayed coefficients check as follows:

* the mass term contributes `r`;
* `g/4 * sum q^4` contributes `3g/(8V) * sum S_y`;
* an internal edge contributes `lambda/(8V) * (q_e-q_f)^2`.

The associated double-commutator identity has the separate factor `hbar^2`;
the Hessian itself does not.  This separation is correct.  The remaining
questions are whether every form-core and spectral first-moment assertion is
accepted by an independent analyst; those are not closed here.

## A15: form identity, absolute sums, and cutoff order

At fixed `R`, `A_R=R tanh(Q_0/R)` is a bounded Lipschitz multiplier and its
derivative is `sech^2(Q_0/R)`.  Product-form cancellation gives

`h[A_R psi_i] - E_i ||A_R psi_i||^2`
`= (2m)^(-1) rho_{psi_i}(sech^4(Q_0/R))`.

The product-rule estimate with the shifted nonnegative form controls both
energy-weighted matrix-element sums.  Because each paired spectral summand in
`c_R` is nonnegative, the finite spectral projection may be taken first and
then sent to infinity.  Regrouping gives the exact local normalization

`c_R = (beta/m) rho(sech^4(Q_0/R))`,

not a global momentum identity.  Only after this fixed-`R` cutoff is removed
does dominated/bounded convergence give `g(A_R) -> rho(Q_0^2)` and
`c_R -> beta/m`.  The Duhamel form is recovered by the thermal `L^2` bound and
the clipped-loop estimate, rather than by asserting a trace of an unbounded
operator.  The order `M -> infinity` at fixed `R`, followed by `R -> infinity`,
is therefore logically coherent.

This row is still conditional on the manuscript's form-core, energy-weighted
sum, and loop-identification details.  It does not produce a common
infinite-volume unbounded operator or a volume-uniform core.

## A16: FKG moment chain

The internal edge polynomial has nonnegative off-diagonal Hessian for the log
density, so the finite mesh laws are associated.  The manuscript then passes
bounded continuous increasing tests through the actual loop weak limit and
extends to bounded Borel upper sets using the closed positive cone.  Coordinate
products are recovered by clipping and the stated fourth-moment bound.

At zero source, parity makes coordinate means zero.  Association therefore
gives nonnegative off-diagonal coordinate products in the periodic law and its
parity-invariant zero-source limits.  The two graph identities are expectation
identities:

`E D_0^int = 3 E S_0 - 2 sum_edges E(q_e q_f) <= 3 E S_0`,

and `E Q_0^2 >= E S_0/8`.  Combining them with the collective Hessian gives
`E Q_0^2 >= -r/[3(g+lambda)]` for `r<0`.  No pointwise graph inequality is
used.  The remaining open point is an independent acceptance of the
continuous-loop association and selected-law cone/topology passage.

## A22: finite Falk--Bruch normalization

For a bounded self-adjoint finite matrix, the manuscript defines the ordinary
thermal form `g`, the logarithmic-mean Duhamel form `b`, and
`c=beta sum (E_j-E_i)(p_i-p_j)|A_ij|^2`.  The logarithmic-mean ratio is
`x coth(x)` with `x=|log p_i-log p_j|/2`, while `c/(4b)` is the weighted mean
of `x^2`.  The explicitly differentiated function
`Phi(u)=sqrt(u)coth(sqrt(u))` is increasing and concave.  Jensen therefore
gives the stated lower bound

`b(A) >= g(A) f(c(A)/(4g(A)))`,

where `x tanh(x)=k` and `f(k)=tanh(x)/x`.  The orientation is important:
`k=c/(4g) >= z tanh(z)` for `z^2=c/(4b)`, hence the solution `x` satisfies
`x>=z`; this yields the displayed lower bound.  Degenerate-energy pairs and
the `c=0` case are included, and the zero matrix is interpreted by homogeneity.
The finite proof is an explicit normalization check, not a new theorem or an
imported radial phase result.

## A17: squared-tail endpoint lemma and strict cusp

The endpoint lemma uses only pointwise convergence of finite-volume log MGFs
on a two-sided source interval to a finite, even convex limit.  For a fixed
positive test source, Chernoff bounds give an exponentially small tail for
`X_n/V_n` outside `ell+epsilon`.  Layer-cake integration makes the squared
tail vanish as `V_n -> infinity`, so
`limsup E[(X_n/V_n)^2] <= ell^2` without differentiating finite-volume second
moments at the nondifferentiable point.

The source dictionary has `E Y_L^2 = beta^2 Pi_L`, with the source in the
MGF equal to `h` (not `beta h`).  Combining the local Duhamel lower bound with
the nonzero-mode subtraction gives
`p_beta'(0+) >= beta sqrt(delta_beta)` and hence
`D_+ P_beta(0) >= sqrt(delta_beta)/8` whenever `delta_beta>0`.  Evenness gives
the opposite left slope.  This is a sufficient strict-cusp statement only;
it is not an exact critical-temperature result.  Its open dependencies are
the pressure-limit and source-window hypotheses, not an illicit derivative
interchange in the endpoint lemma itself.

## A18: source-selected DLR state and parity witness

The positive differentiability points are taken to zero only after a spatial
accumulation has been made at each fixed source.  The source-window tightness,
compact-uniform kernel continuity, and a second local clipping passage preserve
the tangent expectation in a zero-source DLR state.  The cusp alone is not used
as a DLR construction.  Global parity intertwines the zero-source
specification, so the parity image has the opposite collective expectation.
The bounded clipped coordinate gives a finite cylinder witness after choosing
`R` large enough; the states are not claimed to be extremal, pure, clustering,
or exhaustive.

This interface is logically separate from A17 and remains open until the
source-window DLR compactness and unbounded-local-observable passage receive an
independent signed review.

## Adversarial checks and non-claims

1. No step identifies the finite-volume zero-source periodic accumulation with
   a positive phase; the positive phase is source-selected.
2. No inverse spatial Laplacian is applied to the constant mode, and the
   three-dimensional infrared sum is kept separate from the collective local
   bound.
3. The factors `beta/m`, `beta^2`, `1/(8 beta)`, and `hbar^2` occur in distinct
   identities; none is silently transferred between them.
4. The finite spectral cutoff is not treated as operator-norm convergence, and
   no canonical commutation relation is asserted in the cutoff matrix algebra.
5. The threshold `A_0>I_3, beta>beta_*` is a strict sufficient regime.  Equality
   and the complement are undecided, not no-phase results.
6. The finite diagnostics previously registered for the collective and cusp
   content remain finite reproducibility checks only.  They do not certify the
   unbounded limits, the theorem, or publication readiness.

## Required next gate

Obtain an independent mathematical audit of A14--A18 and A22, with explicit
attention to the form-core and spectral-regrouping steps, the continuous-loop
FKG topology, and the source-window DLR passage.  If the reviewer requests a
repair, create a new immutable checkpoint and integrated replay; never rewrite
the historical runs.  Keep `submission-readiness.md` at R-497/T0,
`claim_bearing=false`, `UNFROZEN_CONTENT_REVIEW`, and `pdf_status=DEFERRED`.
