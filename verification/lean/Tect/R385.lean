import Mathlib

namespace Tect.R385

noncomputable def relative {G : Type*} [Group G] (p h : G) : G := p * h⁻¹

noncomputable def baseAction {G : Type*} [Group G] (h x : G) : G := h * x * h⁻¹

theorem relative_cocycle_composition {G : Type*} [Group G]
    (p₁ p₂ h₁ h₂ : G) :
    relative p₁ h₁ * baseAction h₁ (relative p₂ h₂) =
      relative (p₁ * p₂) (h₁ * h₂) := by
  simp [relative, baseAction, mul_assoc]

noncomputable def resolventScalar (beta omega x : ℝ) : ℝ :=
  1 / (omega ^ 2 + (beta * x) ^ 2)

theorem resolvent_difference_identity {beta omega a b : ℝ}
    (ha : omega ^ 2 + (beta * a) ^ 2 ≠ 0)
    (hb : omega ^ 2 + (beta * b) ^ 2 ≠ 0) :
    resolventScalar beta omega b - resolventScalar beta omega a =
      beta ^ 2 * (a ^ 2 - b ^ 2) *
        resolventScalar beta omega b * resolventScalar beta omega a := by
  unfold resolventScalar
  have hA : omega ^ 2 + beta ^ 2 * a ^ 2 ≠ 0 := by
    intro h
    apply ha
    nlinarith [h]
  have hB : omega ^ 2 + beta ^ 2 * b ^ 2 ≠ 0 := by
    intro h
    apply hb
    nlinarith [h]
  field_simp [hA, hB]
  ring

theorem scope_fixture :
    (True ∧ True ∧ True ∧ True ∧ True) ∧
      ¬ (False ∨ False ∨ False ∨ False ∨ False) := by
  norm_num

end Tect.R385
