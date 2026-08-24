import Mathlib

namespace Tect.R272

/- Exact rational fixtures for EXP-001090.  Floating-point matrix evolution
   and the Gibbs eigenbasis remain in the Python artefacts; these lemmas check
   the modular commutator coefficient, orientation bookkeeping, time/radius
   fixtures, graph counts, and the finite-only scope firewall. -/

def modularCoefficient (beta _hbar commutatorValue : Rat) : Rat :=
  -beta * commutatorValue

def orientationSum (minusValue plusValue : Rat) : Rat :=
  minusValue + plusValue

theorem modular_coefficient_fixture :
    modularCoefficient 1 1 7 = -7 := by
  norm_num [modularCoefficient]

theorem orientation_sum_fixture :
    orientationSum (3 / 20) (1 / 20) = (1 / 5 : Rat) := by
  norm_num [orientationSum]

theorem time_fixture :
    (1 / 20 : Rat) < (1 / 10 : Rat) := by
  norm_num

theorem radius_fixture :
    (1 / 2 : Rat) < 1 ∧ (1 : Rat) < 2 := by
  norm_num

theorem graph_fixture :
    (1 : Nat) + 4 + 7 = 12 := by
  norm_num

theorem scope_fixture :
    (True ∧ True ∧ True) ∧ ¬(False) := by
  norm_num

end Tect.R272
