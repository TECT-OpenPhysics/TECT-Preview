"""Exact ideal optical covariance only; no EXCH-to-apparatus map is tested."""
import argparse
import hashlib
import json
from pathlib import Path

import sympy as s


ROOT = Path(__file__).resolve().parents[2]
CARD = ROOT / "strategy/physical-candidates/R581-optical-comparator.json"


def run(source_pdf=None):
    card = json.loads(CARD.read_text(encoding="utf-8"))
    for name, expected in card["authority_sha256"].items():
        if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != expected:
            raise ValueError(f"EXCH source mismatch: {name}")
    if source_pdf and hashlib.sha256(source_pdf.read_bytes()).hexdigest() != card["reference"]["sha256"]:
        raise ValueError("Optical source differs from the pinned version.")
    p, u, v, x, y, a = s.symbols("p u v x y a", complex=True)
    k, sigma, delta = s.symbols("k sigma delta", real=True)
    ii, root = s.I, s.sqrt(2)
    vec = s.Matrix
    swap = lambda t: vec([t[0], -ii*t[2], ii*t[1]])
    field = lambda z, h, j: vec([k*(sigma-z-h*j), -h+z*s.conjugate(j), -j+z*s.conjugate(h)])
    intensity = lambda h, j: h*s.conjugate(h)+j*s.conjugate(j)
    lg = lambda h, j: vec([(h-ii*j)/root, (h+ii*j)/root])
    hg = lambda h, j: vec([(h+j)/root, ii*(h-j)/root])
    z, xy = vec([p,u,v]), vec([x,y])
    w = swap(z)
    checks = {}

    def check(label, expressions):
        if not all(s.simplify(t) == 0 for t in expressions):
            raise AssertionError(label)
        checks[label] = "PASS"

    check("HG_LG_inverse", hg(*lg(x,y))-xy)
    check("A_and_B_are_interchanged_with_pump_fixed",
          swap(vec([p,*lg(a,ii*a)]))-vec([p,*lg(ii*a,a)]))
    check("HG_reflection_is_signed_LG_swap", w.subs({u:lg(x,y)[0],v:lg(x,y)[1]}, simultaneous=True)-vec([p,*lg(y,x)]))
    check("involution", swap(w)-z)
    check("entire_LG_drift_commutes", field(*w)-swap(field(*z)))
    check("total_intensity_invariant", [intensity(w[1],w[2])-intensity(u,v)])
    # Independent representation: derive both HG component equations, including the pump.
    dh = field(p,*lg(x,y))
    hgf = vec([dh[0],*hg(dh[1],dh[2])])
    check("direct_HG_drift", hgf-vec([k*(sigma-p-(x*x+y*y)/2),-x+p*s.conjugate(x),-y+p*s.conjugate(y)]))
    check("basis_preserves_total_signal", [intensity(*lg(x,y))-intensity(x,y)])
    # Hostile: an unequal hypothetical HG loss breaks the symmetry, not a second model test.
    gx, gy = -(1+delta)*x+p*s.conjugate(x), -y+p*s.conjugate(y)
    residual = s.expand(gx.xreplace({x:y})-gy)
    if residual == 0 or s.simplify(residual+delta*y) != 0:
        raise AssertionError("unequal-loss negative control")
    checks["reject_unequal_loss_as_invariant"] = "PASS"
    return {"scope":"Classical ideal comparator only, no physical sign evaluation.",
            "checks":checks, "source_pdf_sha256_verified":bool(source_pdf)}


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source-pdf", type=Path)
    ap.add_argument("--write-run", action="store_true")
    args = ap.parse_args()
    result = run(args.source_pdf)
    payload = json.dumps(result, indent=2) + "\n"
    if args.write_run:
        if not args.source_pdf:
            ap.error("--write-run requires --source-pdf")
        dest = ROOT / json.loads(CARD.read_text(encoding="utf-8"))["run"]
        with dest.open("x", encoding="utf-8", newline="\n") as output:
            output.write(payload)
    print(payload, end="")
