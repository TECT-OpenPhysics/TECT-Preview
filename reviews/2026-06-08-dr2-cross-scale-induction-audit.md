# Operator adversarial audit -- DR-2 cross-scale induction (2026-06-08)

**Target**: `dr2-cross-scale-induction-260608-v1.0` (decoupling-iteration
energy bound), submitted at unrestricted DR-2 T5.

**Verdict**: NOT T5. Request a v1.1 repair of the iteration lemma. Do NOT flip
DR2-SHARE.

## Findings

1. **Recurring false identity (load-bearing).** Section 2's iteration lemma
   re-uses `||f_theta||_{L^4}^4 = E_+(Q_theta)` -- the SAME error class as the
   torus identity corrected in `dr2-decoupling-closure v1.1`. For `q in S^2`
   the frequencies are non-integer, so the unit-cube `L^4` integral is a product
   of sinc factors, not the additive-energy Kronecker count. Numerics do not
   replace the missing analytic bridge.

2. **Geometry overclaim.** Section 3 states the affine map sends a cap "exactly"
   to a unit paraboloid patch. A small cap of `S^2` is a uniformly-curved `C^2`
   graph, not literally the standard paraboloid; the affine map preserves
   additive energy exactly but does not map the sphere onto the paraboloid.

3. **One residual stated where there are two.** The honest residual is (R1) the
   local cap-`L^4`-norm to `E_+(Q_theta)` bridge, and (R2) the multi-scale
   eps-bookkeeping. v1.0 collapsed these into a single "cited bookkeeping".

## Requested repair (operator-supplied recommendation)

Rewrite the iteration lemma in Besicovitch / weighted-decoupling form:
define `M(F) := limsup_{R->inf} (1/|B_R|) int_{B_R} F`; establish
`M(|f_Q|^4) = E_+(Q)` for any finite `Q in S^2`; apply the weighted
Bourgain-Demeter decoupling inequality on balls `B_R`, average over translates,
and pass to the Besicovitch mean to obtain
`E_+(Q) <=_eps delta^{-eps} (sum_theta E_+(Q_theta)^{1/2})^2`.
Soften the rescaling: "The affine rescaling preserves additive energy exactly.
The rescaled cap is a uniformly curved graph patch, not literally the original
unit sphere. The decoupling constants remain uniform by the standard stability
of decoupling for nondegenerate C^2 perturbations of the paraboloid."

Keep the grade at T4+ / T5-candidate (not accepted T5); DR2-SHARE OPEN, B5 T5,
B1 T6, H-ADM-COH retained.

## Meta-feedback (binding)

Documents were being written without sufficient adversarial self-review.
Strengthen the self-review on every document before claiming a grade, audit the
code more thoroughly, and do not forget the established rules (versioned
re-issue, atomic writes, no overclaim, no self-flip).

## Disposition

- Repaired by `dr2-cross-scale-induction-260608-260608-v1.1` (Besicovitch-mean
  bridge; softened rescaling; two-residual framing R1/R2; grade withdrawn
  T5 -> T4+/T5-candidate; strengthened Section 5 self-adversarial review).
- Script `dr2_decoupling_iteration.py` v1.1: added an exact-E_+ code-audit gate
  (random set `= 2N^2 - N`) and an explicit PROXY-partition caveat (numerics
  ILLUSTRATIVE, not a faithful decoupling test).
- Memory `feedback-tect-thorough-self-review` recorded (the additive-energy /
  Besicovitch recurrence-class; rigorous code-audit habit).
- NO gate/tier/hypothesis flip. DR2-SHARE OPEN, B5 T5, B1 T6, H-ADM-COH retained.
