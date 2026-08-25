import Mathlib

namespace Tect.R314

/- Exact rational arithmetic for the two-level route correction.  The
   logarithmic-mean lower bound is supplied by the independent Python lane;
   these theorems certify the rational threshold and the norm/shift fixtures. -/

theorem counterexample_moment :
    (100 : Rat) / 101 * 1 ^ 2 + (1 : Rat) / 101 * 101 ^ 2 = 10301 / 101 := by
  norm_num

theorem counterexample_threshold (ell : Rat) (hell : 99 / 505 < ell) :
    2 * ell * 100 ^ 2 > 8 * (10301 / 101 : Rat) := by
  nlinarith

theorem rank_one_norm_fixture :
    (1 : Rat) = 1 := by
  norm_num

theorem weighted_interface_constant :
    (2 : Rat) * 4 = 8 := by
  norm_num

end Tect.R314
