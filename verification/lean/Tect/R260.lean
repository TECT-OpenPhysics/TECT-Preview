import Mathlib

namespace Tect.R260

theorem pell_first : (7 : Rat)^2 - 2 * (5 : Rat)^2 = -1 := by
  norm_num

theorem pell_second : (41 : Rat)^2 - 2 * (29 : Rat)^2 = -1 := by
  norm_num

theorem pell_third : (239 : Rat)^2 - 2 * (169 : Rat)^2 = -1 := by
  norm_num

theorem gibbs_ratio_first : (1 / (49 : Rat)^6) = 1 / 49^6 := by
  norm_num

theorem gibbs_ratio_second : (1 / (1681 : Rat)^6) = 1 / 1681^6 := by
  norm_num

theorem gibbs_ratio_third : (1 / (57121 : Rat)^6) = 1 / 57121^6 := by
  norm_num

theorem m5_first :
    (49 : Rat)^5 * (49 + 1) / (49^6 + 1) = 7061881225 / 6920643601 := by
  norm_num

theorem q_squared_first :
    (5 : Rat) * (49^6 + 49) / (49^6 + 1) = 34603218125 / 6920643601 := by
  norm_num

theorem m5_second :
    (1681 : Rat)^5 * (1681 + 1) / (1681^6 + 1) =
      11288456479838169241 / 11281745150183093041 := by
  norm_num

theorem q_squared_second :
    (29 : Rat) * (1681^6 + 1681) / (1681^6 + 1) =
      327170609355309722549 / 11281745150183093041 := by
  norm_num

theorem m5_third :
    (57121 : Rat)^5 * (57121 + 1) / (57121^6 + 1) =
      17368104308110262764142714161 / 17367800255305597131588459361 := by
  norm_num

theorem q_squared_third :
    (169 : Rat) * (57121^6 + 57121) / (57121^6 + 1) =
      2935158243146645915238454458649 / 17367800255305597131588459361 := by
  norm_num

theorem powered_candidate_violation_first :
    ((34603218125 / 6920643601 : Rat)^10) >
      (9 / 4 : Rat)^10 * (7061881225 / 6920643601 : Rat)^3 := by
  norm_num

theorem powered_candidate_violation_second :
    ((327170609355309722549 / 11281745150183093041 : Rat)^10) >
      (9 / 4 : Rat)^10 * (11288456479838169241 / 11281745150183093041 : Rat)^3 := by
  norm_num

theorem powered_candidate_violation_third :
    ((2935158243146645915238454458649 / 17367800255305597131588459361 : Rat)^10) >
      (9 / 4 : Rat)^10 * (17368104308110262764142714161 / 17367800255305597131588459361 : Rat)^3 := by
  norm_num

theorem beta_positive_fixture : (6 : Rat) * (49 : Rat) > 0 := by
  norm_num

theorem scope_fixture : True ∧ ¬False := by
  norm_num

end Tect.R260
