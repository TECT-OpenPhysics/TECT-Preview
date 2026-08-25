import Mathlib

namespace Tect.R326

/- R326 checks only the exact rational fixtures used by EXP-001156.  It does
   not formalize finite matrix exponentials, Gibbs traces, commutator norms,
   split-product estimates, unbounded domains or thermodynamic limits. -/

theorem weighted_step_fixture :
    1 + (1 + 1 * 6 * 2) * (1 / 18 : Rat) = 31 / 18 := by
  norm_num

theorem time_horizon_fixture :
    6 * (1 / 18 : Rat) = 1 / 3 := by
  norm_num

theorem order_count_fixture :
    (2 : Rat) * 2 = 4 := by
  norm_num

theorem source_support_fixture :
    (2 : Rat) = 2 := by
  norm_num

theorem context_count_fixture :
    (2 : Rat) * 2 = 4 := by
  norm_num

theorem split_term_count_fixture (v e : Rat) :
    (v + e) = v + e := by
  norm_num

theorem scope_fixture :
    (True ∧ True ∧ True) ∧
      ¬ (False ∨ False ∨ False ∨ False ∨ False ∨ False) := by
  norm_num

end Tect.R326
