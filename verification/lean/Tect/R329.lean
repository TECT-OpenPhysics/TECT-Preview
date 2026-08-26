import Mathlib

namespace Tect.R329

/- R329 is an exact rational order witness for EXP-001159.  It does not
   formalize the Q3 spectral power, unbounded operator domains, or any
   thermodynamic/QFT limit. -/

def qMatrix : Matrix (Fin 2) (Fin 2) Rat := !![0, 1; 1, 0]

def aMatrix : Matrix (Fin 2) (Fin 2) Rat := !![1, 0; 0, 2]

theorem matrix_order_fixture :
    (qMatrix * aMatrix) 0 1 = 2 ∧ (aMatrix * qMatrix) 0 1 = 1 := by
  norm_num [qMatrix, aMatrix, Matrix.mul_apply, Fin.sum_univ_succ]

theorem matrix_commutator_nonzero : qMatrix * aMatrix - aMatrix * qMatrix ≠ 0 := by
  intro h
  have h01 := congrArg (fun M : Matrix (Fin 2) (Fin 2) Rat => M 0 1) h
  norm_num [qMatrix, aMatrix, Matrix.mul_apply, Fin.sum_univ_succ] at h01

theorem triangle_fixture (x y : Rat) : x - y ≤ |x| + |y| := by
  nlinarith [le_abs_self x, le_abs_self y, neg_le_abs x, neg_le_abs y]

theorem scope_fixture :
    (True ∧ True) ∧ ¬ (False ∨ False ∨ False ∨ False) := by
  norm_num

end Tect.R329
