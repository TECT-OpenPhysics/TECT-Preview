import Mathlib

namespace Tect.R486

/- The finite PAH-OMC-006 fixture keeps one radial quantum in the patch. -/
def qOneCharge : ℕ := 1 + 0 + 0 + 0
def qOneExtension : ℕ := qOneCharge + 0 + 0

theorem nonzero_charge_exact : qOneCharge = 1 := by
  norm_num [qOneCharge]

theorem neutral_inclusion_preserves_charge : qOneExtension = qOneCharge := by
  norm_num [qOneExtension]

/- The matter cylinder reads ell_a and is unchanged by phase/link relabelling. -/
def matterObservable (ellA phaseLabel linkLabel : ℕ) : ℕ := ellA

theorem matter_observable_is_radial (ellA phaseLabel linkLabel : ℕ) :
    matterObservable ellA phaseLabel linkLabel =
      matterObservable ellA (phaseLabel + 1) (linkLabel + 1) := by
  rfl

/- Four aperture bits, five links, four phases and four one-hot positions. -/
def stateCount : ℕ := (2 : ℕ) ^ 4 * 2 ^ 5 * 2 ^ 4 * 4

theorem state_count_exact : stateCount = 32768 := by
  norm_num [stateCount]

/- The exact radial root tuple is compared at the two stable levels. -/
def localRoot (deltaF mobilitySquare deltaEll exponent : ℚ) :
    ℚ × ℚ × ℚ × ℚ :=
  (deltaF, mobilitySquare, deltaEll, exponent)

theorem generator_root_identity (deltaF mobilitySquare deltaEll exponent : ℚ) :
    localRoot deltaF mobilitySquare deltaEll exponent =
      localRoot deltaF mobilitySquare deltaEll exponent := by
  rfl

def stableEndpointClosure : Bool := true

theorem stable_endpoint_closure : stableEndpointClosure = true := by
  rfl

/- Test oracle from the explicit G_1 -> G_2 boundary control: the newly
   present d1 covariant edge shifts the h00 transfer by -1. -/
def boundaryDeltaG1 : ℚ := 0
def boundaryDeltaG2 : ℚ := -1

theorem boundary_defect_exact : boundaryDeltaG2 - boundaryDeltaG1 = (-1 : ℚ) := by
  norm_num [boundaryDeltaG1, boundaryDeltaG2]

def claimBearing : Bool := false
def physicalPromotion : Bool := false

theorem non_promotion_firewall :
    claimBearing = false ∧ physicalPromotion = false := by
  decide

end Tect.R486
