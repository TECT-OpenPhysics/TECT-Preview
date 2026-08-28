import Mathlib

namespace Tect.R399

/- R399 formalizes the scalar shell-to-Dirichlet transfer only.  The
  conditional laws, birth-death spectra and Q3 limits are computed in the
  executable lanes; no thermodynamic assertion is made here. -/

theorem conditional_variance_identity (p f m : ℝ) :
    p * (f - m) ^ 2 = p * f ^ 2 - 2 * p * m * f + p * m ^ 2 := by
  ring

theorem birth_death_poincare {variance dirichlet lambda : ℝ}
    (hlambda : 0 < lambda) (hdom : lambda * variance ≤ dirichlet) :
    variance ≤ dirichlet / lambda := by
  apply (le_div_iff₀ hlambda).2
  nlinarith

theorem weighted_shell_transfer {weight variance dirichlet lambda : ℝ}
    (hweight : 0 ≤ weight) (hlambda : 0 < lambda)
    (hdom : lambda * variance ≤ dirichlet) :
    weight * variance ≤ weight * dirichlet / lambda := by
  have hbase : variance ≤ dirichlet / lambda :=
    birth_death_poincare hlambda hdom
  calc
    weight * variance ≤ weight * (dirichlet / lambda) :=
      mul_le_mul_of_nonneg_left hbase hweight
    _ = weight * dirichlet / lambda := by ring

theorem finite_scope :
    (0 < (1 : ℝ) / 8) ∧ ((1 : ℝ) / 8 ≤ 1) ∧ ((1 : ℝ) / 8 ≤ 2) := by
  norm_num

end Tect.R399
