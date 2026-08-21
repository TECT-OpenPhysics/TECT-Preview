import Mathlib

namespace Tect.R181

/-
  The R-177 incidence has one common heat block, root 1, root 2, and a
  future residual.  On the two-root source coordinates, the root-2 feedback
  is the lower-triangular map T(x,y)=(x,beta*x+y).  This file checks the
  registered beta=1/2 block exactly.  It is a finite incidence/Gram lemma,
  not the production spatial mixed-Gram theorem.
-/

def feedback (x y : Rat) : Prod Rat Rat := (x, x / 2 + y)

def sourceNorm (x y : Rat) : Rat := x ^ 2 + y ^ 2

def outputNorm (x y : Rat) : Rat :=
  x ^ 2 + (x / 2 + y) ^ 2

def gram : Matrix (Fin 2) (Fin 2) Rat :=
  !![5 / 4, 1 / 2; 1 / 2, 1]

theorem feedback_formula (x y : Rat) :
    feedback x y = (x, x / 2 + y) := by
  rfl

theorem gram_matrix_is_feedback_transpose_feedback :
    gram =
      Matrix.transpose (!![1, 0; 1 / 2, 1] : Matrix (Fin 2) (Fin 2) Rat) *
        (!![1, 0; 1 / 2, 1] : Matrix (Fin 2) (Fin 2) Rat) := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    norm_num [gram, Matrix.mul_apply, Fin.sum_univ_succ]

theorem gram_quadratic (x y : Rat) :
    x * ((5 / 4 : Rat) * x + (1 / 2 : Rat) * y) +
      y * ((1 / 2 : Rat) * x + y) = outputNorm x y := by
  simp [outputNorm]
  ring

theorem feedback_defect_decomposition (x y : Rat) :
    2 * sourceNorm x y - outputNorm x y =
      (y - x / 2) ^ 2 + x ^ 2 / 2 := by
  simp [sourceNorm, outputNorm]
  ring

theorem feedback_mixed_gram_bound (x y : Rat) :
    outputNorm x y <= 2 * sourceNorm x y := by
  have h : 0 <= (y - x / 2) ^ 2 + x ^ 2 / 2 := by positivity
  nlinarith [feedback_defect_decomposition x y]

theorem feedback_bound_strict_off_zero (x y : Rat) (hxy : Or (Not (x = 0)) (Not (y = 0))) :
    outputNorm x y < 2 * sourceNorm x y := by
  have h : 0 < (y - x / 2) ^ 2 + x ^ 2 / 2 := by
    have hne : Not ((y - x / 2) ^ 2 + x ^ 2 / 2 = 0) := by
      intro hzero
      cases hxy with
      | inl hx =>
          have hx0 : x = 0 := by
            nlinarith [sq_nonneg (y - x / 2)]
          exact hx hx0
      | inr hy =>
          have hx0 : x = 0 := by
            nlinarith [sq_nonneg (y - x / 2)]
          have hy0 : y = 0 := by
            nlinarith [hzero, hx0]
          exact hy hy0
    have hnonneg : 0 <= (y - x / 2) ^ 2 + x ^ 2 / 2 := by positivity
    exact lt_of_le_of_ne hnonneg (Ne.symm hne)
  nlinarith [feedback_defect_decomposition x y]

theorem feedback_zero_defect (x y : Rat) :
    Iff (2 * sourceNorm x y - outputNorm x y = 0) (And (x = 0) (y = 0)) := by
  constructor
  case mp =>
    intro h
    have hsquares : (y - x / 2) ^ 2 + x ^ 2 / 2 = 0 := by
      nlinarith [feedback_defect_decomposition x y]
    have hx : x = 0 := by
      nlinarith [sq_nonneg (y - x / 2)]
    have hy : y = 0 := by
      nlinarith [sq_nonneg (y - x / 2)]
    exact And.intro hx hy
  case mpr =>
    intro h
    cases h with
    | intro hx hy =>
        subst x
        subst y
        norm_num [sourceNorm, outputNorm]

end Tect.R181
