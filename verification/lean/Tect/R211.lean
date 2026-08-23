import Mathlib

namespace Tect.R211

theorem q3_force_fixture : (3 / 5 : Real) + 3 * (2 / 7) = 51 / 35 := by
  norm_num

theorem slope_gap : 0 < ((3 / 5 : Real) + 3 * (2 / 7)) * 2 - 2 := by
  norm_num

theorem fixture_difference :
    0 < (((3 / 5 : Real) + 3 * (2 / 7)) * 2 * 10 - 3 / 2 -
      (1 + 1 * 2 / (10 ^ 2)) * (2 * 10)) := by
  norm_num

theorem commutator_initial_bound (a : Real) : 2 * a = a + a := by
  ring

end Tect.R211
