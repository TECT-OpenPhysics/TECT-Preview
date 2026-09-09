import Mathlib

namespace Tect.PahOmc020DiagonalLocality

def threshold (s k radius : Nat) : Nat := max 2 (s + radius * k + 1)

theorem diagonal_exceeds (s n : Nat) :
    n < threshold s (n + 1) 2 := by
  unfold threshold
  omega

theorem no_uniform_fixed_n (s n : Nat) :
    ¬ (∀ k : Nat, threshold s k 2 ≤ n) := by
  intro h
  have diagonal := diagonal_exceeds s n
  have bounded := h (n + 1)
  omega

theorem threshold_unbounded (s m : Nat) :
    ∃ k : Nat, m < threshold s k 2 := by
  exact ⟨m + 1, diagonal_exceeds s m⟩

theorem no_uniform_eventual (s : Nat) :
    ¬ (∃ n0 : Nat, ∀ k : Nat, threshold s k 2 ≤ n0) := by
  rintro ⟨n0, h⟩
  exact no_uniform_fixed_n s n0 h

def claimBearing : Bool := false
def activeGateChange : Bool := false
def physicalPromotion : Bool := false

theorem nonpromotion_firewall :
    claimBearing = false ∧ activeGateChange = false ∧ physicalPromotion = false := by
  decide

end Tect.PahOmc020DiagonalLocality
