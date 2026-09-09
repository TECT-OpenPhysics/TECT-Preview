import Mathlib

namespace Tect.PahOmc020Radial

/- These declarations formalize only the rational envelope used for the
   amplitude-only sector.  They do not formalize the PAH measure, the
   variation-of-constants theorem, the R-510 state limit, the R-512 form
   representation, or the full anchored-n semigroup problem. -/

def h (j : ℕ) : ℚ := ((1 : ℚ) / 2) ^ j

theorem residual_coefficient (H L hstep : ℚ) :
    H * (2 * L * hstep) ^ 2 / 2 = 2 * H * L ^ 2 * hstep ^ 2 := by
  ring

theorem compact_time_error (T H L hstep : ℚ) :
    T * (2 * H * L * hstep) = 2 * T * H * L * hstep := by
  ring

theorem mesh_half_step (j : ℕ) :
    h (j + 1) = h j / 2 := by
  unfold h
  rw [pow_succ]
  ring

theorem mesh_positive (j : ℕ) : 0 < h j := by
  unfold h
  positivity

theorem mesh_strict_decay (j : ℕ) : h (j + 1) < h j := by
  rw [mesh_half_step]
  have hp : 0 < h j := mesh_positive j
  nlinarith

theorem radial_fixture_small :
    (7 / 4 : ℚ) * (2 * (3 / 2 : ℚ) * (5 / 3 : ℚ)) * h 10 < 1 / 100 := by
  norm_num [h]

theorem independent_fixture_small :
    (5 / 4 : ℚ) * (2 * (4 / 3 : ℚ) * (7 / 2 : ℚ)) * h 11 < 1 / 100 := by
  norm_num [h]

end Tect.PahOmc020Radial
