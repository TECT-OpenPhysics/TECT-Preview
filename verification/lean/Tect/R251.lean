import Mathlib

namespace Tect.R251

theorem bridge_fixture :
    9 * ((139 / 4 : Rat)^3 + 2 * (15 : Rat)^3 * 3) = 35834571 / 64 := by
  norm_num

theorem force_fourth_fixture :
    ((122099 / 35840 : Rat)^4) * (40 / 3 : Rat)^3 *
        (35834571 / 64 : Rat) =
      884928390316245388540002019 / 4949863909294080 := by
  norm_num

theorem force_ceiling_fixture :
    (884928390316245388540002019 / 4949863909294080 : Rat) <
      (423000 : Rat)^2 := by
  norm_num

theorem force_norm_upper_fixture :
    2 * (1 / 4 : Rat)^2 * 423000 = 52875 := by
  norm_num

theorem kinetic_upper_fixture :
    (49153 / 65536 : Rat) < 1 := by
  norm_num

theorem full_triangle_upper_fixture :
    (1 + 230 : Rat)^2 = 53361 := by
  norm_num

theorem scope_fixture : True ∧ ¬False := by
  norm_num

end Tect.R251
