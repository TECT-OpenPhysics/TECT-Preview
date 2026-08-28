import Mathlib

namespace Tect.R405

/- R405 formalizes only scalar phase-partition bookkeeping.  Matrix spectra,
   Gibbs measures, phase limits and operator domains remain outside this file. -/

theorem sector_mass_nonnegative {x y : ℝ} (hx : 0 ≤ x) (hy : 0 ≤ y) :
    0 ≤ x + y := by
  exact add_nonneg hx hy

theorem cross_capacity_nonnegative {x : ℝ} (hx : 0 ≤ x) :
    0 ≤ x := by
  exact hx

theorem finite_phase_split_scope :
    (0 < (1 : ℝ) / 2) ∧ ((1 : ℝ) / 2 ≤ 1) ∧ (0 ≤ (3 : ℝ) / 5) := by
  norm_num

end Tect.R405
