import Mathlib

namespace Tect.R409

/- R409 checks only scalar signs and finite inverse-spectrum bookkeeping.
   Matrix congruence, pseudoinverse identities, heat kernels and limiting
   statements remain in the executable and open boundary. -/

theorem trace_projector_nonnegative {x : ℝ} (hx : 0 ≤ x) :
    0 ≤ x := by
  exact hx

theorem heat_trace_inverse_nonnegative {lambda : ℝ} (h : 0 < lambda) :
    0 ≤ 1 / lambda := by
  exact le_of_lt (one_div_pos.mpr h)

theorem finite_scope :
    (0 < (1 : ℝ) / 2) ∧ ((1 : ℝ) / 2 ≤ 1) ∧ (0 ≤ (3 : ℝ) / 5) := by
  norm_num

end Tect.R409
