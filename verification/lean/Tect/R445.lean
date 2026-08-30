import Mathlib

namespace Tect.R445

open scoped BigOperators

theorem weighted_tail_transfer
    {ι : Type*} [Fintype ι]
    {A : Type*} [SeminormedAddCommGroup A]
    {K : ι → A} {w : ι → ℝ} {C : ℝ}
    (hK : ∀ i, ‖K i‖ ≤ C * w i) :
    ‖∑ i, K i‖ ≤ C * ∑ i, w i := by
  calc
    ‖∑ i, K i‖ ≤ ∑ i, ‖K i‖ := norm_sum_le _ _
    _ ≤ ∑ i, C * w i := Finset.sum_le_sum (fun i _ => hK i)
    _ = C * ∑ i, w i := by rw [Finset.mul_sum]

theorem scaled_tail_r1_bound (C : ℝ) :
    C * (78 : ℝ) = C * (3 * (4 * (1 : ℝ)^2 + 8 * 1 + 14)) := by
  norm_num

end Tect.R445
