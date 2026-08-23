import Mathlib

namespace Tect.R205

/-!
  Finite projected-root cross-check.  The support filtration is a candidate
  on a finite Fourier slice; it is not a production A1/QFT owner.
-/

def Supported (S : Finset (Fin 16)) (f : Fin 16 → ℂ) : Prop :=
  ∀ k, k ∉ S → f k = 0

theorem diagonal_preserves_support {S : Finset (Fin 16)}
    {a f : Fin 16 → ℂ} (hf : Supported S f) :
    Supported S (fun k => a k * f k) := by
  intro k hk
  simp [hf k hk]

theorem support_levels_nested :
    ({1, 2} : Finset (Fin 16)) ⊆ ({15, 0, 1, 2, 3, 4} : Finset (Fin 16)) := by
  intro k hk
  simp only [Finset.mem_insert, Finset.mem_singleton] at hk ⊢
  rcases hk with rfl | rfl <;> decide

theorem level_one_is_proper :
    ({15, 0, 1, 2, 3, 4} : Finset (Fin 16)) ≠ Finset.univ := by
  decide

theorem level_two_is_full :
    ({0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15} : Finset (Fin 16))
      = Finset.univ := by
  decide

theorem quadratic_core_lower_bound :
    (4740336473 : ℚ) / 10000000000
      - ((-9252754126 : ℚ) / 10000000000)^2 / (4 * (1 : ℚ))
      = (26000000000947494031 : ℚ) / 100000000000000000000 := by
  norm_num

theorem quadratic_core_lower_bound_positive :
    (0 : ℚ) < (26000000000947494031 : ℚ) / 100000000000000000000 := by
  norm_num

end Tect.R205
