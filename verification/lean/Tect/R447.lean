import Mathlib

namespace Tect.R447

theorem interval_subtraction_lower
    {dlo dhi ilo ihi : ℚ}
    (hd : dlo ≤ dhi) (hi : ilo ≤ ihi) :
    dlo - ihi ≤ dhi - ilo := by
  linarith

theorem display_interval :
    (174 : ℚ) / 100 - 5 / 100 = 169 / 100 ∧
      (174 : ℚ) / 100 + 5 / 100 = 179 / 100 := by
  norm_num

theorem simultaneous_envelope :
    ((169 : ℚ) / 100 - 0, (179 : ℚ) / 100 - 0) =
      (169 / 100, 179 / 100) := by
  norm_num

theorem ten_second_envelope :
    ((169 : ℚ) / 100 - 10, (179 : ℚ) / 100 - 10) =
      (-831 / 100, -821 / 100) := by
  norm_num

theorem broad_exotic_envelope :
    ((169 : ℚ) / 100 - 1000, (179 : ℚ) / 100 - (-100)) =
      (-99831 / 100, 10179 / 100) := by
  norm_num

theorem broad_contains_simultaneous :
    (-99831 : ℚ) / 100 ≤ 169 / 100 ∧
      179 / 100 ≤ 10179 / 100 := by
  norm_num

theorem broad_contains_ten_second :
    (-99831 : ℚ) / 100 ≤ -831 / 100 ∧
      -821 / 100 ≤ 10179 / 100 := by
  norm_num

theorem union_envelope :
    min ((169 : ℚ) / 100) (-831 / 100) = -831 / 100 ∧
      max (179 / 100) (10179 / 100) = 10179 / 100 := by
  norm_num

end Tect.R447
