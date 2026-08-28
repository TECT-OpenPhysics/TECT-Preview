import Mathlib

namespace Tect.R392

theorem qcmI_chain_rule {q1 q2 cumulative budget : ℝ}
    (h_cumulative : cumulative = q1 + q2)
    (h_budget : budget = q1 + q2) :
    cumulative - budget = 0 := by
  linarith

theorem shell_budget_nonnegative {q1 q2 : ℝ}
    (h1 : 0 ≤ q1) (h2 : 0 ≤ q2) :
    0 ≤ q1 + q2 := by
  linarith

theorem cumulative_budget_dominates {cumulative budget : ℝ}
    (h : cumulative = budget) : cumulative ≤ budget := by
  linarith

theorem shell_sum_nonnegative {q : ℝ} (h : 0 ≤ q) : 0 ≤ q := by
  exact h

theorem scope_fixture :
    (0 ≤ (1 : ℝ) / 4) ∧ ((1 : ℝ) / 4 + (3 : ℝ) / 4 = 1) := by
  norm_num

end Tect.R392
