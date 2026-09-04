# Theorem-applicability audit — A2/R-157/R-158

Status: `INTERNAL-APPLICABILITY-AUDIT / NOT EXTERNAL-REVIEWED` (manuscript
v0.1.38, 2026-09-04).

This record identifies every general analytic result used in the paper, fixes
its spaces and hypotheses, and distinguishes a direct paper proof from a
background citation.  It is an internal audit aid.  It is not a signed referee
report, a source-owner decision, a novelty certificate, or a claim-tier
promotion.

## Fixed analytic setting

- Space: the finite periodic torus `T^3_16`, with a three-component complex
  field realified as `R^6`.
- Pivot: real `L^2`; evolution/form space: `H^2`; operator domain: `H^4`.
- Linear part: the positive self-adjoint modewise Hermitian Fourier multiplier
  `L`, with `D(L^alpha)=H^(4 alpha)` and graph-equivalent periodic Sobolev
  norms.
- Nonlinear part: `N=N_loc+N_II`, whose coefficient denominators are bounded
  below by the fixed positive density floor `epsilon_rho=10^-12`.
- Time interval: every fixed finite `[0,T]`; positive-time smoothing is stated
  only on compact subintervals of `(0,infinity)`.

## Applicability matrix

| analytic result | exact hypotheses used here | where discharged | disposition |
|---|---|---|---|
| Analytic semigroup and fractional smoothing | `L` is positive self-adjoint on real `L^2`; its eigenvalues obey `c(1+|k|^4) <= ell <= C(1+|k|^4)`; `D(L^alpha)=H^(4 alpha)` | Manuscript Sec. 4.1 and Eqs. `semigroup-fractional`, `semigroup` | `DIRECT`. The spectral supremum proves the only semigroup bounds used. Pazy and Amann are background references, not hidden premises. |
| Local mild fixed point | `N:H^2 -> L^2` is locally Lipschitz; `L^(1/2)e^(-tL)` is `O(t^-1/2)`; the kernel is integrable | Eqs. `local-lipschitz`, `mild-fixed-point`, `mild-contraction` | `DIRECT`. The Duhamel map is a contraction on an `H^2`-bounded ball for `C_R T^(1/2)<1`; the same estimate supplies the continuation alternative. |
| Galerkin compactness | `u_n` bounded in `L^2_t H^4`, `partial_t u_n` bounded in `L^2_t L^2`; finite torus Fourier basis | Eq. `fourier-compact-tail` and the following finite-mode argument | `DIRECT SPECIAL CASE`. High modes are uniformly small in `L^2_t H^2`; each fixed low-mode vector is bounded in finite-dimensional `H^1_t` and is compact in `L^2_t`. Simon's compactness paper is cited for context, but no unlisted version of the lemma is needed. |
| Nonlinear Galerkin passage | common `L^infinity_t H^2` ball; strong `L^2_t H^2` convergence; local Lipschitz constant uniform on that ball | Sec. 4.3 immediately after `fourier-compact-tail` | `DIRECT`. `N(u_n) -> N(u)` strongly in `L^2_t L^2`; weak `L^2_t H^4` bounds pass to the limit. |
| Hilbert-scale continuity and quadratic chain rule | `w in L^2_t D(L) intersect H^1_t L^2`; `L` positive self-adjoint | Eq. `hilbert-scale-chain` | `DIRECT`. Spectral truncation gives the identity, weak midpoint continuity, norm continuity, and hence `C_t D(L^(1/2))=C_t H^2`, including the initial endpoint. |
| Nonlinear energy chain rule | `u in L^infinity_t H^2 intersect H^1_t L^2`; `D Phi=N:H^2 -> L^2` locally Lipschitz | Eqs. `chain-rule-limit`, `nonlinear-chain` | `DIRECT`. Fourier projection plus time mollification reduces to the finite-dimensional chain rule; the strong limits are displayed. |
| Weakly singular Gronwall | common finite-time `H^2` ball and kernel `k(t)=t^-1/2` | Eqs. `singular-gronwall`, `singular-gronwall-reduction` | `DIRECT`. Two Volterra iterations use `k*k=pi` and reduce the estimate to ordinary Gronwall. |
| Positive-time endpoint cancellation | `N(u)` is positive-time Holder into the chosen base space; `0<theta<1`; `||Le^(-rL)|| <= C/r` | Eqs. `positive-time-h2-holder`, `endpoint-cancellation`, `endpoint-integrability`, and the shifted-base estimates | `DIRECT`. The singular endpoint is cancelled and the remaining `r^(theta-1)` integral is finite. |
| Periodic Sobolev and Moser estimates | dimension `d=3`; fixed compact torus; `H^2 -> L^infinity intersect W^(1,6)`; smooth coefficient maps on the positive-floor range | Eqs. `coefficient-lipschitz`, `classii-lipschitz`, `moser-tame` | `STANDARD, EXPLICITLY INSTANTIATED`. The exact exponents and product spaces are printed. An external reviewer must still confirm every differentiated coefficient and tame constant dependence. |
| Direct method for the grand potential | coercivity in `H^2`; weak `H^2` subsequence; compact `H^2 -> C^(0,alpha)` for `alpha<1/2`; positivity of the Class-II quadratic coefficient matrix | Sec. 6.3, Eqs. `ensemble-high-frequency`, `ensemble-polynomial-coercivity` | `DIRECT AT FIXED VOLUME`. Uniform coefficient convergence and weak `H^1` convergence yield Class-II weak lower semicontinuity. No infinite-volume compactness is claimed. |
| Weak closure of fixed charge | weak `H^2` convergence on the fixed torus and compact `H^2 -> L^2` | Sec. 6.3 fixed-charge paragraph | `DIRECT`. A strong `L^2` subsequence preserves `Q=||Psi||_2^2/2`. |

