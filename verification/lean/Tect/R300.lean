import Mathlib

namespace Tect.R300

/- R300 formalizes the exact scalar polynomial envelope behind EXP-001129.
   It does not formalize unbounded operators, quadratic-form closures, or
   thermodynamic limits. -/

def bond (x y : Rat) : Rat :=
  (3 / 5 : Rat) * (x - y)^2 / 2 + (1 / 10 : Rat) * (x - y)^2 * (x^2 + y^2) / 4

def coordinateMajorant (x y : Rat) : Rat :=
  (3 / 5 : Rat) * (x^2 + y^2) + (1 / 10 : Rat) * (x^4 + y^4)

def auxiliary (x p : Rat) : Rat := p^2 / 2 + (3 / 5 : Rat) * x^4 / 4

def onsite (x p : Rat) : Rat := p^2 / 2 - x^2 / 2 + (3 / 5 : Rat) * x^4 / 4

theorem bond_quartic_domination (x y : Rat) :
    bond x y ≤ coordinateMajorant x y := by
  have hxy : 0 ≤ (x^2 + y^2) * (x + y)^2 := by positivity
  have hquartic : (x - y)^2 * (x^2 + y^2) ≤ 2 * (x^2 + y^2)^2 := by
    nlinarith [hxy]
  have hsum : (x^2 + y^2)^2 ≤ 2 * (x^4 + y^4) := by
    nlinarith [sq_nonneg (x^2 - y^2)]
  unfold bond coordinateMajorant
  ring_nf at hquartic hsum ⊢
  nlinarith [hquartic, hsum]

theorem single_quartic_domination (x : Rat) :
    (3 / 5 : Rat) * x^2 + (1 / 10 : Rat) * x^4 ≤
      (5 / 3 : Rat) * ((3 / 5 : Rat) * x^4 / 4) + 3 / 5 := by
  have h := sq_nonneg (x^2 - 2)
  nlinarith [h]

theorem onsite_square_completion (x p : Rat) :
    auxiliary x p ≤ 2 * onsite x p + 5 / 3 := by
  unfold auxiliary onsite
  have hp := sq_nonneg p
  have hx := sq_nonneg (x^2 - 10 / 3)
  nlinarith [hp, hx]

theorem coordinate_to_auxiliary (x y p q : Rat) :
    coordinateMajorant x y ≤ (5 / 3 : Rat) * (auxiliary x p + auxiliary y q) + 6 / 5 := by
  have hx := single_quartic_domination x
  have hy := single_quartic_domination y
  have hp := sq_nonneg p
  have hq := sq_nonneg q
  unfold coordinateMajorant auxiliary at *
  nlinarith [hx, hy, hp, hq]

theorem full_bond_form_envelope (x y p q : Rat) :
    bond x y ≤ (10 / 3 : Rat) * (onsite x p + onsite y q) + 304 / 45 := by
  calc
    bond x y ≤ coordinateMajorant x y := bond_quartic_domination x y
    _ ≤ (5 / 3 : Rat) * (auxiliary x p + auxiliary y q) + 6 / 5 := coordinate_to_auxiliary x y p q
    _ ≤ (5 / 3 : Rat) * (2 * (onsite x p + onsite y q) + 10 / 3) + 6 / 5 := by
      have hx := onsite_square_completion x p
      have hy := onsite_square_completion y q
      nlinarith [hx, hy]
    _ = (10 / 3 : Rat) * (onsite x p + onsite y q) + 304 / 45 := by
      ring

theorem envelope_constants :
    (1 + 4 * (1 / 10 : Rat) / (3 / 5 : Rat)) = 5 / 3 ∧
      (5 / 3 : Rat) * 2 * (5 / 3) + 2 * (3 / 5 : Rat)^2 / (3 / 5) = 304 / 45 := by
  norm_num

theorem scope_fixture :
    (True ∧ True ∧ True) ∧ ¬ False := by
  norm_num

end Tect.R300
