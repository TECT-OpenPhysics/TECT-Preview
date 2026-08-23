import Mathlib

namespace Tect.R207

/-!
  Exact algebraic cross-check for the Q3 state-weighted envelope.

  The analytic hypotheses (positive finite-volume K, form inequalities and
  domains) are not encoded here.  These theorems check only the conjugation
  multiplication and inverse identities used by the executable fixture.
-/

def conjugate {α : Type*} [Monoid α] (s r a : α) : α := s * a * r

theorem conjugate_mul {α : Type*} [Monoid α] {s r a b : α}
    (hrs : r * s = 1) :
    conjugate s r (a * b) = conjugate s r a * conjugate s r b := by
  calc
    conjugate s r (a * b) = s * a * b * r := by simp [conjugate, mul_assoc]
    _ = s * a * (r * s) * b * r := by rw [hrs]; simp
    _ = conjugate s r a * conjugate s r b := by simp [conjugate, mul_assoc]

theorem conjugate_one {α : Type*} [Monoid α] {s r : α}
    (hsr : s * r = 1) : conjugate s r 1 = 1 := by
  simp [conjugate, hsr]

theorem conjugate_inverse {α : Type*} [Monoid α] {s r a : α}
    (hrs : r * s = 1) (hsr : s * r = 1) :
    conjugate r s (conjugate s r a) = a := by
  calc
    conjugate r s (conjugate s r a) = r * s * a * r * s := by simp [conjugate, mul_assoc]
    _ = a := by simp [mul_assoc, hrs, hsr]

theorem rational_fixture_inverse :
    ((2 : ℚ) * (1 / 2 : ℚ) = 1) ∧ ((1 / 2 : ℚ) * (2 : ℚ) = 1) := by
  norm_num

end Tect.R207
