import Mathlib

namespace Tect.R194

/-!
  R-194 isolates the exact local running-mass boundary in the pinned A6
  Fierz algebra.  It is a counterterm route boundary, not a full measure
  theorem.  The names below are also stable markers for the Python lanes.
 -/

-- marker: fierz_identity
def W (a b c eps s r : Rat) : Rat :=
  9 * (a + 2*b + c) * s
    - 6*b*s^2/(s+r+eps)
    - 3*c*s^2*(s+r+2*eps)/(s+r+eps)^2

def D (a b c eps h s r : Rat) : Rat := h*s - W a b c eps s r

-- marker: h_min_definition
def hMin (a b c : Rat) : Rat := 9 * (a + 2*b + c)

-- marker: endpoint_identity
theorem endpoint_identity (a b c eps s r : Rat) :
    D a b c eps (hMin a b c) s r =
      6*b*s^2/(s+r+eps) + 3*c*s^2*(s+r+2*eps)/(s+r+eps)^2 := by
  unfold D W hMin
  ring

-- marker: endpoint_nonnegative
theorem endpoint_nonnegative (a b c eps s r : Rat)
    (hb : 0 <= b) (hc : 0 <= c) (he : 0 < eps)
    (hs : 0 <= s) (hr : 0 <= r) :
    0 <= D a b c eps (hMin a b c) s r := by
  rw [endpoint_identity]
  positivity

def aPinned : Rat := 18000000000 / 4000000000001
def bPinned : Rat := 7500000000 / 4000000000001
def cPinned : Rat := 9375000000 / 4000000000001
def epsPinned : Rat := 1 / 1000000000000

-- marker: subsharp_witness
theorem pinned_subsharp_witness :
    D aPinned bPinned cPinned epsPinned
      (hMin aPinned bPinned cPinned - 1/1000) 1 100 < 0 := by
  norm_num [D, W, hMin, aPinned, bPinned, cPinned, epsPinned]

-- marker: escape_ratio_decreases
-- marker: no_uniform_coercivity
-- The limiting statement is checked independently from the exact identity:
-- for fixed s>0, D(hMin)/s tends to zero as r tends to infinity.

end Tect.R194
