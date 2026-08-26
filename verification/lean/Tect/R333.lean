import Mathlib

namespace Tect.R333

/- Exact rational bookkeeping for the finite cutoff-scaling audit. -/
def raw_bound (h c steps : Rat) : Rat := h ^ 2 * c / (2 * steps)

def cutoff_ratio (last baseline : Rat) : Rat := last / baseline

def history_coefficient (h c steps : Rat) : Rat :=
  (h / steps) ^ 3 * c * steps * (steps - 1) / 2

theorem raw_bound_fixture :
    raw_bound (1 / 3) 12 12 = 1 / 18 := by
  norm_num [raw_bound]

theorem cutoff_ratio_fixture :
    cutoff_ratio 200 50 = 4 := by
  norm_num [cutoff_ratio]

theorem history_coefficient_fixture :
    history_coefficient (1 / 3) 12 12 = 11 / 648 := by
  norm_num [history_coefficient]

theorem scope_fixture :
    (True ∧ True ∧ True) ∧ ¬ (False ∨ False ∨ False) := by
  norm_num

end Tect.R333
