import Mathlib

namespace Tect.R341

theorem normalized_product_sum_lift {ι κ : Type*} [Fintype ι] [Fintype κ]
    [Nonempty ι] [Nonempty κ] (f g : ι → ℝ) :
    (1 / ((Fintype.card ι : ℝ) * Fintype.card κ)) *
        (∑ p : ι × κ, f p.1 * g p.1) =
      (1 / (Fintype.card ι : ℝ)) * (∑ i : ι, f i * g i) := by
  rw [Fintype.sum_prod_type]
  simp only [Finset.sum_const, Finset.card_univ]
  field_simp
  simp [nsmul_eq_mul]
  rw [← Finset.mul_sum]

end Tect.R341
