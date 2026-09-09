import Mathlib

namespace Tect.PahOmc024

def rateA (n : ℕ) : ℚ := 1 / (2 : ℚ) ^ n

def rateB (n : ℕ) : ℚ := rateA n / 2

def derivativeGap (n : ℕ) : ℚ := (rateA n - rateB n) / 2

def targetBound (n : ℕ) : ℚ := rateA n / 2

theorem rateA_positive (n : ℕ) : 0 < rateA n := by
  unfold rateA
  positivity

theorem derivative_gap_positive (n : ℕ) : 0 < derivativeGap n := by
  unfold derivativeGap rateB
  have h : 0 < rateA n := rateA_positive n
  linarith

theorem derivative_gap_le_target_bound (n : ℕ) : derivativeGap n ≤ targetBound n := by
  unfold derivativeGap targetBound rateB
  have h : 0 ≤ rateA n := le_of_lt (rateA_positive n)
  linarith

theorem derivative_gap_halves (n : ℕ) : derivativeGap (n + 1) = derivativeGap n / 2 := by
  unfold derivativeGap rateB rateA
  rw [pow_succ]
  field_simp

theorem derivative_gap_at_eight : derivativeGap 8 = (1 : ℚ) / 1024 := by
  norm_num [derivativeGap, rateB, rateA]

theorem derivative_gap_at_eight_small : derivativeGap 8 < (1 : ℚ) / 1000 := by
  rw [derivative_gap_at_eight]
  norm_num

end Tect.PahOmc024
