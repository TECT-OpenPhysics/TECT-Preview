import Mathlib

namespace Tect.R348

theorem two_slice_arithmetic_mean (x y : Rat) (h : 0 ≤ (x - y) ^ 2) :
    2 * x * y ≤ x ^ 2 + y ^ 2 := by
  nlinarith

theorem euclidean_tail_scalar_envelope
    (two_slice equal_time operator_bound : Rat)
    (h_two_nonnegative : 0 ≤ two_slice)
    (h_amgm : two_slice ≤ equal_time)
    (h_operator : equal_time ≤ operator_bound) :
    two_slice ≤ operator_bound := by
  linarith

end Tect.R348
