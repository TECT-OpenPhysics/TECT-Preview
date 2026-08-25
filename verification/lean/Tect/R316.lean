import Mathlib

namespace Tect.R316

theorem global_context_formula_fixture (n : Rat) :
    (2 / 3 : Rat) * (4 + 14 * n / 9 + n ^ 2 / 9) =
      8 / 3 + 28 * n / 27 + 2 * n ^ 2 / 27 := by
  ring

theorem global_context_quadratic_lower (n : Rat) (hn : 0 <= n) :
    2 * n ^ 2 / 27 <= 8 / 3 + 28 * n / 27 + 2 * n ^ 2 / 27 := by
  nlinarith

theorem threshold_witness (C N : Rat) (hN : 0 <= N)
    (hC : C < 2 * N ^ 2 / 27) :
    C < 8 / 3 + 28 * N / 27 + 2 * N ^ 2 / 27 := by
  nlinarith

theorem global_context_origin_fixture :
    (8 / 3 + 28 * (0 : Rat) / 27 + 2 * (0 : Rat) ^ 2 / 27) = 8 / 3 := by
  norm_num

theorem global_context_sample_fixture :
    (8 / 3 + 28 * (12 : Rat) / 27 + 2 * (12 : Rat) ^ 2 / 27) = 232 / 9 := by
  norm_num

end Tect.R316
