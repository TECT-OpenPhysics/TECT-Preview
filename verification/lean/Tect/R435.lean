import Mathlib

namespace Tect.R435

/- Lean checks the scalar arithmetic for the d=17 finite certificate.  The
   interval matrix operations and eigenvalue enclosure remain executable
   Python evidence; this file contains no uniform or physical assertion. -/

theorem d17_block_dimensions :
    (81 : ℕ) + 64 + 72 + 72 = 289 := by
  norm_num

theorem finite_gap_probe_order :
    (21 : ℚ) / 5 < 17 / 4 ∧
    (17 : ℚ) / 4 < 43 / 10 := by
  norm_num

theorem unconditional_row_split :
    (9 : ℕ) + 8 = 17 ∧ (4 : ℕ) < 13 ∧ (13 : ℕ) < 17 := by
  norm_num

theorem finite_source_scope :
    (2 : ℕ) = 2 ∧ (17 : ℕ) * 17 = 289 ∧ (8 : ℕ) = 8 := by
  norm_num

end Tect.R435
