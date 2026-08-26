import Mathlib

namespace Tect.R335

/- Exact rational bookkeeping for signed union-group cancellation. -/
def signed_pair (forward reverse : Rat) : Rat := forward - reverse

def weighted_proxy (horizon coefficient steps : Rat) : Rat :=
  horizon ^ 2 * coefficient / (2 * steps)

theorem signed_pair_fixture :
    signed_pair 7 3 = 4 := by
  norm_num [signed_pair]

theorem reverse_antisymmetry_fixture :
    signed_pair 7 3 + signed_pair 3 7 = 0 := by
  norm_num [signed_pair]

theorem weighted_proxy_fixture :
    weighted_proxy (1 / 3) 12 12 = 1 / 18 := by
  norm_num [weighted_proxy]

theorem scope_fixture :
    (True ∧ True ∧ True) ∧ ¬ (False ∨ False ∨ False) := by
  norm_num

end Tect.R335
