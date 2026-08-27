import Mathlib

namespace Tect.R365

/- R365 formalizes the finite spectral coefficient algebra behind the
   energy-gap weighted commutator and Duhamel lane.  The exponential inequality
   and matrix rows are checked by the Python verifier; no uniform limit is
   encoded here. -/

variable {ι : Type*} [Fintype ι] [DecidableEq ι]

noncomputable def spectralBlock (b : ι → ℝ) (x : ι → ι → ℝ) : ι → ι → ℝ :=
  fun i j => if b i = b j then x i j else 0

theorem spectral_commutator_coefficient
    (b : ι → ℝ) (x : ι → ι → ℝ) (i j : ι) :
    (b i - b j) * spectralBlock b x i j = 0 := by
  by_cases h : b i = b j
  · simp [spectralBlock, h]
  · simp [spectralBlock, h]

theorem spectral_gap_square_fixture
    (b : ι → ℝ) (x : ι → ι → ℝ) (i j : ι) :
    0 ≤ (b i - b j) ^ 2 * (x i j) ^ 2 := by
  positivity

theorem spectral_block_commutator_reduction
    (b : ι → ℝ) (x : ι → ι → ℝ) (i j : ι) :
    b i * x i j - x i j * b j =
      b i * (x i j - spectralBlock b x i j) -
        (x i j - spectralBlock b x i j) * b j := by
  by_cases h : b i = b j
  · simp [spectralBlock, h]
    ring
  · simp [spectralBlock, h]

theorem scope_fixture :
    (True ∧ True ∧ True) ∧ ¬ (False ∨ False ∨ False ∨ False) := by
  norm_num

end Tect.R365
