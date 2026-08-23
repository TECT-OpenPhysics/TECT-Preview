import Mathlib

namespace Tect.R203

/-!
  Symbolic frequency cross-check for the finite F_ref/QFT and two-root
  production-cylinder interface.  The file does not identify a production
  heat-root map; it only proves the algebraic scale relation used by the
  audit.
-/

def kinetic (r z y m h : ℝ) : ℝ := r + z * (m * h) ^ 2 + y * (m * h) ^ 4

theorem scaled_square (m h : ℝ) : (m * (2 * h)) ^ 2 = 4 * (m * h) ^ 2 := by
  ring

theorem scaled_fourth (m h : ℝ) : (m * (2 * h)) ^ 4 = 16 * (m * h) ^ 4 := by
  ring

theorem formula_scale_difference (r z y m h : ℝ) :
    kinetic r z y m (2 * h) - kinetic r z y m h =
      3 * z * (m * h) ^ 2 + 15 * y * (m * h) ^ 4 := by
  simp [kinetic]
  ring

theorem root_norm_square (h : ℝ) : (2 * h) ^ 2 = 4 * h ^ 2 := by
  ring

theorem completed_square_identity (r z y q mu x : ℝ) (hy : y ≠ 0)
    (hq : q ^ 2 = -z / (2 * y)) (hmu : mu = r - z ^ 2 / (4 * y)) :
    r + z * x ^ 2 + y * x ^ 4 = y * (x ^ 2 - q ^ 2) ^ 2 + mu := by
  rw [hq, hmu]
  field_simp [hy]
  ring

end Tect.R203
