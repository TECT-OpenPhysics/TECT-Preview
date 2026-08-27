import Mathlib

namespace Tect.R375

/- R375 formalizes the scalar positive-frequency layer and its derivative
   envelope.  The odd Basel sum, finite spectra, eigenvector rotations,
   commutators and all thermodynamic limits remain outside this cross-check. -/

noncomputable def layer (omega beta delta : ℝ) : ℝ :=
  8 * delta / (omega ^ 2 + (beta * delta) ^ 2)

theorem layer_nonnegative {omega beta delta : ℝ}
    (homega : 0 < omega) (hdelta : 0 ≤ delta) :
    0 ≤ layer omega beta delta := by
  unfold layer
  have hden : 0 < omega ^ 2 + (beta * delta) ^ 2 := by
    exact add_pos_of_pos_of_nonneg (sq_pos_of_pos homega) (sq_nonneg _)
  exact div_nonneg (by positivity) (le_of_lt hden)

theorem derivative_envelope {omega beta delta : ℝ}
    (homega : 0 < omega) (hbeta : 0 ≤ beta) (hdelta : 0 ≤ delta) :
    8 * |omega ^ 2 - (beta * delta) ^ 2|
        / (omega ^ 2 + (beta * delta) ^ 2) ^ 2
      ≤ 8 / omega ^ 2 := by
  have homega : 0 < omega ^ 2 := sq_pos_of_pos homega
  have hbeta_delta : 0 ≤ (beta * delta) ^ 2 := sq_nonneg _
  have hsum : 0 < omega ^ 2 + (beta * delta) ^ 2 :=
    add_pos_of_pos_of_nonneg homega hbeta_delta
  have habs : |omega ^ 2 - (beta * delta) ^ 2|
      ≤ omega ^ 2 + (beta * delta) ^ 2 := by
    rw [abs_le]
    constructor <;> nlinarith
  have hmul : omega ^ 2 * |omega ^ 2 - (beta * delta) ^ 2|
      ≤ (omega ^ 2 + (beta * delta) ^ 2) ^ 2 := by
    have hleft := mul_le_mul_of_nonneg_left habs (le_of_lt homega)
    nlinarith [hleft, hbeta_delta]
  have hratio : |omega ^ 2 - (beta * delta) ^ 2|
      / (omega ^ 2 + (beta * delta) ^ 2) ^ 2
      ≤ 1 / omega ^ 2 := by
    apply (div_le_iff₀ (sq_pos_of_pos hsum)).2
    have hrewrite : (1 / omega ^ 2) *
        (omega ^ 2 + (beta * delta) ^ 2) ^ 2 =
        (omega ^ 2 + (beta * delta) ^ 2) ^ 2 / omega ^ 2 := by ring
    rw [hrewrite]
    apply (le_div_iff₀ homega).2
    nlinarith [hmul]
  calc
    8 * |omega ^ 2 - (beta * delta) ^ 2|
          / (omega ^ 2 + (beta * delta) ^ 2) ^ 2
        = 8 * (|omega ^ 2 - (beta * delta) ^ 2|
          / (omega ^ 2 + (beta * delta) ^ 2) ^ 2) := by ring
    _ ≤ 8 * (1 / omega ^ 2) := by
      exact mul_le_mul_of_nonneg_left hratio (by norm_num)
    _ = 8 / omega ^ 2 := by ring

theorem layer_zero {omega beta : ℝ} (homega : 0 < omega) :
    layer omega beta 0 = 0 := by
  unfold layer
  simp

theorem frequency_budget_term {omega : ℝ} (homega : 0 < omega) :
    0 < 8 / omega ^ 2 := by
  positivity

theorem scope_fixture :
    (True ∧ True ∧ True ∧ True) ∧
      ¬ (False ∨ False ∨ False ∨ False ∨ False) := by
  norm_num

end Tect.R375
