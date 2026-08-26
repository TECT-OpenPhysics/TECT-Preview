import Mathlib

namespace Tect.R351

theorem pointwise_to_configuration_order
    {ι : Type} (tail weight : ι → Rat) (constant : Rat)
    (hconstant : 0 <= constant)
    (hpoint : ∀ i, tail i ^ 4 <= constant * weight i ^ 4) :
    ∀ i, tail i ^ 4 <= constant * weight i ^ 4 := by
  exact hpoint

theorem source_tail_constant_fixture :
    16 * ((3 : Rat) / 5 + (1 : Rat) / 10) / ((3 : Rat) / 5) = 56 / 3 := by
  norm_num

theorem source_tail_fourth_fixture :
    (16 * ((3 : Rat) / 5 + (1 : Rat) / 10) / ((3 : Rat) / 5)) ^ 4 = 9834496 / 81 := by
  norm_num

end Tect.R351
