import Mathlib

namespace Tect.R264

def weightedRight (u kp : Rat) : Rat := (u * kp)^2

def weightedCorrected (u kp h v k0 r : Rat) : Rat :=
  (u * kp)^2 + (u * kp + h * v * k0 + r * k0)^2

def weightedIdeal (u kp h v k0 : Rat) : Rat :=
  (u * kp)^2 + (u * kp + h * v * k0)^2

theorem weighted_right_fixture :
    weightedRight (3 / 2) 2 = 9 := by
  norm_num [weightedRight]

theorem weighted_corrected_fixture :
    weightedCorrected (3 / 2) 2 1 (5 / 2) (3 / 2) (1 / 2) = 261 / 4 := by
  norm_num [weightedCorrected]

theorem weighted_ideal_fixture :
    weightedIdeal (3 / 2) 2 1 (5 / 2) (3 / 2) = 873 / 16 := by
  norm_num [weightedIdeal]

theorem residual_fixture :
    weightedCorrected (3 / 2) 2 1 (5 / 2) (3 / 2) (1 / 2) -
        weightedIdeal (3 / 2) 2 1 (5 / 2) (3 / 2) = 171 / 16 := by
  norm_num [weightedCorrected, weightedIdeal]

theorem commutator_fixture :
    weightedCorrected (3 / 2) 2 1 (5 / 2) (3 / 2) 0 =
        weightedIdeal (3 / 2) 2 1 (5 / 2) (3 / 2) := by
  norm_num [weightedCorrected, weightedIdeal]

theorem scope_fixture : True ∧ ¬False := by
  norm_num

end Tect.R264
