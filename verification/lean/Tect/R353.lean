import Mathlib

namespace Tect.R353

/-- The limiting three-word Gram quadratic form is a sum of two squares. -/
theorem gram_limit_quadratic_fixture (c0 c1 c2 : Rat) :
    c0 ^ 2 + 2 * c0 * c1 + 2 * c1 ^ 2 + 2 * c1 * c2 + c2 ^ 2 =
      (c0 + c1) ^ 2 + (c1 + c2) ^ 2 := by
  ring

/-- The limiting Gram quadratic form is nonnegative for every coefficient vector. -/
theorem gram_limit_nonnegative_fixture (c0 c1 c2 : Rat) :
    0 <= c0 ^ 2 + 2 * c0 * c1 + 2 * c1 ^ 2 + 2 * c1 * c2 + c2 ^ 2 := by
  nlinarith [sq_nonneg (c0 + c1), sq_nonneg (c1 + c2)]

/-- Adding a nonnegative diagonal sequence preserves the finite Gram positivity fixture. -/
theorem gram_sequence_nonnegative_fixture (n : Nat) (hn : 0 < n) (c0 c1 c2 : Rat) :
    0 <= c0 ^ 2 + 2 * c0 * c1 + 2 * c1 ^ 2 + 2 * c1 * c2 + c2 ^ 2 +
      (1 / (n : Rat)) * (c0 ^ 2 + c1 ^ 2 + c2 ^ 2) := by
  have hnrat : (0 : Rat) < (n : Rat) := by exact_mod_cast hn
  have hinv : (0 : Rat) <= 1 / (n : Rat) := by positivity
  nlinarith [sq_nonneg (c0 + c1), sq_nonneg (c1 + c2), sq_nonneg c0, sq_nonneg c1, sq_nonneg c2]

/-- The finite KMS complement fixture has the same value on both sides. -/
theorem kms_complement_fixture :
    (2 : Rat) + 1 / 2 = 2 + 1 / 2 := by
  norm_num

/-- The limiting KMS values agree. -/
theorem kms_limit_fixture : (2 : Rat) = 2 := by
  rfl

end Tect.R353
