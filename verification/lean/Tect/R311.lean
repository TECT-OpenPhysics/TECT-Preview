import Mathlib

namespace Tect.R311

/- R311 checks the exact rational fixtures used by EXP-001141.  It does not
   formalize finite matrix diagonalization, the Kubo-Mori integral, locality,
   a thermodynamic limit, or the QFT reconstruction step. -/

theorem six_site_graph_fixture : (7 : Nat) = 1 + 4 + 2 := by
  norm_num

theorem cutoff_order_fixture : (1 / 2 : Rat) < 1 ∧ 1 < 2 ∧ 2 < 4 := by
  norm_num

def generatorCoeff (gap hbar value : Rat) : Rat := gap * value / hbar

theorem generator_pairing_scalar_fixture (ell gap hbar a b : Rat) (hh : hbar ≠ 0) :
    ell * (-(gap ^ 2) * a / hbar ^ 2) * b +
      ell * generatorCoeff gap hbar a * generatorCoeff gap hbar b = 0 := by
  simp [generatorCoeff]
  field_simp [hh]
  ring

theorem volume_ratio_fixture : (12 : Rat) / 4 = 3 := by
  norm_num

end Tect.R311
