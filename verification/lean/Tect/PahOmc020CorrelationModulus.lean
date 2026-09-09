import Mathlib

/-!
Finite rational checks for the PAH-OMC-020 deterministic correlation modulus.
Only the nonnegative form-energy budget, product domination, and fixtures are
formalized.  No stopping-time process or infinite-volume limit is asserted.
-/

namespace Tect.PahOmc020CorrelationModulus

def budget (d m h l : Rat) : Rat := 2 * d * m ^ 2 + 2 * h * l ^ 2

theorem budget_nonnegative {d m h l : Rat}
    (hd : 0 ≤ d) (hh : 0 ≤ h) : 0 ≤ budget d m h l := by
  unfold budget
  nlinarith [sq_nonneg m, sq_nonneg l]

theorem product_domination {δ ef eg bf bg : Rat}
    (hδ : 0 ≤ δ) (hef : 0 ≤ ef) (heg : 0 ≤ eg)
    (hbf : 0 ≤ bf) (hbg : 0 ≤ bg)
    (hef_le : ef ≤ bf) (heg_le : eg ≤ bg) :
    δ ^ 2 * ef * eg ≤ δ ^ 2 * bf * bg := by
  have hleft : 0 ≤ (bf - ef) * bg := mul_nonneg (sub_nonneg.mpr hef_le) hbg
  have hright : 0 ≤ ef * (bg - eg) := mul_nonneg hef (sub_nonneg.mpr heg_le)
  have hprod : ef * eg ≤ bf * bg := by
    nlinarith
  have hdelta : 0 ≤ δ ^ 2 := sq_nonneg δ
  have hgap : 0 ≤ δ ^ 2 * (bf * bg - ef * eg) := mul_nonneg hdelta (sub_nonneg.mpr hprod)
  nlinarith

theorem source_fixture_budget :
    budget 10 2 20 1 = 120 := by
  norm_num [budget]

theorem source_fixture_same_modulus :
    (1 / 100 : Rat) * budget 10 2 20 1 = 6 / 5 := by
  norm_num [budget]

theorem time_gap_square_decreases (b : Rat) (hb : 0 < b) :
    (b / 2) ^ 2 < b ^ 2 := by
  nlinarith [sq_pos_of_pos hb]

end Tect.PahOmc020CorrelationModulus
