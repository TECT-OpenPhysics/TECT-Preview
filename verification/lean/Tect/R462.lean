import Mathlib

namespace Tect.R462

/-!
  R-462 checks the exact algebraic normal form of the active Bloch branch.
  Frame and connected-domain hypotheses stay outside this kernel file.
 -/

def qForm (a b c x y : Rat) : Rat :=
  a * x ^ 2 + 2 * b * x * y + c * y ^ 2

-- marker: normal_form_decomposition
theorem normal_form_decomposition (a b c s ds delta n₁ n₂ n₃ t₁ t₂ t₃ : Rat)
    (hn : n₁ ^ 2 + n₂ ^ 2 + n₃ ^ 2 = 1)
    (ht : n₁ * t₁ + n₂ * t₂ + n₃ * t₃ = 0) :
    qForm a b c (ds * n₁ + s * t₁) (delta * n₁ + s * t₁) +
        qForm a b c (ds * n₂ + s * t₂) (delta * n₂ + s * t₂) +
        qForm a b c (ds * n₃ + s * t₃) (delta * n₃ + s * t₃) =
      qForm a b c ds delta +
        (a + 2 * b + c) * s ^ 2 * (t₁ ^ 2 + t₂ ^ 2 + t₃ ^ 2) := by
  have hj :
      (ds * n₁ + s * t₁) ^ 2 + (ds * n₂ + s * t₂) ^ 2 +
          (ds * n₃ + s * t₃) ^ 2 =
        ds ^ 2 + s ^ 2 * (t₁ ^ 2 + t₂ ^ 2 + t₃ ^ 2) := by
    calc
      _ = ds ^ 2 * (n₁ ^ 2 + n₂ ^ 2 + n₃ ^ 2) +
          2 * ds * s * (n₁ * t₁ + n₂ * t₂ + n₃ * t₃) +
          s ^ 2 * (t₁ ^ 2 + t₂ ^ 2 + t₃ ^ 2) := by ring
      _ = ds ^ 2 + s ^ 2 * (t₁ ^ 2 + t₂ ^ 2 + t₃ ^ 2) := by rw [hn, ht]; ring
  have hk :
      (delta * n₁ + s * t₁) ^ 2 + (delta * n₂ + s * t₂) ^ 2 +
          (delta * n₃ + s * t₃) ^ 2 =
        delta ^ 2 + s ^ 2 * (t₁ ^ 2 + t₂ ^ 2 + t₃ ^ 2) := by
    calc
      _ = delta ^ 2 * (n₁ ^ 2 + n₂ ^ 2 + n₃ ^ 2) +
          2 * delta * s * (n₁ * t₁ + n₂ * t₂ + n₃ * t₃) +
          s ^ 2 * (t₁ ^ 2 + t₂ ^ 2 + t₃ ^ 2) := by ring
      _ = delta ^ 2 + s ^ 2 * (t₁ ^ 2 + t₂ ^ 2 + t₃ ^ 2) := by rw [hn, ht]; ring
  have hjk :
      (ds * n₁ + s * t₁) * (delta * n₁ + s * t₁) +
          (ds * n₂ + s * t₂) * (delta * n₂ + s * t₂) +
          (ds * n₃ + s * t₃) * (delta * n₃ + s * t₃) =
        ds * delta + s ^ 2 * (t₁ ^ 2 + t₂ ^ 2 + t₃ ^ 2) := by
    calc
      _ = ds * delta * (n₁ ^ 2 + n₂ ^ 2 + n₃ ^ 2) +
          (ds + delta) * s * (n₁ * t₁ + n₂ * t₂ + n₃ * t₃) +
          s ^ 2 * (t₁ ^ 2 + t₂ ^ 2 + t₃ ^ 2) := by ring
      _ = ds * delta + s ^ 2 * (t₁ ^ 2 + t₂ ^ 2 + t₃ ^ 2) := by rw [hn, ht]; ring
  unfold qForm
  linear_combination a * hj + 2 * b * hjk + c * hk

-- marker: angular_coefficient_positive
theorem angular_coefficient_positive (a b c : Rat)
    (ha : 0 < a) (hdet : 0 < a * c - b ^ 2) :
    0 < a + 2 * b + c := by
  have hsum : 0 < (a + b) ^ 2 + (a * c - b ^ 2) :=
    add_pos_of_nonneg_of_pos (sq_nonneg (a + b)) hdet
  have hid : (a + b) ^ 2 + (a * c - b ^ 2) = a * (a + 2 * b + c) := by
    ring
  rw [hid] at hsum
  nlinarith

-- marker: radial_form_zero
theorem radial_form_zero (a b c x y : Rat)
    (ha : 0 < a) (hdet : 0 < a * c - b ^ 2)
    (hzero : qForm a b c x y = 0) :
    x = 0 ∧ y = 0 := by
  have ha0 : a ≠ 0 := ne_of_gt ha
  have hdecomp : qForm a b c x y =
      (a * x + b * y) ^ 2 / a + (a * c - b ^ 2) * y ^ 2 / a := by
    unfold qForm
    field_simp
    ring
  rw [hdecomp] at hzero
  have hfirst : 0 ≤ (a * x + b * y) ^ 2 / a := by positivity
  have hsecond : 0 ≤ (a * c - b ^ 2) * y ^ 2 / a := by positivity
  have hyterm : (a * c - b ^ 2) * y ^ 2 / a = 0 := by nlinarith
  have hy_sq : y ^ 2 = 0 := by
    have hcoef : 0 < (a * c - b ^ 2) / a := div_pos hdet ha
    have hcoef_ne : (a * c - b ^ 2) / a ≠ 0 := ne_of_gt hcoef
    have hprod : ((a * c - b ^ 2) / a) * y ^ 2 = 0 := by
      calc
        ((a * c - b ^ 2) / a) * y ^ 2 = (a * c - b ^ 2) * y ^ 2 / a := by ring
        _ = 0 := hyterm
    exact (mul_eq_zero.mp hprod).resolve_left hcoef_ne
  have hy : y = 0 := sq_eq_zero_iff.mp hy_sq
  have hxterm : (a * x + b * y) ^ 2 / a = 0 := by nlinarith
  have hxlin : a * x + b * y = 0 := by
    have hprod : (a * x + b * y) ^ 2 = 0 := by
      field_simp [ha0] at hxterm
      simpa using hxterm
    exact sq_eq_zero_iff.mp hprod
  have hax : a * x = 0 := by simpa [hy] using hxlin
  have hx : x = 0 := (mul_eq_zero.mp hax).resolve_left (ne_of_gt ha)
  exact ⟨hx, hy⟩

-- marker: active_denominator_positive
theorem active_denominator_positive (rho eps : Rat)
    (hrho : 0 ≤ rho) (heps : 0 < eps) :
    0 < rho + eps := by
  positivity

end Tect.R462
