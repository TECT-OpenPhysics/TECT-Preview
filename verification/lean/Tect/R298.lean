import Mathlib

namespace Tect.R298

/- R298 checks the exact scalar polynomial and power-count fixtures behind
   EXP-001127.  It does not formalize unbounded operators, translated packets,
   or thermodynamic limits. -/

def bond (c lam q v : Rat) : Rat := c * (q - v)^2 / 2 + lam * (q - v)^2 * (q^2 + v^2) / 4

def force (c lam q v : Rat) : Rat := c * (q - v) + lam * (q - v) * (2*q^2 - q*v + v^2) / 2

theorem tail_bond_fixture (c lam q : Rat) :
    bond c lam q 0 = c*q^2/2 + lam*q^4/4 := by
  simp [bond]
  ring

theorem tail_force_fixture (c lam q : Rat) :
    force c lam q 0 = c*q + lam*q^3 := by
  simp [force]
  ring

theorem mixed_tail_expansion (c lam q : Rat) :
    bond c lam q 0 * force c lam q 0 =
      c^2*q^3/2 + 3*c*lam*q^5/4 + lam^2*q^7/4 := by
  simp [bond, force]
  ring

theorem quartic_power_deficit :
    (7 : Rat) - 4 * (3 / 4 : Rat) = 4 := by
  norm_num

theorem quadratic_boundary_deficit :
    (3 : Rat) - 4 * (3 / 4 : Rat) = 0 := by
  norm_num

theorem leading_coefficient_positive {lam : Rat} (h : 0 < lam) :
    0 < lam^2 / 4 := by
  positivity

theorem scope_fixture :
    (True ∧ True ∧ True ∧ True) ∧ ¬ False := by
  norm_num

end Tect.R298
