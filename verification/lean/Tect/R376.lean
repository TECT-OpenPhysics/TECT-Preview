import Mathlib

namespace Tect.R376

/- R376 formalizes only the scalar cusp inequality used by the finite
   Hilbert-Schmidt functional-calculus interface.  Matrix functional calculus,
   Schatten estimates, locality and all limits remain outside this file. -/

theorem abs_value_lipschitz (x y : ℝ) :
    |abs x - abs y| ≤ |x - y| := by
  have hxy : |x| ≤ |x - y| + |y| := by
    calc
      |x| = |(x - y) + y| := by congr 1 <;> ring
      _ ≤ |x - y| + |y| := abs_add_le _ _
  have hyx : |y| ≤ |x - y| + |x| := by
    calc
      |y| = |(y - x) + x| := by congr 1 <;> ring
      _ ≤ |y - x| + |x| := abs_add_le _ _
      _ = |x - y| + |x| := by rw [abs_sub_comm]
  rw [abs_le]
  constructor <;> linarith

theorem abs_value_zero : |(0 : ℝ)| = 0 := by norm_num

theorem scope_fixture :
    (True ∧ True) ∧ ¬ (False ∨ False ∨ False) := by
  norm_num

end Tect.R376
