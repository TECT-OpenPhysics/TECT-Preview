import Mathlib

namespace Tect.R390

theorem gibbs_tail_term_bound {alpha beta energy value : ℝ}
    (_h_alpha : 0 ≤ alpha) (h_order : alpha ≤ beta) (h_window : energy ≤ value) :
    Real.exp (-beta * value) ≤
      Real.exp (-(beta - alpha) * energy) * Real.exp (-alpha * value) := by
  rw [← Real.exp_add]
  apply Real.exp_le_exp.mpr
  nlinarith

theorem window_mass_split {mass tail : ℝ} (h_split : mass + tail = 1) :
    tail = 1 - mass := by
  linarith

theorem local_duality_scope {full local_value : ℝ} (h_duality : full = local_value) :
    |full - local_value| = 0 := by
  rw [h_duality, sub_self, abs_zero]

theorem scope_fixture :
    (0 ≤ (1 : ℝ) / 4) ∧ ((1 : ℝ) / 4 + (3 : ℝ) / 4 = 1) := by
  norm_num

end Tect.R390
