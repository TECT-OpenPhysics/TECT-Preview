import Mathlib

/-!
Conditional owner-packet sufficiency bridge for PAH-OMC-020.

The packet is an antecedent, not an existing source fact.  These declarations
formalize the exact logical implication from a complete ten-field packet plus
the registered J/D estimates to the nested j-before-n epsilon conclusion.
They do not construct the packet, a common Hilbert space, a path law, or any
physical interpretation.
-/

namespace Tect.PahOmc020OwnerPacketSufficiency

def FixedJZero (jBound : Nat → Nat → Rat) : Prop :=
  ∀ n ε, 0 < ε → ∃ J₀, ∀ j, J₀ ≤ j → jBound n j < ε / 2

def AnchoredDZero (dBound : Nat → Rat) : Prop :=
  ∀ ε, 0 < ε → ∃ N, ∀ n, N ≤ n → dBound n < ε / 2

def OrderedErrorZero (err : Nat → Nat → Rat) : Prop :=
  ∀ ε, 0 < ε → ∃ N, ∀ n, N ≤ n → ∃ J₀, ∀ j, J₀ ≤ j → err n j < ε

def CompletePacket
    (authority rootSemantics commonRealization n1Recovery n2bForm
      n2cN4Boundary n2dTarget fullDomainJ anchoredD verification : Prop) : Prop :=
  authority ∧ rootSemantics ∧ commonRealization ∧ n1Recovery ∧ n2bForm ∧
    n2cN4Boundary ∧ n2dTarget ∧ fullDomainJ ∧ anchoredD ∧ verification

theorem ordered_error_from_complete_packet
    (err jBound : Nat → Nat → Rat) (dBound : Nat → Rat)
    (authority rootSemantics commonRealization n1Recovery n2bForm
      n2cN4Boundary n2dTarget fullDomainJ anchoredD verification : Prop)
    (hpacket : CompletePacket authority rootSemantics commonRealization n1Recovery
      n2bForm n2cN4Boundary n2dTarget fullDomainJ anchoredD verification)
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

theorem missing_root_field_rejects
    (rootSemantics commonRealization n1Recovery n2bForm
      n2cN4Boundary n2dTarget fullDomainJ anchoredD verification : Prop) :
    ¬ CompletePacket False rootSemantics commonRealization n1Recovery n2bForm
      n2cN4Boundary n2dTarget fullDomainJ anchoredD verification := by
  intro h
  exact h.1

theorem radial_partial_packet_rejects
    (fullDomainJ anchoredD : Prop) :
    ¬ CompletePacket False False False False False False False fullDomainJ anchoredD False := by
  intro h
  exact h.1

theorem complete_packet_has_full_domain_terms
    (authority rootSemantics commonRealization n1Recovery n2bForm
      n2cN4Boundary n2dTarget fullDomainJ anchoredD verification : Prop)
    (hpacket : CompletePacket authority rootSemantics commonRealization n1Recovery
      n2bForm n2cN4Boundary n2dTarget fullDomainJ anchoredD verification) :
    fullDomainJ ∧ anchoredD := by
  exact ⟨hpacket.2.2.2.2.2.2.2.1, hpacket.2.2.2.2.2.2.2.2.1⟩

end Tect.PahOmc020OwnerPacketSufficiency
