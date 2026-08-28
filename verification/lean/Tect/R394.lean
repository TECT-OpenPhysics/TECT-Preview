import Mathlib

namespace Tect.R394

theorem energy_tail_markov {tail moment cutoff : ℝ}
    (h_cutoff : 0 < cutoff) (h_tail : 0 ≤ tail)
    (h_moment : cutoff * tail ≤ moment) :
    tail ≤ moment / cutoff := by
  apply (le_div_iff₀ h_cutoff).2
  nlinarith

theorem weighted_energy_tail_markov {tail moment cutoff : ℝ}
    (h_cutoff : 0 < cutoff) (h_tail : 0 ≤ tail)
    (h_moment : cutoff * tail ≤ moment) :
    tail ≤ moment / cutoff := by
  apply (le_div_iff₀ h_cutoff).2
  nlinarith

theorem finite_scope :
    (0 < (1 : ℝ) / 2) ∧ ((1 : ℝ) / 2 ≤ 1) ∧ ((1 : ℝ) / 2 ≤ 2) := by
  norm_num

end Tect.R394
