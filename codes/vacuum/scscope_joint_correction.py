"""scscope_joint_correction.py -- SELF-CAUGHT CORRECTION of the SC-SCOPE lift.

scscope-floor-sharpening v1.0-v1.2 used paired = rho/(1+max[R_s+R_q]) = rho/2.872
(the joint-PAIRING formula). But that formula's linear-in-rho scaling is a LOCAL
approximation at rho=2.6; the physically-correct accounting (scscope_joint_endpoint.py)
treats the sunset as an ABSOLUTE third-cumulant cost C_sunset=composed/1.13 that
does NOT vanish as the second-order floor thickens, so the joint ratio SATURATES
(it does not grow linearly). Under that additive bookkeeping the sharpened floor
does NOT cleanly close the endpoint:
  rho=6.55 -> joint x0.945 < 1 (conservative K_floor=T');
  threshold rho>=9.85; rho_lat=12.6 (verified K_floor=0.52T') -> x1.026 (marginal).
Hence the SC-SCOPE all-orders endpoint lift is RETRACTED: the floor sharpening is
a real PARTIAL advance (x0.757 -> x0.945..x1.026) but NOT a clean closure.

self-test asserts (exit 0 iff all pass).
"""
__version__ = "1.0.0"
__first_issued__ = "2026-06-08"
__claims__ = ["B5-BEYOND-LAYER-BOUND", "B1-RH-ENUM"]
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import sectorb_common as sb
REPO = Path(__file__).resolve().parents[2]
CLAIMS=[]
def claim(n,c,d=""): CLAIMS.append(dict(name=n,passed=bool(c),detail=d)); print(f"  [{'PASS' if c else 'FAIL'}] {n} {d}")
MARGIN=sb.margin_of(0.005)["margin"]; SUNSET=1.13; R_MAX=1.019
def joint_additive(rho):
    C2=MARGIN/rho; composed=MARGIN*(1-1/rho); return MARGIN/(C2+composed/SUNSET+R_MAX*C2)

# (1) reproduce the original honest negative at rho=2.6
claim("reproduces_original_negative", abs(joint_additive(2.6)-0.757)<0.01,
      f"(additive joint at rho=2.6 = x{joint_additive(2.6):.3f} reproduces the scscope_joint_endpoint x0.757)")
# (2) the additive bookkeeping SATURATES (does not grow linearly like rho/2.872)
sat=joint_additive(1e6)
claim("additive_saturates", sat<1.2 and joint_additive(100)<sat+0.01,
      f"(additive joint -> x{sat:.3f} as rho->inf (sunset-limited), NOT linear in rho: the pairing formula "
      "rho/2.872 was a local approximation, wrong when extrapolated)")
# (3) the sharpened floor does NOT cleanly close (conservative K_floor=T')
rho_cons=266.7/40.7   # K_floor<=T'<=n_pack
claim("conservative_does_not_close", joint_additive(rho_cons)<1.0,
      f"(K_floor<=T'<=n_pack=40.7 => rho_lat={rho_cons:.2f} => additive joint x{joint_additive(rho_cons):.3f} < 1 "
      "-- the floor sharpening alone does NOT close the endpoint under the correct bookkeeping)")
# (4) even the verified K_floor=0.52T' is only MARGINAL
rho_ver=266.7/(0.52*40.7)
claim("verified_ratio_marginal", 1.0 < joint_additive(rho_ver) < 1.1,
      f"(K_floor=0.52T' (verified on tiny shells) => rho_lat={rho_ver:.2f} => x{joint_additive(rho_ver):.3f} -- "
      "marginal (<x1.05), too thin and ratio-dependent to claim a lift)")
# (5) threshold
lo,hi=2.0,100.0
for _ in range(60):
    m=(lo+hi)/2
    if joint_additive(m)<1: lo=m
    else: hi=m
rstar=(lo+hi)/2
claim("threshold_is_9p85_not_3p9", abs(rstar-9.85)<0.3,
      f"(additive bookkeeping needs rho >= {rstar:.2f} (NOT the 3.9 my note used); requires K_floor <= "
      f"{266.7/rstar:.1f}, i.e. T' <= {266.7/rstar:.0f} (or <= {266.7/rstar/0.52:.0f} with the 0.52 ratio))")

print(f"\nPARTIAL ADVANCE (honest): the proved floor sharpening (K_floor<=T') moves the additive endpoint joint")
print(f"from x0.757 to x{joint_additive(rho_cons):.3f} (conservative) .. x{joint_additive(rho_ver):.3f} (verified-ratio)")
print("-- a real improvement, but NOT a clean closure. SC-SCOPE lift RETRACTED; SC-SCOPE restored as a B1 hypothesis.")
ok=all(c["passed"] for c in CLAIMS)
out=REPO/"claims"/"B5-BEYOND-LAYER-BOUND"/"runs"/"260608-scscope-joint-correction"
out.mkdir(parents=True,exist_ok=True)
(out/"result.json").write_text(json.dumps(dict(script="scscope_joint_correction.py",version=__version__,
    rho_threshold=rstar,joint_at_6p55=joint_additive(6.55),joint_at_rho_cons=joint_additive(rho_cons),
    joint_at_rho_ver=joint_additive(rho_ver),saturation=sat,claims=CLAIMS,all_pass=ok),indent=2))
print(f"\nclaims {sum(c['passed'] for c in CLAIMS)}/{len(CLAIMS)} {'PASS' if ok else 'FAIL'}")
sys.exit(0 if ok else 1)
