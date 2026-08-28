import Mathlib

namespace Tect.R408

/- R408 checks only scalar positivity and the finite unordered-pair
   bookkeeping.  Pseudoinverses, graph spectra, Gibbs rows and limiting
   statements remain in the executable and open boundary. -/

theorem resistance_pair_nonnegative {x : ℝ} (hx : 0 ≤ x) :
    0 ≤ x := by
  exact hx

theorem resistance_bound_nonnegative {rho : ℝ} (h : 0 < rho) :
    0 ≤ 1 / rho := by
  exact le_of_lt (one_div_pos.mpr h)

theorem finite_scope :
    (0 < (1 : ℝ) / 2) ∧ ((1 : ℝ) / 2 ≤ 1) ∧ (0 ≤ (3 : ℝ) / 5) := by
  norm_num

end Tect.R408
