import Mathlib

namespace Tect.R506

/-!
  Conditional tail-control bridge for the PAH-OMC-014 cylinder Cauchy test.

  A future source-owned sector law may provide a nonnegative tail mass bound
  on a finite complement and a common bound on the cylinder values.  This
  file proves only the resulting weighted tail estimate.  It supplies no
  sector weights, no PAH component values, and no limit or projective law.
-/

def weightedTail {ι : Type*} [Fintype ι]
    (s : Finset ι) (w a : ι → ℝ) : ℝ :=
  Finset.sum s (fun i => w i * a i)

theorem weighted_tail_abs_bound
    {ι : Type*} [Fintype ι]
    (s : Finset ι) (w a : ι → ℝ) (c tau : ℝ)
    (hw : ∀ i, 0 ≤ w i)
    (hc : 0 ≤ c)
    (hbound : ∀ i ∈ s, |a i| ≤ c)
    (htail : Finset.sum s w ≤ tau) :
    |weightedTail s w a| ≤ c * tau := by
  unfold weightedTail
  calc
    |Finset.sum s (fun i => w i * a i)| ≤
        Finset.sum s (fun i => |w i * a i|) := by
      exact Finset.abs_sum_le_sum_abs (fun i => w i * a i) s
    _ = Finset.sum s (fun i => w i * |a i|) := by
      apply Finset.sum_congr rfl
      intro i hi
      rw [abs_mul, abs_of_nonneg (hw i)]
    _ ≤ Finset.sum s (fun i => w i * c) := by
      apply Finset.sum_le_sum
      intro i hi
      exact mul_le_mul_of_nonneg_left (hbound i hi) (hw i)
    _ = c * Finset.sum s w := by
      calc
        Finset.sum s (fun i => w i * c) = (Finset.sum s w) * c := by
          symm
          exact Finset.sum_mul s w c
        _ = c * Finset.sum s w := by ring
    _ ≤ c * tau := by
      exact mul_le_mul_of_nonneg_left htail hc

theorem tail_bound_zero
    {ι : Type*} [Fintype ι]
    (s : Finset ι) (w a : ι → ℝ)
    (hbound : ∀ i ∈ s, |a i| ≤ 0) :
    |weightedTail s w a| = 0 := by
  have hzero : ∀ i ∈ s, a i = 0 := by
    intro i hi
    have habs : |a i| = 0 := le_antisymm (hbound i hi) (abs_nonneg _)
    exact abs_eq_zero.mp habs
  have hsum : Finset.sum s (fun i => w i * a i) = 0 := by
    apply Finset.sum_eq_zero
    intro i hi
    simp [hzero i hi]
  rw [weightedTail, hsum, abs_zero]

end Tect.R506
