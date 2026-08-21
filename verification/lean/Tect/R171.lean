import Mathlib

/-!
R-171 kernel cross-check.

This file formalises only the exact rational/algebraic core of the registered
A7 Class-II endpoint witness.  It deliberately does not assert the full A1
action, a covariance-normal composite, a Gibbs/Nelson estimate, a physical
empty comparison, or any continuum/thermodynamic limit.

The numerical inputs are hypotheses here.  A result package must separately
bridge them to the hash-pinned manifest; this keeps the theorem honest and
prevents a pasted derived decimal from becoming an unnoticed assumption.
-/

namespace Tect.R171

theorem bracket_numerator_identity
    {a b c eps r : Rat}
    (hden : Not (r + eps = 0)) :
    (2 * a + 4 * b * eps / (r + eps) +
        2 * c * eps ^ 2 / (r + eps) ^ 2) * (r + eps) ^ 2 =
      2 * a * r ^ 2 + 4 * eps * (a + b) * r +
        2 * eps ^ 2 * (a + 2 * b + c) := by
  field_simp [hden]
  ring

theorem bracket_positive
    {a b c eps r : Real}
    (ha : 0 < a) (hb : 0 < b) (hc : 0 < c)
    (heps : 0 < eps) (hr : r >= 0) :
    0 < 2 * a + 4 * b * eps / (r + eps) +
      2 * c * eps ^ 2 / (r + eps) ^ 2 := by
  have hden : 0 < r + eps := by linarith
  have hden_sq : 0 < (r + eps) ^ 2 := sq_pos_of_pos hden
  positivity

theorem bracket_numerator_coefficients_positive
    {a b c eps : Rat}
    (ha : 0 < a) (hb : 0 < b) (hc : 0 < c)
    (heps : 0 < eps) :
    And (0 < 2 * a)
      (And (0 < 4 * eps * (a + b))
        (0 < 2 * eps ^ 2 * (a + 2 * b + c))) := by
  constructor
  case left => positivity
  case right => constructor <;> positivity

theorem endpoint_secant_sign
    {a b c eps amp : Real} {theta : Real}
    (ha : 0 < a) (hb : 0 < b) (hc : 0 < c)
    (heps : 0 < eps) (hpoint : Not (amp * Real.sin theta = 0)) :
    0 < (amp * Real.sin theta) ^ 2 *
      (2 * a + 4 * b * eps /
        ((amp * Real.cos theta) ^ 2 + eps) +
        2 * c * eps ^ 2 /
          ((amp * Real.cos theta) ^ 2 + eps) ^ 2) := by
  have hs : (amp * Real.cos theta) ^ 2 >= 0 := sq_nonneg _
  have hbracket :
      0 < 2 * a + 4 * b * eps /
          ((amp * Real.cos theta) ^ 2 + eps) +
        2 * c * eps ^ 2 /
          ((amp * Real.cos theta) ^ 2 + eps) ^ 2 := by
    exact bracket_positive ha hb hc heps hs
  have hpref : 0 < (amp * Real.sin theta) ^ 2 := sq_pos_of_ne_zero hpoint
  positivity

end Tect.R171
