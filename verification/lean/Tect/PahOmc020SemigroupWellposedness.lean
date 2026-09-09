import Mathlib

namespace Tect.PahOmc020SemigroupWellposedness

/- These declarations formalize the exact finite derivative gap in the
   R-527 source-multiplicity witness.  They do not choose an owner convention,
   construct a path law, or assert anchored-n convergence. -/

theorem exp_neg_two_pos : 0 < Real.exp (-2 : ℝ) := by
  positivity

theorem labelled_minus_deduplicated :
    (2 : ℝ) * Real.exp (-2 : ℝ) - Real.exp (-2 : ℝ) = Real.exp (-2 : ℝ) := by
  ring

theorem derivative_gap_nonzero :
    (2 : ℝ) * Real.exp (-2 : ℝ) ≠ Real.exp (-2 : ℝ) := by
  intro h
  have hgap : Real.exp (-2 : ℝ) = 0 := by linarith
  linarith [exp_neg_two_pos]

theorem same_finite_semigroup_would_force_equal_derivatives
    (dA dB : ℝ)
    (hA : dA = (2 : ℝ) * Real.exp (-2 : ℝ))
    (hB : dB = Real.exp (-2 : ℝ))
    (hSame : dA = dB) : False := by
  apply derivative_gap_nonzero
  calc
    (2 : ℝ) * Real.exp (-2 : ℝ) = dA := hA.symm
    _ = dB := hSame
    _ = Real.exp (-2 : ℝ) := hB

theorem owner_fix_is_required :
    ¬ ((2 : ℝ) * Real.exp (-2 : ℝ) = Real.exp (-2 : ℝ)) :=
  derivative_gap_nonzero

end Tect.PahOmc020SemigroupWellposedness
