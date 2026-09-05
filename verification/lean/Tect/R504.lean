import Mathlib

namespace Tect.R504

/-!
  Conditional convex-separation bridge for the PAH-OMC-014 projective test.

  A future source-owned packet may provide component mismatch values d(i) for
  one common cylinder.  This file does not choose sector weights or assert
  that such a one-sided separator exists.  It only proves that a normalized
  nonnegative mixture cannot have zero mismatch when every component is
  bounded below by one common positive constant.
-/

def weightedMismatch {ι : Type*} [Fintype ι]
    (w d : ι → ℝ) : ℝ :=
  ∑ i, w i * d i

theorem weighted_mismatch_lower_bound
    {ι : Type*} [Fintype ι]
    (w d : ι → ℝ) (c : ℝ)
    (hw : ∀ i, 0 ≤ w i)
    (hw_sum : ∑ i, w i = 1)
    (hsep : ∀ i, c ≤ d i) :
    c ≤ weightedMismatch w d := by
  unfold weightedMismatch
  calc
    c = (∑ i, w i) * c := by rw [hw_sum, one_mul]
    _ = ∑ i, w i * c := by rw [Finset.sum_mul]
    _ ≤ ∑ i, w i * d i := by
      apply Finset.sum_le_sum
      intro i hi
      exact mul_le_mul_of_nonneg_left (hsep i) (hw i)

theorem weighted_mismatch_nonzero
    {ι : Type*} [Fintype ι]
    (w d : ι → ℝ) (c : ℝ)
    (hw : ∀ i, 0 ≤ w i)
    (hw_sum : ∑ i, w i = 1)
    (hsep : ∀ i, c ≤ d i)
    (hc : 0 < c) :
    weightedMismatch w d ≠ 0 := by
  have hlower := weighted_mismatch_lower_bound w d c hw hw_sum hsep
  have hpositive : 0 < weightedMismatch w d := lt_of_lt_of_le hc hlower
  exact ne_of_gt hpositive

end Tect.R504
