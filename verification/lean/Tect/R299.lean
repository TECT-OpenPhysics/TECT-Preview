import Mathlib

namespace Tect.R299

/- R299 checks only the scalar bookkeeping behind EXP-001128.  It does not
   encode finite matrices, unbounded Q3 domains, or thermodynamic limits. -/

def weighted (k x : Rat) : Rat := k * x / k

theorem commuting_weight_isometry (k x u : Rat) (hk : k ≠ 0) (hu : u ≠ 0) :
    weighted k (u * x / u) = weighted k x := by
  simp [weighted, hk, hu]

theorem two_orientation_multiplier (gplus gminus m : Rat) :
    (gminus * gplus) * m = gminus * (gplus * m) := by
  ring

theorem recurrence_reduction_fixture :
    (1 + (3 / 4 : Rat) * (1 / 8 : Rat)) *
      (1 + (3 / 4 : Rat) * (1 / 8 : Rat)) = 1225 / 1024 := by
  norm_num

theorem two_orientation_fixture :
    (2 : Rat) * (3 : Rat) = 6 := by
  norm_num

end Tect.R299
