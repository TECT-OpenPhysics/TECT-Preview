import Mathlib

namespace Tect.R295

/- R295 checks only the exact scalar fixture behind EXP-001124.  It does not
   formalize C*-states, traces, unbounded operators, or a QFT limit. -/

def square (x : Rat) : Rat := x * x

theorem rotation_norm_fixture : square (3 / 5 : Rat) + square (4 / 5 : Rat) = 1 := by
  norm_num [square]

theorem tail_square_fixture : square (1 : Rat) * (1 / 2 : Rat) + square (1 : Rat) * (1 / 3 : Rat) + square (-2 : Rat) * (1 / 6 : Rat) = 3 / 2 := by
  norm_num [square]

theorem dual_tail_static_fixture :
    ((1 : Rat) * (1 / 2 : Rat) + (1 : Rat) * (1 / 3 : Rat) + (-2 : Rat) * (-2 : Rat) * (1 / 6 : Rat)) = 3 / 2 := by
  norm_num

theorem scope_fixture : (True ∧ True ∧ True) ∧ ¬ False := by
  norm_num

end Tect.R295
