import Mathlib

namespace Tect.R267

def directBound (time weight : Rat) : Rat := 2 * time * weight
def modularBound (beta time weight : Rat) : Rat := beta * directBound time weight

theorem direct_fixture : directBound (1 / 10) (3 / 5) = 3 / 25 := by
  norm_num [directBound]

theorem modular_fixture : modularBound 1 (1 / 10) (3 / 5) = 3 / 25 := by
  norm_num [modularBound, directBound]

theorem zero_tail_fixture : (2 : Rat) - 2 = 0 := by
  norm_num

theorem orientation_fixture : (1 : Rat) + 1 = 2 := by
  norm_num

theorem scope_fixture : True ∧ ¬False := by
  norm_num

end Tect.R267
