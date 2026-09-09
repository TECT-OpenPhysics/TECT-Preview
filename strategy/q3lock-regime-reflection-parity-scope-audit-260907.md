# Q3LOCK regime, reflection, parity, and scope audit

Date: 2026-09-07  
Result line: R-497  
Exploration: EXP-001629  
Paper package: `publish/papers/q3lock-phase-coexistence/`  
Status: `T0 / INTERNAL_REVIEW_ONLY / claim_bearing=false`

## Scope and disposition

This bounded audit covers proof-audit rows A19--A23: the strict sufficient
regime, synchronization of the two limit branches and nonclaims, the
Hilbert-valued reflection-positive kernel, the finite Falk--Bruch normalization
boundary already cross-linked to A22, and parity-based distinction of the two
source-selected DLR states.  It is an internal source/content audit only.  It
does not turn any row into an independently signed PASS and does not authorize
a paper PDF.

Disposition: **conditionally internally consistent; independent review remains
open**.  The current proof-audit matrix therefore keeps A19--A23 `OPEN`.

## A19: strict sufficient regime, not an exact critical point

The manuscript uses the local collective lower bound and the nonzero-mode
subtraction in the order

`Pi_L >= d_beta - I_{3,L}/(2 beta c)`,

then takes the spatial liminf.  With `x_beta tanh(x_beta)=beta/(4m theta_Q)`
and `A_0=8cm theta_Q^2`, the exact algebra is

`2 beta c delta_beta = A_0 tanh(x_beta)^2 - I_3`.

When `A_0>I_3`, the value
`rho_* = sqrt(I_3/A_0)` lies in `(0,1)`, so
`x_* = artanh(rho_*)` and
`beta_* = 4m theta_Q x_* rho_*` are finite.  Strict monotonicity of
`x tanh(x)` and `tanh(x)^2` gives `delta_beta>0` exactly for the displayed
sufficient condition `beta>beta_*` within this lower-bound argument.  At
equality or when `A_0<=I_3`, the lower bound is nonpositive; the manuscript
makes no phase-absence inference.  The observation that the sufficient set is
nonempty is made by choosing finite model parameters, not by taking a
zero-temperature or infinite-mass limit.

This is a regime statement, not an exact critical-temperature theorem and not
a result for the complement of the sufficient set.

## A20: branch order, source normalization, and nonclaims

The composition dictionary keeps the two branches distinct.  The fluctuation
branch uses the zero-source periodic law, the Duhamel matrix, and the spatial
limit.  The state-selection branch first fixes a nonzero source, takes a
spatial accumulation at that source, and only then sends differentiability
points `h_j` down to zero.  The manuscript explicitly forbids a simultaneous
`h=h(L)` limit and does not identify a zero-source periodic accumulation with a
positive phase.

The source convention is consistent in the three places where a factor could
be lost:

* the finite source is `e^{h X_L}`, with `X_L` already containing the time
  integral;
* `p'_{beta,L}(h)=E[X_L]/V=beta E[Q_0]`;
* `P'_{beta,L}(h)=E[Q_0]/8`, so a cusp lower bound is divided by eight only
  after taking the positive square root.

The front matter, theorem remark, crosswalk, source ledger, and readiness
section agree on the nonclaims: no all-parameter phase theorem, no phase
absence outside the sufficient regime, no extremality/purity/clustering or
DLR-simplex classification, no common real-time dynamics or KMS result, no
ground-state gap or continuum limit, and no TECT/cosmology conclusion.  These
boundaries are scope controls, not evidence that the conditional theorem has
been independently accepted.

## A21: Hilbert-valued kernel and spatial reflection positivity

The local measure `nu_h` is finite because the scalar quartic dominates its
negative quadratic and source terms while the Q3 locking term is nonnegative.
The product of local measures and within-half bonds is therefore a finite half
measure.  The spatial crossing interaction is the Hilbert kernel

`K(v,w)=exp[-c ||v-w||_{L^2([0,beta];R^8)^M}^2/2]`.

Finite-rank orthogonal projections produce ordinary finite-dimensional Gaussian
Gram representations.  Strong convergence of the projections gives pointwise
convergence to `K`, and bounded convergence against a finite complex measure
preserves positive definiteness.  Pushing the bounded complex half-measure
`F alpha_h` through the vector of crossing loops then proves
`E[F Theta F]>=0` for bounded Borel plus-half tests.

The reflection geometry has two link-reflection planes and `2L^2` crossing
bonds for even `L>=4`; the reflected minus-half local and internal-bond measure
is the same as the plus-half measure for a spatially constant real source.
Thus the factorization is spatial reflection positivity.  The manuscript
explicitly does not call it a real-time Osterwalder--Schrader reconstruction,
and the later finite-mesh FSS estimate is not presented as an unexplained
consequence of reflection positivity.

The remaining open item is independent acceptance of the measurable
factorization and all finite-measure/form hypotheses, not a missing infinite
dimensional Lebesgue measure or a hidden Gaussian prior.

## A22 cross-reference: finite Falk--Bruch boundary

The finite logarithmic-mean proof is already audited in EXP-001628.  Its use
here is limited to the fixed-volume bounded multiplier and ordered spectral
cutoff.  No radial phase theorem, unbounded infinite-volume operator theorem,
or scalar reduction is imported through the reflection or threshold sections.

## A23: parity and a bounded local witness

At zero source every term in the finite specification is invariant under the
global sign map, including the boundary pairing after both interior and
boundary loops are negated.  The oscillator reference is symmetric, so a
change of variables gives

`pi_Delta^0(f | Theta xi) = pi_Delta^0(f o Theta | xi)`.

Consequently the parity image of a zero-source DLR state is again a tempered
zero-source DLR state.  The source-selected state has positive collective
expectation only after the strict cusp has been established; its parity image
has the opposite sign.

The unbounded expectation is not used as the sole measurable witness.  A
finite clipping radius `R` is chosen after construction.  The common second
moment bound gives the two clipping errors at most `C_2/R`, so for
`R>2C_2/sqrt(delta_beta)` the bounded continuous cylinder observable
`clip_R(Q_0)` has strictly different expectations in the two states.  This
proves distinctness without asserting extremality, purity, clustering, or
uniqueness.

## Hostile checks and non-claims

1. Replacing `A_0>I_3` by equality makes the displayed lower bound zero; no
   phase-absence statement is licensed.
2. Applying parity to a periodic zero-source accumulation before the
   source-window construction would only produce a symmetric pair and would
   not prove a positive phase; the manuscript does not take that shortcut.
3. The Hilbert kernel is positive definite, but this alone is not a temporal
   OS reconstruction, KMS dynamics, or a mass-gap result.
4. The factor eight in the pressure derivative comes from the eight-component
   normalized collective direction and pressure convention; it is not an
   extra component factor in the FSS Poisson norm.
5. A finite bounded witness distinguishes the two constructed laws; it does
   not classify the full DLR simplex.

## Required next gate

Obtain signed independent review of the A19--A23 interfaces, especially the
reflection-factorization measurability, the source/pressure branch order, and
the DLR parity witness.  If a reviewer requests a correction, create a new
immutable replay checkpoint and preserve all historical result bytes.  Keep
R-497 at T0, `claim_bearing=false`, `UNFROZEN_CONTENT_REVIEW`, and
`pdf_status=DEFERRED` until all proof, literature, notation, hash, and release
gates are discharged.
