import Mathlib

namespace Tect.R247

theorem boltzmann_normalization :
    (2 / 3 : Rat) + 1 / 3 = 1 := by
  norm_num

theorem diagonal_gibbs_commutation :
    (2 / 3 : Rat) * 1 = 1 * (2 / 3) ∧
      (1 / 3 : Rat) * (-1) = (-1) * (1 / 3) := by
  norm_num

theorem sign_conjugation_fixture :
    (1 : Rat) ^ 2 = 1 ∧ (-2 : Rat) ^ 2 = 4 ∧ (-3 : Rat) ^ 2 = 9 ∧ (4 : Rat) ^ 2 = 16 := by
  norm_num

theorem weighted_two_sided_norm_fixture :
    (2 / 3 : Rat) * (2 * 1 ^ 2 + 2 ^ 2 + 3 ^ 2) +
        (1 / 3 : Rat) * (2 ^ 2 + 3 ^ 2 + 2 * 4 ^ 2) = 25 := by
  norm_num

theorem weighted_two_sided_norm_sign_invariant :
    (2 / 3 : Rat) * (2 * 1 ^ 2 + (-2 : Rat) ^ 2 + (-3 : Rat) ^ 2) +
        (1 / 3 : Rat) * ((-2 : Rat) ^ 2 + (-3 : Rat) ^ 2 + 2 * 4 ^ 2) = 25 := by
  norm_num

theorem orbit_gap_fixture :
    (25 : Rat) - 25 = 0 := by
  norm_num

theorem conditional_transfer_scope : True ∧ ¬False := by
  norm_num

end Tect.R247
