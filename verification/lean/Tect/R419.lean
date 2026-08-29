import Mathlib

namespace Tect.R419

/- R419 formalizes only scalar positivity and finite-grid bookkeeping.  The
   Q3 Hamiltonian diagonalization, conditional rows, matrix spectra and every
   volume or continuum limit remain executable/open analysis. -/

theorem positive_tail_rate {v lv : ℝ} (hv : 0 < v) (hlv : lv < 0) :
    0 < -lv / v := by
  exact div_pos (neg_pos.mpr hlv) hv

theorem core_tail_envelope {gap core_mass tail_mass : ℝ}
    (hgap : 0 < gap) (hcore : (9 : ℝ) / 10 < core_mass)
    (htail : tail_mass < (3 : ℝ) / 100) :
    0 < gap ∧ 0 < core_mass ∧ 0 < 1 - tail_mass := by
  constructor
  · exact hgap
  constructor
  · linarith
  · linarith

theorem volume_grid :
    (2 : ℕ) < 3 ∧ (3 : ℕ) < 4 ∧ 3 ≤ 4 := by
  omega

theorem finite_scope :
    (0 < (1 : ℝ) / 40) ∧ ((1 : ℝ) / 40 < (1 : ℝ) / 10) ∧
      (0 < (4 : ℝ)) ∧ ((4 : ℝ) < 12) := by
  norm_num

end Tect.R419
