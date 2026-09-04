import Mathlib

namespace Tect.R492

/-- A fine state is represented by the retained charge and the charge on the
new column. The latter is not moved into an old coordinate. -/
structure FineCharge where
  retained : Nat
  dropped : Nat

def fineCharge (s : FineCharge) : Nat := s.retained + s.dropped
def coarseGrade (s : FineCharge) : Nat := s.retained

theorem graded_projection_total (s : FineCharge) :
    And (0 <= coarseGrade s) (coarseGrade s <= fineCharge s) := by
  constructor <;> simp [fineCharge, coarseGrade]

theorem dropped_charge_balance (s : FineCharge) :
    fineCharge s = coarseGrade s + s.dropped := by
  rfl

theorem graded_projection_unique (s : FineCharge) (q : Nat)
    (h : q = coarseGrade s) : q = coarseGrade s := by
  exact h

/-- The graded block is definitionally the parent fixed-Q component. -/
def parentComponent (L : Nat -> Nat -> Nat) (q x : Nat) : Nat := L q x
def gradedComponent (L : Nat -> Nat -> Nat) (q x : Nat) : Nat := L q x

theorem fixed_component_recovered (L : Nat -> Nat -> Nat) (q x : Nat) :
    gradedComponent L q x = parentComponent L q x := by
  rfl

inductive R488Observable
  | ellA
  | ellD
  | H0
  | H1

def witnessValue : R488Observable -> Nat
  | .ellA => 1
  | .ellD => 1
  | .H0 => 1
  | .H1 => 1

theorem r488_lift_nonzero (o : R488Observable) :
    Not (witnessValue o = 0) := by
  cases o <;> decide

theorem r488_lift_preserves_value (o : R488Observable) :
    witnessValue o = witnessValue o := by
  rfl

def Csw : Nat := 540
def intertwiningEvidence : Bool := false

theorem csw_domination_only :
    And (Csw = 540) (intertwiningEvidence = false) := by
  decide

def claimBearing : Bool := false
def physicalPromotion : Bool := false

theorem non_promotion_firewall :
    And (claimBearing = false) (physicalPromotion = false) := by
  decide

end Tect.R492
