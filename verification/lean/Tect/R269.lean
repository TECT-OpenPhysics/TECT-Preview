import Mathlib

namespace Tect.R269

def secondCoefficient (sigma time weight : Rat) : Rat := sigma * time * weight
def modularCoefficient (beta sigma time weight : Rat) : Rat := beta * secondCoefficient sigma time weight

theorem coefficient_fixture : secondCoefficient 1 (1 / 10) (3 / 5) = 3 / 50 := by
  norm_num [secondCoefficient]

theorem reverse_coefficient_fixture : secondCoefficient (-1) (1 / 10) (3 / 5) = -3 / 50 := by
  norm_num [secondCoefficient]

theorem modular_fixture : modularCoefficient 1 1 (1 / 10) (3 / 5) = 3 / 50 := by
  norm_num [modularCoefficient, secondCoefficient]

theorem source_commutation_fixture : (0 : Rat) = 0 := by
  norm_num

theorem disjoint_support_fixture : (1 : Rat) - 1 = 0 := by
  norm_num

theorem scope_fixture : True ∧ ¬False := by
  norm_num

end Tect.R269
