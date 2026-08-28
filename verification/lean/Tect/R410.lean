import Mathlib

namespace Tect.R410

theorem mode_envelope_nonnegative {x : ℝ} (hx : 0 ≤ x) : 0 ≤ x := hx

theorem zeta_bound_nonnegative {c : ℝ} (hc : 0 < c) : 0 ≤ (1 : ℝ) / c := by
  exact le_of_lt (one_div_pos.mpr hc)

theorem finite_scope :
    (0 < (1 : ℝ) / 2) ∧ ((1 : ℝ) / 2 ≤ 1) ∧ (0 ≤ (3 : ℝ) / 5) := by
  norm_num

end Tect.R410
