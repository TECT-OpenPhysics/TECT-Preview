import Mathlib

namespace Tect.R503

/- A conditional finite-sector error bridge for PAH-OMC-014.  The weights and
   component values are variables supplied by a future source-owned packet;
   this file neither chooses a sector law nor asserts a PAH limit. -/

def mixture {ι : Type*} [Fintype ι] (w a : ι → ℝ) : ℝ :=
  ∑ i, w i * a i

theorem finite_mixture_difference_bound
    {ι : Type*} [Fintype ι]
    (w₁ w₂ a₁ a₂ : ι → ℝ)
    (e_w e_a C : ℝ)
    (h_w : ∀ i, |w₁ i - w₂ i| ≤ e_w)
    (h_a : ∀ i, |a₁ i - a₂ i| ≤ e_a)
    (h_C : ∀ i, |a₂ i| ≤ C)
    (h_w₁ : ∀ i, |w₁ i| ≤ 1)
    (he_w : 0 ≤ e_w) :
    |mixture w₁ a₁ - mixture w₂ a₂| ≤
      (Fintype.card ι : ℝ) * (C * e_w + e_a) := by
  classical
  unfold mixture
  rw [← Finset.sum_sub_distrib]
  calc
    |∑ i, (w₁ i * a₁ i - w₂ i * a₂ i)|
        ≤ ∑ i, |w₁ i * a₁ i - w₂ i * a₂ i| := by
          exact Finset.abs_sum_le_sum_abs (fun i => w₁ i * a₁ i - w₂ i * a₂ i) Finset.univ
    _ ≤ ∑ i, (C * e_w + e_a) := by
      apply Finset.sum_le_sum
      intro i hi
      calc
        |w₁ i * a₁ i - w₂ i * a₂ i|
            = |(w₁ i - w₂ i) * a₂ i + w₁ i * (a₁ i - a₂ i)| := by
                congr 1
                ring
        _ ≤ |(w₁ i - w₂ i) * a₂ i| + |w₁ i * (a₁ i - a₂ i)| := by
              exact abs_add_le _ _
        _ = |w₁ i - w₂ i| * |a₂ i| + |w₁ i| * |a₁ i - a₂ i| := by
              rw [abs_mul, abs_mul]
        _ ≤ C * e_w + e_a := by
              have hfirst : |w₁ i - w₂ i| * |a₂ i| ≤ e_w * C := by
                exact mul_le_mul (h_w i) (h_C i) (abs_nonneg _) he_w
              have hsecond : |w₁ i| * |a₁ i - a₂ i| ≤ e_a := by
                have hmul := mul_le_mul (h_w₁ i) (h_a i) (abs_nonneg _) (by linarith)
                simpa using hmul
              nlinarith [hfirst, hsecond]
    _ = (Fintype.card ι : ℝ) * (C * e_w + e_a) := by
          simp [Finset.sum_const, add_mul, mul_comm, mul_assoc]

end Tect.R503
