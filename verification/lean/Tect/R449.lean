import Mathlib

namespace Tect.R449

structure OwnerSlots where
  generator : Bool
  state : Bool
  projection : Bool
  timeBoundary : Bool
  heatRoot : Bool
  filtration : Bool
  replicas : Bool
  rawCurrent : Bool
  qLedger : Bool

def complete (s : OwnerSlots) : Prop :=
  s.generator = true ∧ s.state = true ∧ s.projection = true ∧
  s.timeBoundary = true ∧ s.heatRoot = true ∧ s.filtration = true ∧
  s.replicas = true ∧ s.rawCurrent = true ∧ s.qLedger = true

def a2Slots : OwnerSlots :=
  { generator := false, state := false, projection := false, timeBoundary := false,
    heatRoot := false, filtration := false, replicas := false, rawCurrent := false,
    qLedger := false }

theorem complete_requires_heat_root (s : OwnerSlots) (h : complete s) :
    s.heatRoot = true := by
  exact h.2.2.2.2.1

theorem a2_owner_incomplete : ¬ complete a2Slots := by
  simp [complete, a2Slots]

theorem a2_heat_root_missing : a2Slots.heatRoot = false := by
  rfl

structure InverseStages where
  fReg : Bool
  fLim : Bool
  fEff : Bool
  fObs : Bool
  prospective : Bool

def inverseComplete (s : InverseStages) : Prop :=
  s.fReg = true ∧ s.fLim = true ∧ s.fEff = true ∧
  s.fObs = true ∧ s.prospective = true

def currentInverse : InverseStages :=
  { fReg := false, fLim := false, fEff := false, fObs := false, prospective := false }

theorem inverse_not_complete : ¬ inverseComplete currentInverse := by
  simp [inverseComplete, currentInverse]

theorem parked_owner_and_inverse :
    ¬ complete a2Slots ∧ ¬ inverseComplete currentInverse := by
  exact ⟨a2_owner_incomplete, inverse_not_complete⟩

end Tect.R449
