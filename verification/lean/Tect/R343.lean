import Mathlib

namespace Tect.R343

def commutator {ι : Type*} [Fintype ι] (a b : Matrix ι ι ℝ) : Matrix ι ι ℝ :=
  a * b - b * a

theorem commutator_difference {ι : Type*} [Fintype ι]
    (h0 delta a : Matrix ι ι ℝ) :
    commutator (h0 + delta) a - commutator h0 a = commutator delta a := by
  simp only [commutator, add_mul, mul_add]
  noncomm_ring

theorem commutator_difference_zero {ι : Type*} [Fintype ι]
    (h0 delta a : Matrix ι ι ℝ) (hcomm : delta * a = a * delta) :
    commutator (h0 + delta) a - commutator h0 a = 0 := by
  rw [commutator_difference]
  simp [commutator, hcomm]

end Tect.R343
