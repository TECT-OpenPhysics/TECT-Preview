import Mathlib

namespace Tect.R204

/-!
  Scalar checks for the cutoff-uniform diagonal-Gaussian Fourier comparison
  bound.  The lattice split and convergence argument are stated in the
  certificate; this file checks the exact shell polynomial, pointwise
  majorant, and assembled rational constants without importing a production
  heat/root map.
-/

theorem max_shell_card (m : ℚ) :
    (2 * m + 1) ^ 3 - (2 * m - 1) ^ 3 = 24 * m ^ 2 + 2 := by
  ring

theorem shell_weight_bound (m : ℚ) (hm : 1 ≤ m) :
    (24 * m ^ 2 + 2) / (1 + m ^ 2) ^ 2 ≤ 26 / m ^ 2 := by
  have hm0 : 0 < m := by linarith
  have hm2 : 0 < m ^ 2 := sq_pos_of_pos hm0
  have hden : 0 < (1 + m ^ 2) ^ 2 := by positivity
  apply (div_le_div_iff₀ hden hm2).2
  nlinarith [sq_nonneg m, sq_nonneg (m ^ 2)]

theorem convolution_multiplier :
    (2 : ℚ) * 4 ^ 2 = 32 := by
  norm_num

theorem l1_proxy_bound :
    (1 : ℚ) + 26 * 2 = 53 := by
  norm_num

theorem shell_sum_bound :
    (26 : ℚ) * 2 = 52 := by
  norm_num

theorem uniform_charge_bound :
    (6 : ℚ) * 32 * 53 * 52 = 529152 := by
  norm_num

theorem heat_ratio_le_one (r2 : ℚ) (hr : 0 ≤ r2) :
    r2 / (1 + r2) ≤ 1 := by
  have hden : 0 < 1 + r2 := by linarith
  apply (div_le_iff₀ hden).2
  linarith

end Tect.R204
