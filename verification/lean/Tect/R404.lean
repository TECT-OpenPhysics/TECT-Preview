import Mathlib

namespace Tect.R404

/- R404 formalizes only scalar nonnegativity and finite scope arithmetic for
   the intrinsic kinetic graph diagnostic.  Matrix spectra, Gibbs rows and
   all regulator or physical limits remain outside this entrypoint. -/

theorem graph_gap_nonnegative {x : ℝ} (hx : 0 ≤ x) :
    0 ≤ x := by
  exact hx

theorem variance_nonnegative {x : ℝ} :
    0 ≤ x ^ 2 := by
  exact sq_nonneg x

theorem finite_scope :
    (0 < (1 : ℝ) / 2) ∧ ((1 : ℝ) / 2 ≤ 1) := by
  norm_num

end Tect.R404
