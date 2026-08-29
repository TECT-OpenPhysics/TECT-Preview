import Mathlib

namespace Tect.R422

/- R422 formalizes the conservative scalar two-block reserve only.  The Q3
   matrix lane, its finite-grid diagnostics, common cores and all limits remain
   outside this Lean checkpoint. -/

theorem abs_product_budget (x y : ℝ) :
    2 * |x * y| ≤ x ^ 2 + y ^ 2 := by
  rw [abs_mul]
  have hx : 0 ≤ |x| := abs_nonneg x
  have hy : 0 ≤ |y| := abs_nonneg y
  have hsqx : |x| ^ 2 = x ^ 2 := sq_abs x
  have hsqy : |y| ^ 2 = y ^ 2 := sq_abs y
  nlinarith [sq_nonneg (|x| - |y|)]

theorem two_by_two_reserve_bound
    (a b eta x y lambda : ℝ)
    (_ha : 0 ≤ a) (_hb : 0 ≤ b) (heta : 0 ≤ eta)
    (hlambda : lambda = min a b - eta) :
    lambda * (x ^ 2 + y ^ 2) ≤ a * x ^ 2 + b * y ^ 2 + 2 * eta * x * y := by
  have hmin_a : min a b ≤ a := min_le_left _ _
  have hmin_b : min a b ≤ b := min_le_right _ _
  have hdiag : min a b * (x ^ 2 + y ^ 2) ≤ a * x ^ 2 + b * y ^ 2 := by
    have hx : 0 ≤ x ^ 2 := sq_nonneg x
    have hy : 0 ≤ y ^ 2 := sq_nonneg y
    nlinarith [mul_nonneg (sub_nonneg.mpr hmin_a) hx,
      mul_nonneg (sub_nonneg.mpr hmin_b) hy]
  have hbudget : 2 * eta * |x * y| ≤ eta * (x ^ 2 + y ^ 2) := by
    have h := abs_product_budget x y
    have hm := mul_le_mul_of_nonneg_left h heta
    nlinarith
  have hcross : -eta * (x ^ 2 + y ^ 2) ≤ 2 * eta * x * y := by
    have habs : -|x * y| ≤ x * y := neg_abs_le (x * y)
    have hm : -2 * eta * |x * y| ≤ 2 * eta * (x * y) := by
      have hmul := mul_le_mul_of_nonneg_left habs (show 0 ≤ 2 * eta by positivity)
      nlinarith
    nlinarith
  rw [hlambda]
  nlinarith [hdiag, hbudget, hcross]

theorem reserve_eigenvalue_nonnegative_condition
    (a b eta : ℝ) (hmin : eta ≤ min a b) :
    0 ≤ min a b - eta := by
  linarith

theorem finite_scope :
    (0 : ℝ) < (1 : ℝ) / 40 ∧ (4 : ℝ) > 0 ∧ (3 : ℕ) < 12 := by
  norm_num

end Tect.R422
