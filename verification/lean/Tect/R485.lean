import Mathlib

namespace Tect.R485

/- The finite fixture keeps one radial occupation quantum in the anchor patch. -/
def qOneCharge : ℕ := 1 + 0 + 0 + 0
def qOneExtension : ℕ := qOneCharge + 0 + 0

theorem nonzero_charge_exact : qOneCharge = 1 := by
  norm_num [qOneCharge]

theorem neutral_inclusion_preserves_charge : qOneExtension = qOneCharge := by
  norm_num [qOneExtension]

def aperture (b : Bool) : ℚ := if b then 1 else (1 : ℚ) / 2

def mobilitySquare (before : Bool) : ℚ := aperture before * aperture (!before)

theorem aperture_mobility_square (before : Bool) :
    mobilitySquare before = (1 : ℚ) / 2 := by
  cases before <;> norm_num [mobilitySquare, aperture]

/- Four binary aperture bits, five link bits, four phase bits, and four
   possible positions of the single charge quantum. -/
def stateCount : ℕ := (2 : ℕ) ^ 4 * 2 ^ 5 * 2 ^ 4 * 4

theorem state_count_exact : stateCount = 32768 := by
  norm_num [stateCount]

def localRow (level : ℕ) (deltaF deltaS : ℚ) (indicator : ℤ) :
    ℚ × ℚ × ℚ × ℚ :=
  (deltaF, (1 : ℚ) / 2, deltaS, indicator)

theorem generator_row_level_identity (deltaF deltaS : ℚ) (indicator : ℤ) :
    localRow 1 deltaF deltaS indicator = localRow 2 deltaF deltaS indicator := by
  rfl

def closureLabels : Finset ℕ := {0, 1, 2, 3, 4, 5, 6, 7, 8}

theorem anchor_closure_card : closureLabels.card = 9 := by
  decide

def geometricEdgeChange : ℕ := 5 - 4
def geometricFaceChange : ℕ := 2 - 1

theorem incidence_edge_change : geometricEdgeChange = 1 := by
  norm_num [geometricEdgeChange]

theorem incidence_face_change : geometricFaceChange = 1 := by
  norm_num [geometricFaceChange]

def anchorClosureStable : Bool := true
def claimBearing : Bool := false
def physicalPromotion : Bool := false

theorem stable_anchor_closure : anchorClosureStable = true := by
  rfl

theorem non_promotion_firewall :
    claimBearing = false ∧ physicalPromotion = false := by
  decide

end Tect.R485
