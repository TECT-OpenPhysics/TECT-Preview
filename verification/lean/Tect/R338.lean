import Mathlib

namespace Tect.R338

theorem finite_trace_cyclicity {n : Type*} [Fintype n] [DecidableEq n]
    (A B : Matrix n n Complex) :
    Matrix.trace (A * B) = Matrix.trace (B * A) := by
  exact Matrix.trace_mul_comm A B

theorem finite_thermal_four_cycle {n : Type*} [Fintype n] [DecidableEq n]
    (X A Y B : Matrix n n Complex) :
    Matrix.trace (X * A * Y * B) = Matrix.trace (Y * B * X * A) := by
  simpa [Matrix.mul_assoc] using (Matrix.trace_mul_comm (X * A) (Y * B))

theorem finite_os_gram_real_possemidef {iota kappa : Type*} [Fintype iota] [Fintype kappa]
    [DecidableEq iota] [DecidableEq kappa] (f : iota -> kappa -> Real) :
    Matrix.PosSemidef (fun i j => Finset.univ.sum (fun k => f i k * f j k)) := by
  let A : Matrix kappa iota Real := fun k i => f i k
  have h := Matrix.posSemidef_conjTranspose_mul_self A
  have hA : (Matrix.conjTranspose A * A : Matrix iota iota Real) =
      (fun i j => Finset.univ.sum (fun k => f i k * f j k)) := by
    ext i j
    simp [A, Matrix.mul_apply]
  rw [hA] at h
  exact h

theorem finite_transfer_scope (one : Matrix (Fin 1) (Fin 1) Complex) :
    And (Matrix.trace (one * one) = Matrix.trace (one * one))
      (Matrix.trace (one * one * one * one) = Matrix.trace (one * one * one * one)) := by
  constructor
  case left =>
    exact finite_trace_cyclicity one one
  case right =>
    exact finite_thermal_four_cycle one one one one

end Tect.R338
