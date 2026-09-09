import Mathlib

/-!
Finite rational consequences for the PAH-OMC-020 local path-tightness
contract.  These declarations verify only the two-square increment envelope,
its nonnegativity, a Markov quotient, and monotonicity in the time increment.
They do not construct a stochastic process or prove a limit theorem.
-/

namespace Tect.PahOmc020PathTightness

theorem two_square_sum (a b : Rat) :
    (a + b) ^ 2 ≤ 2 * a ^ 2 + 2 * b ^ 2 := by
  nlinarith [sq_nonneg (a - b)]

theorem envelope_nonnegative (delta kGamma kL : Rat)
    (hdelta : 0 ≤ delta) (hGamma : 0 ≤ kGamma) (hL : 0 ≤ kL) :
    0 ≤ 2 * delta * kGamma + 2 * delta ^ 2 * kL := by
  positivity

theorem markov_bound_nonnegative (delta kGamma kL eps : Rat)
    (hdelta : 0 ≤ delta) (hGamma : 0 ≤ kGamma) (hL : 0 ≤ kL)
    (heps : 0 < eps) :
    0 ≤ (2 * delta * kGamma + 2 * delta ^ 2 * kL) / eps ^ 2 := by
  positivity

theorem envelope_decreases (small large kGamma kL : Rat)
    (hsmall : 0 ≤ small) (horder : small ≤ large)
    (hGamma : 0 ≤ kGamma) (hL : 0 ≤ kL) :
    2 * small * kGamma + 2 * small ^ 2 * kL ≤
      2 * large * kGamma + 2 * large ^ 2 * kL := by
  have hdiff : 0 ≤ large - small := by linarith
  have hsum : 0 ≤ large + small := by linarith
  have hsq : 0 ≤ (large - small) * (large + small) :=
    mul_nonneg hdiff hsum
  have hlin : 0 ≤ (large - small) * kGamma :=
    mul_nonneg hdiff hGamma
  nlinarith

theorem source_constants_fixture :
    (540 : Rat) = 60 * 9 ∧ (60 : Rat) = 60 := by
  norm_num

theorem compact_time_fixture :
    (0 : Rat) ≤
      2 * (1 / 1000) * (540 * 2 * (1 / 4) ^ 2) +
      2 * (1 / 1000) ^ 2 * (60 * 2 * (60 * 2 * (1 / 4) ^ 2)) := by
  norm_num

end Tect.PahOmc020PathTightness
