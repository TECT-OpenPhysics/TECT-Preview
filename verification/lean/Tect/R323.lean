import Mathlib

namespace Tect.R323

/- R323 checks only the exact rational composition and finite-time scaling for
   EXP-001153.  It does not formalize the upstream Gibbs isometry, unbounded
   CCR domains, modular derivatives, product closure or thermodynamic limits. -/

theorem multi_support_kinetic_fixture :
    2 * (2 : Rat)^3 * (
      ((1 / 4 : Rat)^4) * (32 * 3 + (1 / 4 : Rat)^4 / 2) +
      ((-1 / 3 : Rat)^4) * (32 * 3 + (-1 / 3 : Rat)^4 / 2)) =
      1341774241 / 53747712 := by
  norm_num

theorem force_safe_fixture :
    2 * ((7 / 12 : Rat)^2) * (2282697884376432 / 5 : Rat) =
      1553502726867294 / 5 := by
  norm_num

theorem full_word_fixture :
    2 * ((1341774241 / 53747712 : Rat) +
      (1553502726867294 / 5 : Rat)) =
      83497217154884689002533 / 134369280 := by
  norm_num

theorem duhamel_one_orientation_fixture :
    (1 / 3 : Rat)^4 *
      (83497217154884689002533 / 134369280 : Rat) / 4 =
      83497217154884689002533 / 43535646720 := by
  norm_num

theorem duhamel_two_orientation_fixture :
    (1 / 3 : Rat)^4 *
      (83497217154884689002533 / 134369280 : Rat) =
      83497217154884689002533 / 10883911680 := by
  norm_num

theorem product_cost_fixture :
    2 * (2 : Rat)^2 + (7 / 2 : Rat)^2 = 81 / 4 ∧
      21 * (81 / 4 : Rat) = 1701 / 4 := by
  norm_num

theorem kernel_fixture :
    (((1 / 3 : Rat)^2) / 2)^2 = 1 / 324 := by
  norm_num

theorem scope_fixture :
    (True ∧ True ∧ True ∧ True ∧ True) ∧
      ¬ (False ∨ False ∨ False ∨ False ∨ False ∨ False ∨ False) := by
  norm_num

end Tect.R323
