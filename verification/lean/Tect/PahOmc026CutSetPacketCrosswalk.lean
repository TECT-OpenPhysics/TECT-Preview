import Mathlib

namespace Tect.PahOmc026

structure Packet where
  authority : Prop
  rootSemantics : Prop
  commonRealization : Prop
  n1Recovery : Prop
  n2bForm : Prop
  n2cN4Boundary : Prop
  n2dTarget : Prop
  fullDomainJ : Prop
  anchoredD : Prop
  verification : Prop

def sourceCut (p : Packet) : Prop :=
  p.authority ∧ p.rootSemantics

def comparisonCut (p : Packet) : Prop :=
  p.commonRealization ∧ p.n1Recovery ∧ p.n2bForm ∧ p.n2cN4Boundary ∧ p.n2dTarget

def temporalCut (p : Packet) : Prop :=
  p.fullDomainJ ∧ p.anchoredD

def completePacket (p : Packet) : Prop :=
  sourceCut p ∧ comparisonCut p ∧ temporalCut p ∧ p.verification

def cutSetAdmissible (p : Packet) : Prop :=
  sourceCut p ∧ comparisonCut p ∧ temporalCut p

theorem complete_packet_implies_cuts (p : Packet)
    (h : completePacket p) : cutSetAdmissible p := by
  exact ⟨h.1, h.2.1, h.2.2.1⟩

theorem complete_packet_has_verification (p : Packet)
    (h : completePacket p) : p.verification := by
  exact h.2.2.2

theorem cutset_without_packet_is_possible :
    ∃ p : Packet, cutSetAdmissible p ∧ ¬ completePacket p := by
  let p : Packet := {
    authority := True,
    rootSemantics := True,
    commonRealization := True,
    n1Recovery := True,
    n2bForm := True,
    n2cN4Boundary := True,
    n2dTarget := True,
    fullDomainJ := True,
    anchoredD := True,
    verification := False
  }
  refine ⟨p, ?_, ?_⟩
  · exact ⟨⟨by trivial, by trivial⟩, ⟨by trivial, by trivial, by trivial, by trivial, by trivial⟩, ⟨by trivial, by trivial⟩⟩
  · intro h
    exact h.2.2.2

theorem missing_source_rejects (p : Packet) (h : ¬ sourceCut p) :
    ¬ completePacket p := by
  intro hp
  exact h (complete_packet_implies_cuts p hp).1

theorem missing_verification_rejects (p : Packet) (h : ¬ p.verification) :
    ¬ completePacket p := by
  intro hp
  exact h (complete_packet_has_verification p hp)

def FixedJZero (jBound : Nat → Nat → Rat) : Prop :=
  ∀ n ε, 0 < ε → ∃ J₀, ∀ j, J₀ ≤ j → jBound n j < ε / 2

def AnchoredDZero (dBound : Nat → Rat) : Prop :=
  ∀ ε, 0 < ε → ∃ N, ∀ n, N ≤ n → dBound n < ε / 2

def OrderedErrorZero (err : Nat → Nat → Rat) : Prop :=
  ∀ ε, 0 < ε → ∃ N, ∀ n, N ≤ n → ∃ J₀, ∀ j, J₀ ≤ j → err n j < ε

theorem ordered_error_from_packet
    (p : Packet) (err jBound : Nat → Nat → Rat) (dBound : Nat → Rat)
    (_hp : completePacket p)
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
  have hd := hN n hn
  have hjb := hJ₀ j hj
  have he := (hbound n j).2
  linarith

end Tect.PahOmc026
