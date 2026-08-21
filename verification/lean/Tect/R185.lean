import Mathlib

namespace Tect.R185

theorem finite_packet_cauchy_bound {Alpha : Type*} (s : Finset Alpha)
    (f g : Alpha -> Rat) :
    (Finset.sum s (fun i => f i * g i)) ^ 2 <=
      (Finset.sum s (fun i => f i ^ 2)) * (Finset.sum s (fun i => g i ^ 2)) := by
  simpa using (Finset.sum_mul_sq_le_sq_mul_sq s f g)

theorem three_packet_fixture :
    ((2 : Rat) * 4 + (-1) * 5 + 3 * (-2)) ^ 2 <=
      ((2 : Rat) ^ 2 + (-1) ^ 2 + 3 ^ 2) *
        ((4 : Rat) ^ 2 + 5 ^ 2 + (-2 : Rat) ^ 2) := by
  norm_num

theorem three_packet_gap :
    ((2 : Rat) ^ 2 + (-1) ^ 2 + 3 ^ 2) *
        ((4 : Rat) ^ 2 + 5 ^ 2 + (-2 : Rat) ^ 2) -
      ((2 : Rat) * 4 + (-1) * 5 + 3 * (-2)) ^ 2 = 621 := by
  norm_num

end Tect.R185
