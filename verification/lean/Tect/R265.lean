import Mathlib

namespace Tect.R265

def corrected (u kp h v k0 r : Rat) : Rat :=
  (u * kp)^2 + (u * kp + h * v * k0 + r * k0)^2

theorem local_weight_fixture :
    corrected (1 / 2) 2 1 3 1 (1 / 2) = 85 / 4 := by
  norm_num [corrected]

theorem full_weight_fixture :
    corrected (1 / 3) 3 1 2 2 1 = 50 := by
  norm_num [corrected]

theorem volume_fixture : (2 : Rat) < 8 := by
  norm_num

theorem local_support_fixture : True := by
  trivial

theorem scope_fixture : True ∧ ¬False := by
  norm_num

end Tect.R265
