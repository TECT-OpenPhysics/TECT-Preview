import Mathlib

namespace Tect.R263

def mixedBoundSquared (u k h v : Rat) : Rat := (u * k)^2 + (u * k + h * v)^2

theorem mixed_bound_fixture :
    mixedBoundSquared 3 2 1 4 = 136 := by
  norm_num [mixedBoundSquared]

theorem force_fixture :
    (1 : Rat) * (2 - (-1)) + (1 / 10 : Rat) * (2 - (-1)) *
        (2 * 2^2 - 2 * (-1) + (-1)^2) / 2 = 93 / 20 := by
  norm_num

theorem force_prime_fixture :
    (1 : Rat) + (1 / 10 : Rat) *
        (2^2 + (-1)^2 + (2 - (-1))^2 + 4 * 2 * (2 - (-1))) / 2 = 29 / 10 := by
  norm_num

theorem product_rule_fixture :
    (93 / 20 : Rat) * (29 / 10) = 2697 / 200 := by
  norm_num

theorem finite_scaling_diagnostic_fixture :
    (33 : Rat) < 170 ∧ (170 : Rat) < 509 ∧ (509 : Rat) < 1190 := by
  norm_num

theorem scope_fixture : True ∧ ¬False := by
  norm_num

end Tect.R263
