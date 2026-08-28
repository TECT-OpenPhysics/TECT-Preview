import Mathlib

namespace Tect.R386

/- The finite Python lanes use matrices.  These theorems isolate the
   algebraic reason for the zero-time anchor without claiming an analytic
   domain or a thermodynamic limit. -/

theorem commute_inverse_of_commute {G : Type*} [Group G] {b a : G}
    (h : Commute b a) : Commute b a⁻¹ := by
  exact h.inv_right

noncomputable def comm {R : Type*} [Ring R] (x y : R) : R := x * y - y * x

theorem commutator_difference {R : Type*} [Ring R] (h b a : R) :
    comm (h + b) a - comm h a = comm b a := by
  simp [comm]
  noncomm_ring

theorem anchored_first_variation {R : Type*} [Ring R] (h b a : R)
    (hzero : comm b a = 0) :
    comm (h + b) a - comm h a = 0 := by
  rw [commutator_difference, hzero]

theorem anchored_second_variation {R : Type*} [Ring R] (h b a : R)
    (hzero : comm b a = 0) :
    comm (h + b) (comm (h + b) a) - comm h (comm h a) =
      comm b (comm h a) := by
  have hcomm : comm (h + b) a = comm h a := by
    have hdiff := commutator_difference h b a
    rw [hzero] at hdiff
    exact sub_eq_zero.mp hdiff
  rw [hcomm]
  exact commutator_difference h b (comm h a)

theorem scope_fixture :
    (True ∧ True ∧ True ∧ True ∧ True) ∧
      ¬ (False ∨ False ∨ False ∨ False ∨ False) := by
  norm_num

end Tect.R386
