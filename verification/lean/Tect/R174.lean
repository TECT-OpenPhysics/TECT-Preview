import Mathlib

namespace Tect.R174

/-
  Scalar block algebra for the registered two-root production-cylinder
  interface.  The analytic A1 matrices, Gaussian laws, and torus owner remain
  outside this kernel file; this file checks only the exact cross-root
  contraction identities used by the certificate.
-/

theorem same_root_cross_zero (a w c s : Rat) :
    a * c * (-w * a * s) + a * s * (w * a * c) = 0 := by
  ring

theorem cross_block_formula (a1 a2 w1 w2 c1 s1 c2 s2 : Rat) :
    let x1v2 := a1 * c1 * (-w2 * a2 * s2) + a1 * s1 * (w2 * a2 * c2)
    let x2v1 := a2 * c2 * (-w1 * a1 * s1) + a2 * s2 * (w1 * a1 * c1)
    And (x1v2 = w2 * a1 * a2 * (s1 * c2 - c1 * s2))
      (And (x2v1 = -w1 * a1 * a2 * (s1 * c2 - c1 * s2))
        (x1v2 + x2v1 = a1 * a2 * (w2 - w1) * (s1 * c2 - c1 * s2))) := by
  dsimp
  constructor
  case left => ring
  constructor
  case left => ring
  case right => ring

theorem field_cross_formula (a1 a2 c1 s1 c2 s2 : Rat) :
    let x1x2 := a1 * c1 * (a2 * c2) + a1 * s1 * (a2 * s2)
    x1x2 = a1 * a2 * (c1 * c2 + s1 * s2) := by
  dsimp
  ring

theorem current_cross_formula (a1 a2 w1 w2 c1 s1 c2 s2 : Rat) :
    let v1v2 := (-w1 * a1 * s1) * (-w2 * a2 * s2)
      + (w1 * a1 * c1) * (w2 * a2 * c2)
    v1v2 = w1 * w2 * a1 * a2 * (c1 * c2 + s1 * s2) := by
  dsimp
  ring

theorem same_phase_cross_zero (a1 a2 w1 w2 c s : Rat) :
    a1 * a2 * (w2 - w1) * (s * c - c * s) = 0 := by
  ring

theorem equal_frequency_cross_zero (a1 a2 w c1 s1 c2 s2 : Rat) :
    a1 * a2 * (w - w) * (s1 * c2 - c1 * s2) = 0 := by
  ring

theorem nonzero_cross_fixture :
    (1 : Rat) * 1 * (2 - 1) * (0 * 0 - 1 * 1) = -1 := by
  norm_num

theorem cross_block_bundle (a1 a2 w1 w2 c1 s1 c2 s2 : Rat) :
    let field_cross := a1 * a2 * (c1 * c2 + s1 * s2)
    let current_cross := w1 * w2 * a1 * a2 * (c1 * c2 + s1 * s2)
    let cross_block := a1 * a2 * (w2 - w1) * (s1 * c2 - c1 * s2)
    And (field_cross = a1 * a2 * (c1 * c2 + s1 * s2))
      (And (current_cross = w1 * w2 * a1 * a2 * (c1 * c2 + s1 * s2))
        (cross_block = a1 * a2 * (w2 - w1) * (s1 * c2 - c1 * s2))) := by
  dsimp
  exact And.intro rfl (And.intro rfl rfl)

end Tect.R174
