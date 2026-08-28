import Mathlib

namespace Tect.R400

/- R400 formalizes only scalar positivity used by the finite cutoff profile
   audit.  The Q3 Gibbs spectra and all cutoff statements remain executable
   evidence, not Lean theorems. -/

theorem positive_gap_ratio {g₁ g₂ : ℝ} (h₁ : 0 < g₁) (h₂ : 0 < g₂) :
    0 < g₂ / g₁ := by
  positivity

theorem profile_min_positive {g : ℝ} (h : 0 < g) :
    0 < min g g := by
  simpa using h

theorem finite_scope :
    (0 < (1 : ℝ) / 8) ∧ ((1 : ℝ) / 8 ≤ 1) ∧ ((1 : ℝ) / 8 ≤ 2) := by
  norm_num

end Tect.R400