## Primary-source applicability notes

1. Pazy, *Semigroups of Linear Operators and Applications to Partial
   Differential Equations*, Springer, 1983,
   DOI `10.1007/978-1-4612-5561-1`, covers abstract Cauchy problems, nonlinear
   evolution equations, and PDE applications.  The paper does not invoke a
   numbered theorem from this book: the Fourier multiplier gives the required
   analytic-semigroup estimates directly.
2. Amann, *Linear and Quasilinear Parabolic Problems*, Vol. I, Birkhauser,
   1995, DOI `10.1007/978-3-0348-9221-6`, is likewise background for abstract
   analytic-semigroup theory.  No maximal-regularity or quasilinear theorem
   from it is used as an unstated premise.
3. Simon, “Compact sets in the space `L^p(0,T;B)`,” *Ann. Mat. Pura Appl.*
   146 (1987), 65–96, DOI `10.1007/BF01762360`, treats compactness from a
   compact spatial embedding and time regularity in Bochner spaces.  The
   paper's exact triplet is `H^4 compactly embedded in H^2 continuously
   embedded in L^2`, with both time exponents equal to two.  Manuscript
   v0.1.38 also proves this special case directly by Fourier truncation.

All remaining bibliography entries are prior-work comparisons or physical
context.  They are not premises of A2, R-157, or R-158.

## Adversarial checks

1. **Endpoint compactness.** The proof uses strong convergence in
   `L^2(0,T;H^2)`, not an unjustified compact embedding into
   `C([0,T];H^2)`.  Strong time continuity is obtained separately from the
   Hilbert-scale identity.
2. **Critical Sobolev exponent.** The `H^2 -> W^(1,6)` embedding is continuous
   at the three-dimensional endpoint; compactness is never claimed at that
   endpoint.  Compact `H^2 -> C^(0,alpha)` is used only for `alpha<1/2`.
3. **Uniform nonlinear constant.** The Lipschitz constant is taken on the
   common energy-controlled `H^2` ball, so it is independent of the Galerkin
   index but may depend on the finite time interval and initial energy.
4. **Initial endpoint.** The Galerkin initial data converge in `H^2`, their
   energies converge, and the spectral midpoint identity gives the exact
   chain rule through `s=0`.
5. **No false externalization.** A passing structural parser only verifies
   that these hypotheses and proof components are present.  It does not judge
   their mathematical correctness or substitute for the signed independent
   audit.

## Remaining review authority

The internal applicability disposition is `READY FOR SIGNED AUDIT`, not
`EXTERNALLY VERIFIED`.  Completion still requires:

- an independent mathematician to check each row against the exact equations
  and return `PASS` or a precise repair;
- the canonical source owner to resolve the Class-II Laplacian convention;
- a specialist to review the prior-work/novelty crosswalk; and
- the operator to confirm the final integrated package, commit, backup, and
  later capstone state.

Reopen this audit after any change to the operator, nonlinear map, field
space, domain, time regularity, compactness proof, ensemble, or cited analytic
source.