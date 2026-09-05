import Mathlib

namespace Tect.R505

/-!
  Conditional convex-hull diagnostic for the PAH-OMC-014 projective test.

  For a finite component block, a normalized nonnegative mixture whose scalar
  mismatch is exactly zero must contain at least one nonpositive and one
  nonnegative component mismatch.  This is only a necessary sign condition:
  it does not supply a PAH sector law or assert that cancellation is
  attainable for the source-owned components.
-/

def weightedMismatch {ι : Type*} [Fintype ι]
    (w d : ι → ℝ) : ℝ :=
  ∑ i, w i * d i

theorem zero_mixture_requires_sign_change
    {ι : Type*} [Fintype ι] [Nonempty ι]
    (w d : ι → ℝ)
    (hw : ∀ i, 0 ≤ w i)
    (hw_sum : ∑ i, w i = 1)
    (hzero : weightedMismatch w d = 0) :
    (∃ i, d i ≤ 0) ∧ (∃ j, 0 ≤ d j) := by
  have hpos_weight : ∃ i, 0 < w i := by
    by_contra hnone
    push Not at hnone
    have hw_eq_zero : ∀ i, w i = 0 := by
      intro i
      exact le_antisymm (hnone i) (hw i)
    have hsum_zero : (∑ i, w i) = 0 := by
      simp [hw_eq_zero]
    linarith
  rcases hpos_weight with ⟨i0, hi0⟩
  constructor
  · by_contra hno
    push Not at hno
    have hprod_nonneg : ∀ i ∈ (Finset.univ : Finset ι), 0 ≤ w i * d i := by
      intro i hi
      exact mul_nonneg (hw i) (le_of_lt (hno i))
    have hprod_pos : ∃ i ∈ (Finset.univ : Finset ι), 0 < w i * d i := by
      refine ⟨i0, Finset.mem_univ _, mul_pos hi0 (hno i0)⟩
    have hsum_pos : 0 < ∑ i ∈ (Finset.univ : Finset ι), w i * d i :=
      Finset.sum_pos' hprod_nonneg hprod_pos
    have : 0 < weightedMismatch w d := by
      simpa [weightedMismatch] using hsum_pos
    linarith
  · by_contra hno
    push Not at hno
    have hprod_nonpos : ∀ i ∈ (Finset.univ : Finset ι), w i * d i ≤ 0 := by
      intro i hi
      exact mul_nonpos_of_nonneg_of_nonpos (hw i) (le_of_lt (hno i))
    have hneg_weighted : 0 < ∑ i ∈ (Finset.univ : Finset ι), w i * (-d i) := by
      have hnonneg : ∀ i ∈ (Finset.univ : Finset ι), 0 ≤ w i * (-d i) := by
        intro i hi
        exact mul_nonneg (hw i) (le_of_lt (neg_pos.mpr (hno i)))
      have hpos : ∃ i ∈ (Finset.univ : Finset ι), 0 < w i * (-d i) := by
        refine ⟨i0, Finset.mem_univ _, mul_pos hi0 (neg_pos.mpr (hno i0))⟩
      exact Finset.sum_pos' hnonneg hpos
    have hsum_neg : (∑ i ∈ (Finset.univ : Finset ι), w i * d i) < 0 := by
      have hrewrite : (∑ i ∈ (Finset.univ : Finset ι), w i * (-d i)) =
          -(∑ i ∈ (Finset.univ : Finset ι), w i * d i) := by
        simp [mul_neg, Finset.sum_neg_distrib]
      linarith
    have : weightedMismatch w d < 0 := by
      simpa [weightedMismatch] using hsum_neg
    linarith

end Tect.R505
