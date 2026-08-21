import Mathlib

namespace Tect.R175

/-
  A canonical duplicated square-root basis for the six-real antipodal
  covariance block.  The analytic positivity of the A1 covariance is an
  external hypothesis; this kernel file checks only the exact block algebra
  needed to freeze one basis for R150/R174.
-/

variable {I R : Type*} [Fintype I] [DecidableEq I] [CommRing R]

def duplicate (A : Matrix I I R) : Matrix (Sum I I) (Sum I I) R :=
  Matrix.fromBlocks A 0 0 A

def complexStructure : Matrix (Sum I I) (Sum I I) R :=
  Matrix.fromBlocks 0 (-1) 1 0

theorem duplicate_transpose_mul (L : Matrix I I R) :
    duplicate L * Matrix.transpose (duplicate L) = duplicate (L * Matrix.transpose L) := by
  simp [duplicate, Matrix.fromBlocks_multiply, Matrix.fromBlocks_transpose]

theorem duplicate_commutes_with_complexStructure (L : Matrix I I R) :
    complexStructure * duplicate L = duplicate L * complexStructure := by
  simp [complexStructure, duplicate, Matrix.fromBlocks_multiply]

theorem duplicated_square_root (C L : Matrix I I R)
    (h : L * Matrix.transpose L = C) :
    duplicate L * Matrix.transpose (duplicate L) = duplicate C := by
  rw [duplicate_transpose_mul, h]

theorem duplicated_basis_preserves_complex_structure (L : Matrix I I R) :
    complexStructure * duplicate L = duplicate L * complexStructure :=
  duplicate_commutes_with_complexStructure L

end Tect.R175
