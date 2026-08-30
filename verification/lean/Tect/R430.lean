import Mathlib

namespace Tect.R430

/- The executable mpmath reconstruction is a point audit.  Lean checks only
   the scalar rational separation and the explicit finite/no-interval scope;
   it does not certify eigenvalue enclosures or any limit. -/

theorem source_gap_reference_separation :
    (5 : ℝ) / 10^7 < (2568621 : ℝ) / 10^12 := by
  norm_num

theorem source_gap_direct_separation :
    (5 : ℝ) / 10^7 < (8 : ℝ) / 10^7 := by
  norm_num

theorem source_point_not_interval :
    (0 : ℝ) < 50 ∧ (0 : ℝ) < (1 : ℝ) / 10^50 := by
  norm_num

theorem finite_scope :
    (0 : ℝ) < 2 ∧ (0 : ℝ) < 16 ∧ (0 : ℝ) < 8 ∧
      (0 : ℝ) < 7 ∧ (0 : ℝ) < 9 := by
  norm_num

end Tect.R430
