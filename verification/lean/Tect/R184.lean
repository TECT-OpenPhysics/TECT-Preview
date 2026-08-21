import Mathlib

namespace Tect.R184

theorem two_block_douglas_identity (s1 s2 h1 h2 : Rat) :
    (s1 * h1 + s2 * h2) ^ 2 + (s1 * h2 - s2 * h1) ^ 2 =
      (s1 ^ 2 + s2 ^ 2) * (h1 ^ 2 + h2 ^ 2) := by
  ring

theorem two_block_douglas_bound (s1 s2 h1 h2 : Rat) :
    (s1 * h1 + s2 * h2) ^ 2 <= (s1 ^ 2 + s2 ^ 2) * (h1 ^ 2 + h2 ^ 2) := by
  have wedge_nonnegative : 0 <= (s1 * h2 - s2 * h1) ^ 2 := sq_nonneg _
  nlinarith [two_block_douglas_identity s1 s2 h1 h2]

theorem fixture_identity :
    ((3 : Rat) * 5 + 4 * (-2)) ^ 2 + ((3 : Rat) * (-2) - 4 * 5) ^ 2 =
      ((3 : Rat) ^ 2 + 4 ^ 2) * (5 ^ 2 + (-2 : Rat) ^ 2) := by
  norm_num

theorem fixture_gap :
    ((3 : Rat) ^ 2 + 4 ^ 2) * (5 ^ 2 + (-2 : Rat) ^ 2) -
      ((3 : Rat) * 5 + 4 * (-2)) ^ 2 = 26 ^ 2 := by
  norm_num

end Tect.R184
