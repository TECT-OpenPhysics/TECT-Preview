import Mathlib

namespace Tect.R436

/- Lean checks the scalar arithmetic for the d=18 finite certificate.  The
   interval matrix operations and eigenvalue enclosure remain executable
   Python evidence; this file contains no uniform or physical assertion. -/

theorem d18_block_dimensions :
    (90 : ℕ) + 72 + 81 + 81 = 324 := by
  norm_num

theorem finite_gap_probe_order :
    (43 : ℚ) / 10 < 22 / 5 ∧
    (22 : ℚ) / 5 < 9 / 2 := by
  norm_num

theorem unconditional_row_split :
    (8 : ℕ) + 10 = 18 ∧ (5 : ℕ) < 13 ∧ (13 : ℕ) < 18 := by
  norm_num

theorem finite_source_scope :
    (2 : ℕ) = 2 ∧ (18 : ℕ) * 18 = 324 ∧ (8 : ℕ) = 8 := by
  norm_num

end Tect.R436
