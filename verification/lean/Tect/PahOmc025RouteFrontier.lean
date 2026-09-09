import Mathlib

namespace Tect.PahOmc025

structure CutSet where
  sourceSemantics : Prop
  comparisonRoute : Prop
  temporalControl : Prop

def admissible (c : CutSet) : Prop :=
  c.sourceSemantics ∧ c.comparisonRoute ∧ c.temporalControl

def formRoute (commonMap liminf recovery target transfer : Prop) : Prop :=
  commonMap ∧ liminf ∧ recovery ∧ target ∧ transfer

def pathRoute (commonSpace tightness generatorEq uniqueness transfer : Prop) : Prop :=
  commonSpace ∧ tightness ∧ generatorEq ∧ uniqueness ∧ transfer

theorem admissible_iff (c : CutSet) :
    admissible c ↔ c.sourceSemantics ∧ c.comparisonRoute ∧ c.temporalControl := by
  rfl

theorem missing_source_blocks (c : CutSet) (h : ¬ c.sourceSemantics) :
    ¬ admissible c := by
  intro hc
  exact h hc.1

theorem missing_comparison_blocks (c : CutSet) (h : ¬ c.comparisonRoute) :
    ¬ admissible c := by
  intro hc
  exact h hc.2.1

theorem missing_temporal_blocks (c : CutSet) (h : ¬ c.temporalControl) :
    ¬ admissible c := by
  intro hc
  exact h hc.2.2

theorem form_route_needs_all
    (commonMap liminf recovery target transfer : Prop) :
    formRoute commonMap liminf recovery target transfer →
      commonMap ∧ liminf ∧ recovery ∧ target ∧ transfer := by
  intro h
  exact h

theorem path_route_needs_all
    (commonSpace tightness generatorEq uniqueness transfer : Prop) :
    pathRoute commonSpace tightness generatorEq uniqueness transfer →
      commonSpace ∧ tightness ∧ generatorEq ∧ uniqueness ∧ transfer := by
  intro h
  exact h

theorem either_route_is_not_shortcut
    (source temporal formReady pathReady : Prop)
    (hsource : ¬ source) :
    ¬ (source ∧ (formReady ∨ pathReady) ∧ temporal) := by
  intro h
  exact hsource h.1

theorem complete_cuts_admit
    (source comparison temporal : Prop)
    (hs : source) (hc : comparison) (ht : temporal) :
    admissible ⟨source, comparison, temporal⟩ := by
  exact ⟨hs, hc, ht⟩

end Tect.PahOmc025
