import Mathlib

namespace Tect.R487

/- The finite fixture retains one radial quantum under the neutral inclusion. -/
def qOneCharge : ℕ := 1 + 0 + 0 + 0
def qOneExtension : ℕ := qOneCharge + 0 + 0

theorem nonzero_charge_exact : qOneCharge = 1 := by
  norm_num [qOneCharge]

theorem neutral_inclusion_preserves_charge : qOneExtension = qOneCharge := by
  rfl

/- The oriented first split triangle has edges h00, v1 and d0^{-1}.
   Gauge shifts cancel before taking the Z_2 character. -/
def triangleGaugeShift (ga gb gd : ℤ) : ℤ :=
  (gb - ga) + (gd - gb) - (gd - ga)

theorem triangle_gauge_shift_cancels (ga gb gd : ℤ) :
    triangleGaugeShift ga gb gd = 0 := by
  dsimp [triangleGaugeShift]
  ring

def triangleExponent (uh uv ud ga gb gd : ℤ) : ℤ :=
  (uh + gb - ga) + (uv + gd - gb) - (ud + gd - ga)

theorem holonomy_gauge_invariant (uh uv ud ga gb gd : ℤ) :
    triangleExponent uh uv ud ga gb gd = uh + uv - ud := by
  dsimp [triangleExponent]
  ring

/- Four aperture bits, five links, four phases and four one-hot positions. -/
def stateCount : ℕ := (2 : ℕ) ^ 4 * 2 ^ 5 * 2 ^ 4 * 4

theorem state_count_exact : stateCount = 32768 := by
  norm_num [stateCount]

/- K=2 retains both directed link labels, even when their maps coincide. -/
def linkChannelMultiplicity : ℕ := 1 + 1

theorem link_channel_multiplicity : linkChannelMultiplicity = 2 := by
  norm_num [linkChannelMultiplicity]

/- The exact root tuple is compared by the executable lanes; this theorem
   records the equality target without replacing that finite enumeration. -/
def jointRoot (deltaF mobilitySquare deltaEll deltaH exponent : ℚ) :
    ℚ × ℚ × ℚ × ℚ × ℚ :=
  (deltaF, mobilitySquare, deltaEll, deltaH, exponent)

theorem joint_root_identity (deltaF mobilitySquare deltaEll deltaH exponent : ℚ) :
    jointRoot deltaF mobilitySquare deltaEll deltaH exponent =
      jointRoot deltaF mobilitySquare deltaEll deltaH exponent := by
  rfl

/- The inherited G_1 -> G_2 matter-transfer boundary control is exact. -/
def boundaryDeltaG1 : ℚ := 0
def boundaryDeltaG2 : ℚ := -1

theorem boundary_defect_exact :
    boundaryDeltaG2 - boundaryDeltaG1 = (-1 : ℚ) := by
  norm_num [boundaryDeltaG1, boundaryDeltaG2]

def claimBearing : Bool := false
def physicalPromotion : Bool := false

theorem non_promotion_firewall :
    claimBearing = false ∧ physicalPromotion = false := by
  decide

end Tect.R487
