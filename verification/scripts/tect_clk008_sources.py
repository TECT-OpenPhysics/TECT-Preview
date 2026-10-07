"""Reproduce bounded CLK008 source-byte and product-structure audit.

No orbital interpolation, GR correction, parameter fitting or clock-value
interpretation occurs. Counts derive from actual source records; expected
sample counts below are independent-review TEST ORACLES, not physics inputs.
"""
import argparse
from collections import Counter
from decimal import Decimal
from pathlib import Path
import json
import tect_clk008_primary as io

MANIFEST = io.ROOT/'strategy/clock/TECT-CLK-008-sources-v1.json'


def parse_clock(text):
    lines = text.splitlines()
    end = next(i for i,line in enumerate(lines) if 'END OF HEADER' in line)
    reference = next(line.split()[0] for line in lines[:end] if 'ANALYSIS CLK REF' in line)
    out = {}
    for sat in ('E18','E14'):
        rows = [line.split() for line in lines[end+1:] if line.startswith('AS '+sat+' ')]
        assert rows
        epochs = [Decimal(r[5])*3600+Decimal(r[6])*60+Decimal(r[7]) for r in rows]
        counts = Counter(int(r[8]) for r in rows)
        assert epochs == sorted(set(epochs))
        assert all(Decimal(r[9]).is_finite() for r in rows)
        assert all(r[2:5] == ['2016','5','29'] for r in rows)
        steps = sorted(set(b-a for a,b in zip(epochs,epochs[1:])))
        out[sat] = {'records':len(rows), 'numeric_field_counts':dict(sorted(counts.items())),
                    'first_seconds':str(epochs[0]), 'last_seconds':str(epochs[-1]),
                    'step_seconds':[str(v) for v in steps],
                    'per_record_sigma_supplied':any(int(r[8])>=2 for r in rows)}
    return {'reference_receiver':reference,'format':'RINEX_CLOCK_2.00',
            'header_lines':end+1,'selected':out}


def parse_orbit(text):
    lines = text.splitlines()
    assert lines[0].startswith('#cV') and lines[-1].strip() == 'EOF'
    declared = int(lines[0].split()[6])
    epochs = [line.split()[1:] for line in lines if line.startswith('* ')]
    assert len(epochs) == declared
    assert 'GPS' in next(line for line in lines if line.startswith('%c'))
    counts = {sat:{kind:sum(line.startswith(kind+sat+' ') for line in lines)
                   for kind in ('P','V')} for sat in ('E18','E14')}
    return {'format':'SP3_c_velocity','frame':lines[0].split()[8], 'epoch_time':'GPS',
            'epochs':len(epochs),'declared_step_seconds':lines[1].split()[3],
            'first_epoch':epochs[0], 'last_epoch':epochs[-1], 'record_counts':counts,
            'full_clock_orbit_covariance_supplied':False}


def run(cache):
    io.inputs()
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    sources = manifest['sources']
    receipts = {}
    for key,value in sources.items():
        path = cache/value['filename']
        assert io.sha(path) == value['sha256'], key
        receipts[key] = {'sha256':value['sha256'],'bytes':path.stat().st_size}
    clock = parse_clock((cache/sources['R3CLK']['filename']).read_text(encoding='ascii'))
    orbit = parse_orbit((cache/sources['R3SP3']['filename']).read_text(encoding='ascii'))
    assert clock['reference_receiver'] == 'TWTF'  # reviewed header oracle
    for value in clock['selected'].values():
        assert value['records'] == 2880 and value['numeric_field_counts'] == {1:2880}
        assert [Decimal(v) for v in value['step_seconds']] == [Decimal(30)]
        assert not value['per_record_sigma_supplied']
    assert orbit['epochs'] == 289 and Decimal(orbit['declared_step_seconds']) == 300
    assert orbit['frame'] == 'IGS14'
    assert all(v == {'P':289,'V':289} for v in orbit['record_counts'].values())
    srp = (cache/sources['R3SRP']['filename']).read_text(encoding='ascii')
    blocks = [line[1:] for line in srp.splitlines() if line.startswith('+')]
    maps = sorted(set((parts[1],parts[2]) for line in srp.splitlines()
                      if len(parts:=line.split())>=3 and parts[1] in ('E201','E202')))
    assert maps == [('E201','E18'),('E202','E14')]
    assert blocks == ['FILE/REFERENCE','SRP/DESCRIPTION','SRP/SOLUTION']
    sls = (cache/sources['R3SLS']['filename']).read_text(encoding='ascii')
    assert 'Quick-Look Residual Analysis Report' in sls
    selected = [line for line in sls.splitlines() if '16/05/29' in line]
    same_day = {sat:sum(sat in line for line in selected) for sat in ('E18','E14')}
    assert same_day['E18'] == 0 and same_day['E14'] > 0
    # Serializing numeric-field keys as strings avoids JSON int-key ambiguity.
    value = {'schema':'tect/clk008-sources/1.0','status':'PASS_SOURCE_STRUCTURE_ONLY',
             'script_sha256':io.sha(Path(__file__)), 'manifest_sha256':io.sha(MANIFEST),
             'receipts':receipts,'clock':clock,'orbit':orbit,'srp_blocks':blocks,
             'satellite_mapping':maps,'sample_day_slr_passages':same_day,
             'clock_identity_crosswalk':{'E18':'GSAT0201 PHM-B within paper interval',
                                         'E14':'GSAT0202 RAFS excluded by paper PHM selection'},
             'full_paper_reproduction':False,'empirical_fit':False,'coverage_certified':False,
             'upc_clock_series_used':False,'physical_promotion':False}
    return json.loads(json.dumps(value))


if __name__ == '__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--cache',type=Path,default=io.ROOT/'internal/clock/clk008/sources')
    ap.add_argument('--check',action='store_true')
    args=ap.parse_args()
    value=run(args.cache)
    io.issue_or_check(value,io.RUNS/'sources.json',args.check)
    print('CLK008 SOURCES:',value['status'],len(value['receipts']))
