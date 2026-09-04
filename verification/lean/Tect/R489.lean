import Mathlib

namespace Tect.R489

/- Exact rational witness from the PAH-001 aperture root on every G_n, n >= 2. -/
def deltaF (R : ℚ) : ℚ := -(7 / 24 : ℚ) * R^2 - 5 / 8

def midpointExponent (R : ℚ) : ℚ := -deltaF R / 2

theorem delta_formula (R : ℚ) :
    deltaF R = -(7 / 24 : ℚ) * R^2 - 5 / 8 := by
  rfl

theorem exponent_formula (R : ℚ) :
    midpointExponent R = (7 / 48 : ℚ) * R^2 + 5 / 16 := by
  dsimp [midpointExponent, deltaF]
  ring

theorem rate_quadratic_coefficient_positive :
    (0 : ℚ) < (7 / 48 : ℚ) := by
  norm_num

theorem exponent_step_growth (R : ℚ) (hR : 0 ≤ R) :
    midpointExponent R < midpointExponent (R + 1) := by
  rw [exponent_formula, exponent_formula]
  nlinarith [sq_nonneg R]

def mobilitySquare : ℚ := 1 / 2

theorem mobility_square_exact :
    mobilitySquare = (1 / 2 : ℚ) := by
  norm_num [mobilitySquare]

def rootWeight : ℕ := 6

theorem root_weight_positive :
    0 < rootWeight := by
  norm_num [rootWeight]

/- The executable result is a method-level negative only. -/
def claimBearing : Bool := false
def physicalPromotion : Bool := false

theorem non_promotion_firewall :
    claimBearing = false ∧ physicalPromotion = false := by
  decide

end Tect.R489
