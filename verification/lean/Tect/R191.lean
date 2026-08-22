import Mathlib

namespace Tect.R191

/-!
  Exact finite algebra for the next A13 production-cylinder prerequisite.
  The endpoint polynomial is the side-16 two-mode A1 scalar owner.  The
  incidence map is the registered common-heat/root-1/root-2/future order.
  This file checks the algebraic telescope and the concrete rational fixture;
  it does not assert that the finite owner is the production progressive owner.
-/

def m4 (a b : Rat) : Rat :=
  3 * (a ^ 4 + b ^ 4) / 8 + 3 * a ^ 2 * b ^ 2 / 2

def m6 (a b : Rat) : Rat :=
  5 * (a ^ 6 + b ^ 6) / 16 +
    105 * a ^ 4 * b ^ 2 / 32 +
    45 * a ^ 2 * b ^ 4 / 16

def owner (q1 q2 a b : Rat) : Rat :=
  q1 * a ^ 2 + q2 * b ^ 2 - (43 / 400) * m4 a b + (27 / 100) * m6 a b

def ea (q1 q2 a b : Rat) : Rat :=
  a * (81 * a ^ 4 / 160 + 567 * a ^ 2 * b ^ 2 / 160 +
      243 * b ^ 4 / 160 - 129 * a ^ 2 / 400 -
      129 * b ^ 2 / 400 + q1 * 2)

def eb (q1 q2 a b : Rat) : Rat :=
  b * (567 * a ^ 4 / 320 + 243 * a ^ 2 * b ^ 2 / 80 +
      81 * b ^ 4 / 160 - 129 * a ^ 2 / 400 -
      129 * b ^ 2 / 800 + q2 * 2)

def beta : Rat := 1 / 2

def g1 (h r1 : Rat) : Rat := h + r1

def g2 (h r1 r2 : Rat) : Rat := h + beta * g1 h r1 + r2

def stage0A (h : Rat) : Rat := h
def stage0B (h : Rat) : Rat := h
def stage1A (h r1 : Rat) : Rat := g1 h r1
def stage1B (h r1 : Rat) : Rat := h + beta * g1 h r1
def stage2A (h r1 r2 : Rat) : Rat := g1 h r1
def stage2B (h r1 r2 : Rat) : Rat := g2 h r1 r2
def stage3A (h r1 r2 f1 : Rat) : Rat := g1 h r1 + f1
def stage3B (h r1 r2 f2 : Rat) : Rat := g2 h r1 r2 + f2

def dR1 (q1 q2 h r1 r2 f1 f2 : Rat) : Rat :=
  ea q1 q2 (stage3A h r1 r2 f1) (stage3B h r1 r2 f2) +
    beta * eb q1 q2 (stage3A h r1 r2 f1) (stage3B h r1 r2 f2)

def dR2 (q1 q2 h r1 r2 f1 f2 : Rat) : Rat :=
  eb q1 q2 (stage3A h r1 r2 f1) (stage3B h r1 r2 f2)

def dF1 (q1 q2 h r1 r2 f1 f2 : Rat) : Rat :=
  ea q1 q2 (stage3A h r1 r2 f1) (stage3B h r1 r2 f2)

def dF2 (q1 q2 h r1 r2 f1 f2 : Rat) : Rat :=
  eb q1 q2 (stage3A h r1 r2 f1) (stage3B h r1 r2 f2)

theorem moment_fixture :
    m4 (1 / 1) (1 / 1) = 9 / 4 /\
      m6 (1 / 1) (1 / 1) = 215 / 32 := by
  norm_num [m4, m6]

theorem incidence_telescope (q1 q2 h r1 r2 f1 f2 : Rat) :
    owner q1 q2 (stage3A h r1 r2 f1) (stage3B h r1 r2 f2) -
        owner q1 q2 (stage0A h) (stage0B h) =
      (owner q1 q2 (stage1A h r1) (stage1B h r1) -
        owner q1 q2 (stage0A h) (stage0B h)) +
      (owner q1 q2 (stage2A h r1 r2) (stage2B h r1 r2) -
        owner q1 q2 (stage1A h r1) (stage1B h r1)) +
      (owner q1 q2 (stage3A h r1 r2 f1) (stage3B h r1 r2 f2) -
        owner q1 q2 (stage2A h r1 r2) (stage2B h r1 r2)) := by
  simp [owner, m4, m6, stage0A, stage0B, stage1A, stage1B,
    stage2A, stage2B, stage3A, stage3B, g1, g2, beta]

theorem feedback_chain_rule (q1 q2 h r1 r2 f1 f2 : Rat) :
    dR1 q1 q2 h r1 r2 f1 f2 =
        ea q1 q2 (stage3A h r1 r2 f1) (stage3B h r1 r2 f2) +
          beta * eb q1 q2 (stage3A h r1 r2 f1) (stage3B h r1 r2 f2) /\
      dR2 q1 q2 h r1 r2 f1 f2 =
        eb q1 q2 (stage3A h r1 r2 f1) (stage3B h r1 r2 f2) /\
      dF1 q1 q2 h r1 r2 f1 f2 =
        ea q1 q2 (stage3A h r1 r2 f1) (stage3B h r1 r2 f2) /\
      dF2 q1 q2 h r1 r2 f1 f2 =
        eb q1 q2 (stage3A h r1 r2 f1) (stage3B h r1 r2 f2) := by
  simp [dR1, dR2, dF1, dF2]

theorem registered_fixture :
    let q1 : Rat := 1 / 8
    let q2 : Rat := 1 / 8
    let h : Rat := 1 / 5
    let r1 : Rat := 1 / 10
    let r2 : Rat := -(1 / 20)
    let f1 : Rat := 1 / 20
    let f2 : Rat := -(1 / 10)
    owner q1 q2 (stage3A h r1 r2 f1) (stage3B h r1 r2 f2) - owner q1 q2 h h =
        40816479 / 4096000000 /\
      owner q1 q2 (stage1A h r1) (stage1B h r1) - owner q1 q2 h h =
        332706119 / 20480000000 /\
      owner q1 q2 (stage2A h r1 r2) (stage2B h r1 r2) -
          owner q1 q2 (stage1A h r1) (stage1B h r1) =
        -(84198439 / 20480000000) /\
      owner q1 q2 (stage3A h r1 r2 f1) (stage3B h r1 r2 f2) -
          owner q1 q2 (stage2A h r1 r2) (stage2B h r1 r2) =
        -(8885057 / 4096000000) := by
  constructor
  · norm_num [owner, m4, m6, stage0A, stage0B, stage1A, stage1B,
      stage2A, stage2B, stage3A, stage3B, g1, g2, beta]
  constructor
  · norm_num [owner, m4, m6, stage0A, stage0B, stage1A, stage1B,
      stage2A, stage2B, stage3A, stage3B, g1, g2, beta]
  constructor
  · norm_num [owner, m4, m6, stage0A, stage0B, stage1A, stage1B,
      stage2A, stage2B, stage3A, stage3B, g1, g2, beta]
  · norm_num [owner, m4, m6, stage0A, stage0B, stage1A, stage1B,
      stage2A, stage2B, stage3A, stage3B, g1, g2, beta]

theorem registered_endpoint_positive :
    (0 : Rat) < 40816479 / 4096000000 := by
  norm_num

end Tect.R191
