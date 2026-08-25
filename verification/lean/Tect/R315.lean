import Mathlib

namespace Tect.R315

theorem weighted_gap_term (ell pi pj ki kj q : Rat)
    (hell : 0 <= ell) (hmean : 2 * ell <= pi + pj) (hq : 0 <= q) :
    2 * ell * (ki - kj) ^ 2 * q <=
      2 * (pi + pj) * (ki ^ 2 + kj ^ 2) * q := by
  have hgap : (ki - kj) ^ 2 <= 2 * (ki ^ 2 + kj ^ 2) := by
    nlinarith [sq_nonneg (ki + kj)]
  have h1 : (2 * ell * q) * (ki - kj) ^ 2 <=
      (2 * ell * q) * (2 * (ki ^ 2 + kj ^ 2)) := by
    exact mul_le_mul_of_nonneg_left hgap (by positivity)
  have h2 : (2 * ell) * (2 * (ki ^ 2 + kj ^ 2) * q) <=
      (pi + pj) * (2 * (ki ^ 2 + kj ^ 2) * q) := by
    exact mul_le_mul_of_nonneg_right hmean (by positivity)
  calc
    2 * ell * (ki - kj) ^ 2 * q = (2 * ell * q) * (ki - kj) ^ 2 := by ring
    _ <= (2 * ell * q) * (2 * (ki ^ 2 + kj ^ 2)) := h1
    _ = (2 * ell) * (2 * (ki ^ 2 + kj ^ 2) * q) := by ring
    _ <= (pi + pj) * (2 * (ki ^ 2 + kj ^ 2) * q) := h2
    _ = 2 * (pi + pj) * (ki ^ 2 + kj ^ 2) * q := by ring

theorem four_context_constant : (2 : Rat) * 4 = 8 := by
  norm_num

theorem coarse_trace_fixture :
    4 * ((10301 : Rat) / 101 + (1 ^ 2 + 101 ^ 2)) = 4162812 / 101 := by
  norm_num

theorem shifted_gap_fixture : (101 : Rat) - 1 = 100 := by
  norm_num

end Tect.R315
