import Mathlib

namespace Tect.R426

/- R426 formalizes only scalar bookkeeping for the high-cutoff finite stress.
   Gibbs reconstruction, matrix spectra and every regulator limit remain
   executable/open analysis. -/

theorem high_cutoff_grid :
    (14 : ℕ) < 16 ∧ (16 : ℕ) < 18 ∧ (18 : ℕ) < 20 ∧
      (20 : ℕ) < 24 ∧ (24 : ℕ) < 28 ∧ (28 : ℕ) < 30 ∧ (30 : ℕ) < 32 := by
  norm_num

theorem positive_envelope (a b x y : ℝ) :
    min a b * (x ^ 2 + y ^ 2) ≤ a * x ^ 2 + b * y ^ 2 := by
  have hmin_a : min a b ≤ a := min_le_left _ _
  have hmin_b : min a b ≤ b := min_le_right _ _
  have hx : 0 ≤ x ^ 2 := sq_nonneg x
  have hy : 0 ≤ y ^ 2 := sq_nonneg y
  nlinarith [mul_nonneg (sub_nonneg.mpr hmin_a) hx,
    mul_nonneg (sub_nonneg.mpr hmin_b) hy]

theorem finite_scope :
    (0 : ℝ) < (1 : ℝ) / 40 ∧ (0 : ℝ) < 4 ∧ (0 : ℝ) < (1 : ℝ) / 10^8 := by
  norm_num

end Tect.R426
