import Mathlib

namespace Tect.R340

open scoped ComplexConjugate

theorem finite_complex_gram_entry_perturbation {iota kappa : Type*} [Fintype kappa]
    [DecidableEq kappa] (f g : iota -> kappa -> Complex) (i j : iota) :
    ‖(Finset.univ.sum (fun k => conj (f i k) * f j k)) -
      (Finset.univ.sum (fun k => conj (g i k) * g j k))‖ <=
      (Finset.univ.sum (fun k => ‖f i k - g i k‖ * ‖f j k‖)) +
      (Finset.univ.sum (fun k => ‖g i k‖ * ‖f j k - g j k‖)) := by
  have hsum :
      (Finset.univ.sum (fun k => conj (f i k) * f j k)) -
        (Finset.univ.sum (fun k => conj (g i k) * g j k)) =
      Finset.univ.sum (fun k => conj (f i k) * f j k - conj (g i k) * g j k) :=
    (Finset.sum_sub_distrib _ _).symm
  rw [hsum]
  calc
    ‖Finset.univ.sum (fun k => conj (f i k) * f j k - conj (g i k) * g j k)‖ <=
        Finset.univ.sum (fun k => ‖conj (f i k) * f j k - conj (g i k) * g j k‖) :=
      norm_sum_le _ _
    _ <= Finset.univ.sum
        (fun k => ‖f i k - g i k‖ * ‖f j k‖ +
          ‖g i k‖ * ‖f j k - g j k‖) := by
      apply Finset.sum_le_sum
      intro k hk
      calc
        ‖conj (f i k) * f j k - conj (g i k) * g j k‖ =
            ‖conj (f i k - g i k) * f j k +
              conj (g i k) * (f j k - g j k)‖ := by
              congr 1
              simp only [map_sub]
              ring_nf
        _ <= ‖conj (f i k - g i k) * f j k‖ +
            ‖conj (g i k) * (f j k - g j k)‖ := norm_add_le _ _
        _ = ‖f i k - g i k‖ * ‖f j k‖ +
            ‖g i k‖ * ‖f j k - g j k‖ := by
              rw [norm_mul, norm_mul, Complex.norm_conj, Complex.norm_conj]
    _ = (Finset.univ.sum (fun k => ‖f i k - g i k‖ * ‖f j k‖)) +
        (Finset.univ.sum (fun k => ‖g i k‖ * ‖f j k - g j k‖)) := by
      rw [Finset.sum_add_distrib]

end Tect.R340
