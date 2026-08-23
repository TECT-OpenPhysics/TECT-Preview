import Mathlib

namespace Tect.R206

/-!
  Finite three-dimensional shell projection.  The support calculation is a
  QFT-compatible finite Fourier comparison, not a production-owner theorem.
-/

def Supported (S : Finset (Fin 16)) (f : Fin 16 → ℂ) : Prop :=
  ∀ k, k ∉ S → f k = 0

theorem diagonal_preserves_support {S : Finset (Fin 16)}
    {a f : Fin 16 → ℂ} (hf : Supported S f) :
    Supported S (fun k => a k * f k) := by
  intro k hk
  simp [hf k hk]

theorem two_coordinate_card : ({1, 15} : Finset (Fin 16)).card = 2 := by
  decide

theorem six_coordinate_card : ({1, 3, 5, 11, 13, 15} : Finset (Fin 16)).card = 6 := by
  decide

theorem eight_coordinate_card : ({1, 3, 5, 7, 9, 11, 13, 15} : Finset (Fin 16)).card = 8 := by
  decide

theorem seed_card_factor : (2 : ℕ)^3 = 8 := by
  norm_num

theorem intermediate_card_factor : (6 : ℕ)^3 = 216 := by
  norm_num

theorem endpoint_card_factor : (8 : ℕ)^3 = 512 := by
  norm_num

theorem quadratic_core_lower_bound :
    (4740336473 : ℚ) / 10000000000
      - ((-9252754126 : ℚ) / 10000000000)^2 / (4 * (1 : ℚ))
      = (26000000000947494031 : ℚ) / 100000000000000000000 := by
  norm_num

theorem quadratic_core_lower_bound_positive :
    (0 : ℚ) < (26000000000947494031 : ℚ) / 100000000000000000000 := by
  norm_num

end Tect.R206
