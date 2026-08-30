import Mathlib

namespace Tect.R456

noncomputable def weightedKernel (k x : ℚ) : ℕ → ℚ
  | 0 => 0
  | n + 1 => k * weightedKernel k x n + x ^ n

theorem weighted_row_identity {a b wx wy : ℚ} (hwx : wx ≠ 0) :
    (a * wx + b * wy) / wx = a + b * wy / wx := by
  field_simp [hwx]

theorem weighted_diagonal_entry {a wx wy : ℚ} (hwx : wx ≠ 0) :
    (a * wy) / wx = a * (wy / wx) := by
  field_simp [hwx]

theorem weighted_path_kernel (k x : ℚ) (n : ℕ) :
    weightedKernel k x (n + 1) = k * weightedKernel k x n + x ^ n := by
  rfl

theorem weighted_resonance (x : ℚ) (n : ℕ) :
    weightedKernel x x (n + 1) = x * weightedKernel x x n + x ^ n := by
  rfl

theorem weighted_two_base_threshold {kbar s : ℚ}
    (_hk0 : 0 ≤ kbar) (hk1 : kbar < 1) (hs0 : 0 ≤ s) (hs1 : s < 1) :
    max kbar (max s ((23 / 26 : ℚ) ^ 4)) < 1 := by
  rw [max_lt_iff, max_lt_iff]
  exact ⟨hk1, hs1, by norm_num⟩

end Tect.R456
