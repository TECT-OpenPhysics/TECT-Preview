import Mathlib

namespace Tect.R278

/- A general domain-transfer lemma for the truncated oscillator boundary.
   The scalar implication is stronger than the probability case: if
   n^2 * p_n tends to zero, then n * sqrt(p_n) tends to zero.  Applied to
   p_n=<psi_n,P_top psi_n>, this is the exact weighted top-tail condition
   needed by the finite CCR defect.  The lemma does not prove that the Q3
   Gibbs or evolved-history tails satisfy the condition. -/

theorem top_tail_to_ccr_defect {p : Nat → ℝ}
    (hweighted : Filter.Tendsto (fun n : Nat => (n : ℝ) ^ 2 * p n)
      Filter.atTop (nhds 0)) :
    Filter.Tendsto (fun n : Nat => (n : ℝ) * Real.sqrt (p n))
      Filter.atTop (nhds 0) := by
  have hsqrt : Filter.Tendsto
      (fun n : Nat => Real.sqrt ((n : ℝ) ^ 2 * p n))
      Filter.atTop (nhds 0) := by
    simpa using hweighted.sqrt
  apply hsqrt.congr
  intro n
  rw [Real.sqrt_mul (sq_nonneg (n : ℝ))]
  rw [Real.sqrt_sq_eq_abs, abs_of_nonneg (Nat.cast_nonneg n)]

theorem top_tail_squared_fixture :
    ((8 : ℝ) ^ 2 * (1 / 64 : ℝ)) = 1 := by
  norm_num

theorem top_tail_defect_fixture :
    (8 : ℝ) * Real.sqrt (1 / 64 : ℝ) = 1 := by
  norm_num

theorem scope_fixture :
    ((8 : ℝ) ^ 2 * (1 / 64 : ℝ)) = 1 ∧
      (8 : ℝ) * Real.sqrt (1 / 64 : ℝ) = 1 := by
  constructor
  · exact top_tail_squared_fixture
  · exact top_tail_defect_fixture

end Tect.R278
