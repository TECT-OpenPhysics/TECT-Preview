import Mathlib

namespace Tect.R382

/- R382 formalizes the scalar positivity facts used when reporting successive
   cutoff ratios.  The numerical profiles and their agreement are executable
   evidence; no monotonicity or continuum limit is asserted here. -/

theorem profile_ratio_nonnegative (a b : ℝ)
    (ha : 0 ≤ a) (hpos : 0 < b) :
    0 ≤ a / b := by
  exact div_nonneg ha (le_of_lt hpos)

theorem profile_ratio_zero_denominator (a : ℝ) (ha : 0 ≤ a) :
    0 ≤ a / 0 := by
  simp

theorem growth_warning_is_diagnostic (ratio threshold : ℝ) :
    ratio > threshold ∨ ¬ ratio > threshold := by
  by_cases h : ratio > threshold
  · exact Or.inl h
  · exact Or.inr h

theorem scope_fixture :
    (True ∧ True ∧ True ∧ True ∧ True) ∧
      ¬ (False ∨ False ∨ False ∨ False ∨ False ∨ False) := by
  norm_num

end Tect.R382
