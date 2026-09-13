import Mathlib

namespace Tect.PahV2GibbsDefect

-- Parameterized bridges only; source rates and the prime construction remain
-- in the written proof and independent executable.
theorem residue_flip (a b p : Nat)
    (ha : a = 1 ∨ a = 2 ∨ a = 3 ∨ a = 4)
    (hb : b = 1 ∨ b = 2 ∨ b = 3 ∨ b = 4)
    (hp : p = 2 ∨ p = 3) (h : p * b % 5 = a) :
    (a = 1 ∨ a = 4) ↔ (b = 2 ∨ b = 3) := by
  rcases ha with rfl | rfl | rfl | rfl <;>
    rcases hb with rfl | rfl | rfl | rfl <;>
    rcases hp with rfl | rfl <;> norm_num at *

theorem cyclotomic_gap_square (c d : Real) (h : (c-d)^2 = 5/4) :
    (8*c-8*d)^2 = 80 := by nlinarith [sq_nonneg (c-d)]

theorem perturbation_lower (z e : Complex) (hz : 8 ≤ ‖z‖)
    (he : ‖e‖ ≤ 1) : 7 ≤ ‖z+e‖ := by
  have h : ‖z‖ ≤ ‖z+e‖ + ‖e‖ := by
    calc
      ‖z‖ = ‖(z+e)-e‖ := by congr 1; ring
      _ ≤ ‖z+e‖ + ‖e‖ := norm_sub_le _ _
  linarith

theorem original_weight_lower {ι : Type*} (s : Finset ι) (w d : ι → Real)
    (hw : ∀ i ∈ s, 0 ≤ w i) (hd : ∀ i ∈ s, 7 ≤ d i)
    (hn : ∑ i ∈ s, w i = 1) : 49 ≤ ∑ i ∈ s, w i * (d i)^2 := by
  have h : ∑ i ∈ s, w i * 49 ≤ ∑ i ∈ s, w i * (d i)^2 := by
    apply Finset.sum_le_sum
    intro i hi
    exact mul_le_mul_of_nonneg_left (by nlinarith [hd i hi]) (hw i hi)
  simpa [← Finset.sum_mul, hn] using h

theorem defect_error_arithmetic (K : Real) (hK : 512 ≤ K) :
    256/K + 256/K ≤ 1 := by
  have hp : 0 < K := by linarith
  have hh : 512/K ≤ 1 := (div_le_iff₀ hp).2 (by linarith)
  calc
    256/K + 256/K = (256+256)/K := (add_div _ _ _).symm
    _ = 512/K := by norm_num
    _ ≤ 1 := hh

end Tect.PahV2GibbsDefect
