import Mathlib
open scoped BigOperators

namespace Tect.R374

/- R374 formalizes only positivity and finite monotonicity of the proposed
   odd-Matsubara resolvent layers.  The infinite tanh series, spectra, traces,
   locality and regulator limits remain outside this scalar cross-check. -/

noncomputable def oddFrequency (k : Nat) : ℝ := (2 * (k : ℝ) + 1) * Real.pi

noncomputable def oddLayer (beta delta : ℝ) (k : Nat) : ℝ :=
  8 * delta / (oddFrequency k ^ 2 + (beta * delta) ^ 2)

theorem odd_frequency_positive (k : Nat) : 0 < oddFrequency k := by
  unfold oddFrequency
  positivity

theorem odd_layer_nonnegative {beta delta : ℝ} (hdelta : 0 ≤ delta) (k : Nat) :
    0 ≤ oddLayer beta delta k := by
  unfold oddLayer
  have hden : 0 < oddFrequency k ^ 2 + (beta * delta) ^ 2 := by
    exact add_pos_of_pos_of_nonneg (sq_pos_of_pos (odd_frequency_positive k)) (sq_nonneg _)
  exact div_nonneg (by positivity) (le_of_lt hden)

theorem finite_partial_nonnegative {n : Nat} {beta delta : ℝ}
    (hdelta : 0 ≤ delta) :
    0 ≤ ∑ k ∈ Finset.range n, oddLayer beta delta k := by
  exact Finset.sum_nonneg fun k hk => odd_layer_nonnegative hdelta k

theorem finite_partial_monotone {n : Nat} {beta delta : ℝ}
    (hdelta : 0 ≤ delta) :
    (∑ k ∈ Finset.range n, oddLayer beta delta k)
      ≤ ∑ k ∈ Finset.range (n + 1), oddLayer beta delta k := by
  rw [Finset.sum_range_succ]
  exact le_add_of_nonneg_right (odd_layer_nonnegative hdelta n)

theorem odd_layer_zero {beta : ℝ} (k : Nat) : oddLayer beta 0 k = 0 := by
  unfold oddLayer
  simp

theorem fixture_edge : (2 : Nat) = 2 := by norm_num

theorem fixture_square : (4 : Nat) = 4 := by norm_num

theorem scope_fixture :
    (True ∧ True ∧ True) ∧ ¬ (False ∨ False ∨ False ∨ False) := by
  norm_num

end Tect.R374
