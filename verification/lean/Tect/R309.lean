import Mathlib

namespace Tect.R309

/- R309 checks the exact polynomial identities behind EXP-001139.  It does
   not formalize Gibbs integration by parts, boundary limits, modular
   derivatives, operator domains, or any thermodynamic/QFT limit. -/

theorem potential_completion_square (q : Rat) :
    17 / 12 - q ^ 2 / 2 + 3 * q ^ 4 / 20 =
      1 + 3 * (q ^ 2 - 5 / 3) ^ 2 / 20 := by
  ring

theorem potential_quartic_lower_fixture (q : Rat) :
    q ^ 4 / 20 ≤ 17 / 12 - q ^ 2 / 2 + 3 * q ^ 4 / 20 := by
  nlinarith [sq_nonneg (q ^ 2 - 5 / 2)]

theorem resolvent_first_derivative_formula (q : Rat) :
    (16 + q ^ 2) ^ 2 * (16 * (16 - q ^ 2) / (16 + q ^ 2) ^ 2) =
      16 * (16 - q ^ 2) := by
  have hden : (16 + q ^ 2 : Rat) ≠ 0 := by
    positivity
  field_simp [hden]

theorem resolvent_second_derivative_formula (q : Rat) :
    (16 + q ^ 2) ^ 3 * (32 * q * (q ^ 2 - 48) / (16 + q ^ 2) ^ 3) =
      32 * q * (q ^ 2 - 48) := by
  have hden : (16 + q ^ 2 : Rat) ≠ 0 := by
    positivity
  field_simp [hden]

theorem beta_envelope_fixture (beta : Rat) :
    (1 + 1) / beta = 2 / beta := by
  ring

theorem product_rule_algebra_fixture (fpp fp h hp : Rat) :
    fpp * h + fp * hp = fpp * h + fp * hp := by
  rfl

end Tect.R309
