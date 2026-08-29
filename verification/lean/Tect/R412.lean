import Mathlib

namespace Tect.R412

theorem split_exponents_positive {a b : ℝ} (ha : 0 < a) (hb : 0 < b) :
    0 < a ∧ 0 < b := by
  exact ⟨ha, hb⟩

theorem mixed_tail_nonnegative {s m : ℝ} (hs : 1 < s) (hm : 0 < m) :
    0 ≤ m ^ (1 - s) / (s - 1) := by
  positivity

theorem finite_scope :
    (0 < (1 : ℝ) / 2) ∧ ((1 : ℝ) / 2 < 1) ∧ (0 < (3 : ℝ) / 4) := by
  norm_num

end Tect.R412
