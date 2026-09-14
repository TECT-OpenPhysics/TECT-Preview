import Mathlib

namespace Tect.PahV2GeneratorDefect

/- Integer reduction of the epsilon=1 aperture channel. The written proof
checks full PAH root cancellation and the immutable model-to-integer bridge.
The following statements concern every natural cutoff, not a finite table. -/

def value (M j : Nat) : Int := if j < M then 1 else 0

def ap (M j : Nat) : Int :=
  (if 0 < j then value M (j-1) - value M j else 0) +
  (if j < M then value M (j+1) - value M j else 0)

theorem endpoint_generator (M j : Nat) (hM : 1 ≤ M) (hj : j ≤ M) :
    ap M j = (if j = M then 1 else 0) - (if j+1 = M then 1 else 0) := by
  simp only [ap, value]
  split_ifs <;> omega

theorem fixed_base_pullback (M j : Nat) (hM : 1 ≤ M) (hj : j ≤ M) :
    (if j / M = 0 then (1 : Int) else 0) = value M j := by
  by_cases hlt : j < M
  · simp [value, hlt, Nat.div_eq_of_lt hlt]
  · have heq : j = M := by omega
    subst j
    have hn : M ≠ 0 := by omega
    simp [value, hn]

theorem adjacent_defect (M j : Nat) (hM : 1 ≤ M) (hj : j ≤ 2*M) :
    ap (2*M) j - ap M (j/2) =
      (if 2*M-2 ≤ j ∧ j < 2*M-1 then (1 : Int) else 0) := by
  rw [endpoint_generator (2*M) j (by omega) hj,
      endpoint_generator M (j/2) hM (by omega)]
  split_ifs <;> omega

theorem arbitrary_cutoff_witness (M : Nat) (hM : 1 ≤ M) :
    ap (2*M) (2*M-2) - ap M ((2*M-2)/2) = 1 := by
  rw [adjacent_defect M (2*M-2) hM (by omega)]
  split_ifs <;> omega

theorem unbounded_tail_witness (R : Nat) :
    ∃ r : Nat, R ≤ r ∧
      ap (2*(2^r)) (2*(2^r)-2) - ap (2^r) ((2*(2^r)-2)/2) = 1 := by
  refine ⟨R, le_refl R, arbitrary_cutoff_witness (2^R) ?_⟩
  have h : 0 < (2 : Nat)^R := by positivity
  omega

end Tect.PahV2GeneratorDefect
