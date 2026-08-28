import Mathlib

open scoped BigOperators

namespace Tect.R377

/- R377 formalizes the scalar resolvent identity and its positivity domain.
   Matrix inverses, Schatten bounds, locality, and all limits remain outside
   this scalar cross-check. -/

noncomputable def resolventScalar (beta omega x : ℝ) : ℝ :=
  1 / (omega ^ 2 + (beta * x) ^ 2)

theorem denominator_positive {beta omega x : ℝ} (homega : 0 < omega) :
    0 < omega ^ 2 + (beta * x) ^ 2 := by
  positivity

theorem denominator_dominates {beta omega x : ℝ} :
    omega ^ 2 ≤ omega ^ 2 + (beta * x) ^ 2 := by
  nlinarith [sq_nonneg (beta * x)]

theorem resolventScalar_positive {beta omega x : ℝ} (homega : 0 < omega) :
    0 < resolventScalar beta omega x := by
  unfold resolventScalar
  exact one_div_pos.mpr (denominator_positive homega)

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

theorem odd_frequency_positive (k : Nat) :
    0 < (2 * (k : ℝ) + 1) * Real.pi := by
  positivity

theorem scope_fixture :
    (True ∧ True ∧ True) ∧ ¬ (False ∨ False ∨ False ∨ False) := by
  norm_num

end Tect.R377
