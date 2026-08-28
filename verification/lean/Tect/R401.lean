import Mathlib

namespace Tect.R401

/- R401 formalizes only the scalar positivity used by the finite coordinate
   metric audit.  The oscillator spectra and all regulator comparisons stay
   in the executable evidence lanes. -/

theorem positive_spacing_factor {dx : ℝ} (h : 0 < dx) :
    0 < 1 / dx ^ 2 := by
  positivity

theorem positive_metric_ratio {g₁ g₂ : ℝ} (h₁ : 0 < g₁) (h₂ : 0 < g₂) :
    0 < g₂ / g₁ := by
  positivity

theorem finite_scope :
    (0 < (1 : ℝ) / 8) ∧ ((1 : ℝ) / 8 ≤ 1) ∧ ((1 : ℝ) / 8 ≤ 2) := by
  norm_num

end Tect.R401
