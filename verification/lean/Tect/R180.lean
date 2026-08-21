import Mathlib

/-!
R-180 kernel cross-check.

This file checks the exact algebraic core of the R-140 predictable triangular
majorant.  The geometric-series identity, positivity of the closed C=5
majorant under its registered envelope hypotheses, and the two production
exponent margins are kernel-checked over `Rat`.  No production mixed-Gram
envelope, conditional owner intertwiner, source/sextic one-use estimate,
finite-collar headroom, Nelson bound, or limit theorem is encoded here.
-/

namespace Tect.R180

def geom (r : Rat) : Nat -> Rat
  | 0 => 0
  | n + 1 => geom r n + r ^ n

theorem geom_closed {r : Rat} (n : Nat) :
    (1 - r) * geom r n = 1 - r ^ n := by
  induction n with
  | zero => simp [geom]
  | succ n ih =>
      rw [geom, mul_add, ih]
      ring

theorem geom_nonneg {r : Rat} (hr : 0 <= r) (n : Nat) :
    0 <= geom r n := by
  induction n with
  | zero => simp [geom]
  | succ n ih =>
      rw [geom]
      positivity

theorem geom_le_inv_one_sub {r : Rat} (hr0 : 0 <= r) (hr1 : r < 1) (n : Nat) :
    geom r n <= 1 / (1 - r) := by
  have hden : 0 < 1 - r := by linarith
  have hclosed := geom_closed (r := r) n
  have hpow : 0 <= r ^ n := by positivity
  field_simp [ne_of_gt hden]
  nlinarith [hclosed, hpow]

def near (u v q : Rat) : Rat :=
  (u / (1 - u) - v / (1 - v)) / (q - 1)

def farHigh (u rho : Rat) : Rat :=
  u / ((1 - u) * (1 - rho))

def hFive (u v q rho : Rat) : Rat :=
  near u v q + farHigh u rho

theorem near_pos {u v q : Rat}
    (hvu : v < u)
    (hu1 : u < 1) (hv1 : v < 1) (hq : 1 < q) :
    0 < near u v q := by
  have h1u : 0 < 1 - u := by linarith
  have h1v : 0 < 1 - v := by linarith
  have hdiff :
      u / (1 - u) - v / (1 - v) =
        (u - v) / ((1 - u) * (1 - v)) := by
    field_simp [ne_of_gt h1u, ne_of_gt h1v]
    ring
  rw [near, hdiff]
  positivity

theorem far_high_pos {u rho : Rat}
    (hu : 0 < u) (hu1 : u < 1) (hrho1 : rho < 1) :
    0 < farHigh u rho := by
  unfold farHigh
  positivity

theorem hFive_pos {u v q rho : Rat}
    (hu : 0 < u) (hvu : v < u)
    (hu1 : u < 1) (hv1 : v < 1) (hq : 1 < q)
    (hrho1 : rho < 1) :
    0 < hFive u v q rho := by
  unfold hFive
  linarith [near_pos hvu hu1 hv1 hq,
    far_high_pos hu hu1 hrho1]

theorem hFive_fixture :
    hFive (3 / 4) (1 / 4) 2 (1 / 2) = 26 / 3 := by
  norm_num [hFive, near, farHigh]

theorem geom_fixture : geom (1 / 2) 4 = 15 / 8 := by
  norm_num [geom]

theorem production_exponent_margins :
    And (((7 : Rat) / 5) / 2 - 7 / 12 = 7 / 60)
      ((2 : Rat) / 3 - 7 / 12 = 1 / 12) := by
  constructor <;> norm_num

end Tect.R180
