import Mathlib

namespace Tect.R307

/- R307 checks the exact scaling witness behind EXP-001137.  It does not
   formalize a supremum theorem, operator domains, alternative weights, or
   any thermodynamic/continuum limit. -/

theorem epsilon_parameter_fixture (a : Rat) (ha : a ≠ 0) :
    (1 / (a ^ 2) : Rat) * a ^ 2 = 1 := by
  field_simp [ha]

theorem witness_value_fixture (a : Rat) (ha : a ≠ 0) :
    a ^ 2 * a / (a ^ 2 + a ^ 2) = a / 2 := by
  field_simp [ha]
  ring

theorem resolvent_coefficient_fixture (a x : Rat) :
    (a ^ 2 / 2) * (2 * x / (a ^ 2 + x ^ 2)) =
      a ^ 2 * x / (a ^ 2 + x ^ 2) := by
  ring

theorem same_form_growth_fixture (a : Rat) :
    2 * (a / 2) ^ 2 + 1 = a ^ 2 / 2 + 1 := by
  ring

theorem lower_bound_growth_samples :
    (2 * (2 / 2 : Rat) ^ 2 + 1 < 2 * (4 / 2 : Rat) ^ 2 + 1) ∧
      (2 * (4 / 2 : Rat) ^ 2 + 1 < 2 * (8 / 2 : Rat) ^ 2 + 1) ∧
        (2 * (8 / 2 : Rat) ^ 2 + 1 < 2 * (16 / 2 : Rat) ^ 2 + 1) := by
  norm_num

theorem approximation_decay_samples :
    (1 / (2 : Rat) ^ 4) > 1 / (4 : Rat) ^ 4 ∧
      (1 / (4 : Rat) ^ 4) > 1 / (8 : Rat) ^ 4 ∧
        (1 / (8 : Rat) ^ 4) > 1 / (16 : Rat) ^ 4 := by
  norm_num

end Tect.R307
