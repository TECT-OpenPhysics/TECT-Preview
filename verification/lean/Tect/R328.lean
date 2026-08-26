import Mathlib

namespace Tect.R328

/- R328 checks only the exact rational bookkeeping for EXP-001158.  It does
   not formalize finite matrix spectra, unbounded Q3 operators, domains, or
   any thermodynamic/QFT limit. -/

theorem three_quarter_weight_fixture :
    (1 / 8 : Rat)^4 = (1 / 16 : Rat)^3 := by
  norm_num

theorem weight_decay_fixture (d : Nat) :
    ((1 / 16 : Rat)^d)^3 = (1 / 8 : Rat)^(4 * d) := by
  calc
    ((1 / 16 : Rat)^d)^3 = (1 / 16 : Rat)^(d * 3) := by
      exact (pow_mul (1 / 16 : Rat) d 3).symm
    _ = (1 / 16 : Rat)^(3 * d) := by rw [Nat.mul_comm]
    _ = ((1 / 16 : Rat)^3)^d := by
      exact pow_mul (1 / 16 : Rat) 3 d
    _ = ((1 / 8 : Rat)^4)^d := by rw [three_quarter_weight_fixture]
    _ = (1 / 8 : Rat)^(4 * d) := by
      exact (pow_mul (1 / 8 : Rat) 4 d).symm

theorem scope_fixture :
    (True ∧ True ∧ True) ∧ ¬ (False ∨ False ∨ False ∨ False) := by
  norm_num

end Tect.R328
