import Mathlib

namespace Tect.R443

def inBox {d : Nat} (side v : Fin d → Nat) : Prop :=
  ∀ j : Fin d, v j < side j

def incident {d : Nat} (axis : Fin d) (v lower : Fin d → Nat) : Prop :=
  (∀ j : Fin d, j ≠ axis → lower j = v j) ∧
    (lower axis = v axis ∨ lower axis + 1 = v axis)

def boundedIncident {d : Nat} (side : Fin d → Nat) (axis : Fin d)
    (v lower : Fin d → Nat) : Prop :=
  inBox side v ∧ inBox side lower ∧ incident axis v lower

theorem same_colour_incident_unique {d : Nat} (axis : Fin d)
    (v lower₁ lower₂ : Fin d → Nat)
    (h₁ : incident axis v lower₁)
    (h₂ : incident axis v lower₂)
    (hcolour : lower₁ axis % 2 = lower₂ axis % 2) :
    lower₁ = lower₂ := by
  have haxis : lower₁ axis = lower₂ axis := by
    rcases h₁.2 with h₁f | h₁b <;> rcases h₂.2 with h₂f | h₂b <;> omega
  funext j
  by_cases h : j = axis
  · subst j
    exact haxis
  · exact (h₁.1 j h).trans (h₂.1 j h).symm

theorem arbitrary_box_layer_matching {d : Nat} (side : Fin d → Nat)
    (axis : Fin d) (v lower₁ lower₂ : Fin d → Nat)
    (h₁ : boundedIncident side axis v lower₁)
    (h₂ : boundedIncident side axis v lower₂)
    (hcolour : lower₁ axis % 2 = lower₂ axis % 2) :
    lower₁ = lower₂ := by
  exact same_colour_incident_unique axis v lower₁ lower₂ h₁.2.2 h₂.2.2 hcolour

theorem six_colour_layers (hthree : (3 : Nat) = 3) : 3 * 2 = 6 := by
  omega

end Tect.R443
