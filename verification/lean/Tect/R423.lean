import Mathlib

namespace Tect.R423

/- R423 formalizes only the scalar edgewise Cauchy-capacity envelope and the
   resulting two-block reserve.  Directed maxima, Q3 matrices, common cores
   and all uniform/physical limits remain executable/open analysis. -/

theorem scalar_cauchy_capacity (rhoC rhoT x y : ℝ)
    (hC : 0 ≤ rhoC) (hT : 0 ≤ rhoT) :
    2 * Real.sqrt (rhoC * rhoT) * |x * y| ≤
      rhoC * x ^ 2 + rhoT * y ^ 2 := by
  have hprod : 0 ≤ rhoC * rhoT := mul_nonneg hC hT
  have hCroot : (Real.sqrt rhoC) ^ 2 = rhoC := by
    simpa using Real.sq_sqrt hC
  have hTroot : (Real.sqrt rhoT) ^ 2 = rhoT := by
    simpa using Real.sq_sqrt hT
  have hrootprod : Real.sqrt (rhoC * rhoT) = Real.sqrt rhoC * Real.sqrt rhoT := by
    simpa [Real.sqrt_mul hC]
  have hsquare := sq_nonneg (Real.sqrt rhoC * |x| - Real.sqrt rhoT * |y|)
  have hxabs : |x| ^ 2 = x ^ 2 := sq_abs x
  have hyabs : |y| ^ 2 = y ^ 2 := sq_abs y
  rw [abs_mul, hrootprod]
  nlinarith

theorem capacity_reserve_bound
    (a b rhoC rhoT z x y : ℝ)
    (ha : 0 ≤ a) (hb : 0 ≤ b) (hC : 0 ≤ rhoC) (hT : 0 ≤ rhoT)
    (hz : |z| ≤ Real.sqrt (rhoC * rhoT)) :
    (min a b - Real.sqrt (rhoC * rhoT)) * (x ^ 2 + y ^ 2) ≤
      a * x ^ 2 + b * y ^ 2 + 2 * z * x * y := by
  have hcap : 0 ≤ Real.sqrt (rhoC * rhoT) := Real.sqrt_nonneg _
  have hmin_a : min a b ≤ a := min_le_left _ _
  have hmin_b : min a b ≤ b := min_le_right _ _
  have hdiag : min a b * (x ^ 2 + y ^ 2) ≤ a * x ^ 2 + b * y ^ 2 := by
    have hx : 0 ≤ x ^ 2 := sq_nonneg x
    have hy : 0 ≤ y ^ 2 := sq_nonneg y
    nlinarith [mul_nonneg (sub_nonneg.mpr hmin_a) hx,
      mul_nonneg (sub_nonneg.mpr hmin_b) hy]
  have hcapacity := scalar_cauchy_capacity rhoC rhoT x y hC hT
  have hzxy : |z * x * y| ≤ Real.sqrt (rhoC * rhoT) * |x * y| := by
    calc
      |z * x * y| = |z| * |x| * |y| := by rw [abs_mul, abs_mul]
      _ = |z| * |x * y| := by rw [abs_mul]; ring
      _ ≤ Real.sqrt (rhoC * rhoT) * |x * y| := by
        exact mul_le_mul_of_nonneg_right hz (abs_nonneg (x * y))
  have habs_product : 2 * |x * y| ≤ x ^ 2 + y ^ 2 := by
    rw [abs_mul]
    nlinarith [sq_nonneg (|x| - |y|), sq_abs x, sq_abs y]
  have hbudget : 2 * Real.sqrt (rhoC * rhoT) * |x * y| ≤
      Real.sqrt (rhoC * rhoT) * (x ^ 2 + y ^ 2) := by
    have hmul := mul_le_mul_of_nonneg_left habs_product hcap
    nlinarith
  have hcross : -Real.sqrt (rhoC * rhoT) * (x ^ 2 + y ^ 2) ≤ 2 * z * x * y := by
    have hneg : -2 * Real.sqrt (rhoC * rhoT) * |x * y| ≤ 2 * z * x * y := by
      have hlow : -|z * x * y| ≤ z * x * y := neg_abs_le (z * x * y)
      have hmul := mul_le_mul_of_nonneg_left hlow (show 0 ≤ 2 by norm_num)
      have hbound : -2 * Real.sqrt (rhoC * rhoT) * |x * y| ≤ -2 * |z * x * y| := by
        nlinarith [hzxy]
      linarith
    nlinarith [hbudget, hneg]
  nlinarith [hdiag, hcross]

theorem finite_scope :
    (0 : ℝ) < (1 : ℝ) / 40 ∧ (4 : ℝ) > 0 ∧ (0 : ℝ) ≤ Real.sqrt ((2 : ℝ) * 3) := by
  norm_num

end Tect.R423
