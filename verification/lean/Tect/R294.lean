import Mathlib

namespace Tect.R294

/- R294 checks only exact scalar bookkeeping for EXP-001123.  It does not
   formalize matrix exponentials, truncated CCR, Gibbs limits, or QFT. -/

def twoSided (right left : Rat) : Rat := right + left

theorem two_sided_fixture (right left : Rat) : twoSided right left = right + left := by
  rfl

theorem dual_trace_fixture (trace : Rat) (h : trace = 1) : trace = 1 := by
  exact h

theorem signed_orientation_count : (2 : Nat) = 1 + 1 := by
  norm_num

theorem volume_edge_count : (1 : Nat) + 4 = 5 := by
  norm_num

theorem ratio_tail_fixture (tail time : Rat) (ht : tail ≠ 0) (hm : time ≠ 0) :
    (time * tail) / (time * tail) = 1 := by
  field_simp [ht, hm]

theorem scope_fixture : (True ∧ True ∧ True ∧ True) ∧ ¬ False := by
  norm_num

end Tect.R294
