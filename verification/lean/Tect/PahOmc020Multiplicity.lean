import Mathlib

namespace Tect.PahOmc020Multiplicity

noncomputable section

/- The K=2 link signs in the frozen PAH source represent the same group
   element.  The two declarations make that coincidence explicit. -/
def zeta2Plus : ℤ := -1
def zeta2Minus : ℤ := -1

theorem zeta2_pm_coincide : zeta2Plus = zeta2Minus := by
  rfl

def linkFlip (u : Bool) : Bool := !u

theorem link_flip_involutive (u : Bool) : linkFlip (linkFlip u) = u := by
  cases u <;> rfl

/- Exact rational evaluation of the Wilson term on the existing triangular
   face: all three endpoint apertures are 1/2, so J_e=J_p=2. -/
def edgeStiffness : ℚ := 2 / ((1 / 2) + (1 / 2))
def faceStiffness : ℚ := (edgeStiffness + edgeStiffness + edgeStiffness) / 3
def wilsonDelta : ℚ := faceStiffness * (1 - (-1)) - faceStiffness * (1 - 1)
def mobilitySquare : ℚ := (1 / 2) * (1 / 2)
def midpointExponent : ℚ := -(1 : ℚ) * wilsonDelta / 2

theorem edge_stiffness_exact : edgeStiffness = 2 := by
  norm_num [edgeStiffness]

theorem face_stiffness_exact : faceStiffness = 2 := by
  norm_num [faceStiffness, edgeStiffness]

theorem wilson_delta_exact : wilsonDelta = 4 := by
  norm_num [wilsonDelta, faceStiffness, edgeStiffness]

theorem mobility_square_exact : mobilitySquare = (1 : ℚ) / 4 := by
  norm_num [mobilitySquare]

theorem midpoint_exponent_exact : midpointExponent = -2 := by
  norm_num [midpointExponent, wilsonDelta, faceStiffness, edgeStiffness]

/- f=1-Re(U_p) changes by 2 when the closed-face holonomy flips.  The
   midpoint rate has mobility 1/2 and exponent -2. -/
def oneRootContribution : ℝ := (1 / 2 : ℝ) * 2 * Real.exp (-2)
def labelledContribution : ℝ := oneRootContribution + oneRootContribution
def deduplicatedContribution : ℝ := oneRootContribution

theorem one_root_contribution_exact : oneRootContribution = Real.exp (-2) := by
  dsimp [oneRootContribution]
  ring

theorem labelled_generator_exact : labelledContribution = 2 * Real.exp (-2) := by
  rw [show labelledContribution = oneRootContribution + oneRootContribution by rfl]
  rw [one_root_contribution_exact]
  ring

theorem deduplicated_generator_exact : deduplicatedContribution = Real.exp (-2) := by
  exact one_root_contribution_exact

theorem generator_gap_exact :
    labelledContribution - deduplicatedContribution = Real.exp (-2) := by
  rw [labelled_generator_exact, deduplicated_generator_exact]
  ring

theorem generator_gap_positive :
    0 < labelledContribution - deduplicatedContribution := by
  rw [generator_gap_exact]
  exact Real.exp_pos _

theorem inverse_convention_difference :
    (2 : ℕ) ≠ 1 := by
  decide

end
end Tect.PahOmc020Multiplicity
