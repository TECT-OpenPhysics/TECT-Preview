import Mathlib

namespace Tect.R452

noncomputable def resolvent (k r : ℚ) : ℕ → ℚ
  | 0 => 0
  | n + 1 => k * resolvent k r n + r ^ n

theorem resolvent_step (k r : ℚ) (n : ℕ) :
    resolvent k r (n + 1) = k * resolvent k r n + r ^ n := by
  rfl

theorem resolvent_nonresonant_step (A k r : ℚ) (hkr : k ≠ r) (n : ℕ) :
    k * (A * (k ^ n - r ^ n) / (k - r)) + A * r ^ n =
      A * (k ^ (n + 1) - r ^ (n + 1)) / (k - r) := by
  field_simp [hkr]
  ring

theorem resolvent_resonant_step (A k : ℚ) (n : ℕ) :
    k * (A * (n : ℚ) * k ^ (n - 1)) + A * k ^ n =
      A * (n + 1 : ℕ) * k ^ n := by
  cases n with
  | zero => norm_num
  | succ n =>
      simp [pow_succ]
      ring

theorem parent_decay_ratio :
    (23 / 26 : ℚ) ^ 4 = 279841 / 456976 := by
  norm_num

theorem parent_decay_lt_one :
    (0 : ℚ) < (23 / 26 : ℚ) ^ 4 ∧ (23 / 26 : ℚ) ^ 4 < 1 := by
  norm_num

theorem contraction_decay_bound {k : ℚ} (_hk0 : 0 ≤ k) (hk1 : k < 1) :
    max k ((23 / 26 : ℚ) ^ 4) < 1 := by
  rw [max_lt_iff]
  exact ⟨hk1, by norm_num⟩

end Tect.R452
