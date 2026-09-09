import Mathlib

namespace Tect.PahOmc020FiniteSemigroup

open scoped BigOperators

def iterate {X : Type*} (T : X → X) : Nat → X → X
  | 0 => id
  | k + 1 => fun x => T (iterate T k x)

def expPartial {X : Type*} [AddCommGroup X] [Module ℚ X]
    (T : X → X) (t : ℚ) (N : Nat) (x : X) : X :=
  Finset.sum (Finset.range (N + 1)) (fun k =>
    ((t ^ k) / (Nat.factorial k : ℚ)) • iterate T k x)

theorem iterate_intertwines
    {V W : Type*} (A : V → V) (B : W → W)
    (I : W → V) (h : ∀ x, A (I x) = I (B x)) :
    ∀ k x, iterate A k (I x) = I (iterate B k x) := by
  intro k
  induction k with
  | zero =>
      intro x
      rfl
  | succ k ih =>
      intro x
      calc
        iterate A (k + 1) (I x) = A (iterate A k (I x)) := by rfl
        _ = A (I (iterate B k x)) := by rw [ih x]
        _ = I (B (iterate B k x)) := h (iterate B k x)
        _ = I (iterate B (k + 1) x) := by rfl

theorem exp_partial_intertwines
    {V W : Type*} [AddCommGroup V] [AddCommGroup W]
    [Module ℚ V] [Module ℚ W]
    (A : V → V) (B : W → W) (I : W →ₗ[ℚ] V)
    (h : ∀ x, A (I x) = I (B x)) (t : ℚ) (N : Nat) (x : W) :
    expPartial A t N (I x) = I (expPartial B t N x) := by
  unfold expPartial
  rw [map_sum]
  apply Finset.sum_congr rfl
  intro k hk
  rw [map_smul]
  rw [iterate_intertwines A B I h k x]

theorem restricted_iterate_intertwines
    {V W : Type*} (A : V → V) (B : W → W)
    (I : W → V) (C : Set W)
    (h : ∀ x, x ∈ C → A (I x) = I (B x))
    (hC : ∀ x, x ∈ C → B x ∈ C) :
    ∀ k x, x ∈ C → iterate A k (I x) = I (iterate B k x) := by
  have hmem : ∀ k x, x ∈ C → iterate B k x ∈ C := by
    intro k
    induction k with
    | zero =>
        intro x hx
        exact hx
    | succ k ih =>
        intro x hx
        exact hC (iterate B k x) (ih x hx)
  intro k
  induction k with
  | zero =>
      intro x hx
      rfl
  | succ k ih =>
      intro x hx
      calc
        iterate A (k + 1) (I x) = A (iterate A k (I x)) := by rfl
        _ = A (I (iterate B k x)) := by rw [ih x hx]
        _ = I (B (iterate B k x)) := h (iterate B k x) (hmem k x hx)
        _ = I (iterate B (k + 1) x) := by rfl

theorem coefficient_identity_requires_iterate_scope
    {V W : Type*} (A : V → V) (B : W → W)
    (I : W → V) (C : Set W)
    (h : ∀ x, x ∈ C → A (I x) = I (B x))
    (hC : ∀ x, x ∈ C → B x ∈ C) :
    ∀ k x, x ∈ C → iterate A k (I x) = I (iterate B k x) :=
  restricted_iterate_intertwines A B I C h hC

def claimBearing : Bool := false
def activeGateChange : Bool := false

theorem finite_bridge_nonpromotion :
    claimBearing = false ∧ activeGateChange = false := by
  decide

end Tect.PahOmc020FiniteSemigroup
