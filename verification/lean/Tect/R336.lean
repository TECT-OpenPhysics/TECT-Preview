import Mathlib

namespace Tect.R336

/- Exact rational bookkeeping for the centered global-energy obstruction. -/

theorem centered_D_row_formula (n : Rat) :
    (2 / 3 : Rat) * (2 * n / 9 + (2 / 3) ^ 2) =
      4 * n / 27 + 8 / 27 := by
  ring

theorem centered_D_column_formula (n : Rat) :
    (1 / 3 : Rat) * (2 * n / 9 + (1 / 3) ^ 2) =
      2 * n / 27 + 1 / 27 := by
  ring

theorem centered_D_star_row_formula (n : Rat) :
    (1 / 3 : Rat) * (2 * n / 9 + (1 / 3) ^ 2) =
      2 * n / 27 + 1 / 27 := by
  ring

theorem centered_D_star_column_formula (n : Rat) :
    (2 / 3 : Rat) * (2 * n / 9 + (2 / 3) ^ 2) =
      4 * n / 27 + 8 / 27 := by
  ring

theorem centered_linear_lower (n : Rat) (_hn : 0 <= n) :
    4 * n / 27 <= 4 * n / 27 + 8 / 27 := by
  nlinarith

theorem centered_column_linear_lower (n : Rat) (_hn : 0 <= n) :
    2 * n / 27 <= 2 * n / 27 + 1 / 27 := by
  nlinarith

theorem uncentered_quadratic_formula (n : Rat) :
    (2 / 3 : Rat) * (4 + 14 * n / 9 + n ^ 2 / 9) =
      8 / 3 + 28 * n / 27 + 2 * n ^ 2 / 27 := by
  ring

theorem centered_threshold (C N : Rat) (hN : 0 <= N)
    (hC : C < 2 * N / 27) :
    C < 4 * N / 27 + 8 / 27 := by
  nlinarith

theorem scope_fixture :
    (True ∧ True ∧ True ∧ True) ∧
      ¬ (False ∨ False ∨ False ∨ False) := by
  norm_num

end Tect.R336
