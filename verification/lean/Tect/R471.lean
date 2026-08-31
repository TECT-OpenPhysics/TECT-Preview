import Mathlib

namespace Tect.R471

structure Packet where
  sourceHash : Bool
  ownerSlots : Bool
  fReg : Bool
  fLim : Bool
  fEff : Bool
  fObs : Bool
  holdout : Bool
  scorer : Bool
  synthetic : Bool
  methodsUnchanged : Bool

def productionAdmissible (p : Packet) : Prop :=
  p.sourceHash = true ∧ p.ownerSlots = true ∧
  p.fReg = true ∧ p.fLim = true ∧ p.fEff = true ∧ p.fObs = true ∧
  p.holdout = true ∧ p.scorer = true ∧ p.synthetic = false ∧
  p.methodsUnchanged = true

def current : Packet :=
  { sourceHash := false, ownerSlots := false, fReg := false, fLim := false,
    fEff := false, fObs := false, holdout := false, scorer := false,
    synthetic := false, methodsUnchanged := true }

def completeSynthetic : Packet :=
  { sourceHash := true, ownerSlots := true, fReg := true, fLim := true,
    fEff := true, fObs := true, holdout := true, scorer := true,
    synthetic := true, methodsUnchanged := true }

theorem current_not_admitted : ¬ productionAdmissible current := by
  simp [productionAdmissible, current]

theorem synthetic_never_admitted (p : Packet) (h : p.synthetic = true) :
    ¬ productionAdmissible p := by
  intro hadmit
  rcases hadmit with ⟨_, _, _, _, _, _, _, _, hsynthetic, _⟩
  exact Bool.noConfusion (hsynthetic.symm.trans h)

theorem missing_freg_blocks (p : Packet) (h : p.fReg = false) :
    ¬ productionAdmissible p := by
  intro hadmit
  exact Bool.noConfusion (hadmit.2.2.1.symm.trans h)

theorem missing_flim_blocks (p : Packet) (h : p.fLim = false) :
    ¬ productionAdmissible p := by
  intro hadmit
  exact Bool.noConfusion (hadmit.2.2.2.1.symm.trans h)

theorem missing_holdout_blocks (p : Packet) (h : p.holdout = false) :
    ¬ productionAdmissible p := by
  intro hadmit
  exact Bool.noConfusion (hadmit.2.2.2.2.2.2.1.symm.trans h)

theorem methods_required (p : Packet) (h : p.methodsUnchanged = false) :
    ¬ productionAdmissible p := by
  intro hadmit
  rcases hadmit with ⟨_, _, _, _, _, _, _, _, _, hmethods⟩
  exact Bool.noConfusion (hmethods.symm.trans h)

theorem synthetic_fixture_is_not_production :
    ¬ productionAdmissible completeSynthetic := by
  exact synthetic_never_admitted completeSynthetic rfl

theorem parked_owner_and_inverse :
    ¬ productionAdmissible current ∧ ¬ productionAdmissible completeSynthetic := by
  exact ⟨current_not_admitted, synthetic_fixture_is_not_production⟩

end Tect.R471
