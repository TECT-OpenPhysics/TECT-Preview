import Mathlib.Data.Real.Basic
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Ring

set_option maxHeartbeats 100000

/- Conditional algebra only. No satellite estimator or empirical law is encoded. -/
namespace TectClockOrbit

theorem calibrated_clock_response (k o t : ℝ) (h : 1 + o*t ≠ 0) :
    (1+k*t)/(1+o*t)-1 = (k-o)*t/(1+o*t) := by
  have h' : 1+t*o ≠ 0 := by simpa [mul_comm] using h
  field_simp [h, h']
  <;> ring

theorem orbit_freefall_relation (q b k o t : ℝ)
    (ho : 1+o*t ≠ 0) (hb : 1+b*t ≠ 0) :
    (q+(o-b)*(q*t/(1+b*t)))*((k-o)*t/(1+o*t))
      -(k-o)*(q*t/(1+b*t)) = 0 := by
  field_simp [ho, hb]
  <;> ring

theorem common_potential_cancels (a k u : ℝ) :
    (1+a*k)*u-(1+a*k)*u = 0 := by ring

theorem different_ground_term (a k h u v : ℝ) :
    ((1+a*h)*u-(1+a*k)*v)-(1+a*k)*(u-v) = a*(h-k)*u := by ring

theorem response_error_expansion (q b k o A E da de : ℝ) :
    (q+(o-b)*(E+de))*(A+da)-(k-o)*(E+de)
      -((q+(o-b)*E)*A-(k-o)*E)
      = (q+(o-b)*E)*da+((o-b)*A-(k-o))*de+(o-b)*da*de := by ring

end TectClockOrbit
