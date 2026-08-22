import Mathlib

namespace Tect.R195

/-! Spatial constant-field lift of the R-194 local running-mass escape. -/

def W (a b c eps s r : Rat) : Rat :=
  9 * (a + 2*b + c) * s
    - 6*b*s^2/(s+r+eps)
    - 3*c*s^2*(s+r+2*eps)/(s+r+eps)^2

def D (a b c eps h s r : Rat) : Rat := h*s - W a b c eps s r

def hMin (a b c : Rat) : Rat := 9 * (a + 2*b + c)

-- marker: spatial_constant_field
-- A constant field on a finite torus multiplies the local density by its volume.
theorem integrated_identity (a b c eps s r V : Rat) :
    V * D a b c eps (hMin a b c) s r =
      V * (6*b*s^2/(s+r+eps) + 3*c*s^2*(s+r+2*eps)/(s+r+eps)^2) := by
  unfold D W hMin
  ring

-- marker: scaled_ratio_identity
-- The volume cancels from the coercivity ratio on the constant-field subspace.
theorem scaled_ratio_identity (a b c eps s r V : Rat) (hs : 0 < s) (hV : 0 < V) :
    (V * D a b c eps (hMin a b c) s r) / (V*s) =
      6*b*s/(s+r+eps) + 3*c*s*(s+r+2*eps)/(s+r+eps)^2 := by
  rw [integrated_identity]
  field_simp

-- marker: ratio_bound
-- For r >= s+2 eps the local ratio has an explicit O(1/r) upper bound.
theorem ratio_bound (a b c eps s r : Rat)
    (hb : 0 <= b) (hc : 0 <= c) (he : 0 < eps)
    (hs : 0 < s) (hr : 0 < r)
    (hlarge : s + 2*eps <= r) :
    (D a b c eps (hMin a b c) s r) / s <= 6*s*(b+c)/r := by
  have hden : 0 < s + r + eps := by positivity
  have hden2 : 0 < (s+r+eps)^2 := sq_pos_of_pos hden
  have hsr : s + 2*eps <= r := hlarge
  have hnum : s+r+2*eps <= 2*r := by linarith
  have hsrpos : 0 < s+r+eps := hden
  have hrnonneg : 0 <= r := le_of_lt hr
  have hterm1 : 6*b*s/(s+r+eps) <= 6*b*s/r := by
    have hA : 0 <= 6*b*s := by positivity
    have hdenlower : r <= s+r+eps := by linarith
    exact div_le_div_of_nonneg_left hA hr hdenlower
  have hterm2 : 3*c*s*(s+r+2*eps)/(s+r+eps)^2 <= 6*c*s/r := by
    have hdenlower : r <= s+r+eps := by linarith
    have hdenlower2 : r^2 <= (s+r+eps)^2 := by nlinarith
    have hratio : (s+r+2*eps)/(s+r+eps)^2 <= 2/r := by
      apply (div_le_div_iff₀ hden2 hr).2
      have hNr : (s+r+2*eps)*r <= (2*r)*r := by
        exact mul_le_mul_of_nonneg_right hnum hrnonneg
      nlinarith [hNr, hdenlower2]
    have hfactor : 0 <= 3*c*s := by positivity
    calc
      3*c*s*(s+r+2*eps)/(s+r+eps)^2 = 3*c*s * ((s+r+2*eps)/(s+r+eps)^2) := by ring
      _ <= 3*c*s * (2/r) := mul_le_mul_of_nonneg_left hratio hfactor
      _ = 6*c*s/r := by ring
  have hsum :
      6*b*s/(s+r+eps) + 3*c*s*(s+r+2*eps)/(s+r+eps)^2 <=
        6*b*s/r + 6*c*s/r := by linarith
  calc
    (D a b c eps (hMin a b c) s r) / s =
        (6*b*s^2/(s+r+eps) + 3*c*s^2*(s+r+2*eps)/(s+r+eps)^2) / s := by
          unfold D W hMin
          field_simp
          ring
    _ = 6*b*s/(s+r+eps) + 3*c*s*(s+r+2*eps)/(s+r+eps)^2 := by
          field_simp
    _ <= 6*b*s/r + 6*c*s/r := hsum
    _ = 6*s*(b+c)/r := by ring

end Tect.R195
