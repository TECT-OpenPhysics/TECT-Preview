import Mathlib

namespace Tect.R415

theorem schur_gap_positive {coarse residual : ℝ}
    (hcoarse : 0 < coarse) (hresidual : 0 < residual) :
    0 < (1 / 2 : ℝ) * min coarse residual := by
  have hmin : 0 < min coarse residual := lt_min hcoarse hresidual
  positivity

theorem late_exponential_factor_nonnegative {h gap dt : ℝ}
    (hh : 0 ≤ h) (hgap : 0 ≤ gap) (hdt : 0 ≤ dt) :
    0 ≤ h * Real.exp (-gap * dt) := by
  positivity

theorem green_bound_nonnegative {short late : ℝ}
    (hshort : 0 ≤ short) (hlate : 0 ≤ late) :
    0 ≤ short + late := by
  linarith

theorem finite_scope :
    (0 < (1 : ℝ) / 2) ∧ ((1 : ℝ) / 2 < 1) ∧
      (0 < (9 : ℝ) / 10) ∧ ((9 : ℝ) / 10 < 1) := by
  norm_num

end Tect.R415
