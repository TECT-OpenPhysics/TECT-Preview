import Mathlib

namespace Tect.R308

/- R308 checks the exact pointwise inequalities behind EXP-001138.  It does
   not formalize compact-support localization, operator commutators,
   cancellation, or a thermodynamic/QFT limit. -/

theorem force_lower_fixture (y : Rat) (hy : 64 ≤ y) :
    y / 2 ≤ -1 + 3 * y / 5 := by
  nlinarith

theorem resolvent_derivative_lower_fixture (y : Rat) (hy : 64 ≤ y) :
    2 * (16 + y) ^ 2 ≤ 16 * y * (y - 16) := by
  have hy0 : 0 ≤ y := by nlinarith
  have hsq : 64 * y ≤ y ^ 2 := by
    nlinarith [mul_nonneg (sub_nonneg.mpr hy) hy0]
  nlinarith [hsq]

theorem combined_force_derivative_lower_fixture (y : Rat) (hy : 64 ≤ y) :
    (16 + y) ^ 2 ≤ 16 * (-1 + 3 * y / 5) * (y - 16) := by
  have hy0 : 0 ≤ y := by nlinarith
  have hlin : 0 ≤ 43 * y - 1008 := by nlinarith
  have hprod : 0 ≤ y * (43 * y - 1008) := mul_nonneg hy0 hlin
  nlinarith [hprod]

theorem potential_lower_fixture (y : Rat) :
    y ^ 2 / 20 ≤ 17 / 12 - y / 2 + 3 * y ^ 2 / 20 := by
  nlinarith [sq_nonneg (y - 5 / 2)]

theorem leading_coefficient_fixture :
    (3 / 5 : Rat) * 16 = 48 / 5 := by
  norm_num

end Tect.R308
