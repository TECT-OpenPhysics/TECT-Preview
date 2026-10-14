import Mathlib.Analysis.SpecialFunctions.Exp
import Mathlib.MeasureTheory.Integral.IntervalIntegral.Basic
import Mathlib.Analysis.Complex.Basic
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Positivity

open MeasureTheory
namespace Tect.PahV2ReadoutFreezing

-- Parameterized bridges only. Source bounds, finite contraction, Duhamel,
-- density sandwich, Fourier orthogonality and cutoff limit remain external.

theorem generator_lipschitz_bound {ι : Type*} (s : Finset ι)
    (rate step : ι → Real) (jump : ι → Complex) (cap lip : Real)
    (hlip : 0 ≤ lip) (hr : ∀ i ∈ s, 0 ≤ rate i)
    (hc : ∀ i ∈ s, rate i ≤ cap) (hs : ∀ i ∈ s, 0 ≤ step i)
    (hj : ∀ i ∈ s, ‖jump i‖ ≤ lip * step i) :
    ‖∑ i ∈ s, (rate i : Complex) * jump i‖ ≤
      cap * lip * ∑ i ∈ s, step i := by
  calc
    ‖∑ i ∈ s, (rate i : Complex) * jump i‖
        ≤ ∑ i ∈ s, ‖(rate i : Complex) * jump i‖ := norm_sum_le _ _
    _ = ∑ i ∈ s, rate i * ‖jump i‖ := by
      apply Finset.sum_congr rfl
      intro i hi
      simp [Complex.norm_real, abs_of_nonneg (hr i hi)]
    _ ≤ ∑ i ∈ s, cap * (lip * step i) := by
      apply Finset.sum_le_sum
      intro i hi
      calc
        rate i * ‖jump i‖ ≤ rate i * (lip * step i) :=
          mul_le_mul_of_nonneg_left (hj i hi) (hr i hi)
        _ ≤ cap * (lip * step i) :=
          mul_le_mul_of_nonneg_right (hc i hi) (mul_nonneg hlip (hs i hi))
    _ = cap * lip * ∑ i ∈ s, step i := by
      simp [← Finset.mul_sum, mul_assoc]

theorem supplied_contraction_duhamel_bound
    {E : Type*} [NormedAddCommGroup E] [NormedSpace Real E]
    (curve : Real → E) (defect generator : E) (t T b : Real)
    (ht : 0 ≤ t) (hT : t ≤ T) (hb : 0 ≤ b)
    (identity : defect = ∫ u in (0 : Real)..t, curve u)
    (contract : ∀ u ∈ Set.uIoc (0 : Real) t, ‖curve u‖ ≤ ‖generator‖)
    (bound : ‖generator‖ ≤ b) : ‖defect‖ ≤ T * b := by
  rw [identity]
  have h := intervalIntegral.norm_integral_le_of_norm_le_const contract
  simp only [sub_zero, abs_of_nonneg ht] at h
  calc
    ‖∫ u in (0 : Real)..t, curve u‖ ≤ ‖generator‖ * t := h
    _ ≤ b * T := mul_le_mul bound hT ht hb
    _ = T * b := mul_comm _ _

theorem weighted_quadratic_domination {ι : Type*} (s : Finset ι)
    (w q x : ι → Real) (eta a : Real)
    (hw : ∀ i ∈ s, eta * q i ≤ w i) :
    eta * (∑ i ∈ s, q i * (x i - a)^2) ≤
      ∑ i ∈ s, w i * (x i - a)^2 := by
  calc
    eta * (∑ i ∈ s, q i * (x i - a)^2)
        = ∑ i ∈ s, (eta * q i) * (x i - a)^2 := by
          simp [Finset.mul_sum, mul_assoc]
    _ ≤ ∑ i ∈ s, w i * (x i - a)^2 := by
      apply Finset.sum_le_sum
      intro i hi
      exact mul_le_mul_of_nonneg_right (hw i hi) (sq_nonneg _)

theorem centered_square_expansion {ι : Type*} (s : Finset ι)
    (q x : ι → Real) (a v : Real)
    (hn : ∑ i ∈ s, q i = 1)
    (hm : ∑ i ∈ s, q i * x i = 0)
    (hv : ∑ i ∈ s, q i * (x i)^2 = v) :
    ∑ i ∈ s, q i * (x i-a)^2 = v + a^2 := by
  calc
    ∑ i ∈ s, q i * (x i-a)^2
        = ∑ i ∈ s, (q i * (x i)^2 - 2*a*(q i*x i) + a^2*q i) := by
          apply Finset.sum_congr rfl
          intro i _
          ring
    _ = v + a^2 := by
      simp [Finset.sum_add_distrib, Finset.sum_sub_distrib,
        ← Finset.mul_sum, hn, hm, hv]

theorem variance_lower_from_reference {ι : Type*} (s : Finset ι)
    (w q x : ι → Real) (eta a v : Real) (he : 0 ≤ eta)
    (hw : ∀ i ∈ s, eta * q i ≤ w i)
    (hn : ∑ i ∈ s, q i = 1)
    (hm : ∑ i ∈ s, q i * x i = 0)
    (hv : ∑ i ∈ s, q i * (x i)^2 = v) :
    eta * v ≤ ∑ i ∈ s, w i * (x i-a)^2 := by
  have hd := weighted_quadratic_domination s w q x eta a hw
  rw [centered_square_expansion s q x a v hn hm hv] at hd
  have hn2 := mul_nonneg he (sq_nonneg a)
  nlinarith

theorem positive_variance_certificate
    (beta B P variance : Real) (hP : 0 < P)
    (hv : Real.exp (-2 * beta * B) * (1 / (2*P)) ≤ variance) :
    0 < variance := by
  have h := mul_pos (Real.exp_pos (-2 * beta * B))
    (div_pos (by norm_num : (0 : Real) < 1) (by positivity : 0 < 2*P))
  exact lt_of_lt_of_le h hv

end Tect.PahV2ReadoutFreezing
