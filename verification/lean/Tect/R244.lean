import Mathlib

namespace Tect.R244

theorem initial_fourth_power_fixture :
    ((1 / 4 : Rat)^4) * (122099 / 35840 : Rat)^4 * (40 / 3 : Rat)^3
        * (35834571 / 64 : Rat)
      = 884928390316245388540002019 / 1267165160779284480 := by
  norm_num [div_pow]

theorem initial_safe_ceiling_fixture :
    ((1 / 4 : Rat)^4) * (122099 / 35840 : Rat)^4 * (40 / 3 : Rat)^3
        * (35834571 / 64 : Rat)
      <= (163 : Rat)^4 := by
  norm_num [div_pow]

theorem zero_initial_data_remainder_fixture (t k : Rat) (ht : 0 <= t) (hk : 0 <= k) :
    0 <= t^2 * k / 2 := by
  positivity

theorem two_orientation_fixture :
    (1 / 100 : Rat)^2 * ((163 : Rat) + 163) / 2 = 163 / 10000 := by
  norm_num

theorem modular_orientation_fixture :
    (1 / 100 : Rat)^2 * ((326 : Rat) + 326) / 2 = 163 / 5000 := by
  norm_num

theorem scalar_remainder_identity (t k : Rat) :
    (k * t^2 / 2) + (k * t^2 / 2) = k * t^2 := by
  ring

theorem scope_fixture : True ∧ ¬False := by
  norm_num

end Tect.R244
