import Mathlib

namespace Tect.R397

theorem one_minus_exp_le_linear {s x : ℝ} (hs : 0 ≤ s) (hx : 0 ≤ x) :
    1 - Real.exp (-s * x) ≤ s * x := by
  have h := Real.add_one_le_exp (-s * x)
  nlinarith

theorem semigroup_filter_composition {s t x : ℝ} :
    Real.exp (-s * x / 2) * Real.exp (-t * x / 2) =
      Real.exp (-(s + t) * x / 2) := by
  rw [← Real.exp_add]
  congr 1
  ring

theorem normalized_triangle_envelope {d e q : ℝ}
    (hd : 0 ≤ d) (he : 0 ≤ e) (hq : 0 ≤ q)
    (h1 : d ≤ e) (h2 : e ≤ q) :
    d ≤ q := by
  linarith

theorem finite_scope :
    (0 < (1 : ℝ) / 8) ∧ ((1 : ℝ) / 8 ≤ 1) ∧ ((1 : ℝ) / 8 ≤ 2) := by
  norm_num

end Tect.R397
