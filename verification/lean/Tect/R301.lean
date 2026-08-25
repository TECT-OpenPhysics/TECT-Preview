import Mathlib

namespace Tect.R301

/- R301 checks the exact rational lower-bound and shifted-form bookkeeping
   behind EXP-001130.  It does not formalize Friedrichs operators or domains. -/

def onsite (x p : Rat) : Rat := p^2 / 2 - x^2 / 2 + (3 / 5 : Rat) * x^4 / 4

def bond (x y : Rat) : Rat :=
  (3 / 5 : Rat) * (x - y)^2 / 2 + (1 / 10 : Rat) * (x - y)^2 * (x^2 + y^2) / 4

theorem onsite_lower_fixture (x p : Rat) :
    -5 / 12 ≤ onsite x p := by
  unfold onsite
  nlinarith [sq_nonneg p, sq_nonneg (x^2 - 5 / 3)]

theorem bond_nonnegative_fixture (x y : Rat) :
    0 ≤ bond x y := by
  unfold bond
  positivity

theorem edge_form_comparison_fixture (h b : Rat)
    (hb : b ≤ (10 / 3 : Rat) * h + 304 / 45) :
    h + b + 11 / 6 ≤ (13 / 3 : Rat) * (h + 11 / 6) + 29 / 45 := by
  linarith

theorem reverse_form_comparison_fixture (h b : Rat)
    (hb : 0 ≤ b) :
    h + 11 / 6 ≤ h + b + 11 / 6 := by
  linarith

theorem two_orientation_constant_fixture :
    (13 / 3 : Rat) + 29 / 45 = 224 / 45 := by
  norm_num

theorem canonical_shift_fixture :
    -5 / 6 + 11 / 6 = (1 : Rat) := by
  norm_num

theorem scope_fixture :
    (True ∧ True ∧ True) ∧ ¬ False := by
  norm_num

end Tect.R301
