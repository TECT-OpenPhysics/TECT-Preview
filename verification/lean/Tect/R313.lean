import Mathlib

namespace Tect.R313

/- The finite transfer lane uses these exact rational inequalities.  The
   Python rows supply the matrix/spectral data; this file deliberately does
   not assert a common-core or uniform QFT theorem. -/

theorem gap_square_bound (ki kj : Rat) :
    (ki - kj) ^ 2 <= 2 * (ki ^ 2 + kj ^ 2) := by
  nlinarith [sq_nonneg (ki + kj)]

theorem spectral_term_bound (ell pi pj ki kj : Rat)
    (hell : 0 <= ell) (hmean : 2 * ell <= pi + pj) :
    2 * ell * (ki - kj) ^ 2 <= 2 * (pi + pj) * (ki ^ 2 + kj ^ 2) := by
  have hg := gap_square_bound ki kj
  have hsum : 0 <= pi + pj := by nlinarith
  nlinarith

theorem aggregate_constant_fixture : (8 : Rat) * (3 / 2) = 12 := by
  norm_num

theorem moment_shift_fixture (e e0 : Rat) (h : e0 <= e) :
    0 <= e - e0 + 1 := by
  nlinarith

end Tect.R313
