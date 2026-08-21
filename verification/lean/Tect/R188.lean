import Mathlib

namespace Tect.R188

def atom (c e1 e2 : Rat) : Rat := e2 * (1 + c * e1)

def j0 (c : Rat) : Rat :=
  (atom c (-1) (-1) ^ 2 + atom c (-1) 1 ^ 2 +
      atom c 1 (-1) ^ 2 + atom c 1 1 ^ 2) / 4

def j1 (c e1 : Rat) : Rat :=
  (atom c e1 (-1) ^ 2 + atom c e1 1 ^ 2) / 2

def j2 (c e1 e2 : Rat) : Rat := atom c e1 e2 ^ 2

def dH1 (c e1 : Rat) : Rat := j1 c e1 - j0 c

def dH2 (c e1 e2 : Rat) : Rat := j2 c e1 e2 - j1 c e1

def secant1 (c e1 : Rat) : Rat := (0 : Rat) - 0

def secant2 (c e1 e2 : Rat) : Rat := atom c e1 e2 ^ 2 - 0

def defect1 (c e1 : Rat) : Rat := j1 c e1 - j0 c

def defect2 (c e1 e2 : Rat) : Rat := 0 - j1 c e1

theorem jensen_defect_telescope (c e1 e2 : Rat) :
    dH1 c e1 + dH2 c e1 e2 = j2 c e1 e2 - j0 c := by
  simp [dH1, dH2]

theorem jensen_defect_fixture :
    j0 (2 / 5) = 29 / 25 /\
      j1 (2 / 5) 1 = 49 / 25 /\
      j1 (2 / 5) (-1) = 9 / 25 /\
      j2 (2 / 5) 1 1 = 49 / 25 /\
      j2 (2 / 5) (-1) (-1) = 9 / 25 /\
      dH1 (2 / 5) 1 = 4 / 5 /\
      dH1 (2 / 5) (-1) = -(4 / 5) /\
      dH2 (2 / 5) 1 1 = 0 /\
      dH2 (2 / 5) (-1) (-1) = 0 := by
  norm_num [atom, j0, j1, j2, dH1, dH2]

theorem signed_endpoint_mean_zero :
    ((j2 (2 / 5) (-1) (-1) - j0 (2 / 5)) +
        (j2 (2 / 5) (-1) 1 - j0 (2 / 5)) +
        (j2 (2 / 5) 1 (-1) - j0 (2 / 5)) +
        (j2 (2 / 5) 1 1 - j0 (2 / 5))) / 4 = 0 := by
  norm_num [atom, j0, j2]

theorem absolute_jensen_defect_positive :
    (|defect1 (2 / 5) (-1)| + |defect1 (2 / 5) 1|) / 2 = 4 / 5 /\
      (4 / 5 : Rat) > 0 := by
  norm_num [atom, j0, j1, defect1]

theorem secant_defect_recombination_fixture :
    dH1 (2 / 5) 1 = secant1 (2 / 5) 1 + defect1 (2 / 5) 1 /\
      dH2 (2 / 5) 1 1 = secant2 (2 / 5) 1 1 + defect2 (2 / 5) 1 1 := by
  norm_num [atom, j0, j1, j2, dH1, dH2, secant1, secant2, defect1, defect2]

end Tect.R188
