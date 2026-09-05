import Mathlib

namespace Tect.R507

/-!
  Conditional composition bridge for the PAH-OMC-014 full-Q Cauchy split.

  A finite common block is controlled by one supplied bound, and each omitted
  tail by its own supplied bound.  This theorem combines those three estimates
  by the triangle inequality only.  The block and tail values remain
  source-owned inputs; no PAH sector law or limit is instantiated here.
-/

theorem finite_block_plus_two_tail_bound
    {I : Type*} [Fintype I]
    (block1 block2 tail1 tail2 : Real)
    (e_w e_a C tau1 tau2 : Real)
    (h_block :
      |block1 - block2| <= (Fintype.card I : Real) * (C * e_w + e_a))
    (h_tail1 : |tail1| <= C * tau1)
    (h_tail2 : |tail2| <= C * tau2) :
    |(block1 + tail1) - (block2 + tail2)| <=
      (Fintype.card I : Real) * (C * e_w + e_a) + C * tau1 + C * tau2 := by
  have h_tail_difference : |tail1 - tail2| <= C * tau1 + C * tau2 := by
    calc
      |tail1 - tail2| <= |tail1| + |tail2| := by
        simpa using (abs_sub_le tail1 0 tail2)
      _ <= C * tau1 + C * tau2 := add_le_add h_tail1 h_tail2
  calc
    |(block1 + tail1) - (block2 + tail2)| =
        |(block1 - block2) + (tail1 - tail2)| := by
          congr 1
          ring
    _ <= |block1 - block2| + |tail1 - tail2| := by
          exact abs_add_le _ _
    _ <= (Fintype.card I : Real) * (C * e_w + e_a) +
          (C * tau1 + C * tau2) := add_le_add h_block h_tail_difference
    _ = (Fintype.card I : Real) * (C * e_w + e_a) +
          C * tau1 + C * tau2 := by ring

theorem zero_tail_pair_is_block_bound
    {I : Type*} [Fintype I]
    (block1 block2 : Real) (e_w e_a C : Real)
    (h_block :
      |block1 - block2| <= (Fintype.card I : Real) * (C * e_w + e_a)) :
    |(block1 + 0) - (block2 + 0)| <=
      (Fintype.card I : Real) * (C * e_w + e_a) := by
  simpa using h_block

end Tect.R507
