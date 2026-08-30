import Mathlib

namespace Tect.R440

theorem box_222_edge_count : (2 - 1) * 2 * 2 + (2 - 1) * 2 * 2 + (2 - 1) * 2 * 2 = (12 : ℕ) := by
  norm_num

theorem box_333_edge_count : (3 - 1) * 3 * 3 + (3 - 1) * 3 * 3 + (3 - 1) * 3 * 3 = (54 : ℕ) := by
  norm_num

theorem box_543_edge_count : (5 - 1) * 4 * 3 + (4 - 1) * 5 * 3 + (3 - 1) * 5 * 4 = (133 : ℕ) := by
  norm_num

theorem matching_layer_count : (3 : ℕ) * 2 = 6 := by
  norm_num

theorem derived_matching_coefficient :
    (1 : ℚ) + (2 : ℚ) * (3 / 5 : ℚ) ^ 2 / (2 * (7 / 4 : ℚ) * (2 / 5 : ℚ)) = 53 / 35 := by
  norm_num

end Tect.R440
