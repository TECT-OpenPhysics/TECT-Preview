import Mathlib

namespace Tect.R230

theorem context_insert {G : Type} [Group G]
    (a d1 d2 d3 c b : G) :
    a * d1 * d2 * d3 * b⁻¹ =
      (a * d1 * c⁻¹) * (c * d2 * c⁻¹) * (c * d3 * b⁻¹) := by
  simp [mul_assoc]

theorem central_word_rate_fixture :
    (1382807 / 7168 : Rat) > 0 ∧
      (1382807 / 7168 : Rat)^2 > 0 ∧
      (1382807 / 7168 : Rat)^4 > 0 := by
  norm_num

theorem first_passage_exponent_fixture :
    (2 : Rat) * 6 * 2 * (1382807 / 7168) * (1 / 1000) =
      (4148421 / 896000 : Rat) := by
  norm_num

theorem distance_factor_fixture :
    (2 : Rat)^10 = 1024 ∧ (1 / (2 : Rat)^10) = (1 / 1024 : Rat) := by
  norm_num

theorem scope_fixture : True ∧ ¬False := by
  norm_num

end Tect.R230
