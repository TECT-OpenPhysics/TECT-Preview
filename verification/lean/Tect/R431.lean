import Mathlib

namespace Tect.R431

/- The executable interval lanes certify one fixed rounded finite matrix.  Lean
   checks the rational threshold arithmetic and keeps the source/limit scope
   explicit; it does not reimplement the Python interval eigensolver. -/

theorem rounded_snapshot_r422_separation :
    (5 : ℝ) / 10^7 <
      (53631875357 : ℝ) / 10^10 - (5363184967163699 : ℝ) / 10^15 := by
  norm_num

theorem rounded_snapshot_direct_separation :
    (5 : ℝ) / 10^7 <
      (5363188350047810 : ℝ) / 10^15 - (53631875359 : ℝ) / 10^10 := by
  norm_num

theorem rounded_snapshot_bracket_width :
    (53631875359 : ℝ) / 10^10 - (53631875357 : ℝ) / 10^10 <=
      (3 : ℝ) / 10^10 := by
  norm_num

theorem finite_snapshot_scope :
    (0 : ℝ) < 2 ∧ (0 : ℝ) < 16 ∧ (0 : ℝ) < 8 ∧
      (0 : ℝ) < 7 ∧ (0 : ℝ) < 9 := by
  norm_num

end Tect.R431
