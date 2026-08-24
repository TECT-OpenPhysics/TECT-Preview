import Mathlib

namespace Tect.R268

def directBound (time weight : Rat) : Rat := 2 * time * weight
def supportFactor (sites weight : Rat) : Rat := sites * weight

theorem direct_fixture : directBound (1 / 10) (3 / 5) = 3 / 25 := by
  norm_num [directBound]

theorem modular_fixture : directBound (1 / 10) (3 / 5) * (1 : Rat) = 3 / 25 := by
  norm_num [directBound]

theorem two_site_support_fixture : supportFactor 2 (3 / 5) = 6 / 5 := by
  norm_num [supportFactor]

theorem orientation_sum_fixture : (1 : Rat) + 1 = 2 := by
  norm_num

theorem zero_tail_fixture : (2 : Rat) - 2 = 0 := by
  norm_num

theorem scope_fixture : True ∧ ¬False := by
  norm_num

end Tect.R268
