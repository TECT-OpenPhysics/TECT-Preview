import Mathlib

namespace Tect.R417

/- R417 formalizes only scalar Lyapunov-sign, tail-mass and core-gap
   bookkeeping.  The finite matrix generator, log-domain distribution,
   induced spectrum and all continuum or sector limits remain outside this entrypoint. -/

theorem lyapunov_rate_positive {v lv : ℝ} (hv : 0 < v) (hlv : lv < 0) :
    0 < -lv / v := by
  exact div_pos (neg_pos.mpr hlv) hv

theorem tail_mass_nonnegative {m : ℝ} (_hm0 : 0 ≤ m) (hm1 : m ≤ 1) :
    0 ≤ 1 - m := by
  linarith

theorem core_gap_positive {coarse residual : ℝ}
    (hcoarse : 0 < coarse) (hresidual : 0 < residual) :
    0 < (1 / 2 : ℝ) * min coarse residual := by
  have hmin : 0 < min coarse residual := lt_min hcoarse hresidual
  positivity

theorem finite_scope :
    (0 < (1 : ℝ) / 20) ∧ ((1 : ℝ) / 20 < 1) ∧
      (0 < (1 : ℝ) / 40) ∧ ((1 : ℝ) / 40 < (1 : ℝ) / 10) := by
  norm_num

end Tect.R417
