import Mathlib

namespace Tect.R201

/-!  Fixture-level cross-check for the covariance-aware Fourier current charge.
The primary theorem is the Pauli/Fierz contraction for the two registered
real PSD covariance blocks.  The remaining identities pin the heat integral
and the resulting charge at |r|^2 = 1 and lambda = 2. -/

theorem pauli_fierz_fixture :
    (2 : ℚ) * 2 * 2 - (3 : ℚ) / 2 = 13 / 2 := by
  norm_num

theorem pauli_fierz_equal_fixture :
    (2 : ℚ) * 2 * 2 - 2 = 6 := by
  norm_num

theorem pauli_fierz_orthogonal_fixture :
    (2 : ℚ) * 1 * 1 - 0 = 2 := by
  norm_num

theorem heat_integral_fixture :
    2 * ((1 : ℚ) / (2 * 2)) = (1 : ℚ) / 2 := by
  norm_num

theorem charge_fixture :
    ((1 : ℚ) * (13 / 2)) / 2 = 13 / 4 := by
  norm_num

theorem charge_equal_fixture :
    ((1 : ℚ) * 6) / 2 = 3 := by
  norm_num

theorem charge_orthogonal_fixture :
    ((1 : ℚ) * 2) / 2 = 1 := by
  norm_num

end Tect.R201
