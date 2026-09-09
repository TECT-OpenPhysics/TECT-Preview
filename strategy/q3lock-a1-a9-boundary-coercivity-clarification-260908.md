# Q3LOCK A1--A9 finite and DLR boundary-coercivity clarification

Date: 2026-09-08. Exploration: EXP-001675. Task: T-054.
Status: T0 proof-text precision repair and bounded A1--A9 reread;
claim_bearing=false; PDF deferred.
Authority chain: EXP-000780 -> EXP-000781 -> EXP-000782 / R-497.

## Question and scope

The A1--A9 packet was reread against the current manuscript, the Simon
finite-volume crosswalk, the KP general-vector crosswalk, and the existing
finite pressure and source-window audits.  The specific local question was
whether the DLR boundary coercivity estimate silently drops the imaginary-time
length when converting an $L^2$ boundary term into the quartic loop integral.
The reread also checked the finite form/trace, cyclic determinant, pressure
seam, open-box limit, KP envelope, source-window Holder closure, projective
tail direction, and Feller/source-limit interfaces.

## Finding

The displayed coercivity constant was already dimensionally correct,

\[
 C_{\Delta,K}=\beta n\{C_0+J_0^2/(8A)\}+B_K,
\]

but the preceding sentence used an undefined scalar $s$ and did not show the
factor of $\beta$.  The manuscript now sets
$S_y=\|\omega_y\|_{L^2}^2$ and writes
$S_y^2\leq\beta\int_0^\beta|\omega_y|^4$.  Completing the square gives

\[
 \frac A2\int_0^\beta|\omega_y|^4+\frac{\beta J_0^2}{8A}
 \geq \frac{J_0}{2}S_y.
\]

This is a proof-text clarification, not a new bound or a tier change.  The
bounded A1--A9 reread found no additional local sign, factor, edge-count,
source-normalization, limit-order, or topology-direction defect.  In
particular, the absolute harmonic trace factor remains separate from the KP
residual normalizer, and the source-window recursion still proves finiteness
before the Holder fixed-point division.

## Adversarial checks

1. Replacing $S_y^2\leq\beta Q_y$ by $S_y^2\leq Q_y$ would lose a factor of
   $\beta$; the explicit completion-of-square line rejects that shortcut.
2. Using the faster-decaying weight $\alpha_{k+1}>\alpha_k$ would not control
   the $\alpha_k$ tail; the manuscript retains $\alpha_{k+1}<\alpha_k$.
3. Treating the normalized KP loop factor as the absolute heat trace would
   omit $Z_a$; the finite-volume section retains the harmonic trace factor.
4. Replacing the positive seam interaction by a bounded perturbation would
   invalidate the open/periodic pressure transfer; the $288$ endpoint budget
   and form sandwich remain explicit.
5. Treating finite source analyticity as an entire logarithm would ignore
   complex zeros; the manuscript asserts only entire $Z_L$ and real-analytic
   pressure on the real axis.

## Boundary

The clarification does not close A1--A9.  The common form/core and kernel
passage, the cited Simon and KP hypothesis maps, the thermodynamic pressure
limit, source-window estimates, projective compactness, Feller passage, and
source-to-zero DLR composition still require signed location-specific
independent review.  No cusp, DLR multiplicity, phase theorem, claim-tier
promotion, novelty or priority conclusion, TECT-sector conclusion,
submission, release, or PDF follows.  The paper remains T0,
claim_bearing=false, and PDF-deferred.

## Next gate

Issue a fresh non-overwriting replay family for the one-line coercivity
clarification, then send the A1--A9 packet and its replay hashes to the
independent mathematical reviewer.  Keep PDF generation blocked until all
proof rows, literature scope, content organization, and release checks are
finished.
