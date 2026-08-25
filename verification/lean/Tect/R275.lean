import Mathlib

namespace Tect.R275

/- Exact rational fixtures for EXP-001094.  The propositions encode the
   finite truncated-CCR coefficient and the scaling condition only.  They do
   not formalize infinite-dimensional domains, Q3 Gibbs limits, or QFT. -/

def defectCoefficient (n : Rat) : Rat := -n

def squaredDefect (n : Rat) : Rat := n * n

def topAmplitude (n : Rat) (power : Nat) : Rat := 1 / n ^ power

def scaledDefectAmplitude (n : Rat) (power : Nat) : Rat := n * topAmplitude n power

theorem defect_n_two : defectCoefficient 2 = (-2 : Rat) := by
  norm_num [defectCoefficient]

theorem defect_n_four : defectCoefficient 4 = (-4 : Rat) := by
  norm_num [defectCoefficient]

theorem squared_defect_n_four : squaredDefect 4 = (16 : Rat) := by
  norm_num [squaredDefect]

theorem squared_defect_n_eight : squaredDefect 8 = (64 : Rat) := by
  norm_num [squaredDefect]

theorem inverse_tail_scaled_defect : scaledDefectAmplitude 8 2 = (1 / 8 : Rat) := by
  norm_num [scaledDefectAmplitude, topAmplitude]

theorem stronger_inverse_tail_scaled_defect : scaledDefectAmplitude 8 3 = (1 / 64 : Rat) := by
  norm_num [scaledDefectAmplitude, topAmplitude]

theorem boundary_scope :
    (defectCoefficient 4 = (-4 : Rat) ∧ squaredDefect 4 = (16 : Rat)) ∧
    (scaledDefectAmplitude 8 2 = (1 / 8 : Rat) ∧
      scaledDefectAmplitude 8 3 = (1 / 64 : Rat)) := by
  norm_num [defectCoefficient, squaredDefect, scaledDefectAmplitude, topAmplitude]

end Tect.R275
