import Mathlib

namespace Tect.R339

theorem finite_gram_entry_perturbation {iota kappa : Type*} [Fintype kappa]
    [DecidableEq kappa] (f g : iota -> kappa -> Real) (i j : iota) :
    |(Finset.univ.sum (fun k => f i k * f j k)) -
      (Finset.univ.sum (fun k => g i k * g j k))| <=
      (Finset.univ.sum (fun k => |f i k - g i k| * |f j k|)) +
      (Finset.univ.sum (fun k => |g i k| * |f j k - g j k|)) := by
  have hsum :
      (Finset.univ.sum (fun k => f i k * f j k)) -
        (Finset.univ.sum (fun k => g i k * g j k)) =
      Finset.univ.sum (fun k => f i k * f j k - g i k * g j k) :=
    (Finset.sum_sub_distrib _ _).symm
  rw [hsum]
  calc
    |Finset.univ.sum (fun k => f i k * f j k - g i k * g j k)| <=
        Finset.univ.sum (fun k => |f i k * f j k - g i k * g j k|) :=
      Finset.abs_sum_le_sum_abs _ _
    _ <= Finset.univ.sum
        (fun k => |f i k - g i k| * |f j k| +
          |g i k| * |f j k - g j k|) := by
      apply Finset.sum_le_sum
      intro k hk
      calc
        |f i k * f j k - g i k * g j k| =
            |(f i k - g i k) * f j k + g i k * (f j k - g j k)| := by
              congr 1
              ring
        _ <= |(f i k - g i k) * f j k| +
            |g i k * (f j k - g j k)| := abs_add_le _ _
        _ = |f i k - g i k| * |f j k| +
            |g i k| * |f j k - g j k| := by
              rw [abs_mul, abs_mul]
    _ = (Finset.univ.sum (fun k => |f i k - g i k| * |f j k|)) +
        (Finset.univ.sum (fun k => |g i k| * |f j k - g j k|)) := by
      rw [Finset.sum_add_distrib]

end Tect.R339
