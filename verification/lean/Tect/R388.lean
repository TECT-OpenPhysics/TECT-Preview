import Mathlib

namespace Tect.R388

noncomputable def comm {R : Type*} [Ring R] (x y : R) : R := x * y - y * x

theorem jacobi_reduction {R : Type*} [Ring R] (b h a : R)
    (hba : comm b a = 0) :
    comm b (comm h a) = comm (comm b h) a := by
  have hba' : b * a = a * b := by
    exact sub_eq_zero.mp hba
  have hleft : b * a * h = a * b * h := by rw [hba']
  have hright : h * b * a = h * a * b := by
    calc
      h * b * a = h * (b * a) := mul_assoc h b a
      _ = h * (a * b) := congrArg (fun x => h * x) hba'
      _ = h * a * b := (mul_assoc h a b).symm
  calc
    comm b (comm h a) = b * h * a - b * a * h - h * a * b + a * h * b := by
      simp [comm, mul_sub, sub_mul]
      noncomm_ring
    _ = b * h * a - h * a * b - a * b * h + a * h * b := by
      rw [hleft]
      abel
    _ = comm (comm b h) a := by
      simp only [comm, mul_sub, sub_mul]
      rw [← hright]
      simp only [mul_assoc]
      abel

theorem kinetic_coordinate_isolation {R : Type*} [Ring R] (b t v a : R)
    (hva : comm v a = 0) (hba : comm b a = 0) :
    comm b (comm (t + v) a) = comm (comm b t) a := by
  have inner : comm (t + v) a = comm t a := by
    calc
      comm (t + v) a = comm t a + comm v a := by
        simp [comm]
        noncomm_ring
      _ = comm t a := by rw [hva, add_zero]
  rw [inner, jacobi_reduction b t a hba]

theorem scope_fixture :
    (True ∧ True) ∧ ¬ (False ∨ False) := by
  norm_num

end Tect.R388
