import Mathlib

namespace Tect.R350

theorem contraction_bond_envelope
    (c lambda x y u v S : Rat)
    (hc : 0 ≤ c)
    (hl : 0 ≤ lambda)
    (hu : u ^ 2 ≤ x ^ 2)
    (hv : v ^ 2 ≤ y ^ 2)
    (hS : 1 + x ^ 4 + y ^ 4 ≤ S)
    (hBxy : c * (x - y) ^ 2 / 2 + lambda * (x - y) ^ 2 * (x ^ 2 + y ^ 2) / 4 ≤ (c + lambda) * S)
    (hBuv : c * (u - v) ^ 2 / 2 + lambda * (u - v) ^ 2 * (u ^ 2 + v ^ 2) / 4 ≤ (c + lambda) * S) :
    (c * (x - y) ^ 2 / 2 + lambda * (x - y) ^ 2 * (x ^ 2 + y ^ 2) / 4
      - (c * (u - v) ^ 2 / 2 + lambda * (u - v) ^ 2 * (u ^ 2 + v ^ 2) / 4)) ^ 2
      ≤ (2 * (c + lambda) * S) ^ 2 := by
  have hxy : 0 ≤ c * (x - y) ^ 2 / 2 + lambda * (x - y) ^ 2 * (x ^ 2 + y ^ 2) / 4 := by positivity
  have huv : 0 ≤ c * (u - v) ^ 2 / 2 + lambda * (u - v) ^ 2 * (u ^ 2 + v ^ 2) / 4 := by positivity
  nlinarith [sq_nonneg ((c * (x - y) ^ 2 / 2 + lambda * (x - y) ^ 2 * (x ^ 2 + y ^ 2) / 4) - (c * (u - v) ^ 2 / 2 + lambda * (u - v) ^ 2 * (u ^ 2 + v ^ 2) / 4))]

theorem onsite_shift_tail_envelope
    (g r x y kp : Rat)
    (hg : 0 < g)
    (hkp : 0 ≤ kp)
    (hlocal : 1 + x ^ 4 + y ^ 4 ≤ (8 / g) * kp) :
    (1 + x ^ 4 + y ^ 4) ^ 4 ≤ ((8 / g) * kp) ^ 4 := by
  have hleft : 0 ≤ 1 + x ^ 4 + y ^ 4 := by positivity
  exact pow_le_pow_left₀ hleft hlocal 4

theorem local_tail_fourth_envelope
    (c lambda g k t : Rat)
    (hc : 0 ≤ c)
    (hl : 0 ≤ lambda)
    (hg : 0 < g)
    (hkt : 0 ≤ k)
    (ht_nonneg : 0 ≤ t)
    (ht : t ≤ (16 * (c + lambda) / g) * k) :
    t ^ 4 ≤ (16 * (c + lambda) / g) ^ 4 * k ^ 4 := by
  have hcoef : 0 ≤ 16 * (c + lambda) / g := by positivity
  have hright : 0 ≤ (16 * (c + lambda) / g) * k := mul_nonneg hcoef hkt
  have hpow := pow_le_pow_left₀ ht_nonneg ht 4
  simpa [mul_pow] using hpow

end Tect.R350
