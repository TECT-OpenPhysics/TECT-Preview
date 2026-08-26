import Mathlib

namespace Tect.R346

def holderEnvelope (wLeft wRight aLeft aRight : Rat) : Rat :=
  wLeft * aRight + aLeft * wRight

theorem two_term_holder_assembly
    (left right wLeft wRight aLeft aRight : ℝ)
    (hleft : 0 ≤ left) (hright : 0 ≤ right)
    (hwLeft : 0 ≤ wLeft) (hwRight : 0 ≤ wRight)
    (haLeft : 0 ≤ aLeft) (haRight : 0 ≤ aRight)
    (hleft_bound : left ≤ wLeft * aRight)
    (hright_bound : right ≤ aLeft * wRight) :
    left + right ≤ wLeft * aRight + aLeft * wRight := by
  nlinarith

theorem holder_envelope_fixture :
    holderEnvelope (3 / 2) (5 / 4) (7 / 3) (11 / 6) = (17 : Rat) / 3 := by
  norm_num [holderEnvelope]

theorem holder_envelope_nonnegative
    (wLeft wRight aLeft aRight : ℝ)
    (hwLeft : 0 ≤ wLeft) (hwRight : 0 ≤ wRight)
    (haLeft : 0 ≤ aLeft) (haRight : 0 ≤ aRight) :
    0 ≤ wLeft * aRight + aLeft * wRight := by
  positivity

end Tect.R346
