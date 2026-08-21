import Mathlib

namespace Tect.R190

/-!
  The algebraic lower bound used by the arbitrary-polarization two-mode
  A1 production-cylinder diagnostic.  The field-space moment inequalities
  and the positive Class-II quadratic form are supplied as hypotheses by the
  independent lane; Lean checks the exact rational consequence.
-/

def lowerPoly (s : Rat) : Rat :=
  s / 16 - (387 / 6400) * s ^ 2 + (27 / 800) * s ^ 3

theorem lowerPoly_factor (s : Rat) :
    lowerPoly s = s * (864 * s ^ 2 - 1548 * s + 1600) / 25600 := by
  norm_num [lowerPoly]
  ring

theorem lowerPoly_positive {s : Rat} (hs : 0 < s) : 0 < lowerPoly s := by
  have hsq : 0 ≤ (1728 * s - 1548) ^ 2 := sq_nonneg _
  have hquad : 0 < 864 * s ^ 2 - 1548 * s + 1600 := by
    nlinarith
  have hprod : 0 < s * (864 * s ^ 2 - 1548 * s + 1600) :=
    mul_pos hs hquad
  rw [lowerPoly_factor]
  positivity

theorem arbitrary_two_mode_nonnegative {s : Rat} (hs : 0 ≤ s) :
    0 ≤ lowerPoly s := by
  by_cases hpos : 0 < s
  · exact le_of_lt (lowerPoly_positive hpos)
  · have hz : s = 0 := by linarith
    simp [hz, lowerPoly]

theorem arbitrary_two_mode_strict {s : Rat} (hs : 0 < s) :
    0 < s / 16 - (387 / 6400) * s ^ 2 + (27 / 800) * s ^ 3 := by
  exact lowerPoly_positive hs

end Tect.R190
