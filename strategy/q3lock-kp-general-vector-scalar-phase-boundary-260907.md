# Q3LOCK KP general-vector versus scalar-phase boundary audit

Date: 2026-09-07. Exploration: EXP-001620. Task: T-054.
Status: T0, claim_bearing=false, bounded source-applicability comparison only.
This note does not change the EXP-000780 -> EXP-000781 -> EXP-000782 authority
chain, promote a claim, or authorize a paper PDF.

## Primary source and locators

The source is Y. Kozitsky and T. Pasurek, *Euclidean Gibbs Measures of
Interacting Quantum Anharmonic Oscillators*, arXiv:math-ph/0609045v1,
https://arxiv.org/pdf/math-ph/0609045v1. The source-level locators used here
are:

* the Euclidean path representation and its vector loop space, equations
  (2.16)--(2.26), PDF pages 6--8;
* the general existence and compactness theorem, Theorems 3.1--3.4, PDF
  pages 19--20;
* the statement that the stochastic-order, FKG and low-temperature phase
  results in Section 3.2 are for ferroelectric scalar models \(\nu=1\), PDF
  pages 19--21;
* the scalar pressure limit, Theorem 3.10 and Corollary 3.11, PDF page 19;
* the scalar low-temperature coexistence theorem, Theorem 3.12 and
  equations (3.19)--(3.28), PDF pages 19--21;
* the discussion that a common infinite-volume algebraic time evolution is
  not available for the unbounded oscillator model, PDF pages 6--8.

This is a primary comparison source. Its theorems are not silently imported
as proof of the Q3LOCK phase conclusion.

## Hypothesis and conclusion map

| KP result | Source scope | Q3LOCK disposition |
|---|---|---|
| Theorem 3.1 | General \(\nu\)-dimensional oscillator model; nonempty compact tempered Euclidean Gibbs set for every \(\beta>0\) | Closest source for the existence/compactness block; applicability remains conditional on the paper's exact coercive envelope and source-window construction |
| Theorem 3.2 | Common exponential moment estimate for the general tempered set | Comparator for the uniform moment input; the Q3 source-window constants and limiting tangent passage still require the paper's own proof and audit |
| Theorems 3.3--3.4 | General support and high-temperature uniqueness, using the source's decomposition of the one-site potential | No low-temperature Q3 phase conclusion; high-temperature uniqueness is outside the target sufficient regime |
| Theorem 3.8 and its order/FKG machinery | Section 3.2 explicitly assumes ferroelectric scalar models \(\nu=1\) | Does not directly provide continuous-loop FKG or maximal/minimal states for the non-radial eight-component Q3 interaction |
| Theorem 3.10 / Corollary 3.11 | Scalar pressure in the Section 3.2 setting; differentiability implies singleton there | Not a direct pressure-to-DLR theorem for Q3; the paper retains its own finite/open/periodic pressure and source-tangent argument |
| Theorem 3.12 | \(d\ge3\), scalar even uniformly double-well potential, scalar \(J>0\), and threshold (3.27) | Fails at the model level: Q3 has \(\nu=8\) and a non-radial internal quartic, so the scalar polynomial hypotheses and scalar order cone are unavailable |
| Infinite-volume algebraic dynamics discussion | The source says common limiting automorphisms need not exist for unbounded oscillator Hamiltonians | Supports the paper's explicit nonclaim about a common real-time KMS dynamics; it does not replace a constructive KMS theorem |

## Consequence for the Q3LOCK proof architecture

The source cleanly separates two roles that must not be conflated:

1. General-vector DLR existence, compactness and moment control are a
   legitimate comparison/input lane, subject to a line-by-line check of the
   Q3 potential envelope, interaction summability and the source-window limit.
2. The source's order, FKG extremal states, scalar pressure result and
   low-temperature phase theorem belong to its \(\nu=1\) ferroelectric lane.
   They cannot be cited to prove the Q3LOCK non-radial phase sign.

The residual Q3-specific obligations are therefore unchanged but now have an
exact literature boundary: prove the continuous-loop association for the
actual eight-component non-radial density, establish the Hilbert-valued
infrared bound with the zero-mode subtraction, and supply the collective
Falk--Bruch lower bound and source-tangent DLR composition. A radial or scalar
replacement would be a different model.

## Adversarial checks and nonclaims

* **Vector-existence-to-vector-phase shortcut:** rejected. Theorem 3.1 does
  not imply multiplicity; UPHELD as a firewall.
* **Scalar-FKG-to-Q3 shortcut:** rejected. Section 3.2's order cone and
  maximal/minimal construction are explicitly scalar; UPHELD.
* **Pressure differentiability shortcut:** rejected. Corollary 3.11 is not a
  Q3 theorem and does not construct the required source-tangent pair.
* **Dynamics shortcut:** rejected. The source's warning about absent limiting
  automorphisms is a boundary, not a KMS construction.
* **Novelty shortcut:** rejected. Excluding these direct imports does not
  certify priority or publication value; specialist review remains open.

Disposition: **GENERAL DLR EXISTENCE/MOMENT COMPARATOR; SCALAR PHASE RESULTS
DO-NOT-APPLY DIRECTLY.** No theorem tier, claim status, or PDF status changes.
