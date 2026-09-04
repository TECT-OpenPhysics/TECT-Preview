import Mathlib

namespace Tect.R495

/- Conditional finite-sector assembly only.  The theorem assumes a supplied
   nonnegative normalized weight law and says nothing about choosing that law,
   projective consistency, or any infinite-volume limit. -/

def mix {ι X : Type*} [Fintype ι]
    (w : ι → ℝ) (phi : ι → (X → ℝ) → ℝ) (f : X → ℝ) : ℝ :=
  ∑ i, w i * phi i f

theorem mix_nonnegative {ι X : Type*} [Fintype ι]
    (w : ι → ℝ) (phi : ι → (X → ℝ) → ℝ) (f : X → ℝ)
    (hw : ∀ i, 0 ≤ w i)
    (hphi : ∀ i g, (∀ x, 0 ≤ g x) → 0 ≤ phi i g)
    (hf : ∀ x, 0 ≤ f x) :
    0 ≤ mix w phi f := by
  unfold mix
  exact Finset.sum_nonneg fun i _ => mul_nonneg (hw i) (hphi i f hf)

theorem mix_normalized {ι X : Type*} [Fintype ι]
    (w : ι → ℝ) (phi : ι → (X → ℝ) → ℝ)
    (hw : ∑ i, w i = 1)
    (hphi : ∀ i, phi i (fun _ => (1 : ℝ)) = 1) :
    mix w phi (fun _ => (1 : ℝ)) = 1 := by
  unfold mix
  calc
    (∑ i, w i * phi i (fun _ => (1 : ℝ))) =
        ∑ i, w i * 1 := by
          apply Finset.sum_congr rfl
          intro i hi
          rw [hphi i]
    _ = ∑ i, w i := by simp
    _ = 1 := hw

theorem mix_probability_pair
    {ι X : Type*} [Fintype ι]
    (w : ι → ℝ) (phi : ι → (X → ℝ) → ℝ)
    (hw_nonneg : ∀ i, 0 ≤ w i)
    (hw_sum : ∑ i, w i = 1)
    (hphi_pos : ∀ i g, (∀ x, 0 ≤ g x) → 0 ≤ phi i g)
    (hphi_one : ∀ i, phi i (fun _ => (1 : ℝ)) = 1) :
    (∀ f, (∀ x, 0 ≤ f x) → 0 ≤ mix w phi f) ∧
      mix w phi (fun _ => (1 : ℝ)) = 1 := by
  constructor
  · intro f hf
    exact mix_nonnegative w phi f hw_nonneg hphi_pos hf
  · exact mix_normalized w phi hw_sum hphi_one
end Tect.R495

