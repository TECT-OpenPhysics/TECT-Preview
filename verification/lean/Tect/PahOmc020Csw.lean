import Mathlib

namespace Tect.PahOmc020Csw

def pi0 (m : ℚ) : ℚ := 1 / (m + 1)
def pi1 (m : ℚ) : ℚ := m / (m + 1)
def lf0 (m : ℚ) : ℚ := m * ((-1 : ℚ) - 1)
def lf1 : ℚ := 1 * ((1 : ℚ) - (-1 : ℚ))

def firstMoment (m : ℚ) : ℚ := pi0 m * m + pi1 m * 1
def dirichletEnergy (m : ℚ) : ℚ :=
  -(pi0 m * (1 : ℚ) * lf0 m + pi1 m * (-1 : ℚ) * lf1)
def generatorL2Sq (m : ℚ) : ℚ :=
  pi0 m * (lf0 m)^2 + pi1 m * (lf1)^2

theorem denominator_pos (m : ℚ) (hm : 1 ≤ m) : 0 < m + 1 := by
  linarith

theorem detailed_balance (m : ℚ) (hm : 1 ≤ m) :
    pi0 m * m = pi1 m * 1 := by
  have hne : m + 1 ≠ 0 := ne_of_gt (denominator_pos m hm)
  dsimp [pi0, pi1]
  field_simp [hne]

theorem first_moment_formula (m : ℚ) (hm : 1 ≤ m) :
    firstMoment m = 2 * m / (m + 1) := by
  have hne : m + 1 ≠ 0 := ne_of_gt (denominator_pos m hm)
  dsimp [firstMoment, pi0, pi1]
  field_simp [hne]
  ring

theorem first_moment_lt_two (m : ℚ) (hm : 1 ≤ m) : firstMoment m < 2 := by
  rw [first_moment_formula m hm]
  have hpos : 0 < m + 1 := denominator_pos m hm
  apply (div_lt_iff₀ hpos).2
  nlinarith

theorem energy_formula (m : ℚ) (hm : 1 ≤ m) :
    dirichletEnergy m = 4 * m / (m + 1) := by
  have hne : m + 1 ≠ 0 := ne_of_gt (denominator_pos m hm)
  dsimp [dirichletEnergy, pi0, pi1, lf0, lf1]
  field_simp [hne]
  ring

theorem energy_lt_four (m : ℚ) (hm : 1 ≤ m) : dirichletEnergy m < 4 := by
  rw [energy_formula m hm]
  have hpos : 0 < m + 1 := denominator_pos m hm
  apply (div_lt_iff₀ hpos).2
  nlinarith

theorem generator_l2_formula (m : ℚ) (hm : 1 ≤ m) :
    generatorL2Sq m = 4 * m := by
  have hne : m + 1 ≠ 0 := ne_of_gt (denominator_pos m hm)
  dsimp [generatorL2Sq, pi0, pi1, lf0, lf1]
  field_simp [hne]
  ring

theorem generator_l2_unbounded (b : ℚ) (hb : 0 ≤ b) :
    ∃ m : ℚ, 1 ≤ m ∧ b < generatorL2Sq m := by
  refine ⟨b + 1, ?_, ?_⟩
  · linarith
  · rw [generator_l2_formula (b + 1) (by linarith)]
    nlinarith

theorem fixed_first_moment_and_unbounded_l2 (b : ℚ) (hb : 0 ≤ b) :
    ∃ m : ℚ, 1 ≤ m ∧ firstMoment m < 2 ∧ b < generatorL2Sq m := by
  obtain ⟨m, hm, hlarge⟩ := generator_l2_unbounded b hb
  exact ⟨m, hm, first_moment_lt_two m hm, hlarge⟩

end Tect.PahOmc020Csw
