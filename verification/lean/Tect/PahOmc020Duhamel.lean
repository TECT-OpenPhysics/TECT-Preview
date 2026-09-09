import Mathlib

namespace Tect.PahOmc020Duhamel

/- These declarations formalize only the finite arithmetic used by the
   source-local coupling envelope.  They do not assert a coupling existence,
   a Duhamel theorem on the PAH state, or any anchored-n limit. -/

def connectedTerm (a b t : ℚ) (k : ℕ) : ℚ :=
  a * b ^ k * t ^ (k + 1) / ((k + 1).factorial : ℚ)

theorem two_copy_connected_term (a b t : ℚ) (k : ℕ) :
    (2 : ℚ) ^ (k + 1) * connectedTerm a b t k =
      2 * a * (2 * b) ^ k * t ^ (k + 1) / ((k + 1).factorial : ℚ) := by
  unfold connectedTerm
  rw [show (2 : ℚ) ^ (k + 1) = 2 * 2 ^ k by rw [pow_succ]; ring]
  rw [show (2 * b) ^ k = 2 ^ k * b ^ k by rw [mul_pow]]
  ring

theorem simplex_time_integral (t : ℚ) (k : ℕ) :
    t ^ (k + 1) / ((k + 1).factorial : ℚ) =
      (t / ((k + 1 : ℕ) : ℚ)) * t ^ k / (k.factorial : ℚ) := by
  rw [Nat.factorial_succ]
  push_cast
  field_simp
  ring

theorem tail_ratio_lt_one (b t : ℚ) (d : ℕ)
    (hden : 0 < (d + 1 : ℕ)) (hnum : b * t < (d + 1 : ℚ)) :
    b * t / ((d + 1 : ℕ) : ℚ) < 1 := by
  have hdenq : (0 : ℚ) < ((d + 1 : ℕ) : ℚ) := by exact_mod_cast hden
  apply (div_lt_iff₀ hdenq).2
  simpa [mul_comm] using hnum

theorem effective_branching (b : ℕ) (h : b = 144) :
    2 * b = 288 := by omega

theorem connected_count_with_two_copies (a b : ℚ) (k : ℕ) :
    (2 : ℚ) ^ (k + 1) * (a * b ^ k) = 2 * a * (2 * b) ^ k := by
  rw [show (2 : ℚ) ^ (k + 1) = 2 * 2 ^ k by rw [pow_succ]; ring]
  rw [show (2 * b) ^ k = 2 ^ k * b ^ k by rw [mul_pow]]
  ring

end Tect.PahOmc020Duhamel
