import Mathlib

namespace Tect.R208

/-!
  Kernel cross-check for the scalar inequalities used by the Q3 matching-layer
  common-core envelope.  The analytic operator-domain hypotheses, tensor
  locality and exhaustion estimates remain outside this file.
-/

theorem shift_square {p q c d : ℝ} (hd : 0 ≤ d) :
    (p + d * c * q) ^ 2 ≤ (1 + d) * p ^ 2 + (d ^ 2 + d) * (c * q) ^ 2 := by
  have h1 : 0 ≤ d * (p - c * q) ^ 2 := mul_nonneg hd (sq_nonneg (p - c * q))
  have h2 : 0 ≤ d ^ 2 * (c * q) ^ 2 := mul_nonneg (sq_nonneg d) (sq_nonneg (c * q))
  nlinarith

theorem quartic_absorb (q : ℝ) : q ^ 2 ≤ 1 + q ^ 4 / 4 := by
  have h : 0 ≤ (q ^ 2 / 2 - 1) ^ 2 := sq_nonneg (q ^ 2 / 2 - 1)
  nlinarith

theorem matching_weight_transfer {fu fv qu qv kappa : ℝ}
    (hfu : 0 ≤ fu) (hfv : 0 ≤ fv) (hk : 0 ≤ kappa)
    (huf : fu ≤ kappa * fv) (hvf : fv ≤ kappa * fu) :
    fu * qv ^ 2 + fv * qu ^ 2 ≤ kappa * (fu * qu ^ 2 + fv * qv ^ 2) := by
  have hqv : 0 ≤ qv ^ 2 := sq_nonneg qv
  have hqu : 0 ≤ qu ^ 2 := sq_nonneg qu
  have h1 : 0 ≤ (kappa * fv - fu) * qv ^ 2 := mul_nonneg (sub_nonneg.mpr huf) hqv
  have h2 : 0 ≤ (kappa * fu - fv) * qu ^ 2 := mul_nonneg (sub_nonneg.mpr hvf) hqu
  nlinarith

end Tect.R208
