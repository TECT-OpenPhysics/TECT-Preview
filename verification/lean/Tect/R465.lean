import Mathlib

namespace Tect.R465

theorem sextic_coefficient_positive
    (gamma volume : ℚ) (hgamma : 0 < gamma) (hvolume : 0 < volume)
    (m : ℕ) (hm : 0 < m) :
    0 < gamma * volume / (12 * (m : ℚ) ^ 3) := by
  have hmQ : (0 : ℚ) < (m : ℚ) := by exact_mod_cast hm
  positivity

theorem coefficient_scale_identity
    (gamma volume : ℚ) (m : ℕ) (hm : 0 < m) :
    (gamma * volume / (12 * (m : ℚ) ^ 3)) * (m : ℚ) ^ 3 = gamma * volume / 12 := by
  have hmQ : (m : ℚ) ≠ 0 := by
    exact_mod_cast (Nat.ne_of_gt hm)
  field_simp [hmQ]

theorem coefficient_ratio_lt_one
    (a : ℚ) (ha : 0 < a) (n m : ℕ) (hn : 0 < n) (hnm : n < m) :
    a / (m : ℚ) ^ 3 < a / (n : ℚ) ^ 3 := by
  have hnQ : (0 : ℚ) < (n : ℚ) := by exact_mod_cast hn
  have hnmQ : (n : ℚ) < (m : ℚ) := by exact_mod_cast hnm
  have hmQ : (0 : ℚ) < (m : ℚ) := by linarith
  have hcube : (n : ℚ) ^ 3 < (m : ℚ) ^ 3 := by
    have hsum : 0 < (m : ℚ) ^ 2 + (m : ℚ) * (n : ℚ) + (n : ℚ) ^ 2 := by positivity
    have hfactor : (m : ℚ) ^ 3 - (n : ℚ) ^ 3 =
        ((m : ℚ) - (n : ℚ)) * ((m : ℚ) ^ 2 + (m : ℚ) * (n : ℚ) + (n : ℚ) ^ 2) := by ring
    have hdiff : 0 < (m : ℚ) ^ 3 - (n : ℚ) ^ 3 := by
      rw [hfactor]
      exact mul_pos (sub_pos.mpr hnmQ) hsum
    linarith
  exact (div_lt_div_iff₀ (by positivity) (by positivity)).2
    (mul_lt_mul_of_pos_left hcube ha)

theorem beta_coefficient_positive
    (beta gamma volume : ℚ) (hbeta : 0 < beta) (hgamma : 0 < gamma)
    (hvolume : 0 < volume) (m : ℕ) (hm : 0 < m) :
    0 < beta * (gamma * volume / (12 * (m : ℚ) ^ 3)) := by
  have hmQ : (0 : ℚ) < (m : ℚ) := by exact_mod_cast hm
  positivity

end Tect.R465
