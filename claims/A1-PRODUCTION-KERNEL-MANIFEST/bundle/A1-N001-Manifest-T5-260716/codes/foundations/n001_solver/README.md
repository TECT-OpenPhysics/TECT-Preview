# N-001 microscopic PDE solver -- vendored ORIGINAL sources

These are byte-identical copies of the canonical N-001 solver linear-operator sources from the frozen TECT2/Contents tree (Codes/pde/), vendored so the A1-PRODUCTION-KERNEL-MANIFEST reproduction bundle is self-contained and the verifier imports the REAL solver functions (not a mimic):

- `continuation_mu2_v25.py` : `kinetic_coefficients(mu2,Y,q0) -> (r,Z)`; r=mu2+Y q0^4, Z=-2Y q0^2.
- `bloch_linearization.py`  : `bloch_matrix_linear(G*, params)` scalar diagonal L = r + Z|k|^2 + Y|k|^4 + eta_shell*(|k|-q0)^2 (the FULL linear symbol incl. shell-bias).
- `math56_constants.py`     : transitive import dependency of continuation_mu2_v25.py.

Full sha256 (compare against your TECT2/Contents copies):

- `continuation_mu2_v25.py`: `6db0393a31f31eed7dbb109f23b41f07efd884c819999578394a8dad8f3d7432`
- `bloch_linearization.py`: `337bd6de6b31e5230b8d139b75df33b67554edf080719d759697e9390f7a98ed`
- `math56_constants.py`: `6c80859780baf755158c5bcbea1dafdb9928c8b83ed3b1d835226ad1f1dcb3e8`

The pure-Brazovskii A1 kernel is the `eta_shell=0` slice of this symbol; the verifier enforces `eta_shell=0` and asserts the original `bloch_matrix_linear` reduces to r+Z|k|^2+Y|k|^4 = the stored kernel.
