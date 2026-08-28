import Mathlib

namespace Tect.R406

/- R406 formalizes only scalar bookkeeping for the harmonic/residual split.
   Schur spectra, Gibbs rows, graph limits and operator domains remain
   outside this entrypoint. -/

theorem harmonic_residual_square_nonnegative {x : ℝ} :
    0 ≤ x ^ 2 := by
  exact sq_nonneg x

theorem schur_variance_split {a b : ℝ} :
    (a + b) ^ 2 = a ^ 2 + 2 * a * b + b ^ 2 := by
  ring

theorem finite_scope :
    (0 < (1 : ℝ) / 2) ∧ ((1 : ℝ) / 2 ≤ 1) ∧ (0 ≤ (3 : ℝ) / 5) := by
  norm_num

end Tect.R406
