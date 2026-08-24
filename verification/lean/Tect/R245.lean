import Mathlib

namespace Tect.R245

theorem rate_fixture :
    ((1382807 : Rat) / 7168) = 1382807 / 7168 := by
  norm_num

theorem eta_fixture :
    (2 : Rat) * 6 * 2 * (1382807 / 7168 : Rat) * (1 / 10000 : Rat)
      = 4148421 / 8960000 := by
  norm_num

theorem eta_small_fixture :
    (4148421 / 8960000 : Rat) < 1 := by
  norm_num

theorem denominator_fixture :
    1 - (4148421 / 8960000 : Rat) = 4811579 / 8960000 := by
  norm_num

theorem orbit_envelope_fixture :
    (163 : Rat) / (1 - (4148421 / 8960000 : Rat)) = 1460480000 / 4811579 := by
  norm_num

theorem remainder_fixture :
    (1 / 10000 : Rat)^2 * (163 : Rat) / (2 * (1 - (4148421 / 8960000 : Rat)))
      = 4564 / 3007236875 := by
  norm_num [div_pow]

theorem orientation_fixture :
    2 * ((1 / 10000 : Rat)^2 * (163 : Rat) / (2 * (1 - (4148421 / 8960000 : Rat))))
      = 9128 / 3007236875 := by
  norm_num [div_pow]

theorem modular_fixture :
    2 * (2 * ((1 / 10000 : Rat)^2 * (163 : Rat) / (2 * (1 - (4148421 / 8960000 : Rat)))))
      = 18256 / 3007236875 := by
  norm_num [div_pow]

theorem scope_fixture : True ∧ ¬False := by
  norm_num

end Tect.R245
