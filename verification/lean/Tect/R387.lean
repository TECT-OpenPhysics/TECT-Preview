import Mathlib

namespace Tect.R387

/- The finite lanes isolate the part of the anchored nested commutator that
   can depend on the kinetic term.  These theorems encode only the ring
   bookkeeping; no unbounded operator domain or limit is asserted. -/

noncomputable def comm {R : Type*} [Ring R] (x y : R) : R := x * y - y * x

theorem commutator_addition {R : Type*} [Ring R] (t v a : R)
    (hva : comm v a = 0) :
    comm (t + v) a = comm t a := by
  calc
    comm (t + v) a = comm t a + comm v a := by
      simp [comm]
      noncomm_ring
    _ = comm t a := by rw [hva, add_zero]

theorem kinetic_isolation {R : Type*} [Ring R] (b t v a : R)
    (hva : comm v a = 0) :
    comm b (comm (t + v) a) = comm b (comm t a) := by
  rw [commutator_addition t v a hva]

theorem potential_scale_invariance {R : Type*} [Ring R] (b t a scaled_v : R)
    (hscaled : comm scaled_v a = 0) :
    comm b (comm (t + scaled_v) a) = comm b (comm t a) := by
  rw [commutator_addition t scaled_v a hscaled]

theorem scope_fixture :
    (True ∧ True ∧ True) ∧ ¬ (False ∨ False ∨ False) := by
  norm_num

end Tect.R387
