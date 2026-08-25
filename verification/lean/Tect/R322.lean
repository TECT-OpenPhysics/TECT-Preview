import Mathlib

namespace Tect.R322

/- R322 checks only the exact rational coefficient composition for EXP-001152.
   It does not formalize the upstream Gibbs-moment authority, the analytic
   polynomial inequalities, unbounded CCR domains, or any thermodynamic limit. -/

theorem onsite_force_coefficient_fixture :
    8 * (((-9 / 2 : Rat)^4) / (1 / 100 : Rat) +
      ((3 / 5 : Rat)^4) / ((1 / 100 : Rat)^3)) = 1364850 := by
  norm_num

theorem edge_force_polynomial_fixture :
    (2 * (1 : Rat) + 4 * (1 / 10 : Rat))^4 = 20736 / 625 := by
  norm_num

theorem pair_moment_fixture :
    9 * (((139 / 4 : Rat)^3) + 2 * (15 : Rat)^3 * 3) =
      35834571 / 64 := by
  norm_num

theorem force_fourth_fixture :
    8 * ((1364850 : Rat) * 3 +
      (6 : Rat)^4 * ((220167604224 / 5 : Rat))) =
      2282697884376432 / 5 := by
  norm_num

theorem kinetic_fixture :
    ((1 / 4 : Rat)^4) * (64 * 3 + (1 / 4 : Rat)^4) =
      49153 / 65536 := by
  norm_num

theorem full_safe_bound_fixture :
    2 * ((49153 / 65536 : Rat) +
      2 * (1 / 4 : Rat)^2 * (2282697884376432 / 5 : Rat)) =
      18699861068811976709 / 163840 := by
  norm_num

theorem scope_fixture :
    (True ∧ True ∧ True ∧ True ∧ True ∧ True) ∧
      ¬ (False ∨ False ∨ False ∨ False ∨ False) := by
  norm_num

end Tect.R322
