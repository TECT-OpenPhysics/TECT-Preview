import Mathlib

namespace Tect.R416

theorem scaled_weight_positive {w scale : ℝ}
    (hw : 0 < w) (hscale : 0 < scale) :
    0 < w * scale := by
  positivity

theorem constant_mode_projection_nonnegative {x y : ℝ} :
    0 ≤ (x - y) ^ 2 := by
  positivity

theorem schur_gap_positive {coarse residual : ℝ}
    (hcoarse : 0 < coarse) (hresidual : 0 < residual) :
    0 < (1 / 2 : ℝ) * min coarse residual := by
  have hmin : 0 < min coarse residual := lt_min hcoarse hresidual
  positivity

theorem finite_scope :
    (0 < (1 : ℝ) / 2) ∧ ((1 : ℝ) / 2 < 1) ∧
      (0 < (9 : ℝ) / 10) ∧ ((9 : ℝ) / 10 < 1) := by
  norm_num

end Tect.R416
