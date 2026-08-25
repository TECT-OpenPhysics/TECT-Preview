import Mathlib

namespace Tect.R288

/- R288 checks only rational radius-loss and recurrence fixtures.  It does not
   formalize the scalar calculus, exponentials, unbounded operators, or limits. -/

def delta : ℚ := 1 / 10
def time : ℚ := 1 / 5
def neighbours : ℚ := 6
def orientations : ℚ := 2

theorem delta_fixture : delta = 1 / 10 := by
  norm_num [delta]

theorem n1_scale_fixture : (1 : ℚ) / delta = 10 := by
  norm_num [delta]

theorem branch_count_fixture : orientations * neighbours = 12 := by
  norm_num [orientations, neighbours]

theorem rational_exponent_fixture : orientations * neighbours * ((1 : ℚ) / delta) * time = 24 := by
  norm_num [orientations, neighbours, delta, time]

theorem same_radius_witness : (10 : ℚ) ^ 4 > (1 : ℚ) ^ 4 := by
  norm_num

end Tect.R288
