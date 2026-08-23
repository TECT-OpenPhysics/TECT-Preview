import Mathlib

namespace Tect.R209

/-!
  Scalar/context cross-check for EXP-001025.  The finite matrix scripts carry
  the induced-norm and support fixtures; this file checks only the exact
  insertion and endpoint-factor algebra used there.
-/

theorem context_insert (a b c : ℝ) : a * (b * c) = (a * b) * c := by
  ring

theorem abs_product_context (a b : ℝ) : |a * b| = |a| * |b| := by
  exact abs_mul a b

theorem conjugation_factor (g m : ℝ) : g * (m * g) = g ^ 2 * m := by
  ring

theorem half_power_factor (g m : ℝ) : g ^ 0 * m = m := by
  simp

end Tect.R209
