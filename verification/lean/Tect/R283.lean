import Mathlib

namespace Tect.R283

/- Scalar arithmetic only.  The registered Q3 M20/history estimate is a premise
   in the manifest; this file checks the hard-cutoff constants and exact fixture
   instances without asserting a Q3 domain or Dyson theorem. -/

theorem safe_multiplicity_fixture :
    (6 : Rat) * 32 * (2 * 32 + 1) ^ 2 ≤ 54 * (32 : Rat) ^ 3 := by
  norm_num

theorem hard_cutoff_power_fixture :
    ((6 : Rat) * 32 * (2 * 32 + 1) ^ 2) ^ 2 / (4 : Rat) ^ 16
      ≤ (2916 : Rat) / 4 := by
  norm_num

theorem factorial_shell_fixture :
    ((16 : Rat) ^ 32) / Nat.factorial 32
      ≤ ((3 : Rat) / 2) ^ 32 := by
  norm_num [Nat.factorial]

theorem scope_fixture :
    (2916 : Rat) = 54 ^ 2 ∧ (32 : Rat) ^ (2 : Nat) = 1024 ∧
      (0 : Rat) < 2916 := by
  norm_num

end Tect.R283
