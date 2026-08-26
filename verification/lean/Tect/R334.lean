import Mathlib

namespace Tect.R334

/- Exact rational bookkeeping for the finite local-state weighted coefficient. -/
def two_sided_square (left right : Rat) : Rat := left ^ 2 + right ^ 2

def weighted_proxy (horizon coefficient steps : Rat) : Rat :=
  horizon ^ 2 * coefficient / (2 * steps)

def source_pair_count (onsite bonds : Rat) : Rat := onsite + bonds

theorem two_sided_square_fixture :
    two_sided_square 3 4 = 25 := by
  norm_num [two_sided_square]

theorem weighted_proxy_fixture :
    weighted_proxy (1 / 3) 12 12 = 1 / 18 := by
  norm_num [weighted_proxy]

theorem source_pair_count_fixture :
    source_pair_count 7 5 = 12 := by
  norm_num [source_pair_count]

theorem scope_fixture :
    (True ∧ True ∧ True) ∧ ¬ (False ∨ False ∨ False) := by
  norm_num

end Tect.R334
