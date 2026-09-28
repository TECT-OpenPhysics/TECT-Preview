import Mathlib.Data.Real.Basic
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Positivity

set_option maxHeartbeats 50000

/- Conditional rational algebra only. The scalar EFT, atomic response,
   observed errors and physical identity are not encoded in this module. -/
namespace TectClockFreeFall

theorem common_mean (a b s d : ℝ) :
    ((1 + a*s*d^2) + (1 + b*s*d^2))/2 = 1 + ((a+b)/2)*s*d^2 := by ring

theorem cross_probe_null (q k c : ℝ) : q*(-k*c) + k*(q*c) = 0 := by ring

theorem coupling_sign_blind (d : ℝ) : (-d)^2 = d^2 := by ring

theorem denominator_positive (q s u : ℝ) (hq : 0 ≤ q) (hs : 0 ≤ s)
    (hu : 0 ≤ u) : 0 < 1 + q*s*u := by positivity

theorem inverse_recovers_square (q s u : ℝ) (hs : s ≠ 0)
    (hD : 1 + q*s*u ≠ 0) :
      (s*u/(1+q*s*u)) / (s*(1-q*(s*u/(1+q*s*u)))) = u := by
  have hD' : 1+u*s*q ≠ 0 := by
    convert hD using 1 <;> ring
  have h : 1-q*(s*u/(1+q*s*u)) = 1/(1+q*s*u) := by
    field_simp [hD, hD']
    <;> ring
  rw [h]
  field_simp [hs, hD, hD']
  field_simp [hD']
  <;> ring

theorem inverse_difference (q s a b : ℝ) (hs : s ≠ 0)
    (ha : 1-q*a ≠ 0) (hb : 1-q*b ≠ 0) :
    b/(s*(1-q*b)) - a/(s*(1-q*a)) =
      (b-a)/(s*(1-q*a)*(1-q*b)) := by
  have hb' : 1-b*q ≠ 0 := by simpa [mul_comm] using hb
  field_simp [hs, ha, hb]
  field_simp [hb']
  <;> ring

theorem residual_error_expansion (q k z e dq dk dz de : ℝ) :
    (q+dq)*(z+dz)+(k+dk)*(e+de)-(q*z+k*e) =
      q*dz+z*dq+dq*dz+k*de+e*dk+dk*de := by ring

end TectClockFreeFall
