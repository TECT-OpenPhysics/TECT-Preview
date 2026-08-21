import Mathlib

namespace Tect.R176

/-
  A symbolic lower-triangular Cholesky template for the three-dimensional
  A1 production symbol.  The numerical lanes instantiate the six entries at
  k and 2k and then use the inverse-transpose factor as a covariance root.
  This kernel theorem checks the exact Gram identity only; positivity and the
  transcendental pi evaluations remain in the independent executable lanes.
-/

variable {R : Type*} [CommRing R]

def lower3 (s1 q21 q31 s2 q32 s3 : R) : Matrix (Fin 3) (Fin 3) R :=
  !![s1, 0, 0; q21, s2, 0; q31, q32, s3]

def gram3 (s1 q21 q31 s2 q32 s3 : R) : Matrix (Fin 3) (Fin 3) R :=
  !![s1 ^ 2, s1 * q21, s1 * q31;
     s1 * q21, q21 ^ 2 + s2 ^ 2, q21 * q31 + s2 * q32;
     s1 * q31, q21 * q31 + s2 * q32, q31 ^ 2 + q32 ^ 2 + s3 ^ 2]

theorem lower3_gram (s1 q21 q31 s2 q32 s3 : R) :
    lower3 s1 q21 q31 s2 q32 s3 * Matrix.transpose (lower3 s1 q21 q31 s2 q32 s3) =
      gram3 s1 q21 q31 s2 q32 s3 := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp [lower3, gram3, Matrix.mul_apply, Fin.sum_univ_succ] <;> ring

theorem lower3_gram_entrywise (s1 q21 q31 s2 q32 s3 : R) :
    (lower3 s1 q21 q31 s2 q32 s3 * Matrix.transpose (lower3 s1 q21 q31 s2 q32 s3)) =
      gram3 s1 q21 q31 s2 q32 s3 :=
  lower3_gram s1 q21 q31 s2 q32 s3

end Tect.R176
