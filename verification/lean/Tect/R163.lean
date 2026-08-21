import Mathlib

namespace Tect.R163

/-
  Exact rational core of the registered R-163 deterministic dyadic-forest
  boundary.  The analytic forest estimates and their hypotheses remain in the
  R-163 note; this file checks only the displayed rational margins.
-/

theorem retained_coefficient_gap :
    And ((4 : Rat) / 25 - 3 / 100 = 13 / 100)
      ((1 : Rat) / 10 < 13 / 100) := by
  norm_num

theorem t050_threshold_arithmetic :
    And ((5 : Rat) / 11 - 9 / 20 = 1 / 220)
      (And (-2 * ((1 : Rat) / 220) = -1 / 110)
        (-1 / 110 - 9 / 10 = -10 / 11)) := by
  norm_num

theorem sextic_window :
    (3 : Rat) / 20 < 27 / 100 := by
  norm_num

theorem recursive_tangent_guard :
    ((100 : Rat) / 97) ^ 4 < 13 / 10 := by
  norm_num

theorem source_third_derivative_fixture :
    (27 : Rat) / 5 * (3 / 2) / ((1 : Rat) / 2) ^ 5 = 1296 / 5 := by
  norm_num

theorem audit_margin_bundle :
    And ((4 : Rat) / 25 - 3 / 100 > 1 / 10)
      (And ((5 : Rat) / 11 - 9 / 20 = 1 / 220)
        (And (-1 / 110 - 9 / 10 = -10 / 11)
          (And ((3 : Rat) / 20 < 27 / 100)
            (((100 : Rat) / 97) ^ 4 < 13 / 10)))) := by
  norm_num

end Tect.R163
