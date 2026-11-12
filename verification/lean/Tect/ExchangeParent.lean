import Mathlib.Data.Real.Basic
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring

namespace Tect.ExchangeParent

-- Parameterized real algebra only. Analytic flow and compactness stay outside.
theorem exchange_charge_cancellation (e flux : Real) :
    2 * e * flux + 2 * (-e * flux) = 0 := by
  ring

theorem reservoir_square_completion (a r e s : Real) (ha : 0 < a) :
    a*r^2-e*s*r+e^2*s^2/(4*a) = a*(r-e*s/(2*a))^2 := by
  field_simp [ne_of_gt ha]
  ring

theorem reservoir_quadratic_lower (a r e s : Real) (ha : 0 < a) :
    -(e^2*s^2/(4*a)) <= a*r^2-e*s*r := by
  have hsq := mul_nonneg (le_of_lt ha) (sq_nonneg (r-e*s/(2*a)))
  rw [<- reservoir_square_completion a r e s ha] at hsq
  linarith

theorem phase_square_completion (A x c b : Real) (hA : 0 < A) :
    A*(x-c)^2-b*x =
      A*(x-c-b/(2*A))^2-b*c-b^2/(4*A) := by
  field_simp [ne_of_gt hA]
  ring

theorem phase_lower_bound (A x c b : Real) (hA : 0 < A) :
    -b*c-b^2/(4*A) <= A*(x-c)^2-b*x := by
  rw [phase_square_completion A x c b hA]
  have hsq := mul_nonneg (le_of_lt hA) (sq_nonneg (x-c-b/(2*A)))
  linarith

theorem negative_old_coexistence_trial (c mu : Real)
    (hc : 0 < c) (hc1 : c < 1) (hm : 0 < mu) :
    -(1/2+mu)*c^2+c^4/4 < 0 := by
  have hc2 : 0 < c^2 := sq_pos_of_pos hc
  have hc2lt : c^2 < 1 := by
    nlinarith [mul_pos hc (sub_pos.mpr hc1)]
  have hc4 : c^4 < c^2 := by
    nlinarith [mul_pos hc2 (sub_pos.mpr hc2lt)]
  nlinarith [mul_pos hm hc2]

end Tect.ExchangeParent
