import Mathlib

namespace Tect.R178

/-
  Phase-direction differentiation of the complete two-root cross owner.
  The three R-174 blocks are kept with independent coefficients: field-field,
  current-current, and ordered field-current.  This kernel is algebraic; the
  production coefficient/heat/forest owner remains outside Lean.
-/

def fieldCross (a1 a2 c1 s1 c2 s2 : Rat) : Rat :=
  a1 * a2 * (c1 * c2 + s1 * s2)

def currentCross (a1 a2 w1 w2 c1 s1 c2 s2 : Rat) : Rat :=
  w1 * w2 * a1 * a2 * (c1 * c2 + s1 * s2)

def orderedCross (a1 a2 w1 w2 c1 s1 c2 s2 : Rat) : Rat :=
  a1 * a2 * (w2 - w1) * (s1 * c2 - c1 * s2)

def completeCross (f v o a1 a2 w1 w2 c1 s1 c2 s2 : Rat) : Rat :=
  f * fieldCross a1 a2 c1 s1 c2 s2
    + v * currentCross a1 a2 w1 w2 c1 s1 c2 s2
    + o * orderedCross a1 a2 w1 w2 c1 s1 c2 s2

def phaseCosine (c1 s1 c2 s2 : Rat) : Rat := c1 * c2 + s1 * s2

def phaseSine (c1 s1 c2 s2 : Rat) : Rat := s1 * c2 - c1 * s2

theorem complete_cross_d1 (f v o a1 a2 w1 w2 c1 s1 c2 s2 : Rat) :
    let d1 := -(f + v * w1 * w2) * a1 * a2 * phaseSine c1 s1 c2 s2
      + o * a1 * a2 * (w2 - w1) * phaseCosine c1 s1 c2 s2
    d1 = -(f + v * w1 * w2) * a1 * a2 * (s1 * c2 - c1 * s2)
      + o * a1 * a2 * (w2 - w1) * (c1 * c2 + s1 * s2) := by
  dsimp [phaseSine, phaseCosine]

theorem complete_cross_d2 (f v o a1 a2 w1 w2 c1 s1 c2 s2 : Rat) :
    let d2 := (f + v * w1 * w2) * a1 * a2 * phaseSine c1 s1 c2 s2
      - o * a1 * a2 * (w2 - w1) * phaseCosine c1 s1 c2 s2
    d2 = (f + v * w1 * w2) * a1 * a2 * (s1 * c2 - c1 * s2)
      - o * a1 * a2 * (w2 - w1) * (c1 * c2 + s1 * s2) := by
  dsimp [phaseSine, phaseCosine]

theorem phase_derivative_sum_zero (f v o a1 a2 w1 w2 c1 s1 c2 s2 : Rat) :
    (-(f + v * w1 * w2) * a1 * a2 * phaseSine c1 s1 c2 s2
      + o * a1 * a2 * (w2 - w1) * phaseCosine c1 s1 c2 s2)
      + ((f + v * w1 * w2) * a1 * a2 * phaseSine c1 s1 c2 s2
      - o * a1 * a2 * (w2 - w1) * phaseCosine c1 s1 c2 s2) = 0 := by
  ring

theorem ordered_block_is_retained (a1 a2 w1 w2 c1 s1 c2 s2 : Rat) :
    orderedCross a1 a2 w1 w2 c1 s1 c2 s2 =
      a1 * a2 * (w2 - w1) * (s1 * c2 - c1 * s2) := by
  rfl

theorem ordered_block_nonzero_fixture :
    orderedCross 1 1 1 2 1 0 0 1 = -1 := by
  norm_num [orderedCross]

end Tect.R178
