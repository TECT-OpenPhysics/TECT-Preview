import Mathlib

namespace Tect.R421

/- R421 formalizes the two-state ground-state-transform algebra only.  The
   Q3 rows, arbitrary finite sums, unbounded common core and all limits remain
   in the executable/open boundary. -/

theorem two_state_ground_state_transform
    (c v₁ v₂ f₁ f₂ : ℝ) (hv₁ : v₁ ≠ 0) (hv₂ : v₂ ≠ 0) :
    c * (f₁ - f₂) ^ 2 =
      c * ((v₁ - v₂) / v₁) * f₁ ^ 2 +
        c * ((v₂ - v₁) / v₂) * f₂ ^ 2 +
          c * v₁ * v₂ * (f₁ / v₁ - f₂ / v₂) ^ 2 := by
  field_simp [hv₁, hv₂]
  ring

theorem two_state_remainder_nonnegative
    (c v₁ v₂ f₁ f₂ : ℝ) (hc : 0 ≤ c) (hv₁ : 0 < v₁) (hv₂ : 0 < v₂) :
    0 ≤ c * v₁ * v₂ * (f₁ / v₁ - f₂ / v₂) ^ 2 := by
  positivity

theorem two_state_tail_hardy
    (c v₁ v₂ f₁ : ℝ) (hc : 0 ≤ c) (hv₁ : 0 < v₁) (hv₂ : 0 < v₂) :
    c * (f₁ - 0) ^ 2 ≥ c * ((v₁ - v₂) / v₁) * f₁ ^ 2 := by
  have hidentity := two_state_ground_state_transform c v₁ v₂ f₁ 0 (ne_of_gt hv₁) (ne_of_gt hv₂)
  have hrem := two_state_remainder_nonnegative c v₁ v₂ f₁ 0 hc hv₁ hv₂
  nlinarith

theorem finite_scope :
    (0 : ℝ) < (1 : ℝ) / 40 ∧ (4 : ℝ) > 0 ∧ (3 : ℕ) < 12 := by
  norm_num

end Tect.R421
