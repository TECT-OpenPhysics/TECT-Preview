import Mathlib

namespace Tect.R378

/- R378 formalizes the scalar half-density factorization and its arithmetic
   envelope.  Finite matrix spectra, two-sided GNS limits, and locality remain
   outside this scalar cross-check. -/

theorem half_density_pair_factor (a b : ℝ) :
    |a ^ 2 - b ^ 2| = |a - b| * |a + b| := by
  rw [show a ^ 2 - b ^ 2 = (a - b) * (a + b) by ring]
  rw [abs_mul]

theorem pair_am_gm (u v y : ℝ) (hy : 0 ≤ y) :
    2 * |u| * |v| * y ≤ (u ^ 2 + v ^ 2) * y := by
  have h : 2 * |u| * |v| ≤ |u| ^ 2 + |v| ^ 2 := by
    nlinarith [sq_nonneg (|u| - |v|)]
  have hs := mul_le_mul_of_nonneg_right h hy
  simpa [sq_abs] using hs

theorem pair_arithmetic_bound (a b x : ℝ) :
    2 * |a ^ 2 - b ^ 2| * x ^ 2
      ≤ ((a - b) ^ 2 + (a + b) ^ 2) * x ^ 2 := by
  rw [half_density_pair_factor]
  have h := pair_am_gm (a - b) (a + b) (x ^ 2) (sq_nonneg x)
  simpa [mul_assoc, mul_left_comm, mul_comm, sq_abs] using h

theorem pair_shell_nonnegative (a b x : ℝ) :
    0 ≤ |a ^ 2 - b ^ 2| * x ^ 2 := by
  positivity

theorem scope_fixture :
    (True ∧ True ∧ True ∧ True) ∧
      ¬ (False ∨ False ∨ False ∨ False ∨ False) := by
  norm_num

end Tect.R378
