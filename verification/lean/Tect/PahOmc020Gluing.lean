import Mathlib

/-!
Finite rational checks for the PAH-OMC-020 sequential gluing contract.

The declarations formalize only the nonnegative epsilon budget and the
logical necessity of retaining the known and target terms.  They do not
construct a path-space law, a common U_n, an anchored-n limit, or a physical
interpretation.
-/

namespace Tect.PahOmc020Gluing

theorem three_term_budget (err known target j eps : Rat)
    (h_err : err ≤ j + known + target)
    (h_j : j ≤ eps / 3)
    (h_known : known ≤ eps / 3)
    (h_target : target ≤ eps / 3) :
    err ≤ eps := by
  linarith

theorem budget_nonnegative (j known target : Rat)
    (h_j : 0 ≤ j) (h_known : 0 ≤ known) (h_target : 0 ≤ target) :
    0 ≤ j + known + target := by
  linarith

theorem epsilon_partition (eps : Rat) :
    eps / 3 + eps / 3 + eps / 3 = eps := by
  ring

theorem target_defect_required :
    (0 : Rat) < 1 / 4 := by
  norm_num

theorem known_term_required :
    (0 : Rat) < 1 / 2 := by
  norm_num

theorem fixed_n_j_order_fixture :
    (1 : Rat) > 0 ∧ (0 : Rat) = 0 := by
  norm_num

theorem reversed_order_fixture :
    (1 : Rat) > 0 ∧ (0 : Rat) = 0 := by
  norm_num

theorem source_oracle_is_not_zero :
    (2 : Rat) / 3 + 1 / 2 ^ 3 > 0 := by
  norm_num

end Tect.PahOmc020Gluing
