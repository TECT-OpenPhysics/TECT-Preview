import Mathlib

namespace Tect.PahOmc020Lyapunov

def boundaryBound (m b : ℚ) (w d : ℕ) : ℚ := m * b ^ w / b ^ d

theorem probability_bound (p m b : ℚ) (w d : ℕ)
    (hb : 0 < b) (hpath : p * b ^ d ≤ m * b ^ w) :
    p ≤ boundaryBound m b w d := by
  unfold boundaryBound
  apply (le_div_iff₀ (pow_pos hb d)).2
  exact hpath

theorem n4_bound (eta c p m b : ℚ) (w d : ℕ)
    (hc : 0 ≤ c) (hb : 0 < b)
    (heta : eta ^ 2 ≤ c * p)
    (hpath : p * b ^ d ≤ m * b ^ w) :
    eta ^ 2 ≤ c * boundaryBound m b w d := by
  have hp : p ≤ boundaryBound m b w d := probability_bound p m b w d hb hpath
  have hcp : c * p ≤ c * boundaryBound m b w d :=
    mul_le_mul_of_nonneg_left hp hc
  exact le_trans heta hcp

theorem envelope_step_decreases (m : ℚ) (b : ℚ) (w d : ℕ)
    (hm : 0 < m) (hb : 1 < b) :
    boundaryBound m b w (d + 1) < boundaryBound m b w d := by
  unfold boundaryBound
  have hb0 : 0 < b := lt_trans (by norm_num) hb
  have hpow : 0 < b ^ d := pow_pos hb0 d
  have hnum : 0 < m * b ^ w := mul_pos hm (pow_pos hb0 w)
  have hden : 0 < b ^ d * b := mul_pos hpow hb0
  have hlt : m * b ^ w / (b ^ d * b) < m * b ^ w / b ^ d := by
    apply (div_lt_div_iff₀ hden hpow).2
    have hdiff : 0 < b - 1 := sub_pos.mpr hb
    have hprod : 0 < (m * b ^ w) * b ^ d * (b - 1) :=
      mul_pos (mul_pos hnum hpow) hdiff
    nlinarith [hprod]
  simpa [pow_succ, mul_comm, mul_left_comm, mul_assoc] using hlt

theorem zero_boundary_when_zero_mass (b : ℚ) (w d : ℕ) :
    boundaryBound 0 b w d = 0 := by
  unfold boundaryBound
  simp

end Tect.PahOmc020Lyapunov
