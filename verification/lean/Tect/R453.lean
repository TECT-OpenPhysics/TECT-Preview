import Mathlib

namespace Tect.R453

noncomputable def kernel (k x : ℚ) : ℕ → ℚ
  | 0 => 0
  | n + 1 => k * kernel k x n + x ^ n

theorem kernel_step (k x : ℚ) (n : ℕ) :
    kernel k x (n + 1) = k * kernel k x n + x ^ n := by
  rfl

theorem kernel_nonresonant_step (A k x : ℚ) (hkx : k ≠ x) (n : ℕ) :
    k * (A * (k ^ n - x ^ n) / (k - x)) + A * x ^ n =
      A * (k ^ (n + 1) - x ^ (n + 1)) / (k - x) := by
  field_simp [hkx]
  ring

theorem kernel_resonant_step (A k : ℚ) (n : ℕ) :
    k * (A * (n : ℚ) * k ^ (n - 1)) + A * k ^ n =
      A * (n + 1 : ℕ) * k ^ n := by
  cases n with
  | zero => norm_num
  | succ n =>
      simp [pow_succ]
      ring

theorem defect_envelope_step (A D k r s : ℚ) (n : ℕ) :
    k * (A * kernel k r n + D * kernel k s n) + A * r ^ n + D * s ^ n =
      A * kernel k r (n + 1) + D * kernel k s (n + 1) := by
  simp [kernel_step]
  ring

theorem parent_decay_ratio :
    (23 / 26 : ℚ) ^ 4 = 279841 / 456976 := by
  norm_num

theorem parent_decay_lt_one :
    (0 : ℚ) < (23 / 26 : ℚ) ^ 4 ∧ (23 / 26 : ℚ) ^ 4 < 1 := by
  norm_num

theorem two_base_contraction_bound {k s : ℚ}
    (hk0 : 0 ≤ k) (hk1 : k < 1) (hs0 : 0 ≤ s) (hs1 : s < 1) :
    max k (max s ((23 / 26 : ℚ) ^ 4)) < 1 := by
  rw [max_lt_iff, max_lt_iff]
  exact ⟨hk1, hs1, by norm_num⟩

end Tect.R453
