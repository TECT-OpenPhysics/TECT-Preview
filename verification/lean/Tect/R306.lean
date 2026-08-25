import Mathlib

namespace Tect.R306

/- R306 checks the exact rational resolvent and polynomial-gap fixtures behind
   EXP-001136.  It does not formalize the operator commutator, state moments,
   QFT algebra, or any thermodynamic/continuum limit. -/

theorem resolvent_sum_fixture (x : Rat) :
    8 * (2 * x / (x ^ 2 + 16)) = 16 * x / (x ^ 2 + 16) := by
  ring

theorem modulus_gap_identity (x : Rat) :
    4 * (x ^ 2 + 16) ^ 2 - (16 * x) ^ 2 = 4 * (x ^ 2 - 16) ^ 2 := by
  ring

theorem modulus_square_bound (x : Rat) :
    (16 * x / (x ^ 2 + 16)) ^ 2 ≤ 4 := by
  have hden : 0 < x ^ 2 + 16 := by
    nlinarith [sq_nonneg x]
  have hden2 : 0 < (x ^ 2 + 16) ^ 2 := sq_pos_of_pos hden
  have hgap : 0 ≤ 4 * (x ^ 2 - 16) ^ 2 := by positivity
  rw [div_pow]
  apply (div_le_iff₀ hden2).2
  nlinarith [modulus_gap_identity x]

theorem derivative_gap_identity (x : Rat) :
    (x ^ 2 + 16) ^ 4 - (16 * (16 - x ^ 2)) ^ 2 =
      x ^ 2 * (x ^ 6 + 64 * x ^ 4 + 1280 * x ^ 2 + 24576) := by
  ring

theorem derivative_square_bound (x : Rat) :
    (16 * (16 - x ^ 2) / (x ^ 2 + 16) ^ 2) ^ 2 ≤ 1 := by
  have hden : 0 < (x ^ 2 + 16) ^ 4 := by
    positivity
  have hgap : 0 ≤ x ^ 2 * (x ^ 6 + 64 * x ^ 4 + 1280 * x ^ 2 + 24576) := by
    positivity
  rw [div_pow]
  have hpow : ((x ^ 2 + 16) ^ 2) ^ 2 = (x ^ 2 + 16) ^ 4 := by ring
  rw [hpow]
  apply (div_le_iff₀ hden).2
  nlinarith [derivative_gap_identity x]

theorem second_derivative_gap_identity (x : Rat) :
    (x ^ 2 + 16) ^ 6 - (32 * x * (x ^ 2 - 48)) ^ 2 =
      x ^ 12 + 96 * x ^ 10 + 3840 * x ^ 8 + 80896 * x ^ 6 +
        1081344 * x ^ 4 + 3932160 * x ^ 2 + 16777216 := by
  ring

theorem second_derivative_square_bound (x : Rat) :
    (32 * x * (x ^ 2 - 48) / (x ^ 2 + 16) ^ 3) ^ 2 ≤ 1 := by
  have hden : 0 < (x ^ 2 + 16) ^ 6 := by
    positivity
  have hgap :
      0 ≤ x ^ 12 + 96 * x ^ 10 + 3840 * x ^ 8 + 80896 * x ^ 6 +
        1081344 * x ^ 4 + 3932160 * x ^ 2 + 16777216 := by
    positivity
  rw [div_pow]
  have hpow : ((x ^ 2 + 16) ^ 3) ^ 2 = (x ^ 2 + 16) ^ 6 := by ring
  rw [hpow]
  apply (div_le_iff₀ hden).2
  nlinarith [second_derivative_gap_identity x]

theorem approximation_coefficient_fixture :
    (1 / 16 : Rat) ^ 2 = 1 / 256 := by
  norm_num

theorem support_bound_fixture :
    2 * (2 : Rat) ^ 2 + 1 * 4 ^ 0 = 9 := by
  norm_num

theorem cross_orientation_multiplier_fixture :
    (21 : Rat) * 9 = 189 := by
  norm_num

end Tect.R306
