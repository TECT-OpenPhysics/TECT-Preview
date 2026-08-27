import Mathlib

namespace Tect.R366

/- R366 formalizes the scalar square-function envelope used by the finite
   fractional Liouvillian pilot.  Matrix spectral calculations and all
   regulator limits stay in the executable lanes. -/

theorem fractional_half_envelope (y : ℝ) :
    min 4 (y ^ 2) ≤ 2 * |y| := by
  by_cases h : |y| ≤ 2
  · have hprod : 0 ≤ |y| * (2 - |y|) :=
      mul_nonneg (abs_nonneg y) (sub_nonneg.mpr h)
    have habs : |y| ^ 2 = y ^ 2 := sq_abs y
    have hsq : y ^ 2 ≤ 2 * |y| := by
      nlinarith
    exact le_trans (min_le_right 4 (y ^ 2)) hsq
  · have hbig : 2 ≤ |y| := le_of_not_ge h
    have hfour : (4 : ℝ) ≤ 2 * |y| := by nlinarith
    exact le_trans (min_le_left 4 (y ^ 2)) hfour

theorem fractional_theta_one_envelope (y : ℝ) :
    min 4 (y ^ 2) ≤ y ^ 2 :=
  min_le_right 4 (y ^ 2)

theorem scope_fixture :
    (True ∧ True ∧ True) ∧ ¬ (False ∨ False ∨ False ∨ False) := by
  norm_num

end Tect.R366
