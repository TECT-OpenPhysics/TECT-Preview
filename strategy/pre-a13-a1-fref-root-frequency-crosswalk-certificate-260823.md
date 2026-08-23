# F_ref Fourier shell versus two-root cylinder frequency crosswalk

## Status

This is an exploration-only, T0, claim-nonbearing QFT crosswalk under
EXP-000976. It does not modify the frozen R-176 authority and does not close
the R-192 production-owner gate.

## Exact convention comparison

For the declared side-16 torus, the Fourier step is

\[
h=\frac{2\pi}{L}=\frac{\pi}{8}.
\]

The executable R-174/R-176 lanes evaluate the two roots at \(h\) and \(2h\),
so their spatial norm squares are \(|n|^2=1\) and \(|n|^2=4\). The R-176
manifest, however, records `r+Z*(m*pi/L)^2+Y*(m*pi/L)^4` while its code uses
`r+Z*(m*(2*pi/L))^2+Y*(m*(2*pi/L))^4`. The integrated audit does not currently
assert that manifest string against the executable expression.

The finite `F_ref` candidate uses

\[
K_n=Y(|k_n|^2-q_*^2)^2+\mu_*,\qquad q_*^2=-Z/(2Y).
\]

With the registered A1 decimals, \(q_*^2/h^2\) lies in
\((2.9999999999,3.0000000001)\), so the nearest side-16 shell is \(|n|^2=3\),
not the R-176 pair \(|n|^2=1,4\). Numerically the corresponding symbols are
approximately \(K_{3}=0.2600000000095\), \(K_{4}=0.2837815163755\), and
\(K_{1}=0.3551260654717\). The closeness of the decimal data to an exact
\(|n|^2=3\) shell does not create an exact identity with the irrational \(\pi\)
step.

## QFT/dynamics consequence

This does not invalidate the finite Euclidean `F_ref` Gibbs candidate or the
finite two-root covariance witnesses. It does show that no automatic
identification has been supplied between the QFT shell-minimizing Fourier
sector and the production-cylinder root labels. A canonical convention and a
root-labelled heat map must be frozen before `heat_root_incidence` can be
claimed. The full-residue closure in EXP-000975 reinforces this boundary: the
nonlinear finite drift saturates the side-16 residue space and does not itself
select a `k` versus `2k` filtration.

## Adversarial boundary

The audit rejects four shortcuts: treating the manifest typo as harmless while
using it as a source convention; identifying `q_*` with the printed `q_0`
without an error statement; calling the `|n|^2=1,4` roots the F_ref bottom
shell; and promoting identity-mobility Gibbs invariance to the production heat
root/raw-current/q-ledger owner. No R-192, A13, T-050, Sector-A, Pre-A,
physical-empty, continuum, thermodynamic, OS/KMS or real-time conclusion
follows. No PDF is issued.
