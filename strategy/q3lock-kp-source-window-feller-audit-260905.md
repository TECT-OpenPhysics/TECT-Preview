# Q3LOCK KP source-window Feller and specification audit

**Status:** T0 source-to-zero specification audit; no claim-card promotion  
**Date:** 2026-09-05  
**Owner task:** T-054  
**Authority:** EXP-000780 -> EXP-000781 -> EXP-000782  
**Primary source:** Kozitsky--Pasurek, arXiv:math-ph/0609045v1, local specification and Feller statements  
**PDF:** deferred until mathematical content freeze, independent review, clean replay, and final release review

## 1. Purpose and strict boundary

The source-tangent construction needs more than pointwise Feller continuity at
one fixed source.  For `h_n -> 0`, the local KP specification must be compared
uniformly on compact sets of boundary configurations, with a source-uniform
integrable majorant.  This note derives that comparison for a finite Q3LOCK
region and identifies precisely which KP inputs remain imported.

It is a Q3LOCK-local proof-text audit.  It does not certify the source-to-zero
DLR limit, a strict cusp, phase coexistence, or any claim card.  No manuscript
or PDF is created.

## 2. Finite-region conditional law and source factor

Let `Delta` be a finite spatial region and let `xi` be an exterior loop
configuration.  The KP local specification has the form

```text
pi_Delta^h(df|xi)
 = Z_Delta(h,xi)^(-1)
   integral f(omega_Delta xi_Delta^c)
           exp(-A_Delta(omega_Delta|xi) + h*X_Delta(omega_Delta))
           dG_Delta(omega_Delta),
```

where `dG_Delta` is the finite-volume Gaussian reference,
`X_Delta=sum_(y in Delta) integral_0^beta (u,omega_y(tau)) d tau`, and all
spatial boundary couplings are contained in `A_Delta`.  The source changes only
the displayed local linear factor.  This is the source specialization of the
KP specification formulas (2.53)--(2.59), after the Q3LOCK potential and
source normalization are inserted.

## 3. Compact-boundary quartic envelope

Fix `h_0>0` and a compact set `K` in the KP weighted boundary topology
`Omega_alpha`.  Since `Delta` has finitely many boundary neighbours, compactness
of `K` gives a finite bound on each boundary loop norm and on the finitely many
boundary linear functionals entering the spatial bonds.  The Q3LOCK onsite
potential obeys, uniformly for `|h|<=h_0`,

```text
V_(h,a)(q) >= A*|q|^4 - C_0,
A>0,
```

and every boundary coupling is bounded on `K` by a linear term `B_K|q|` plus a
constant.  Quartic Young absorption therefore gives constants `A_K>0` and
`C_K<infinity` such that the conditional action satisfies

```text
A_Delta(omega_Delta|xi) - h*X_Delta(omega_Delta)
  >= A_K*sum_(y in Delta) ||omega_y||_4^4 - C_K
```

for all `xi in K` and `|h|<=h_0`.  The constants depend on `Delta`, `K`, the
fixed model parameters and `h_0`, but not on the particular source `h`.

The same estimate applied on a fixed bounded set of interior loops gives a
strict positive lower bound for `Z_Delta(h,xi)` uniform on
`[-h_0,h_0] x K`.  The KP Feller theorem supplies continuity of the remaining
boundary-dependent integrals; compactness then turns pointwise positivity into
this uniform lower bound.

## 4. Uniform source continuity on compact boundary sets

For `h,h' in [-h_0,h_0]`,

```text
|exp(h*X_Delta)-exp(h'*X_Delta)|
  <= |h-h'|*|X_Delta|*exp(h_0*|X_Delta|).
```

The quartic envelope in Section 3 and the finite-region Holder--Young estimate

```text
|X_Delta| <= C_Delta*(sum_(y in Delta)||omega_y||_4^4)^(1/4)
```

give an integrable majorant for the right-hand side, uniformly in `xi in K`.
The same majorant applies with a bounded continuous test `f`, and the uniform
normalizer lower bound prevents division from losing convergence.  Therefore

```text
sup_(xi in K) |pi_Delta^h(f|xi)-pi_Delta^h'(f|xi)| -> 0
```

as `h -> h'`, for every bounded continuous `f` for which the KP Feller map is
used.  In particular, `pi_Delta^h(f|xi) -> pi_Delta^0(f|xi)` uniformly on `K`.

This is a local source-window estimate, not a new infinite-volume theorem.  It
uses the KP Feller continuity in `xi`, while the uniformity in `h` and the
quartic majorant are Q3LOCK-local.

## 5. Integrating the specification difference against source-varying states

Let `mu_n` be the fixed-source DLR states at `h_n -> 0` from the pressure
tangent construction, and assume their common source-window tightness in
`Omega_alpha`.  For any `epsilon>0`, choose a compact `K` with
`sup_n mu_n(K^c)<epsilon`.  With `||f||_infinity<=1`, Section 4 gives

```text
|integral [pi_Delta^h_n(f|xi)-pi_Delta^0(f|xi)] dmu_n(xi)|
 <= sup_(xi in K)|...| + 2*epsilon,
```

so the integral tends to zero.  Since `pi_Delta^0(f|.)` is bounded continuous
by the KP Feller statement, weak convergence `mu_n -> mu_+` then gives

```text
integral pi_Delta^0(f|xi) dmu_n(xi)
  -> integral pi_Delta^0(f|xi) dmu_+(xi).
```

Combining this with the DLR identity for each `mu_n` yields the zero-source DLR
identity for `mu_+`, provided the KP topology, tightness and local-observable
uniform-integrability inputs are independently accepted.

## 6. Adversarial checks

| Objection | Disposition | Consequence |
|---|---|---|
| Pointwise Feller continuity at `h=0` suffices for source-varying DLR states | **UPHELD AS FALSE** | Uniform-on-compact source continuity and a tightness split are required. |
| Boundary couplings can be ignored in the quartic estimate | **UPHELD AS FALSE** | They produce compact-set-bounded linear terms that must be absorbed explicitly. |
| A positive local partition function has a uniform lower bound automatically | **UPHELD AS FALSE** | Use a bounded interior test set plus KP continuity and compactness of the boundary set. |
| Weak convergence of `mu_n` alone passes the source-dependent kernel | **UPHELD AS FALSE** | First remove the source difference uniformly on a compact boundary set, then use Feller continuity at zero source. |
| This specification estimate proves DLR multiplicity | **UPHELD AS FALSE** | It only supplies one composition step; strict pressure slope and parity remain separate. |

## 7. Remaining independent-review obligations

An independent reviewer must check the exact KP weighted topology, the finite
boundary linear-function estimates, the compact-set normalizer lower bound, and
the quartic source-window constants for the declared Q3LOCK interaction.  The
review must also verify that the bounded-continuous specification identity
extends to the required Borel class by a monotone-class argument.

No strict cusp, positive-lambda phase theorem, DLR multiplicity, extremality,
purity, clustering, common real-time dynamics, KMS state, ground-state phase,
spectral gap, continuum limit, physical vacuum, cosmological conclusion, C6,
CP1, Sector A, or Pre-A closure follows.  PDF generation remains deferred.

## 8. Disposition

The source-window DLR passage is now expressed as a compact-boundary uniform
continuity lemma plus a tightness split.  This removes the hidden assumption
that fixed-source Feller continuity automatically survives `h_n -> 0`, while
retaining all required KP and Q3LOCK hypotheses as explicit review gates.  The
result is a T0 proof-text advance only; no theorem or publication status is
promoted.
