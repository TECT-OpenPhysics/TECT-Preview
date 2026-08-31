import Mathlib

namespace Tect.R463

/-!
  R-463 formalises the local active-branch tube metric interface.  The
  bounded-grid entropy numbers, field correlations, and flat-direction
  interpretation remain outside this algebraic kernel.
 -/

def qForm (a b c x y : Rat) : Rat :=
  a * x ^ 2 + 2 * b * x * y + c * y ^ 2

def activeEnergy2 (a b c kappa x y u₁ u₂ u₃ : Rat) : Rat :=
  qForm a b c x y + kappa * (u₁ ^ 2 + u₂ ^ 2 + u₃ ^ 2)

def tubeMetric (lambda kappa x y u₁ u₂ u₃ : Rat) : Rat :=
  lambda * (x ^ 2 + y ^ 2) + kappa * (u₁ ^ 2 + u₂ ^ 2 + u₃ ^ 2)

def flatEnergy (_f₁ _f₂ : Rat) : Rat := 0

-- marker: radial_gap_identity
theorem radial_gap_identity (a b c x y : Rat) :
    (a + c) * (qForm a b c x y) - (a * c - b ^ 2) * (x ^ 2 + y ^ 2) =
      (a * x + b * y) ^ 2 + (b * x + c * y) ^ 2 := by
  unfold qForm
  ring

-- marker: radial_lower_bound
theorem radial_lower_bound (a b c x y : Rat)
    (ht : 0 < a + c) (_hdet : 0 ≤ a * c - b ^ 2) :
    (a * c - b ^ 2) / (a + c) * (x ^ 2 + y ^ 2) ≤ qForm a b c x y := by
  have hsq : 0 ≤ (a * x + b * y) ^ 2 + (b * x + c * y) ^ 2 :=
    add_nonneg (sq_nonneg _) (sq_nonneg _)
  have hmain : (a * c - b ^ 2) * (x ^ 2 + y ^ 2) ≤
      (a + c) * qForm a b c x y := by
    nlinarith [radial_gap_identity a b c x y]
  have hdiv : (a * c - b ^ 2) * (x ^ 2 + y ^ 2) / (a + c) ≤
      ((a + c) * qForm a b c x y) / (a + c) :=
    (div_le_div_iff_of_pos_right ht).2 hmain
  calc
    (a * c - b ^ 2) / (a + c) * (x ^ 2 + y ^ 2) =
        (a * c - b ^ 2) * (x ^ 2 + y ^ 2) / (a + c) := by ring
    _ ≤ ((a + c) * qForm a b c x y) / (a + c) := hdiv
    _ = qForm a b c x y := by field_simp

-- marker: active_tube_domination
theorem active_tube_domination (a b c lambda kappa mu x y u₁ u₂ u₃ : Rat)
    (ht : 0 < a + c) (hdet : 0 ≤ a * c - b ^ 2)
    (hlambda : lambda ≤ (a * c - b ^ 2) / (a + c))
    (hmu : mu ≤ kappa) :
    tubeMetric lambda mu x y u₁ u₂ u₃ ≤ activeEnergy2 a b c kappa x y u₁ u₂ u₃ := by
  have hradial := radial_lower_bound a b c x y ht hdet
  have hxy : 0 ≤ x ^ 2 + y ^ 2 := add_nonneg (sq_nonneg _) (sq_nonneg _)
  have hu : 0 ≤ u₁ ^ 2 + u₂ ^ 2 + u₃ ^ 2 := by positivity
  have hradial_scaled : lambda * (x ^ 2 + y ^ 2) ≤
      (a * c - b ^ 2) / (a + c) * (x ^ 2 + y ^ 2) :=
    mul_le_mul_of_nonneg_right hlambda hxy
  have hangular_scaled : mu * (u₁ ^ 2 + u₂ ^ 2 + u₃ ^ 2) ≤
      kappa * (u₁ ^ 2 + u₂ ^ 2 + u₃ ^ 2) :=
    mul_le_mul_of_nonneg_right hmu hu
  unfold tubeMetric activeEnergy2
  nlinarith

-- marker: flat_zero_energy
theorem flat_zero_energy (f₁ f₂ : Rat) : flatEnergy f₁ f₂ = 0 := by
  rfl

end Tect.R463
