import Mathlib

namespace Tect.R342

theorem gram_transport_congruence {ι : Type*} [Fintype ι] [DecidableEq ι]
    (a b : Matrix ι ι ℝ) (ha : IsUnit a.det) :
    Matrix.transpose (a⁻¹ * b) * (Matrix.transpose a * a) * (a⁻¹ * b) =
      Matrix.transpose b * b := by
  have hright : a * a⁻¹ = (1 : Matrix ι ι ℝ) := Matrix.mul_nonsing_inv a ha
  have htrans : Matrix.transpose (a⁻¹) * Matrix.transpose a = (1 : Matrix ι ι ℝ) := by
    rw [← Matrix.transpose_mul a (a⁻¹), hright, Matrix.transpose_one]
  calc
    Matrix.transpose (a⁻¹ * b) * (Matrix.transpose a * a) * (a⁻¹ * b) =
        Matrix.transpose b * (Matrix.transpose (a⁻¹) * Matrix.transpose a) *
          (a * a⁻¹) * b := by
      rw [Matrix.transpose_mul]
      noncomm_ring
    _ = Matrix.transpose b * b := by rw [htrans, hright]; simp

end Tect.R342
