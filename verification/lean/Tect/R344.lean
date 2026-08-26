import Mathlib

namespace Tect.R344

def envelope (a b c d x₁ x₂ x₃ x₄ : ℝ) : ℝ :=
  (a + b) * x₁ + (c + d) * x₂ + (a + c) * x₃ + (b + d) * x₄

theorem four_component_envelope
    (a b c d x₁ x₂ x₃ x₄ : ℝ)
    (ha : 0 ≤ a) (hb : 0 ≤ b) (hc : 0 ≤ c) (hd : 0 ≤ d)
    (hx₁ : 0 ≤ x₁) (hx₂ : 0 ≤ x₂) (hx₃ : 0 ≤ x₃) (hx₄ : 0 ≤ x₄) :
    0 ≤ envelope a b c d x₁ x₂ x₃ x₄ := by
  dsimp [envelope]
  positivity

theorem max_pair_sum_bound
    (a b c d x₁ x₂ x₃ x₄ C : ℝ)
    (ha : 0 ≤ a) (hb : 0 ≤ b) (hc : 0 ≤ c) (hd : 0 ≤ d)
    (hx₁ : 0 ≤ x₁) (hx₂ : 0 ≤ x₂) (hx₃ : 0 ≤ x₃) (hx₄ : 0 ≤ x₄)
    (hC : a + b ≤ C) (hD : c + d ≤ C)
    (hE : a + c ≤ C) (hF : b + d ≤ C) :
    envelope a b c d x₁ x₂ x₃ x₄ ≤
      C * (x₁ + x₂ + x₃ + x₄) := by
  dsimp [envelope]
  nlinarith

end Tect.R344
