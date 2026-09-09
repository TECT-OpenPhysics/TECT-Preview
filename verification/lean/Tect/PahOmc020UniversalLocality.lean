import Mathlib

namespace Tect.PahOmc020UniversalLocality

def iterate {X : Type*} (T : X → X) : Nat → X → X
  | 0 => id
  | k + 1 => fun x => T (iterate T k x)

theorem iterate_intertwines
    {V W : Type*} (A : V → V) (B : W → W)
    (I : W → V) (h : ∀ x, A (I x) = I (B x)) :
    ∀ k x, iterate A k (I x) = I (iterate B k x) := by
  intro k
  induction k with
  | zero => intro x; rfl
  | succ k ih =>
      intro x
      calc
        iterate A (k + 1) (I x) = A (iterate A k (I x)) := by rfl
        _ = A (I (iterate B k x)) := by rw [ih x]
        _ = I (B (iterate B k x)) := h (iterate B k x)
        _ = I (iterate B (k + 1) x) := by rfl

def envelopeMax (s k radius : Nat) : Nat := s + radius * k

def threshold (s k radius : Nat) : Nat := max 2 (envelopeMax s k radius + 1)

theorem envelope_strict_before_frontier (s k radius : Nat) :
    envelopeMax s k radius < threshold s k radius := by
  unfold threshold envelopeMax
  omega

theorem radius_two_threshold (s k : Nat) :
    threshold s k 2 = max 2 (s + 2 * k + 1) := by
  simp [threshold, envelopeMax]

theorem threshold_monotone (s k radius : Nat) :
    threshold s k radius ≤ threshold s (k + 1) radius := by
  have hmul : radius * k ≤ radius * (k + 1) := Nat.mul_le_mul_left radius (Nat.le_succ k)
  have hadd : s + radius * k + 1 ≤ s + radius * (k + 1) + 1 := by
    omega
  exact max_le_max_left 2 hadd

theorem ell_origin_threshold (k : Nat) :
    threshold 0 k 2 = max 2 (2 * k + 1) := by
  simp [threshold, envelopeMax]

def claimBearing : Bool := false
def activeGateChange : Bool := false
def physicalPromotion : Bool := false

theorem nonpromotion_firewall :
    claimBearing = false ∧ activeGateChange = false ∧ physicalPromotion = false := by
  decide

end Tect.PahOmc020UniversalLocality
