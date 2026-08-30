import Mathlib

namespace Tect.R438

/- Lean checks the scalar arithmetic for the d=19 finite certificate.  The
   interval matrix operations and eigenvalue enclosure remain executable
   Python evidence; this file contains no uniform or physical assertion. -/

theorem d19_block_dimensions :
    (100 : ℕ) + 81 + 90 + 90 = 361 := by
  norm_num

theorem finite_gap_probe_order :
    (9 : ℚ) / 2 < 23 / 5 ∧
    (23 : ℚ) / 5 < 47 / 10 := by
  norm_num

theorem unconditional_row_split :
    (9 : ℕ) + 10 = 19 ∧ (5 : ℕ) < 14 ∧ (14 : ℕ) < 19 := by
  norm_num

theorem finite_source_scope :
    (2 : ℕ) = 2 ∧ (19 : ℕ) * 19 = 361 ∧ (8 : ℕ) = 8 := by
  norm_num

end Tect.R438
