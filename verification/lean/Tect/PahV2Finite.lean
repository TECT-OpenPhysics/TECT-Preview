import Mathlib

namespace Tect.PahV2Finite

/- Parameterized algebra only. The concrete PAH coordinate space, functional,
symmetries and root-to-state maps are discharged in the separate exact proof.
No theorem here encodes a regulator limit or a physical interpretation. -/

theorem integer_step_inverse (x s : Int) : x + s - s = x := by omega

theorem modular_step_inverse (K : Nat) (x s : ZMod K) :
    x + s - s = x := by ring

theorem incidence_charge_conservation (a b s : Int) :
    (a - s) + (b + s) = a + b := by omega

theorem generator_constant {R : Type*} [Fintype R]
    (rate : R → Real) (k : Real) :
    (∑ r, rate r * (k - k)) = 0 := by simp

theorem gibbs_midpoint_flux (x y beta m z : Real) :
    (Real.exp (-beta*x) / z) * (m * Real.exp (-beta*(y-x)/2)) =
    (Real.exp (-beta*y) / z) * (m * Real.exp (-beta*(x-y)/2)) := by
  have h : -beta*x + (-beta*(y-x)/2) = -beta*y + (-beta*(x-y)/2) := by ring
  calc
    _ = (m/z) * Real.exp (-beta*x + (-beta*(y-x)/2)) := by
      rw [Real.exp_add]; ring
    _ = (m/z) * Real.exp (-beta*y + (-beta*(x-y)/2)) := by rw [h]
    _ = _ := by rw [Real.exp_add]; ring

theorem directed_square_factor (c : Real) (hc : 0 ≤ c) :
    Real.sqrt (c/2) * Real.sqrt (c/2) = c/2 := by
  exact Real.mul_self_sqrt (div_nonneg hc (by norm_num))

theorem adjoint_incoming_outgoing (c fx fy : Complex) :
    (c/2)*(fx-fy) - (c/2)*(fy-fx) = -c*(fy-fx) := by ring

theorem paired_sesquilinear (k a b u v : Complex) :
    (k * star (b-a) * (v-u) + k * star (a-b) * (u-v))/2 =
      -(k * star a * (v-u) + k * star b * (u-v)) := by
  simp only [star_sub]
  ring

theorem commuting_idempotents {V : Type*} [AddCommGroup V] [Module Real V]
    (P Q L : Module.End Real V)
    (hP : P*P=P) (hQ : Q*Q=Q) (hPQ : P*Q=Q*P)
    (hPL : P*L=L*P) (hQL : Q*L=L*Q) :
    (P*Q)*(P*Q)=P*Q ∧ (P*Q)*L=L*(P*Q) := by
  constructor
  · calc
      (P*Q)*(P*Q) = P*(Q*P)*Q := by simp only [mul_assoc]
      _ = P*(P*Q)*Q := by rw [← hPQ]
      _ = (P*P)*(Q*Q) := by simp only [mul_assoc]
      _ = P*Q := by rw [hP,hQ]
  · calc
      (P*Q)*L = P*(Q*L) := by rw [mul_assoc]
      _ = P*(L*Q) := by rw [hQL]
      _ = (P*L)*Q := by rw [mul_assoc]
      _ = (L*P)*Q := by rw [hPL]
      _ = L*(P*Q) := by rw [mul_assoc]

end Tect.PahV2Finite
