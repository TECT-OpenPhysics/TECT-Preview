import Mathlib

namespace Tect.R293

/- R293 formalizes only the declared scalar bookkeeping.  It does not formalize
   matrix exponentials, truncated CCR, unbounded domains, Gibbs limits, or QFT. -/

def tailBound (moment radius : Rat) : Rat := moment / radius ^ 5

theorem kinetic_shift_identity (p a chi : Rat) (hchi : chi ≠ 0) :
    ((p + a) ^ 2 - p ^ 2) / (2 * chi) = a * p / chi + a ^ 2 / (2 * chi) := by
  field_simp [hchi]
  ring

theorem tail_markov_fixture (moment radius : Rat) (hradius : radius ≠ 0) :
    radius ^ 5 * tailBound moment radius = moment := by
  unfold tailBound
  field_simp [hradius]

theorem tail_order_fixture : (8 : Rat) ^ 5 = 32768 := by
  norm_num

theorem tail_ratio_fixture : (3 : Rat) / 2 ≤ 2 := by
  norm_num

theorem scope_fixture : (True ∧ True ∧ True ∧ True) ∧ ¬ False := by
  norm_num

end Tect.R293
