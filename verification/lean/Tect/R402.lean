import Mathlib

namespace Tect.R402

/- R402 formalizes only the scalar positivity and commuting-coordinate
   skeleton used by the finite Hamiltonian carré-du-champ audit.  It does not
   formalize the finite Q3 matrices, Gibbs conditional rows, or any limit. -/

theorem kinetic_prefactor_positive {chi : ℝ} (hchi : 0 < chi) :
    0 < 1 / (2 * chi) := by
  positivity

theorem commutator_square_nonnegative {z : ℝ} :
    0 ≤ z ^ 2 := by
  exact sq_nonneg z

theorem potential_scalar_commutes (v f : ℝ) :
    v * f = f * v := by
  ring

theorem finite_scope :
    (0 < (1 : ℝ) / 2) ∧ ((1 : ℝ) / 2 ≤ 1) := by
  norm_num

end Tect.R402
