import Mathlib

namespace Tect.PahOmc020

open scoped BigOperators

/-
  This file contains only universal algebraic consequences used by the
  fixed-n temporal bridge.  It does not formalize the PAH measure, the
  unbounded generator domain, or either ordered limit.
-/

theorem inverse_pair_form (f ft g gt c : ℝ) :
    -c * (f * (gt - g) + ft * (g - gt)) = c * (ft - f) * (gt - g) := by
  ring

theorem finite_sum_square_bound {ι : Type*} (s : Finset ι) (u : ι → ℝ) :
    (∑ i ∈ s, u i) ^ 2 ≤ (s.card : ℝ) * ∑ i ∈ s, (u i) ^ 2 := by
  simpa using (sq_sum_le_card_mul_sum_sq (s := s) (f := u))

theorem finite_sum_abs_bound {ι : Type*} (s : Finset ι) (u : ι → ℝ)
    (B : ℝ) (hB : 0 ≤ B) (hcard : 1 ≤ s.card)
    (hsq : ∑ i ∈ s, (u i) ^ 2 ≤ B ^ 2) :
    |∑ i ∈ s, u i| ≤ (s.card : ℝ) * B := by
  have hcard0 : 0 ≤ (s.card : ℝ) := by positivity
  have hcard1 : 1 ≤ (s.card : ℝ) := by exact_mod_cast hcard
  have hsum : (∑ i ∈ s, u i) ^ 2 ≤ (s.card : ℝ) * B ^ 2 :=
    (finite_sum_square_bound s u).trans
      (mul_le_mul_of_nonneg_left hsq hcard0)
  have hsqcard : (s.card : ℝ) * B ^ 2 ≤ ((s.card : ℝ) * B) ^ 2 := by
    nlinarith [sq_nonneg B]
  have hnon : 0 ≤ (s.card : ℝ) * B := mul_nonneg hcard0 hB
  rw [abs_le]
  constructor <;> nlinarith [sq_abs (∑ i ∈ s, u i)]

theorem radial_form_coefficient (H L h : ℝ) :
    H * (2 * L * h) ^ 2 / 2 = 2 * H * L ^ 2 * h ^ 2 := by
  ring

theorem split_boundary_gap {a : ℝ} (ha : 0 < a) :
    2 * (1 + a) ^ 2 - 2 * (1 + a) > 0 := by
  nlinarith [sq_nonneg a]

theorem split_fibre_ratio_strict_decay {a b : ℝ} (ha : 0 ≤ a) (hab : a < b) :
    (1 + Real.exp (-(4 : ℝ))) * Real.exp (-(b ^ 2) / 2) <
      (1 + Real.exp (-(4 : ℝ))) * Real.exp (-(a ^ 2) / 2) := by
  have hsq : a ^ 2 < b ^ 2 := by
    nlinarith
  have harg : -(b ^ 2) / 2 < -(a ^ 2) / 2 := by
    nlinarith
  have hexp : Real.exp (-(b ^ 2) / 2) < Real.exp (-(a ^ 2) / 2) :=
    Real.exp_lt_exp.mpr harg
  have hfactor : 0 < 1 + Real.exp (-(4 : ℝ)) := by positivity
  exact mul_lt_mul_of_pos_left hexp hfactor

end Tect.PahOmc020
