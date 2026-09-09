import Mathlib

/-!
Ordered-quantifier bridge for PAH-OMC-020.

This file formalizes only the epsilon implication behind the registered
two-term bound.  It does not supply the PAH owner packet, the common-space
comparison, the `J` limit, the `D` limit, or any physical interpretation.
-/

namespace Tect.PahOmc020OrderedEpsilon

def FixedJZero (jBound : Nat → Nat → Rat) : Prop :=
  ∀ n ε, 0 < ε → ∃ J₀, ∀ j, J₀ ≤ j → jBound n j < ε / 2

def AnchoredDZero (dBound : Nat → Rat) : Prop :=
  ∀ ε, 0 < ε → ∃ N, ∀ n, N ≤ n → dBound n < ε / 2

def OrderedErrorZero (err : Nat → Nat → Rat) : Prop :=
  ∀ ε, 0 < ε → ∃ N, ∀ n, N ≤ n → ∃ J₀, ∀ j, J₀ ≤ j → err n j < ε

theorem ordered_epsilon_bridge
    (err jBound : Nat → Nat → Rat) (dBound : Nat → Rat)
    (hJ : FixedJZero jBound)
    (hD : AnchoredDZero dBound)
    (hbound : ∀ n j, 0 ≤ err n j ∧ err n j ≤ jBound n j + dBound n) :
    OrderedErrorZero err := by
  intro ε hε
  obtain ⟨N, hN⟩ := hD ε hε
  refine ⟨N, ?_⟩
  intro n hn
  obtain ⟨J₀, hJ₀⟩ := hJ n ε hε
  refine ⟨J₀, ?_⟩
  intro j hj
  have h_d := hN n hn
  have h_j := hJ₀ j hj
  have h_e := (hbound n j).2
  linarith

theorem ordered_epsilon_bridge_requires_both_terms
    (err jBound : Nat → Nat → Rat) (dBound : Nat → Rat)
    (hJ : FixedJZero jBound)
    (hD : AnchoredDZero dBound)
    (hbound : ∀ n j, 0 ≤ err n j ∧ err n j ≤ jBound n j + dBound n) :
    OrderedErrorZero err :=
  ordered_epsilon_bridge err jBound dBound hJ hD hbound

theorem split_fixture
    (ε : Rat) (hε : 0 < ε)
    (hJ : (3 : Rat) / 100 < ε / 2)
    (hD : (1 : Rat) / 20 < ε / 2) :
    (3 : Rat) / 100 + 1 / 20 < ε := by
  have hJ' := hJ
  linarith [hJ', hD]

end Tect.PahOmc020OrderedEpsilon
