import Mathlib

namespace Tect.R424

/- This file checks the scalar harmonic split and its finite lower-envelope
   bookkeeping.  Matrix eigensolvers, graph rows and limiting domains remain
   executable checks outside Lean. -/

theorem harmonic_energy_split (a b x y : ℝ) :
    a * x ^ 2 + b * y ^ 2 =
      ((a + b) / 2) * (x ^ 2 + y ^ 2) + ((a - b) / 2) * (x ^ 2 - y ^ 2) := by
  ring

theorem coarse_residual_lower_envelope
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

end Tect.R424
