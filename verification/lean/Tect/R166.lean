import Mathlib

namespace Tect.R166

/- Exact rational core of the registered R-166 sparse-fibre certificate. -/

theorem global_lower_decomposition :
    (-332863942666997 / 439505584128000 : ℚ) =
      -(4 : ℚ) / 5 + 18740524635403 / 439505584128000 := by
  norm_num

theorem stronger_minus_four_fifths_margin :
    (0 : ℚ) < 18740524635403 / 439505584128000 := by
  norm_num

theorem derivative_root_bracket :
    (-1360786403 / 1277632512000 : ℚ) < 0 ∧
      (0 : ℚ) < 97738714417 / 876455903232000 := by
  norm_num

theorem curvature_bracket :
    (-14485115 / 584303935488 : ℚ) < 0 ∧
      (0 : ℚ) < 9542665 / 2337215741952 ∧
      (0 : ℚ) < 6865745 / 5962285056 := by
  norm_num

theorem two_harmonic_counterdirection :
    (3 : ℚ) / 32 / (1 / 4) = 3 / 8 ∧
      (0 : ℚ) < 3 / 8 ∧
      (3 : ℚ) / 8 < 1 := by
  norm_num

theorem rho_choice_and_downstream_constants :
    -(1 : ℚ) / 110 + 3 / 20 = 31 / 220 ∧
      5 / 11 - (3 / 20) / 4 = 367 / 880 ∧
      (1 : ℚ) / 10 < 31 / 220 ∧
      (0 : ℚ) < 367 / 880 := by
  norm_num

theorem rho_margin_target :
    (10 : ℚ) / 11 - 3 / 20 = 167 / 220 ∧
      (0 : ℚ) < 167 / 220 := by
  norm_num

end Tect.R166
