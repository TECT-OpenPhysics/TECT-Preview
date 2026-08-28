import Mathlib

namespace Tect.R379

/- R379 formalizes the scalar three-channel identities behind the
   half-density bridge.  Matrix Hilbert--Schmidt norms and modular limits
   remain outside this cross-check. -/

theorem anticommutator_three_channel (l r t : ℝ) :
    l + r + 2 * t = (l + r) + 2 * t := by
  ring

theorem commutator_three_channel (l r t : ℝ) :
    l + r - 2 * t = (l + r) - 2 * t := by
  ring

theorem commutator_anticommutator_sum (l r t : ℝ) :
    (l + r - 2 * t) + (l + r + 2 * t) = 2 * (l + r) := by
  ring

theorem two_slice_am_gm (u v : ℝ) :
    2 * |u * v| ≤ u ^ 2 + v ^ 2 := by
  have h : 2 * |u| * |v| ≤ |u| ^ 2 + |v| ^ 2 := by
    nlinarith [sq_nonneg (|u| - |v|)]
  simpa [abs_mul, sq_abs, mul_assoc] using h

theorem two_slice_nonnegative (u v : ℝ) :
    0 ≤ |u * v| := by
  positivity

theorem scope_fixture :
    (True ∧ True ∧ True ∧ True) ∧
      ¬ (False ∨ False ∨ False ∨ False ∨ False) := by
  norm_num

end Tect.R379
