import Mathlib

namespace Tect.R476

structure OwnerSlots where
  generatorOrTransfer : Bool
  state : Bool
  physicalProjection : Bool
  timeBoundary : Bool
  heatRootIncidence : Bool
  rootFiltration : Bool
  conditionalReplicas : Bool
  rawCurrentSpatialIntertwiner : Bool
  productionOneUseQLedger : Bool

def ownerComplete (s : OwnerSlots) : Prop :=
  s.generatorOrTransfer = true ∧
  s.state = true ∧
  s.physicalProjection = true ∧
  s.timeBoundary = true ∧
  s.heatRootIncidence = true ∧
  s.rootFiltration = true ∧
  s.conditionalReplicas = true ∧
  s.rawCurrentSpatialIntertwiner = true ∧
  s.productionOneUseQLedger = true

structure Packet where
  sourceHashPinned : Bool
  researcherHypothesis : Bool
  syntheticFixture : Bool
  physicalAuthority : Bool
  ownerSlots : OwnerSlots
  finiteModelConsistent : Bool
  uniformEstimate : Bool
  orderedLimits : Bool
  horizonLabel : Bool
  preAIdentified : Bool
  physicalEmptyBranch : Bool
  methodsUnchanged : Bool

def structurallyRegistered (p : Packet) : Prop :=
  p.sourceHashPinned = true ∧
  p.researcherHypothesis = true ∧
  p.syntheticFixture = false ∧
  ownerComplete p.ownerSlots ∧
  p.methodsUnchanged = true

def limitReady (p : Packet) : Prop :=
  p.uniformEstimate = true ∧ p.orderedLimits = true

def productionAdmissible (p : Packet) : Prop :=
  structurallyRegistered p ∧
  p.physicalAuthority = true ∧
  p.finiteModelConsistent = true ∧
  limitReady p

def physicalEmptyTestReady (p : Packet) : Prop :=
  productionAdmissible p ∧ p.physicalEmptyBranch = true

def completeOwnerSlots : OwnerSlots :=
  { generatorOrTransfer := true
    state := true
    physicalProjection := true
    timeBoundary := true
    heatRootIncidence := true
    rootFiltration := true
    conditionalReplicas := true
    rawCurrentSpatialIntertwiner := true
    productionOneUseQLedger := true }

def candidate : Packet :=
  { sourceHashPinned := true
    researcherHypothesis := true
    syntheticFixture := false
    physicalAuthority := false
    ownerSlots := completeOwnerSlots
    finiteModelConsistent := false
    uniformEstimate := false
    orderedLimits := true
    horizonLabel := true
    preAIdentified := false
    physicalEmptyBranch := false
    methodsUnchanged := true }

def contractFixture : Packet :=
  { sourceHashPinned := true
    researcherHypothesis := true
    syntheticFixture := true
    physicalAuthority := false
    ownerSlots := completeOwnerSlots
    finiteModelConsistent := false
    uniformEstimate := false
    orderedLimits := true
    horizonLabel := true
    preAIdentified := false
    physicalEmptyBranch := false
    methodsUnchanged := true }

theorem candidate_is_structurally_registered :
    structurallyRegistered candidate := by
  simp [structurallyRegistered, candidate, completeOwnerSlots, ownerComplete]

theorem candidate_is_not_production_admitted :
    ¬ productionAdmissible candidate := by
  simp [productionAdmissible, candidate]

theorem missing_owner_slot_blocks_registration
    (p : Packet) (hmissing : ¬ ownerComplete p.ownerSlots) :
    ¬ structurallyRegistered p := by
  intro hregistered
  rcases hregistered with ⟨_, _, _, howners, _⟩
  exact hmissing howners

theorem fixture_blocks_registration :
    ¬ structurallyRegistered contractFixture := by
  simp [structurallyRegistered, contractFixture]

theorem physical_authority_required_for_production
    (p : Packet) (hmissing : p.physicalAuthority = false) :
    ¬ productionAdmissible p := by
  intro hproduction
  rcases hproduction with ⟨_, hauthority, _⟩
  exact Bool.noConfusion (hauthority.symm.trans hmissing)

theorem uniform_estimate_required_for_limit
    (p : Packet) (hmissing : p.uniformEstimate = false) :
    ¬ limitReady p := by
  intro hlimit
  exact Bool.noConfusion (hlimit.1.symm.trans hmissing)

theorem horizon_name_does_not_identify_preA :
    candidate.horizonLabel = true ∧
    candidate.preAIdentified = false ∧
    ¬ (candidate.horizonLabel = true → candidate.preAIdentified = true) := by
  simp [candidate]

theorem physical_empty_requires_separate_branch
    (p : Packet) (hmissing : p.physicalEmptyBranch = false) :
    ¬ physicalEmptyTestReady p := by
  intro hready
  exact Bool.noConfusion (hready.2.symm.trans hmissing)

theorem candidate_methods_remain_unchanged :
    candidate.methodsUnchanged = true ∧
    ∀ p : Packet,
      p.methodsUnchanged = false → ¬ structurallyRegistered p := by
  constructor
  · rfl
  · intro p hchanged hregistered
    rcases hregistered with ⟨_, _, _, _, hmethods⟩
    exact Bool.noConfusion (hmethods.symm.trans hchanged)

end Tect.R476
