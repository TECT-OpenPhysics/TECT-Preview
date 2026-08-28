import Mathlib

namespace Tect.R396

theorem triangle_budget {transport projected delta_abc delta_ab : ℝ}
    (h_transport : transport ≤ projected + delta_abc + delta_ab) :
    transport ≤ projected + delta_abc + delta_ab := by
  exact h_transport

theorem contractivity_split {recovered_delta delta_abc delta_ab : ℝ}
    (h_recovered : 0 ≤ recovered_delta) (h_ab : 0 ≤ delta_ab)
    (h_contract : recovered_delta ≤ delta_ab)
    (h_partial : delta_ab ≤ delta_abc) :
    recovered_delta ≤ delta_abc := by
  linarith

theorem finite_scope :
    (0 < (1 : ℝ) / 2) ∧ ((1 : ℝ) / 2 ≤ 1) ∧ ((1 : ℝ) / 2 ≤ 2) := by
  norm_num

end Tect.R396
