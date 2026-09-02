import Mathlib

namespace Tect.R480

theorem aperture_grid_values :
    ((1 : ℝ) / 2) = (1 : ℝ) / 2 ∧ (1 : ℝ) = 1 := by
  norm_num

theorem hidden_edge_increment_low :
    (((1 : ℝ) - (1 : ℝ) / 2) ^ 2 - ((1 : ℝ) / 2 - (1 : ℝ) / 2) ^ 2) / 2 = (1 : ℝ) / 8 := by
  norm_num

theorem hidden_edge_increment_high :
    (((1 : ℝ) - 1) ^ 2 - ((1 : ℝ) / 2 - 1) ^ 2) / 2 = -(1 : ℝ) / 8 := by
  norm_num

theorem hidden_increment_difference :
    (((1 : ℝ) - (1 : ℝ) / 2) ^ 2 - ((1 : ℝ) / 2 - (1 : ℝ) / 2) ^ 2) / 2 -
        (((1 : ℝ) - 1) ^ 2 - ((1 : ℝ) / 2 - 1) ^ 2) / 2 = (1 : ℝ) / 4 := by
  norm_num

theorem coarse_increment_cancellation :
    (((1 : ℝ) - 1) ^ 2 - ((1 : ℝ) / 2 - 1) ^ 2) / 2 +
        (((1 : ℝ) - (1 : ℝ) / 2) ^ 2 - ((1 : ℝ) / 2 - (1 : ℝ) / 2) ^ 2) / 2 = 0 := by
  norm_num

theorem conditional_factor_gt_one {x : ℝ} (hx : x ≠ 0) :
    1 < (Real.exp x + Real.exp (-x)) / 2 := by
  have h₁ : x + 1 < Real.exp x := Real.add_one_lt_exp hx
  have h₂ : -x + 1 < Real.exp (-x) :=
    Real.add_one_lt_exp (neg_ne_zero.mpr hx)
  nlinarith

theorem witness_factor_gt_one :
    1 < (Real.exp ((1 : ℝ) / 16) + Real.exp (-((1 : ℝ) / 16))) / 2 := by
  exact conditional_factor_gt_one (by norm_num)

theorem witness_normalized_defect_positive :
    0 < (Real.exp ((1 : ℝ) / 16) + Real.exp (-((1 : ℝ) / 16))) / 2 - 1 := by
  linarith [witness_factor_gt_one]

theorem witness_mobility_square :
    ((1 : ℝ) / 2) * 1 = (1 : ℝ) / 2 := by
  norm_num

def conditionalProjectedDiagnosticPass : Bool := false
def strongIntertwiningPass : Bool := false

theorem conditional_defect_keeps_stage2_closed :
    conditionalProjectedDiagnosticPass = false ∧ strongIntertwiningPass = false := by
  decide

end Tect.R480
