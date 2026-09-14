import Mathlib

namespace Tect.PahV2Comparison

/- Parameterized comparison algebra only. The concrete geometry, state
encoding, source admissibility and all-index dictionary are checked in the
separate admission proof. No generator or limit statement is encoded. -/

theorem nested_floor (s d e : Nat) : s / d / e = s / (d * e) :=
  Nat.div_div_eq_div_mul s d e

theorem scaled_right_inverse (q d : Nat) (hd : 0 < d) : d * q / d = q :=
  Nat.mul_div_cancel_left q hd

theorem prefix_monotone (a b d : Nat) (hab : a ≤ b) : a / d ≤ b / d :=
  Nat.div_le_div_right hab

theorem adjacent_prefix_blocks (a b c : Nat) (hab : a ≤ b) (hbc : b ≤ c) :
    (b-a)+(c-b)=c-a := by omega

theorem four_child_telescope (a b c d e : Int) :
    (b-a)+(c-b)+(d-c)+(e-d)=e-a := by omega

theorem terminal_complement (q a b : Nat) (hab : a ≤ b) (hbq : b ≤ q) :
    (b-a)+(q-b)=q-a := by omega

theorem terminal_total (q a : Nat) (haq : a ≤ q) : a+(q-a)=q := by omega

theorem terminal_cutoff_square (q s : Nat) :
    (2*q)/2-s/2 = q-s/2 := by omega

theorem additive_phase_path (K : Nat) (a u v : ZMod K) :
    a*(u+v)=a*u+a*v := by ring

theorem signed_phase (K : Nat) (a u : ZMod K) : a*(-u)=-(a*u) := by ring

theorem gauge_path_telescope (K n : Nat) (g : Nat → ZMod K) :
    (∑ i ∈ Finset.range n, (g (i+1)-g i))=g n-g 0 := by
  induction n with
  | zero => simp
  | succ n ih =>
      rw [Finset.sum_range_succ, ih]
      ring

theorem corner_distance_injective (x y x' y' w : Int)
    (h0 : x+y=x'+y') (h1 : w-x+y=w-x'+y') : x=x' ∧ y=y' := by omega

theorem pullback_composition {X Y Z A : Type*} (p : Y → X) (q : Z → Y)
    (f : X → A) : (f ∘ p) ∘ q = f ∘ (p ∘ q) := rfl

theorem pullback_multiplication {X Y : Type*} (p : Y → X) (f g : X → Complex) :
    (fun x => f x*g x) ∘ p = (fun y => f (p y)*g (p y)) := rfl

theorem pullback_conjugation {X Y : Type*} (p : Y → X) (f : X → Complex) :
    (fun x => star (f x)) ∘ p = (fun y => star (f (p y))) := rfl

theorem pullback_injective {X Y A : Type*} (p : Y → X) (J : X → Y)
    (hpJ : ∀ x, p (J x)=x) : Function.Injective (fun f : X → A => f ∘ p) := by
  intro f g h
  funext x
  have hx := congrFun h (J x)
  simpa only [Function.comp_apply, hpJ] using hx

theorem full_sup_bound_equivalence {X Y : Type*} (p : Y → X) (J : X → Y)
    (hpJ : ∀ x, p (J x)=x) (f : X → Complex) (c : Real) :
    (∀ y, ‖f (p y)‖ ≤ c) ↔ (∀ x, ‖f x‖ ≤ c) := by
  constructor
  · intro h x
    simpa only [hpJ] using h (J x)
  · intro h y
    exact h (p y)

end Tect.PahV2Comparison
