import Mathlib

namespace Tect.R398

/- R398 formalizes only the scalar nonnegativity and bookkeeping skeleton of
  the finite conditioned-collar diagnostic.  Matrix spectra, coordinate
  likelihoods, phase influence and all limiting statements stay outside this
  file. -/

theorem weighted_square_nonnegative {w x : ℝ} (hw : 0 ≤ w) :
    0 ≤ w * x ^ 2 := by
  exact mul_nonneg hw (sq_nonneg x)

theorem local_q2_identity (p l : ℝ) :
    p * l ^ 2 - p = p * (l - 1) ^ 2 + 2 * p * (l - 1) := by
  ring

theorem doob_shell_nonnegative {p x y : ℝ} (hp : 0 ≤ p) :
    0 ≤ p * (x - y) ^ 2 := by
  exact mul_nonneg hp (sq_nonneg (x - y))

theorem finite_scope :
    (0 < (1 : ℝ) / 8) ∧ ((1 : ℝ) / 8 ≤ 1) ∧ ((1 : ℝ) / 8 ≤ 2) := by
  norm_num

end Tect.R398
