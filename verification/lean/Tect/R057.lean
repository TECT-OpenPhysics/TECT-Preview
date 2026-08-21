import Mathlib

namespace Tect.R057

/-
  Exact arithmetic core of the registered R-057 sharp-cube obstruction.
  The analytic inputs M_6 >= 8 and Q_6^2 >= 192 are supplied by the
  hash-pinned A12 theorem package; this file checks their ordered-field
  consequence and the comparison with the registered production target.
-/

theorem boundary_product {m q2 : ℚ} (hm : 8 ≤ m) (hq2 : 192 ≤ q2) :
    (786432 : ℚ) ≤ m ^ 4 * q2 := by
  have hm0 : (0 : ℚ) ≤ m := by linarith
  have hm2 : (64 : ℚ) ≤ m ^ 2 := by
    nlinarith [sq_nonneg (m - 8)]
  have hm4 : (4096 : ℚ) ≤ m ^ 4 := by
    nlinarith [sq_nonneg (m ^ 2 - 64)]
  have hq20 : (0 : ℚ) ≤ q2 := by linarith
  calc
    (786432 : ℚ) = 4096 * 192 := by norm_num
    _ ≤ m ^ 4 * 192 := by gcongr
    _ ≤ m ^ 4 * q2 := by gcongr

theorem sharp_boundary_arithmetic : (8 : ℚ) ^ 4 * 192 = 786432 := by
  norm_num

theorem production_target_gap :
    (2962571266025876 / 100000000000000 : ℚ) < 786432 := by
  norm_num

end Tect.R057
