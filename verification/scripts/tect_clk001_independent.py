#!/usr/bin/env python3
"""Non-importing CLK-001 symbolic and decimal reconstruction, version 1.0.1.

Independent implementation and primary-page extraction, same-task authorship;
not an independent human referee or reanalysis of unavailable raw samples.
"""
import argparse
from decimal import Decimal as D, localcontext
import hashlib
import json
import os
from pathlib import Path
import tempfile
import sympy as s

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'claims/C6-SPACETIME-SIGNATURE/runs/2026-09-14-tect-clk001-v101/independent.json'
EVIDENCE = ROOT/'strategy/clock/TECT-CLK-001-evidence-v1.1.json'
PIN = '01e8dbd2d3bd5014171f0189277a816e29d22f78addba9834f74f40cafc9e40a'


def run(source_cache=False):
    assert hashlib.sha256(EVIDENCE.read_bytes()).hexdigest() == PIN
    e = json.loads(EVIDENCE.read_text(encoding='utf-8'))
    checks = []
    a, b, c, d = s.symbols('a b c d', positive=True)
    ratio = a*d/(b*c)
    assert s.factor(ratio-1) == (a*d-b*c)/(b*c)
    assert s.simplify((a*d-b*c).subs(d, b*c/a)) == 0
    checks.append('symbolic_minor_equivalence_and_basepoint_construction')
    x, y, u, v = s.symbols('x y u v', positive=True)
    assert s.simplify(ratio.subs({a:x*u,b:x*v,c:y*u,d:y*v})-1) == 0
    checks.append('arbitrary_positive_factor_cancellation')
    gradient = s.Matrix([s.diff(s.log(ratio), z) for z in (a,b,c,d)])
    assert gradient == s.Matrix([1/a,-1/b,-1/c,1/d])
    common_mode = s.Matrix([a,b,c,d])
    assert (gradient.T*(common_mode*common_mode.T)*gradient)[0] == 0
    checks.append('differentiated_log_ratio_and_full_covariance_common_mode')
    # Sparse square: three edges cannot determine whether the fourth is observed-compatible.
    predicted_fourth = b*c/a
    assert s.simplify(ratio.subs(d,predicted_fourth)) == 1
    assert s.simplify(ratio.subs(d,2*predicted_fourth)) == 2
    checks.append('unobserved_edge_two_completions')
    bsrc = e['sources']['bothwell']['gradient_budget']
    with localcontext() as context:
        context.prec = 60  # Numerical presentation precision, not an experimental input.
        corrected = D(bsrc['measured']['mean'])-sum(D(z) for z in bsrc['biases'].values())
        variance = sum(D(z)*D(z) for z in bsrc['uncertainties'].values())
        ceiling = variance+D(bsrc['other_uncertainty_upper_exclusive'])**2
        assert corrected == D(bsrc['reported_corrected_mean'])
        assert variance.sqrt().quantize(D('0.1')) == D(bsrc['reported_total_uncertainty'])
        assert ceiling.sqrt().quantize(D('0.1')) == D(bsrc['reported_total_uncertainty'])
        c_si = D(e['reference_formula']['c_m_per_s'])
        bw = D(e['sources']['bothwell']['acceleration']['value'])/c_si**2/D(1000)/D('1e-20')
        ch = D(e['sources']['chou']['acceleration']['value'])*D(e['sources']['chou']['elevation']['change_m'])/c_si**2
        derived = { 'corrected_mean':str(corrected), 'u_lower':str(variance.sqrt()),
                    'u_upper_exclusive':str(ceiling.sqrt()), 'bothwell_M0_budget_units':str(bw),
                    'chou_M0_fractional_shift':str(ch)}
    checks.append('nonimporting_decimal_source_and_units_reconstruction')
    # Fixed primary-page facts are test oracles for an independently transcribed manifest.
    assert bsrc['reported_corrected_mean'] == '-9.8'  # PDF p9 displayed table.
    assert e['sources']['chou']['frequency_shift']['mean'] == '4.1e-17'  # PDF p3 text.
    assert e['sources']['chou']['elevation']['change_m'] == '0.33'  # PDF p3 text.
    checks.append('primary_page_transcription_oracles')
    if source_cache:
        import pdfplumber
        for name, source in e['sources'].items():
            path = Path(source_cache)/source['download_filename']
            assert hashlib.sha256(path.read_bytes()).hexdigest() == source['sha256']
            with pdfplumber.open(path) as pdf:
                assert len(pdf.pages) == source['pages']
                # Page-number and content sanity only: formulas/table visually read separately.
                page = pdf.pages[3 if name == 'bothwell' else 2].extract_text()
                token = 'redshift' if name == 'bothwell' else '4.1'
                assert token in page.lower()
    return {'schema':'tect/clk001-run/1.0','role':'independent','status':'PASS_SCOPED_AUDIT',
            'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'evidence_sha256':PIN,'checks':checks,'check_groups':len(checks),'derived':derived,
            'source_extraction':'pdfplumber optional hash/page/text replay plus previously inspected primary page images; no raw-data reanalysis.',
            'independence':'Does not import primary/hostile scripts. Same-task author, not independent-person review.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    parser.add_argument('--source-cache',type=Path)
    args = parser.parse_args()
    result = run(args.source_cache)
    if args.check:
        assert json.loads(OUT.read_text(encoding='utf-8')) == result
    else:
        assert not OUT.exists(), 'Issued run immutable; use --check'
        OUT.parent.mkdir(parents=True,exist_ok=True)
        fd,tmp=tempfile.mkstemp(dir=OUT.parent,suffix='.tmp')
        with os.fdopen(fd,'w',encoding='utf-8',newline='\n') as handle:
            json.dump(result,handle,sort_keys=True,indent=2);handle.write('\n')
        os.replace(tmp,OUT)
    print('CLK-001 INDEPENDENT: PASS',result['check_groups'],'groups')
