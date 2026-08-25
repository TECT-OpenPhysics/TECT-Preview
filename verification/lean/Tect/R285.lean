import Mathlib

namespace Tect.R285

/- R285 formalizes only the scalar shell-subsequence limit.  The Q3 dual tail
   and both Duhamel integrand estimates are hypotheses in the manifest. -/

theorem inverse_square_tail_limit {C : ℝ} (_hC : 0 ≤ C) :
    Filter.Tendsto
      (fun n : Nat => C * ((n : ℝ)⁻¹) ^ (2 : Nat))
      Filter.atTop (nhds 0) := by
  have hinv : Filter.Tendsto (fun n : Nat => (n : ℝ)⁻¹)
      Filter.atTop (nhds 0) :=
    tendsto_inv_atTop_zero.comp tendsto_natCast_atTop_atTop
  have hpow : Filter.Tendsto (fun n : Nat => ((n : ℝ)⁻¹) ^ (2 : Nat))
      Filter.atTop (nhds 0) := by
    simpa using hinv.pow 2
  simpa using (tendsto_const_nhds.mul hpow)

theorem combined_squared_tail_fixture :
    (1 / 5 : ℝ) ^ 2 *
        ((1 / 2 : ℝ) ^ 2 * 38880 + (3 / 4 : ℝ) ^ 2 * 38880) =
      6318 / 5 := by
  norm_num

theorem scope_fixture :
    (0 : ℝ) < 6318 / 5 ∧
      (6318 / 5 : ℝ) / 25 < 6318 / 5 := by
  norm_num

end Tect.R285
