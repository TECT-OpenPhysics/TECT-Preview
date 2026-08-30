import Mathlib

namespace Tect.R433

/- Lean cross-checks the finite arithmetic and fixed probe separation used by
   R-433.  The directed interval source, Gibbs propagation and residual
   matrix remain executable Python evidence; no limit or physical statement
   is encoded here. -/

theorem source_block_dimensions :
    (72 : ℕ) + 56 + 64 + 64 = 256 := by
  norm_num

theorem polar_residual_bound :
    (2 : ℚ) * (1 / 10^40) < 1 / 2 := by
  norm_num

theorem corrected_row_interval_separation :
    (53631875 : ℚ) / 10^7 > (5363185467163699 : ℚ) / 10^15 ∧
    (5363187535786933 : ℚ) / 10^15 < (5363187850047810 : ℚ) / 10^15 := by
  norm_num

theorem finite_source_scope :
    (2 : ℕ) = 2 ∧ (16 : ℕ) = 16 ∧ (16 : ℕ) * 16 = 256 := by
  norm_num

end Tect.R433
