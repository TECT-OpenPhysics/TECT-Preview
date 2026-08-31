import Mathlib

namespace Tect.R468

theorem interpolation_weight_bounds
    {a b q : ℚ} (hab : a < b) (hqa : a ≤ q) (hqb : q ≤ b) :
    0 ≤ (q - a) / (b - a) ∧ 0 ≤ (b - q) / (b - a) := by
  have hpos : 0 < b - a := sub_pos.mpr hab
  constructor
  · exact div_nonneg (sub_nonneg.mpr hqa) (le_of_lt hpos)
  · exact div_nonneg (sub_nonneg.mpr hqb) (le_of_lt hpos)

theorem interpolation_weight_sum
    {a b q : ℚ} (hab : a < b) :
    (b - q) / (b - a) + (q - a) / (b - a) = 1 := by
  have hne : b - a ≠ 0 := ne_of_gt (sub_pos.mpr hab)
  field_simp [hne]
  ring

theorem covering_closed_interval
    {start stop q : ℚ} (hstart : start ≤ q) (hstop : q ≤ stop) :
    start ≤ q ∧ q ≤ stop := by
  exact ⟨hstart, hstop⟩

theorem nearest_tie_break_is_ordered
    {d₁ d₂ : ℚ} (h : d₁ ≤ d₂) : d₁ ≤ d₂ := by
  exact h

end Tect.R468
