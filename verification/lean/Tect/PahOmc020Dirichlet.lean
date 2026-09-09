import Mathlib

namespace Tect.PahOmc020Dirichlet

open Set
open scoped BigOperators

lemma sq_le_sq_of_abs_le {a b : ℝ} (h : |a| ≤ |b|) : a ^ 2 ≤ b ^ 2 := by
  have hsq : |a| ^ 2 ≤ |b| ^ 2 := by nlinarith [abs_nonneg a, abs_nonneg b]
  simpa [sq_abs] using hsq

noncomputable def normalTrunc (x : ℝ) : ℝ := Set.projIcc (0 : ℝ) 1 (by norm_num) x

theorem normal_trunc_zero : normalTrunc 0 = 0 := by
  simp [normalTrunc]

theorem normal_trunc_one : normalTrunc 1 = 1 := by
  simp [normalTrunc]

theorem normal_trunc_lipschitz (a b : ℝ) :
    |normalTrunc a - normalTrunc b| ≤ |a - b| := by
  simpa [normalTrunc] using
    (Set.abs_projIcc_sub_projIcc (a := (0 : ℝ)) (b := (1 : ℝ)) (by norm_num)
      (c := a) (d := b))

theorem weighted_form_contraction {ι : Type*} (s : Finset ι) (w f g : ι → ℝ)
    (hw : ∀ i ∈ s, 0 ≤ w i)
    (hη : ∀ a b : ℝ, |normalTrunc a - normalTrunc b| ≤ |a - b|) :
    ∑ i ∈ s, w i * (normalTrunc (f i) - normalTrunc (g i)) ^ 2 ≤
      ∑ i ∈ s, w i * (f i - g i) ^ 2 := by
  apply Finset.sum_le_sum
  intro i hi
  have hsq := sq_le_sq_of_abs_le (hη (f i) (g i))
  exact mul_le_mul_of_nonneg_left hsq (hw i hi)

theorem weighted_form_contraction_canonical {ι : Type*} (s : Finset ι) (w f g : ι → ℝ)
    (hw : ∀ i ∈ s, 0 ≤ w i) :
    ∑ i ∈ s, w i * (normalTrunc (f i) - normalTrunc (g i)) ^ 2 ≤
      ∑ i ∈ s, w i * (f i - g i) ^ 2 := by
  exact weighted_form_contraction s w f g hw normal_trunc_lipschitz

theorem constant_one_weighted_energy_zero {ι : Type*} (s : Finset ι) (w : ι → ℝ)
    (hw : ∀ i ∈ s, 0 ≤ w i) :
    ∑ i ∈ s, w i * ((1 : ℝ) - 1) ^ 2 = 0 := by
  simp

theorem normal_trunc_l2_contraction {ι : Type*} (s : Finset ι) (w f : ι → ℝ)
    (hw : ∀ i ∈ s, 0 ≤ w i) :
    ∑ i ∈ s, w i * (normalTrunc (f i)) ^ 2 ≤
      ∑ i ∈ s, w i * (f i) ^ 2 := by
  apply Finset.sum_le_sum
  intro i hi
  have hzero := normal_trunc_zero
  have hsq := sq_le_sq_of_abs_le (normal_trunc_lipschitz (f i) 0)
  simpa [hzero, sub_zero] using mul_le_mul_of_nonneg_left hsq (hw i hi)

end Tect.PahOmc020Dirichlet
