# Literature-first and proof-dependency audit

Target: the full random-coefficient current and centered energy of manuscript
sections 2--4, plus the explicit local and deterministic-background bounds.
Audit date 2026-11-12. Dispositions apply only to the printed fixed model.
Sources were inspected in their primary versions, not accepted from snippets.
No claim of exhaustive literature coverage or first priority is made.

## External applicability

| Source and exact locator | Assumption-to-model crosswalk | Disposition and imported conclusion |
|---|---|---|
| Gubinelli--Imkeller--Perkowski, Forum Math. Pi 3 (2015), e6, DOI 10.1017/fmp.2015.2; Lemmas 2.4 (p.15), 2.6 (pp.17--18), 2.7 (p.18) | SATISFIED: spatial Besov calculus, 1/3<alpha<1/2, beta=alpha, gamma=alpha-1, 2alpha-1<0<3alpha-1. Bounded nonlinearity hypothesis is satisfied after localization; fixed-floor polynomial constants and Gaussian moments remove localization. | APPLIES to commutator/paralinearization. The required Gaussian second level and cross-cutoff convergence are established separately in the paper. |
| Friz--Victoir, Differential equations driven by Gaussian signals, Ann. Inst. H. Poincare 46 (2010),369--413, DOI 10.1214/09-AIHP202; compare also the separate 2007 preprint 0711.0668, Theorem 1 | FAILED as a direct import: the cited rough-path theorem is for a one-parameter process with covariance variation and independence conditions, not a three-dimensional distribution. | DOES-NOT-APPLY to a linewise Stratonovich identification; comparator only. |
| Ohashi--Russo, Bernoulli 30(2) (2024),1197--1230; arXiv:2206.06865v2 Theorem4.1 pp.22--23, DOI10.3150/23-BEJ1629 | UNASSESSED/FAILED for direct transfer: no verified one-parameter restriction, covariance Assumptions A/B/C or Malliavin-integrand crosswalk for this 3D current. | DOES-NOT-APPLY as presently cited. The manuscript makes no such identification. |
| Chandra--Hairer, arXiv:1612.08138v5, Theorems2.33--2.34 pp.24--25 | UNASSESSED: no complete rule/type/homogeneity/cumulant/regularity-structure crosswalk is constructed for this direct rational coefficient. | Background only; NOT-YET-ASSESSED for black-box BPHZ use. No conclusion is imported. The work is cited as a preprint, not with an unverified journal assignment. |
| Coppini--Ruszel--Schuricht, arXiv:2507.05131, Theorem2.4 pp.9--10 and Proposition3.1 p.16 | FAILED as direct import: analytic Wick-functional correlations and distinct-point scaling limits are not the present L2(H^{-1-kappa}) limit with ordinary rational value coefficient. A Taylor series of 1/(rho+eps) about zero has finite radius and cannot be integrated globally without a separate argument. | Comparator. Exact finite Gaussian IBP is used instead of a formal global coefficient expansion. |
| Cipriani--Hazra--Rapoport--Ruszel, J. Stat. Phys.190:171 (2023), Theorem2, DOI10.1007/s10955-023-03187-3 | FAILED as direct import: order-two DGFF covariance, rescaling to white noise and local C^alpha target differ from the order-four fixed-Gaussian composite here. | Comparator; prevents a claim of introducing centered gradient squares. |
| Xu, Commun. Math. Stat.6 (2018),509--532, DOI10.1007/s40304-018-0162-9; arXiv:1810.03850v1, printed Assumptions1.2--1.3 p.4, Theorem1.4 p.5, Example1.6 p.6 | SATISFIED: stationary Gaussian setting and polynomial-growth smoothness. FAILED as direct full-target import: scalar positive singular value covariance with alpha>0, amplitude rescaling and chaos projection, versus the fixed torus's continuous vector value field and conditional derivative square with matrix coefficient. The admitted spectral class also differs from its mollifier setting. | DOES-NOT-APPLY as a direct theorem import; comparator only. Nonpolynomial nonlinearities are already included in Xu, so nonpolynomiality alone is not the contribution. No priority inference follows. |
| Bruned--Gabriel--Hairer--Zambotti, arXiv:1902.02884, Theorem1.2 | FAILED as direct import: one spatial dimension and a dynamical geometric SPDE, rather than this static three-dimensional Gaussian reference. | Comparator for nonlinear derivative products. |

Primary links: https://doi.org/10.1017/fmp.2015.2;
https://www.numdam.org/item/10.1214/09-AIHP202.pdf;
https://arxiv.org/pdf/2206.06865v2;
https://arxiv.org/pdf/1612.08138v5;
https://arxiv.org/pdf/2507.05131;
https://doi.org/10.1007/s10955-023-03187-3;
https://arxiv.org/pdf/1902.02884;
https://arxiv.org/pdf/1810.03850v1.

## Internal applicability and exact identity

The paper copies the A1 manifest byte-for-byte into sources/production-inputs.json
and pins its SHA-256. The exact quadratic symbol, L=16, eta_shell=0, floor,
family matrix, Pauli embedding, and coefficients a,b,c are printed. The
historically inconsistent residual and declared energy are not identified
with the standalone reference. The complex covariance has factor2; the
six-real covariance has factor1. All limits remove only a spectral cutoff
at fixed volume and floor under a common Gaussian coupling.

R-050 is used only for the same current target, with its proof rewritten in
full. Its claimed generic rate and prescribed dyadic assertion are not
inherited. R-051's energy is defined directly at each cutoff; products of
already rough currents are not silently assumed. R-194/R-195 supply the
critical escape boundary, not a missing coercivity estimate. The independent
carrier and deterministic-background results are not transferred to the
self-coupled Gaussian energy's exponential.

## Independent-check disposition

Three separate internal AI audits covered the current, energy/stability and
primary literature. They are internal reviews, not external referee reports.
The paper adds exact rational Wick-pairing tests with nonconstant polynomial
coefficients, distinct from the legacy connection-signature enumeration.
Fresh legacy checks run into new output paths; no issued report is replaced.
The finite audits do not prove the infinite-dimensional limits.

## Adversarial checks and residual contribution

- Convention/sign: real/complex half factor, two cross terms, three spatial
  directions, sextic gamma/6 and family-mass half factor are checked separately.
- Domain/regularity: rational coefficients fix eps>0; reconstruction includes
  the commutator and localization. Deterministic b acts on 18 derivative slots.
- Limits: bounded pointwise-convergent multipliers yield qualitative convergence,
  not a universal rate. Strong weighted kernel convergence handles arbitrary
  oscillatory admitted kernels. H^{-1} and eps removal are not claimed.
- Stability: local pointwise compensation, critical noncoercivity, and a
  deterministic-background exponential bound have distinct quantifiers.

Residual proposition: an explicit model construction with a nonpolynomial
value coefficient, exact conditional contraction and regulator comparison,
combined with sharp Pauli-dependent local compensation boundaries. The
standard commutator, Wick identity and determinant mechanism are not claimed
as new. This supports continuing a specialist-paper candidate; specialist
novelty review may still reclassify it as a technical application note.


## Supplementary audit, review edition 0.1.1

The Xu comparator was identified while preparing actual external review.
Its Theorem1.4 proves convergence of rescaled scalar nonlinear functionals
with lower chaos removed to a Wick power. Example1.6 includes suitable
C^{1+} polynomial-growth nonlinearities. Our claim is therefore not to have
introduced nonpolynomial Gaussian functions. It retains the mixed rational
value/derivative composite without amplitude rescaling and proves its
conditional-centering convergence directly. No theorem statement or model
coefficient is changed by this clarification.
