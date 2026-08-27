import Mathlib

namespace Tect.R362

/- R362 formalizes only the finite classical algebra underlying the local-PVM
   two-copy folding. The Python lanes verify the matrix trace realization on
   finite Q3 split histories. No collar estimate, cutoff/volume uniformity,
   common dynamics, OS/KMS/GNS statement, gap, or continuum limit is encoded. -/

theorem collision_replica_identity {ι : Type*} [Fintype ι]
    (p q : ι → ℝ) :
    (∑ i, (q i) ^ 2 / p i) = ∑ i, (q i * q i) / p i := by
  simp only [pow_two]

theorem reference_collision_is_one {ι : Type*} [Fintype ι]
    (p : ι → ℝ) (hp : ∀ i, p i ≠ 0)
    (hnorm : ∑ i, p i = 1) :
    ∑ i, (p i) ^ 2 / p i = 1 := by
  calc
    (∑ i, (p i) ^ 2 / p i) = ∑ i, p i := by
      apply Finset.sum_congr rfl
      intro i hi
      field_simp [hp i]
    _ = 1 := hnorm

theorem two_phase_mixture_gap_identity
    (w₁ w₂ p₁ p₂ q₁ q₂ : ℝ)
    (hp₁ : p₁ ≠ 0) (hp₂ : p₂ ≠ 0)
    (hmix : w₁ * p₁ + w₂ * p₂ ≠ 0) :
    w₁ * q₁ ^ 2 / p₁ + w₂ * q₂ ^ 2 / p₂ -
        (w₁ * q₁ + w₂ * q₂) ^ 2 / (w₁ * p₁ + w₂ * p₂) =
      w₁ * w₂ * (p₂ * q₁ - p₁ * q₂) ^ 2 /
        (p₁ * p₂ * (w₁ * p₁ + w₂ * p₂)) := by
  field_simp [hp₁, hp₂, hmix]
  ring

theorem two_phase_mixture_convexity
    (w₁ w₂ p₁ p₂ q₁ q₂ : ℝ)
    (hw₁ : 0 ≤ w₁) (hw₂ : 0 ≤ w₂)
    (hp₁ : 0 < p₁) (hp₂ : 0 < p₂)
    (hmix : 0 < w₁ * p₁ + w₂ * p₂) :
    (w₁ * q₁ + w₂ * q₂) ^ 2 / (w₁ * p₁ + w₂ * p₂) ≤
      w₁ * q₁ ^ 2 / p₁ + w₂ * q₂ ^ 2 / p₂ := by
  have hgap := two_phase_mixture_gap_identity w₁ w₂ p₁ p₂ q₁ q₂
    (ne_of_gt hp₁) (ne_of_gt hp₂) (ne_of_gt hmix)
  have hnonneg :
      0 ≤ w₁ * w₂ * (p₂ * q₁ - p₁ * q₂) ^ 2 /
        (p₁ * p₂ * (w₁ * p₁ + w₂ * p₂)) := by
    positivity
  linarith

theorem equality_constant_one_fixture (q p : ℝ) :
    q ^ 2 / p = 1 * (q * q / p) := by
  ring

theorem scope_fixture :
    (True ∧ True ∧ True ∧ True) ∧
      ¬ (False ∨ False ∨ False ∨ False ∨ False ∨ False ∨ False) := by
  norm_num

end Tect.R362
