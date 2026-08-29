import Mathlib

namespace Tect.R425

/- This file checks only the scalar bookkeeping used by the expanded finite
   Schur stress.  Matrix rows, Gibbs reconstruction and all limit interfaces
   remain executable/open analysis. -/

theorem harmonic_residual_bookkeeping (a b x y : ℝ) :
    a * x ^ 2 + b * y ^ 2 =
      ((a + b) / 2) * (x ^ 2 + y ^ 2) + ((a - b) / 2) * (x ^ 2 - y ^ 2) := by
  ring

theorem expanded_grid_lower_envelope
    (a b x y : ℝ) (ha : 0 ≤ a) (hb : 0 ≤ b) :
    min a b * (x ^ 2 + y ^ 2) ≤ a * x ^ 2 + b * y ^ 2 := by
  have hmin_a : min a b ≤ a := min_le_left _ _
  have hmin_b : min a b ≤ b := min_le_right _ _
  have hx : 0 ≤ x ^ 2 := sq_nonneg x
  have hy : 0 ≤ y ^ 2 := sq_nonneg y
  nlinarith [mul_nonneg (sub_nonneg.mpr hmin_a) hx,
    mul_nonneg (sub_nonneg.mpr hmin_b) hy]

theorem finite_scope :
    (0 : ℝ) < (1 : ℝ) / 40 ∧ (0 : ℝ) < 4 ∧ (0 : ℝ) ≤ min (2 : ℝ) 3 := by
  norm_num

end Tect.R425
