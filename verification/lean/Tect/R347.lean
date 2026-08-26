import Mathlib

namespace Tect.R347

theorem unitary_holder_corollary
    (lhs tail : Rat)
    (hlhs : 0 ≤ lhs) (htail : 0 ≤ tail)
    (hbound : lhs ≤ tail + tail) :
    lhs ≤ 2 * tail := by
  nlinarith

theorem selfadjoint_tail_leg_fixture
    (left right : Rat)
    (hleft : left = right) :
    left + right = 2 * left := by
  nlinarith

end Tect.R347
