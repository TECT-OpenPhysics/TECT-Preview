import Mathlib

namespace Tect.R219

theorem edge_shift_source_degree_one :
    (3 + 3 / 2 + 3 + 2 + 1 + 3 / 2 : Rat) = 12 := by
  norm_num

theorem edge_shift_source_degree_two :
    (3 + 3 + 1 + 3 / 2 + 2 + 3 / 2 : Rat) = 12 := by
  norm_num

theorem edge_shift_source_degree_three :
    (1 + 3 / 2 + 1 + 1 / 2 : Rat) = 4 := by
  norm_num

theorem q3_degree_fixture : (3 * 3 : Nat) = 9 := by
  norm_num

theorem top_shift_coefficient :
    (3 / 5 : Rat) + 3 * 4 * (2 / 7 : Rat) = 141 / 35 := by
  norm_num

end Tect.R219
