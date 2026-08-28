import Mathlib

namespace Tect.R407

/- R407 formalizes only scalar bookkeeping for the unordered-pair path bound.
   Conductance matrices, tree algorithms, spectra and regulator limits remain
   outside this entrypoint. -/

theorem canonical_path_load_nonnegative {x : ℝ} (hx : 0 ≤ x) :
    0 ≤ x := by
  exact hx

theorem tree_bound_nonnegative {rho : ℝ} (hrho : 0 < rho) :
    0 ≤ 1 / rho := by
  exact le_of_lt (one_div_pos.mpr hrho)

theorem finite_scope :
    (0 < (1 : ℝ) / 2) ∧ ((1 : ℝ) / 2 ≤ 1) ∧ (0 ≤ (3 : ℝ) / 5) := by
  norm_num

end Tect.R407
