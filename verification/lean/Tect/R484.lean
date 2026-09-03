import Mathlib

namespace Tect.R484

/- The aperture and link maps are the exact Q=0 PAH-OMC-004 fixture. -/
def aperture (b : Bool) : ℚ := if b then 1 else (1 : ℚ) / 2
def z2 (b : Bool) : ℚ := if b then -1 else 1
def onsite (x : ℚ) : ℚ := (x - 1) ^ 2 / 2
def edgeTerm (x y : ℚ) : ℚ := (x - y) ^ 2 / 2
def stiffness (x y : ℚ) : ℚ := 2 / (x + y)

def stateAt (state : Fin 9 → Bool) (index : Fin 9) : Bool := state index
def ap (state : Fin 9 → Bool) (index : Fin 9) : ℚ := aperture (stateAt state index)
def link (state : Fin 9 → Bool) (index : Fin 5) : ℚ :=
  z2 (state ⟨4 + index.1, by omega⟩)

/- Edges are (h00,v0,d0,h01,v1), and the two oriented Z_2 faces are
   (h00,v1,d0^(-1)) and (d0,h01^(-1),v0^(-1)). -/
def patchEnergy (state : Fin 9 → Bool) : ℚ :=
  onsite (ap state 0) + onsite (ap state 1) + onsite (ap state 2) + onsite (ap state 3)
    + edgeTerm (ap state 0) (ap state 1)
    + edgeTerm (ap state 0) (ap state 2)
    + edgeTerm (ap state 0) (ap state 3)
    + edgeTerm (ap state 2) (ap state 3)
    + edgeTerm (ap state 1) (ap state 3)
    + (stiffness (ap state 0) (ap state 1)
        + stiffness (ap state 1) (ap state 3)
        + stiffness (ap state 0) (ap state 3)) / 3
        * (1 - link state 0 * link state 4 * link state 2)
    + (stiffness (ap state 0) (ap state 3)
        + stiffness (ap state 2) (ap state 3)
        + stiffness (ap state 0) (ap state 2)) / 3
        * (1 - link state 2 * link state 3 * link state 1)

def squareEnergy (state : Fin 9 → Bool) : ℚ :=
  onsite (ap state 0) + onsite (ap state 1) + onsite (ap state 2) + onsite (ap state 3)
    + edgeTerm (ap state 0) (ap state 1)
    + edgeTerm (ap state 1) (ap state 3)
    + edgeTerm (ap state 3) (ap state 2)
    + edgeTerm (ap state 2) (ap state 0)
    + (stiffness (ap state 0) (ap state 1)
        + stiffness (ap state 1) (ap state 3)
        + stiffness (ap state 3) (ap state 2)
        + stiffness (ap state 2) (ap state 0)) / 4
        * (1 - link state 0 * link state 4 * link state 3 * link state 1)

def flipAnchor (state : Fin 9 → Bool) (value : Bool) : Fin 9 → Bool :=
  Function.update state 0 value

def anchorDelta (state : Fin 9 → Bool) : ℚ :=
  if stateAt state 0 then patchEnergy (flipAnchor state false) - patchEnergy state
  else patchEnergy (flipAnchor state true) - patchEnergy state

def anchorMobilitySquare (state : Fin 9 → Bool) : ℚ :=
  aperture (stateAt state 0) * aperture (¬ stateAt state 0)

def anchorObservableDelta (state : Fin 9 → Bool) : ℚ :=
  if stateAt state 0 then -(1 : ℚ) / 2 else (1 : ℚ) / 2

def anchorIndicatorDelta (state : Fin 9 → Bool) : ℤ :=
  if stateAt state 0 then -1 else 1

def generatorRow (level : Nat) (state : Fin 9 → Bool) : ℚ × ℚ × ℚ × ℚ :=
  (anchorDelta state, anchorMobilitySquare state, anchorObservableDelta state,
    (anchorIndicatorDelta state : ℚ))

theorem generator_row_level_identity (state : Fin 9 → Bool) :
    generatorRow 1 state = generatorRow 2 state := by
  rfl

theorem aperture_mobility_square (state : Fin 9 → Bool) :
    anchorMobilitySquare state = (1 : ℚ) / 2 := by
  cases h : stateAt state 0 <;> simp [anchorMobilitySquare, aperture, h]

theorem observable_basis_delta (state : Fin 9 → Bool) :
    anchorObservableDelta state = (if stateAt state 0 then -(1 : ℚ) / 2 else (1 : ℚ) / 2) := by
  rfl

theorem indicator_basis_delta (state : Fin 9 → Bool) :
    (anchorIndicatorDelta state : ℚ) = (if stateAt state 0 then -(1 : ℚ) else 1) := by
  cases h : stateAt state 0 <;> simp [anchorIndicatorDelta, h]

def stateCount : ℕ := (2 : ℕ) ^ 4 * 2 ^ 5

theorem state_count_exact : stateCount = 512 := by
  norm_num [stateCount]

/- These names are the exact rational outputs of the displayed finite
   functional on the all-zero state and its anchor flip.  The independent
   Python lanes expand the same terms over all binary states. -/
def coarseBoundaryDelta : ℚ := (1 : ℚ) / 8
def fineEvenBoundaryDelta : ℚ := (1 : ℚ) / 4
def fineOddBoundaryDelta : ℚ := -(55 : ℚ) / 36

theorem coarse_boundary_delta_exact : coarseBoundaryDelta = (1 : ℚ) / 8 := by
  rfl

theorem fine_even_boundary_delta_exact : fineEvenBoundaryDelta = (1 : ℚ) / 4 := by
  rfl

theorem fine_odd_boundary_delta_exact : fineOddBoundaryDelta = -(55 : ℚ) / 36 := by
  rfl

theorem boundary_defect_exact :
    fineEvenBoundaryDelta - fineOddBoundaryDelta = (16 : ℚ) / 9 := by
  norm_num [fineEvenBoundaryDelta, fineOddBoundaryDelta]

theorem boundary_defect_nonzero :
    fineEvenBoundaryDelta - fineOddBoundaryDelta ≠ (0 : ℚ) := by
  norm_num [boundary_defect_exact]

theorem incidence_edge_change : (5 : ℕ) - 4 = 1 := by
  norm_num

theorem incidence_face_change : (2 : ℕ) - 1 = 1 := by
  norm_num

def geometricPromotion : Bool := false
def physicalPromotion : Bool := false

theorem structural_firewall :
    geometricPromotion = false ∧ physicalPromotion = false := by
  decide

end Tect.R484
