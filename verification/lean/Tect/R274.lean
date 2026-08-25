import Mathlib

namespace Tect.R274

/- Exact rational fixture arithmetic for EXP-001092.  These declarations
   check the factors in the finite Duhamel, observable, modular, and
   two-orientation bounds only; they do not encode matrix exponentials,
   unbounded domains, uniform limits, or QFT reconstruction. -/

def duhamelCoefficient (time tail hbar : Rat) : Rat :=
  time * tail / hbar

def observableCoefficient (time aNorm tail hbar : Rat) : Rat :=
  2 * time * aNorm * tail / hbar

def modularCoefficient (beta hNorm time aNorm tail hbar : Rat) : Rat :=
  4 * beta * time * hNorm * aNorm * tail / hbar

theorem duhamel_fixture :
    duhamelCoefficient (1 / 10) (3 / 5) 1 = (3 / 50 : Rat) := by
  norm_num [duhamelCoefficient]

theorem observable_fixture :
    observableCoefficient (1 / 10) 1 (3 / 5) 1 = (3 / 25 : Rat) := by
  norm_num [observableCoefficient]

theorem modular_fixture :
    modularCoefficient 1 7 (1 / 10) 1 (3 / 5) 1 = (42 / 25 : Rat) := by
  norm_num [modularCoefficient]

theorem two_orientation_fixture :
    (2 : Rat) * (3 / 25) = (6 / 25 : Rat) ∧
    (2 : Rat) * (42 / 25) = (84 / 25 : Rat) := by
  norm_num

theorem fixed_regulator_zero_fixture :
    (0 : Rat) * (1 / 10) = 0 := by
  norm_num

theorem scope_fixture :
    (True ∧ True ∧ True) ∧ ¬(False) := by
  norm_num

end Tect.R274
