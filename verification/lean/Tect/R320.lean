import Mathlib

namespace Tect.R320

/- R320 checks only the exact rational bookkeeping for EXP-001150.  It does
   not formalize multiplication operators, Friedrichs representations,
   finite-volume dynamics, or an inductive-limit state. -/

theorem degree_order_fixture :
    (1 : Rat) + (10 / 3) * 6 = 21 := by
  norm_num

theorem product_gradient_fixture :
    (1 : Rat) * (3 / 2) + 2 * 1 = 7 / 2 := by
  norm_num

theorem product_form_fixture :
    2 * (2 : Rat)^2 + (7 / 2)^2 = 81 / 4 := by
  norm_num

theorem embedding_constant_fixture (s v : Rat) (hs : 0 ≤ s) (hv : s ≤ v) :
    (2 : Rat) + s = 2 + s ∧ v - s ≥ 0 := by
  constructor
  · rfl
  · linarith

theorem cross_product_fixture :
    (21 : Rat) * (81 / 4) = 1701 / 4 := by
  norm_num

theorem scope_fixture :
    (True ∧ True ∧ True ∧ True) ∧ ¬ (False ∨ False ∨ False) := by
  norm_num

end Tect.R320
