# R-470 HOLD-LC-001 GbmRsp2 mission-parser owner boundary

R-470 is an additive T-061 provenance result. It preserves the established
T-054 forward method, the T-059/T-061 observation-first inverse method, owner
order, and promotion firewalls. It does not replace or redesign any research
method.

## Exact source pin

The audited public source is the USRA-STI gdt-fermi repository, main commit
a6ef74e7278dbeb35759aadeb8d79ec8c38e6aac, file
src/gdt/missions/fermi/gbm/response.py. Its SHA-256 is
d2c1534ac3fa8eb783ba0a7f13c0e32bdfb7f44c8d0a409b64c7d7cfbfb0a2ba and its
byte length is 12107. The source URL, line ranges and gitignored cache key are
in the machine contract.

## Parser semantics

The source declares GbmRsp2 as a subclass of the core Rsp2. Its open method
delegates the file opening to super().open, snapshots the HDU headers, reads
DRM_NUM, and loops over every segment. For each segment it rebuilds
RspHeaders, reads NUMEBINS and DETCHANS, accesses MATRIX/F_CHAN/N_CHAN/N_GRP,
decompresses the row representation with GbmRsp._decompress_drm, constructs a
ResponseMatrix and a GbmRsp.from_data object using TSTART, TSTOP, TRIGTIME and
detector metadata, appends the object, closes the input and aggregates with
cls.from_rsps.

This is a parser control-flow description only. No HOLD-LC-001 event product is
opened and no response coefficient is interpreted. The audited GbmRsp2.open
body contains no validity, uncertainty, likelihood, interpolation, weighting,
nearest-segment or detector-to-geocenter contract. This bounded absence does
not imply that no other package module can provide such a contract.

## Evidence and adversarial review

Primary and independent lanes use different AST/token implementations and agree
on the source pin, parent R-469 hashes, class/method structure, field access,
per-segment reconstruction and the owner-gap boundary. The hostile lane mutates
source and parent identities, delegation, segment-loop and field semantics,
matrix/event admission, production selection, scoring, prospective status and
method-preservation flags; every mutation is rejected. Lean R470 checks the
finite segment-index and header-offset invariants used by the parser contract.

This is T0 finite mission-source provenance only. It does not admit response
validity, calibration interpolation, detector-to-geocenter timing, uncertainty,
likelihood, covariance, nuisance, a complete inverse map, scoring, a holdout, or
any physical, QFT, Yang-Mills, continuum or mass-gap claim. The next useful
input is the owner-supplied physical validity and timing contract; generic
software-source intake is stopped at this boundary.
