import Mathlib

namespace Tect.PahOmc020Pathword

/- The PAH certificate supplies the measure-theoretic change of variables.
   These declarations check only the exact algebraic transport and simplex
   ratio used by the path-word envelope; they do not formalize a process or a
   varying-Hilbert-space limit. -/

theorem two_step_square_transport (p0 p1 p2 m1 m2 : ℚ)
    (hp0 : p0 ≠ 0) (hp1 : p1 ≠ 0) :
    p0 * (m1 ^ 2 * (p1 / p0)) * (m2 ^ 2 * (p2 / p1)) =
      p2 * m1 ^ 2 * m2 ^ 2 := by
  field_simp [hp0, hp1]

theorem two_step_mobility_product_le_one (m1 m2 : ℚ)
    (hm1 : 0 ≤ m1) (hm1' : m1 ≤ 1)
    (hm2 : 0 ≤ m2) (hm2' : m2 ≤ 1) :
    m1 ^ 2 * m2 ^ 2 ≤ 1 := by
  have h1 : m1 ^ 2 ≤ 1 := by nlinarith
  have h2 : m2 ^ 2 ≤ 1 := by nlinarith
  have h1n : 0 ≤ m1 ^ 2 := sq_nonneg m1
  have hprod : m1 ^ 2 * m2 ^ 2 ≤ m1 ^ 2 := by
    exact (mul_le_mul_of_nonneg_left h2 h1n).trans_eq (by ring)
  exact hprod.trans h1

theorem two_step_stationary_mass_le_terminal (p0 p1 p2 m1 m2 : ℚ)
    (hp0 : p0 ≠ 0) (hp1 : p1 ≠ 0) (hp2 : 0 ≤ p2)
    (hm1 : 0 ≤ m1) (hm1' : m1 ≤ 1)
    (hm2 : 0 ≤ m2) (hm2' : m2 ≤ 1) :
    p0 * (m1 ^ 2 * (p1 / p0)) * (m2 ^ 2 * (p2 / p1)) ≤ p2 := by
  rw [two_step_square_transport p0 p1 p2 m1 m2 hp0 hp1]
  have hprod := two_step_mobility_product_le_one m1 m2 hm1 hm1' hm2 hm2'
  simpa [mul_assoc] using (mul_le_mul_of_nonneg_left hprod hp2)

def wordTerm (a b t : ℚ) (k : ℕ) : ℚ :=
  a * b ^ k * t ^ k / (k.factorial : ℚ)

theorem word_term_succ_ratio (a b t : ℚ) (k : ℕ) :
    wordTerm a b t (k + 1) =
      (b * t / ((k + 1 : ℕ) : ℚ)) * wordTerm a b t k := by
  unfold wordTerm
  rw [Nat.factorial_succ]
  push_cast
  field_simp
  ring

end Tect.PahOmc020Pathword
