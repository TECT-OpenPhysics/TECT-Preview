import Mathlib

namespace Tect.R455

noncomputable def kernel (k x : ℚ) : ℕ → ℚ
  | 0 => 0
  | n + 1 => k * kernel k x n + x ^ n

theorem row_sum_step {a b k x : ℚ}
    (ha : 0 ≤ a) (hb : 0 ≤ b) (hx : 0 ≤ x) (hrow : a + b ≤ k) :
    a * x + b * x ≤ k * x := by
  have h := mul_le_mul_of_nonneg_right hrow hx
  nlinarith

theorem matrix_inf_step {a b c d k x y : ℚ}
    (ha : 0 ≤ a) (hb : 0 ≤ b) (hc : 0 ≤ c) (hd : 0 ≤ d)
    (hrow1 : a + b ≤ k) (hrow2 : c + d ≤ k)
    (hx : 0 ≤ x) (hy : 0 ≤ y) (hk : 0 ≤ k) :
    max (a * x + b * y) (c * x + d * y) ≤ k * max x y := by
  have hmax : 0 ≤ max x y := by
    exact le_trans hx (le_max_left _ _)
  have hxyx : x ≤ max x y := le_max_left _ _
  have hxyy : y ≤ max x y := le_max_right _ _
  have hfirst : a * x + b * y ≤ k * max x y := by
    calc
      a * x + b * y ≤ a * max x y + b * max x y := by
        exact add_le_add (mul_le_mul_of_nonneg_left hxyx ha)
          (mul_le_mul_of_nonneg_left hxyy hb)
      _ = (a + b) * max x y := by ring
      _ ≤ k * max x y := mul_le_mul_of_nonneg_right hrow1 hmax
  have hsecond : c * x + d * y ≤ k * max x y := by
    calc
      c * x + d * y ≤ c * max x y + d * max x y := by
        exact add_le_add (mul_le_mul_of_nonneg_left hxyx hc)
          (mul_le_mul_of_nonneg_left hxyy hd)
      _ = (c + d) * max x y := by ring
      _ ≤ k * max x y := mul_le_mul_of_nonneg_right hrow2 hmax
  exact max_le hfirst hsecond

theorem matrix_path_step {a b c d k x y : ℚ}
    (ha : 0 ≤ a) (hb : 0 ≤ b) (hc : 0 ≤ c) (hd : 0 ≤ d)
    (hrow1 : a + b ≤ k) (hrow2 : c + d ≤ k)
    (hx : 0 ≤ x) (hy : 0 ≤ y) (hk : 0 ≤ k) :
    max (a * x + b * y) (c * x + d * y) ≤ k * max x y := by
  exact matrix_inf_step ha hb hc hd hrow1 hrow2 hx hy hk

theorem kernel_step (k x : ℚ) (n : ℕ) :
    kernel k x (n + 1) = k * kernel k x n + x ^ n := by
  rfl

theorem matrix_defect_envelope_step (A D k r s : ℚ) (n : ℕ) :
    k * (A * kernel k r n + D * kernel k s n) + A * r ^ n + D * s ^ n =
      A * kernel k r (n + 1) + D * kernel k s (n + 1) := by
  simp [kernel_step]
  ring

theorem parent_decay_ratio :
    (23 / 26 : ℚ) ^ 4 = 279841 / 456976 := by
  norm_num

theorem two_base_contraction_bound {kbar s : ℚ}
    (_hk0 : 0 ≤ kbar) (hk1 : kbar < 1) (hs0 : 0 ≤ s) (hs1 : s < 1) :
    max kbar (max s ((23 / 26 : ℚ) ^ 4)) < 1 := by
  rw [max_lt_iff, max_lt_iff]
  exact ⟨hk1, hs1, by norm_num⟩

end Tect.R455
