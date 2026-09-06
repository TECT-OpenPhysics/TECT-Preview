import Mathlib

namespace Tect.PahOmc017

/- Algebraic bridge only. The compact-operator and measure arguments are
proved in the analytic certificates, not encoded by these declarations. -/

theorem labelled_count (n : Nat) : 5*(n+2)+3*n+2=2*(2*(n+2))+(4*n+4) := by omega

theorem endpoint_halves (x y z : Real) : x/2+(x+y)/2+(y+z)/2+z/2=x+y+z := by ring

theorem column_box : (2:Real)*(25/24)+33/8=149/24 := by norm_num

theorem split_box : (3:Real)*(33/8)+2*4=163/8 := by norm_num

theorem kernel_box : (149:Real)/24+163/8=319/12 := by norm_num

theorem radius_lower_positive : (0:Real)<256*Real.exp (-(319:Real)/12) := by positivity

theorem denominator_lower (delta t : Real) (hd : |delta| ≤ t) (ht : t ≤ 1/2) :
    (1:Real)/2 ≤ 1+delta := by
  have h := (abs_le.mp hd).1
  linarith

theorem ratio_identity (a e delta : Real) (h : 1+delta ≠ 0) :
    (a+e)/(1+delta)-a=(e-a*delta)/(1+delta) := by
  field_simp
  ring

theorem normalized_ratio_bound (a e delta F t : Real)
    (hF : 0 ≤ F) (ht0 : 0 ≤ t) (ht : t ≤ 1/2)
    (ha : |a| ≤ F) (he : |e| ≤ F*t) (hd : |delta| ≤ t) :
    |(a+e)/(1+delta)-a| ≤ 4*F*t := by
  have hden := denominator_lower delta t hd ht
  have hpos : 0 < 1+delta := by linarith
  rw [ratio_identity a e delta (ne_of_gt hpos), abs_div, abs_of_pos hpos]
  apply (div_le_iff₀ hpos).2
  have hnum : |e-a*delta| ≤ 2*F*t := by
    calc
      |e-a*delta| ≤ |e|+|a*delta| := abs_sub _ _
      _ = |e| + |a| * |delta| := by rw [abs_mul]
      _ ≤ F*t+F*t := add_le_add he (mul_le_mul ha hd (abs_nonneg _) hF)
      _ = 2*F*t := by ring
  have hm := mul_nonneg (mul_nonneg hF ht0) (show 0 ≤ 1+delta-1/2 by linarith)
  nlinarith

end Tect.PahOmc017
