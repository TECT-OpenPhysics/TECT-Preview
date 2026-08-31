import Mathlib

namespace Tect.R461

/-!
  R-461 kernel-checks the algebraic core of the fixed-floor Class-II
  null-branch dichotomy.  The calculus/connected-torus step remains an
  explicit hypothesis of the surrounding result package.
 -/

def s (x₁ y₁ x₂ y₂ : Rat) : Rat := x₁ ^ 2 + y₁ ^ 2 + x₂ ^ 2 + y₂ ^ 2

def m₁ (x₁ y₁ x₂ y₂ : Rat) : Rat := 2 * (x₁ * x₂ + y₁ * y₂)
def m₂ (x₁ y₁ x₂ y₂ : Rat) : Rat := 2 * (x₁ * y₂ - y₁ * x₂)
def m₃ (x₁ y₁ x₂ y₂ : Rat) : Rat := x₁ ^ 2 + y₁ ^ 2 - x₂ ^ 2 - y₂ ^ 2

-- marker: bloch_identity
theorem bloch_identity (x₁ y₁ x₂ y₂ : Rat) :
    m₁ x₁ y₁ x₂ y₂ ^ 2 + m₂ x₁ y₁ x₂ y₂ ^ 2 + m₃ x₁ y₁ x₂ y₂ ^ 2 =
      s x₁ y₁ x₂ y₂ ^ 2 := by
  unfold m₁ m₂ m₃ s
  ring

-- marker: bloch_zero_implies_doublet_zero
theorem bloch_zero_implies_doublet_zero (x₁ y₁ x₂ y₂ : Rat)
    (h₁ : m₁ x₁ y₁ x₂ y₂ = 0)
    (h₂ : m₂ x₁ y₁ x₂ y₂ = 0)
    (h₃ : m₃ x₁ y₁ x₂ y₂ = 0) :
    x₁ = 0 ∧ y₁ = 0 ∧ x₂ = 0 ∧ y₂ = 0 := by
  have hs : s x₁ y₁ x₂ y₂ = 0 := by
    have hsq : s x₁ y₁ x₂ y₂ ^ 2 = 0 := by
      rw [← bloch_identity x₁ y₁ x₂ y₂, h₁, h₂, h₃]
      norm_num
    exact (sq_eq_zero_iff.mp hsq)
  unfold s at hs
  have h₁sq : 0 ≤ x₁ ^ 2 := sq_nonneg x₁
  have h₂sq : 0 ≤ y₁ ^ 2 := sq_nonneg y₁
  have h₃sq : 0 ≤ x₂ ^ 2 := sq_nonneg x₂
  have h₄sq : 0 ≤ y₂ ^ 2 := sq_nonneg y₂
  have hx₁ : x₁ ^ 2 = 0 := by nlinarith
  have hy₁ : y₁ ^ 2 = 0 := by nlinarith
  have hx₂ : x₂ ^ 2 = 0 := by nlinarith
  have hy₂ : y₂ ^ 2 = 0 := by nlinarith
  exact ⟨sq_eq_zero_iff.mp hx₁, sq_eq_zero_iff.mp hy₁,
    sq_eq_zero_iff.mp hx₂, sq_eq_zero_iff.mp hy₂⟩

def qForm (a b c j k : Rat) : Rat := a * j ^ 2 + 2 * b * j * k + c * k ^ 2

-- marker: positive_form_decomposition
theorem positive_form_decomposition (a b c j k : Rat) (ha : a ≠ 0) :
    qForm a b c j k = (a * j + b * k) ^ 2 / a + (a * c - b ^ 2) * k ^ 2 / a := by
  unfold qForm
  field_simp
  ring

-- marker: positive_form_zero
theorem positive_form_zero (a b c j k : Rat)
    (ha : 0 < a) (hdet : 0 < a * c - b ^ 2)
    (hform : qForm a b c j k = 0) :
    j = 0 ∧ k = 0 := by
  have ha0 : a ≠ 0 := ne_of_gt ha
  rw [positive_form_decomposition a b c j k ha0] at hform
  have hfirst : 0 ≤ (a * j + b * k) ^ 2 / a := by positivity
  have hsecond : 0 ≤ (a * c - b ^ 2) * k ^ 2 / a := by positivity
  have hkterm : (a * c - b ^ 2) * k ^ 2 / a = 0 := by nlinarith
  have hk_sq : k ^ 2 = 0 := by
    have hcoef : 0 < (a * c - b ^ 2) / a := div_pos hdet ha
    have hcoef_ne : (a * c - b ^ 2) / a ≠ 0 := ne_of_gt hcoef
    have hprod : ((a * c - b ^ 2) / a) * k ^ 2 = 0 := by
      calc
        ((a * c - b ^ 2) / a) * k ^ 2 = (a * c - b ^ 2) * k ^ 2 / a := by ring
        _ = 0 := hkterm
    exact (mul_eq_zero.mp hprod).resolve_left hcoef_ne
  have hk : k = 0 := sq_eq_zero_iff.mp hk_sq
  have hjterm : (a * j + b * k) ^ 2 / a = 0 := by nlinarith
  have hj_sq : (a * j + b * k) ^ 2 = 0 := by
    have hprod : (a * j + b * k) ^ 2 = 0 := by
      field_simp [ha0] at hjterm
      simpa using hjterm
    exact hprod
  have hjlin : a * j + b * k = 0 := sq_eq_zero_iff.mp hj_sq
  have haj : a * j = 0 := by simpa [hk] using hjlin
  have hj : j = 0 := (mul_eq_zero.mp haj).resolve_left (ne_of_gt ha)
  exact ⟨hj, hk⟩

-- marker: fixed_floor_denominator_positive
theorem fixed_floor_denominator_positive (rho eps : Rat)
    (hrho : 0 ≤ rho) (heps : 0 < eps) : 0 < rho + eps := by positivity

-- marker: nonzero_bloch_coordinate_has_nonzero_q
theorem nonzero_bloch_coordinate_has_nonzero_q (m rho eps : Rat)
    (hm : m ≠ 0) (hrho : 0 ≤ rho) (heps : 0 < eps) :
    m / (rho + eps) ≠ 0 := by
  have hden : rho + eps ≠ 0 := ne_of_gt (fixed_floor_denominator_positive rho eps hrho heps)
  exact div_ne_zero hm hden

end Tect.R461
