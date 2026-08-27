import Mathlib

namespace Tect.R368

/- R368 formalizes the scalar weighted envelope and the finite Kubo--Mori
   diagonal convention used by the executable actual-Q3 all-prefix audit.
   Matrix spectra, common cores, and regulator limits remain outside Lean. -/

def arithmeticMean (p q : Rat) : Rat := (p + q) / 2

def kuboMoriDiagonal (p : Rat) : Rat := p

theorem kubo_mori_diagonal (p : Rat) : kuboMoriDiagonal p = p := by
  rfl

theorem arithmetic_mean_symmetry (p q : Rat) :
    arithmeticMean p q = arithmeticMean q p := by
  simp [arithmeticMean, add_comm]

theorem half_envelope (y : ℝ) :
    min 4 (y ^ 2) ≤ 2 * |y| := by
  by_cases h : |y| ≤ 2
  · have hprod : 0 ≤ |y| * (2 - |y|) :=
      mul_nonneg (abs_nonneg y) (sub_nonneg.mpr h)
    have habs : |y| ^ 2 = y ^ 2 := sq_abs y
    have hsq : y ^ 2 ≤ 2 * |y| := by
      nlinarith
    exact le_trans (min_le_right 4 (y ^ 2)) hsq
  · have hbig : 2 ≤ |y| := le_of_not_ge h
    have hfour : (4 : ℝ) ≤ 2 * |y| := by nlinarith
    exact le_trans (min_le_left 4 (y ^ 2)) hfour

theorem weighted_half_envelope (w y : ℝ) (hw : 0 ≤ w) :
    w * min 4 (y ^ 2) ≤ w * (2 * |y|) := by
  exact mul_le_mul_of_nonneg_left (half_envelope y) hw

theorem prefix_fixture : (4 : Nat) = 1 + 3 := by
  norm_num

theorem scope_fixture :
    (True ∧ True ∧ True) ∧ ¬ (False ∨ False ∨ False ∨ False) := by
  norm_num

end Tect.R368
