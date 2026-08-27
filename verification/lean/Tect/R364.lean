import Mathlib

namespace Tect.R364

/- R364 formalizes the finite spectral pinching kernel used by the R-364
   Python lanes.  Equal values of b represent one bond-energy eigenspace; the
   resulting off-block part is exactly the only part seen by the diagonal
   commutator.  Weighted norm monotonicity and all continuum/uniformity claims
   remain outside this finite kernel. -/

variable {ι : Type*} [Fintype ι] [DecidableEq ι]

noncomputable def spectralOffDiagonal (b : ι → ℝ) (x : ι → ι → ℝ) : ι → ι → ℝ :=
  fun i j => if b i = b j then 0 else x i j

noncomputable def spectralBlockPart (b : ι → ℝ) (x : ι → ι → ℝ) : ι → ι → ℝ :=
  fun i j => if b i = b j then x i j else 0

theorem spectral_block_offdiagonal_split
    (b : ι → ℝ) (x : ι → ι → ℝ) (i j : ι) :
    x i j = spectralBlockPart b x i j + spectralOffDiagonal b x i j := by
  by_cases h : b i = b j
  · simp [spectralBlockPart, spectralOffDiagonal, h]
  · simp [spectralBlockPart, spectralOffDiagonal, h]

theorem spectral_offdiagonal_reduction
    (b : ι → ℝ) (x : ι → ι → ℝ) (i j : ι) :
    b i * x i j - x i j * b j =
      b i * spectralOffDiagonal b x i j -
        spectralOffDiagonal b x i j * b j := by
  by_cases h : b i = b j
  · simp [spectralOffDiagonal, h]
    ring
  · simp [spectralOffDiagonal, h]

theorem spectral_scalar_centering
    (b : ι → ℝ) (x : ι → ι → ℝ) (c : ℝ) (i j : ι) :
    b i * (x i j - (if b i = b j then c else 0)) -
        (x i j - (if b i = b j then c else 0)) * b j =
      b i * x i j - x i j * b j := by
  by_cases h : b i = b j
  · simp [h]
    ring
  · simp [h]

theorem spectral_block_disjoint
    (b : ι → ℝ) (x : ι → ι → ℝ) (i j : ι) :
    spectralBlockPart b x i j * spectralOffDiagonal b x i j = 0 := by
  by_cases h : b i = b j
  · simp [spectralBlockPart, spectralOffDiagonal, h]
  · simp [spectralBlockPart, spectralOffDiagonal, h]

theorem scope_fixture :
    (True ∧ True ∧ True) ∧ ¬ (False ∨ False ∨ False ∨ False) := by
  norm_num

end Tect.R364
