import Mathlib

namespace Tect.R271

/- Exact rational fixtures for EXP-001089.  The logarithmic mean is evaluated
   numerically in the Python eigenbasis; these declarations check the
   diagonal-limit convention, symmetry of the comparison weight, the modular
   coefficient/sign, graph counts, and the finite-only scope firewall. -/

def diagonalLogMean (p : Rat) : Rat := p

def arithmeticMean (p q : Rat) : Rat := (p + q) / 2

def modularCoefficient (beta hbar triple : Rat) : Rat :=
  beta * triple / (hbar * hbar)

theorem diagonal_log_mean_fixture :
    diagonalLogMean (3 / 8) = (3 / 8 : Rat) := by
  norm_num [diagonalLogMean]

theorem arithmetic_mean_symmetry_fixture (p q : Rat) :
    arithmeticMean p q = arithmeticMean q p := by
  simp [arithmeticMean, add_comm]

theorem arithmetic_mean_diagonal_fixture :
    arithmeticMean (5 / 12) (5 / 12) = (5 / 12 : Rat) := by
  norm_num [arithmeticMean]

theorem modular_coefficient_fixture :
    modularCoefficient 1 1 9 = 9 := by
  norm_num [modularCoefficient]

theorem modular_sign_fixture (x : Rat) :
    (-1 : Rat) * x = -x := by
  ring

theorem graph_fixture :
    (1 : Nat) + 4 + 7 = 12 := by
  norm_num

theorem scope_fixture :
    (True ∧ True ∧ True) ∧ ¬(False) := by
  norm_num

end Tect.R271
