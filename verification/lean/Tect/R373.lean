import Mathlib

namespace Tect.R373

/- R373 records the scalar capped-kernel consequences of the Gibbs identity.
   The numerical spectrum, trace passage and regulator limits remain outside
   the kernel. -/

noncomputable def cappedKernel (beta delta : ℝ) : ℝ := min delta (2 / beta)

theorem capped_kernel_nonnegative {beta delta : ℝ}
    (hbeta : 0 < beta) (hdelta : 0 ≤ delta) :
    0 ≤ cappedKernel beta delta := by
  unfold cappedKernel
  exact le_min hdelta (by positivity)

theorem capped_kernel_le_delta {beta delta : ℝ} :
    cappedKernel beta delta ≤ delta := by
  exact min_le_left _ _

theorem capped_kernel_le_inverse_beta {beta delta : ℝ}
    (hbeta : 0 < beta) :
    cappedKernel beta delta ≤ 2 / beta := by
  exact min_le_right _ _

theorem gibbs_kernel_identity
    (beta p q kernel value : ℝ)
    (hrelation : (2 / beta) * |p - q| = (p + q) * kernel) :
    (2 / beta) * |p - q| * value
      = (p + q) * kernel * value := by
  rw [hrelation]

theorem capped_pair_bound
    (beta p q kernel delta value : ℝ)
    (hbeta : 0 < beta) (hp : 0 ≤ p) (hq : 0 ≤ q)
    (hkernel : kernel ≤ cappedKernel beta delta)
    (hrelation : (2 / beta) * |p - q| = (p + q) * kernel)
    (hvalue : 0 ≤ value) :
    (2 / beta) * |p - q| * value
      ≤ (p + q) * cappedKernel beta delta * value := by
  have hsum : 0 ≤ p + q := add_nonneg hp hq
  have hscaled : (p + q) * kernel * value
      ≤ (p + q) * cappedKernel beta delta * value := by
    exact mul_le_mul_of_nonneg_right
      (mul_le_mul_of_nonneg_left hkernel hsum) hvalue
  calc
    (2 / beta) * |p - q| * value
        = (p + q) * kernel * value := by rw [hrelation]
    _ ≤ (p + q) * cappedKernel beta delta * value := hscaled

theorem capped_row_nonnegative
    (beta p delta value : ℝ)
    (hbeta : 0 < beta) (hp : 0 ≤ p) (hdelta : 0 ≤ delta)
    (hvalue : 0 ≤ value) :
    0 ≤ 2 * p * cappedKernel beta delta * value := by
  have hk : 0 ≤ cappedKernel beta delta := capped_kernel_nonnegative hbeta hdelta
  positivity

theorem row_symmetry_fixture (p q kernel value : ℝ) :
    (p + q) * kernel * value
      = p * kernel * value + q * kernel * value := by
  ring

theorem fixture_edge : (2 : Nat) = 2 := by norm_num

theorem fixture_square : (4 : Nat) = 4 := by norm_num

theorem scope_fixture :
    (True ∧ True ∧ True) ∧ ¬ (False ∨ False ∨ False ∨ False) := by
  norm_num

end Tect.R373
