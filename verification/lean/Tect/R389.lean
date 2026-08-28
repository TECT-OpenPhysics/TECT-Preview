import Mathlib

namespace Tect.R389

noncomputable def projected_square (mass x : ℝ) : ℝ := mass * x ^ 2

theorem projected_seminorm_nonnegative (mass x : ℝ) (hmass : 0 ≤ mass) :
    0 ≤ projected_square mass x := by
  dsimp [projected_square]
  positivity

theorem window_mass_split (mass tail : ℝ) (h : mass + tail = 1) :
    mass = 1 - tail := by
  linarith

theorem scope_fixture :
    projected_square 1 2 = 4 ∧ (0 ≤ (1 : ℝ) / 4) := by
  norm_num [projected_square]

end Tect.R389
