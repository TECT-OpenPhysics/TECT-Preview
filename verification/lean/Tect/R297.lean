import Mathlib

namespace Tect.R297

/- R297 checks only rational condition-number bookkeeping behind EXP-001126.
   It does not formalize traces, matrices, spectra, or thermodynamic limits. -/

def square (x : Rat) : Rat := x * x

theorem condition_number_fixture :
    (4 : Rat) / (1 / 2 : Rat) = 8 := by
  norm_num

theorem two_sided_condition_bound_fixture :
    (1 / 2 : Rat) * 8 = 4 := by
  norm_num

theorem dual_spectrum_fixture :
    (3 / 10 : Rat) + (7 / 10 : Rat) = 1 := by
  norm_num

theorem scope_fixture :
    (True ∧ True ∧ True) ∧ ¬ False := by
  norm_num

end Tect.R297
