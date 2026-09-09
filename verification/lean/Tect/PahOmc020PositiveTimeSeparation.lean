import Mathlib

namespace Tect.PahOmc020PositiveTimeSeparation

/- The derivative-to-bound step is the ordinary first-order calculus input.
   This file checks the exact algebraic implication used after that input:
   a positive derivative gap at a common initial value separates the two
   finite-time values on a right neighbourhood.  It does not choose a PAH
   root owner or assert an anchored limit. -/

theorem first_order_separation
    (u v : ℝ → ℝ) (c δ : ℝ)
    (hc : 0 < c) (hδ : 0 < δ)
    (h0 : u 0 = v 0)
    (hbound : ∀ t, 0 < |t| → |t| < δ →
      |((u t - u 0) - (v t - v 0)) - c * t| < (c / 2) * |t|) :
    ∀ t, 0 < t → t < δ → v t < u t := by
  intro t ht htd
  have herror := hbound t (by simpa [abs_of_pos ht] using ht)
    (by simpa [abs_of_pos ht] using htd)
  have hlow : -((c / 2) * t) < ((u t - u 0) - (v t - v 0)) - c * t :=
    by simpa [abs_of_pos ht] using (abs_lt.mp herror).1
  nlinarith [h0]

theorem explicit_linear_gap :
    ∀ t : ℝ, 0 < t →
      (Real.exp (-2 : ℝ) : ℝ) * t < (2 : ℝ) * Real.exp (-2 : ℝ) * t := by
  intro t ht
  have he : 0 < Real.exp (-2 : ℝ) := by positivity
  nlinarith

theorem derivative_gap_algebra :
    (2 : ℝ) * Real.exp (-2 : ℝ) - Real.exp (-2 : ℝ) = Real.exp (-2 : ℝ) := by
  ring

end Tect.PahOmc020PositiveTimeSeparation
