import Mathlib

namespace Tect.R363

/- R363 formalizes the finite conditional-expectation algebra used by the
   Python Q3 lanes.  A coordinate-diagonal multiplier cannot see the diagonal
   part of a matrix commutator; scalar centering is invisible as well.  The
   weighted Cauchy--Schwarz numerical lane and all continuum/uniformity claims
   remain outside this finite kernel. -/

variable {ι : Type*} [Fintype ι] [DecidableEq ι]

def diagonalPart (x : ι → ι → ℝ) : ι → ι → ℝ :=
  fun i j => if i = j then x i j else 0

def offDiagonalPart (x : ι → ι → ℝ) : ι → ι → ℝ :=
  fun i j => if i = j then 0 else x i j

theorem diagonal_offdiagonal_split (x : ι → ι → ℝ) (i j : ι) :
    x i j = diagonalPart x i j + offDiagonalPart x i j := by
  by_cases h : i = j
  · subst j
    simp [diagonalPart, offDiagonalPart]
  · simp [diagonalPart, offDiagonalPart, h]

theorem diagonal_multiplier_commutator_reduction
    (b : ι → ℝ) (x : ι → ι → ℝ) (i j : ι) :
    b i * x i j - x i j * b j =
      b i * offDiagonalPart x i j - offDiagonalPart x i j * b j := by
  by_cases h : i = j
  · subst j
    simp [offDiagonalPart]
    ring
  · simp [offDiagonalPart, h]

theorem scalar_centering_commutator_invariant
    (b : ι → ℝ) (x : ι → ι → ℝ) (c : ℝ) (i j : ι) :
    b i * (x i j - (if i = j then c else 0)) -
        (x i j - (if i = j then c else 0)) * b j =
      b i * x i j - x i j * b j := by
  by_cases h : i = j
  · subst j
    simp
    ring
  · simp [h]

theorem centered_offdiagonal_reduction
    (b : ι → ℝ) (x : ι → ι → ℝ) (c : ℝ) (i j : ι) :
    b i * (x i j - (if i = j then c else 0)) -
        (x i j - (if i = j then c else 0)) * b j =
      b i * offDiagonalPart (fun a d => x a d - (if a = d then c else 0)) i j -
        offDiagonalPart (fun a d => x a d - (if a = d then c else 0)) i j * b j := by
  by_cases h : i = j
  · subst j
    simp [offDiagonalPart]
    ring
  · simp [offDiagonalPart, h]

theorem scope_fixture :
    (True ∧ True ∧ True) ∧ ¬ (False ∨ False ∨ False ∨ False) := by
  norm_num

end Tect.R363
