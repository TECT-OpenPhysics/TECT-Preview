import Mathlib

namespace Tect.R302

/- R302 checks the exact rational prerequisites for EXP-001131.  The
   semibounded Schrodinger-form representation theorem is used at its
   standard fixed-finite-graph scope; this file does not formalize that
   theorem, unbounded product domains, modular transfer, or limits. -/

def bond (x y : Rat) : Rat :=
  (3 / 5 : Rat) * (x - y)^2 / 2 + (1 / 10 : Rat) * (x - y)^2 * (x^2 + y^2) / 4

def onsite (x p : Rat) : Rat :=
  p^2 / 2 - x^2 / 2 + (3 / 5 : Rat) * x^4 / 4

def coordinateMajorant (x y : Rat) : Rat :=
  (3 / 5 : Rat) * (x^2 + y^2) + (1 / 10 : Rat) * (x^4 + y^4)

def auxiliary (x p : Rat) : Rat :=
  p^2 / 2 + (3 / 5 : Rat) * x^4 / 4

theorem onsite_lower_fixture (x p : Rat) :
    -5 / 12 ≤ onsite x p := by
  unfold onsite
  nlinarith [sq_nonneg p, sq_nonneg (x^2 - 5 / 3)]

theorem bond_nonnegative_fixture (x y : Rat) :
    0 ≤ bond x y := by
  unfold bond
  positivity

theorem bond_envelope_fixture (x y p q : Rat) :
    bond x y ≤ (10 / 3 : Rat) * (onsite x p + onsite y q) + 304 / 45 := by
  have hxy : 0 ≤ (x^2 + y^2) * (x + y)^2 := by positivity
  have hquartic : (x - y)^2 * (x^2 + y^2) ≤ 2 * (x^2 + y^2)^2 := by
    nlinarith [hxy]
  have hsum : (x^2 + y^2)^2 ≤ 2 * (x^4 + y^4) := by
    nlinarith [sq_nonneg (x^2 - y^2)]
  have hcoord : bond x y ≤ coordinateMajorant x y := by
    unfold bond coordinateMajorant
    ring_nf at hquartic hsum ⊢
    nlinarith [hquartic, hsum]
  have hsingle (z : Rat) :
      (3 / 5 : Rat) * z^2 + (1 / 10 : Rat) * z^4 ≤
        (5 / 3 : Rat) * ((3 / 5 : Rat) * z^4 / 4) + 3 / 5 := by
    have hz := sq_nonneg (z^2 - 2)
    nlinarith [hz]
  have haux : coordinateMajorant x y ≤
      (5 / 3 : Rat) * (auxiliary x p + auxiliary y q) + 6 / 5 := by
    have hx := hsingle x
    have hy := hsingle y
    have hp := sq_nonneg p
    have hq := sq_nonneg q
    unfold coordinateMajorant auxiliary at *
    nlinarith [hx, hy, hp, hq]
  have hsq : auxiliary x p + auxiliary y q ≤
      2 * (onsite x p + onsite y q) + 10 / 3 := by
    have hx := sq_nonneg (x^2 - 10 / 3)
    have hy := sq_nonneg (y^2 - 10 / 3)
    have hp := sq_nonneg p
    have hq := sq_nonneg q
    unfold auxiliary onsite at *
    nlinarith [hx, hy, hp, hq]
  calc
    bond x y ≤ coordinateMajorant x y := hcoord
    _ ≤ (5 / 3 : Rat) * (auxiliary x p + auxiliary y q) + 6 / 5 := haux
    _ ≤ (5 / 3 : Rat) * (2 * (onsite x p + onsite y q) + 10 / 3) + 6 / 5 := by
      nlinarith [hsq]
    _ = (10 / 3 : Rat) * (onsite x p + onsite y q) + 304 / 45 := by ring

theorem per_site_shift_fixture :
    -5 / 12 + 17 / 12 = (1 : Rat) := by
  norm_num

theorem shifted_growth_remainder_fixture :
    (304 / 45 : Rat) - 2 * (10 / 3) * (17 / 12) = -121 / 45 := by
  norm_num

theorem bounded_degree_multiplier_fixture :
    (1 : Rat) + (10 / 3) * 6 = 21 := by
  norm_num

theorem shifted_pair_order_fixture (h b : Rat)
    (hb : 0 ≤ b) (hu : b ≤ (10 / 3 : Rat) * h + 304 / 45) :
    h + 17 / 6 ≤ h + b + 17 / 6 ∧
      h + b + 17 / 6 ≤ (13 / 3 : Rat) * (h + 17 / 6) + (-121 / 45 : Rat) := by
  constructor <;> linarith

theorem scope_fixture :
    (True ∧ True ∧ True ∧ True ∧ True) ∧
      ¬ (False ∨ False ∨ False) := by
  norm_num

end Tect.R302
