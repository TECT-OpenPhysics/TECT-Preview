# EXP-000994 — Three-dimensional A1 shell projected filtration

## Exact finite support result

On the side-16 reciprocal torus, the nearest exact shell to the registered
quadratic minimum is the eight-point set

\[
S_0=\{(\pm1,\pm1,\pm1)\}\subset(\mathbb Z/16\mathbb Z)^3.
\]

For the local sextic support rule (N(f)=(\bar f*f)^2*f), use

\[
 C(S)=S+2(S-S)\pmod {16}.
\]

Exact integer set arithmetic gives

\[
 |S_0|=8,\qquad |C(S_0)|=216,qquad |C^2(S_0)|=512.
\]

The coordinate projections are respectively

\[
 \{1,15\},\quad
 \{1,3,5,11,13,15\},\quad
 \{1,3,5,7,9,11,13,15\}.
\]

Thus (S_2) is the odd-residue cube, not all (16^3=4096) residues.  The
support filtration (V_j=\{f:\operatorname{supp}f\subset S_j\}) is nested, and
the nonlinear drift has the upper-bound mapping (V_j\to V_{j+1}).

## Heat and QFT boundary

The diagonal quadratic proxy (H_t\hat f(n)=e^{-t\omega(n)}\hat f(n)) preserves
every (V_j).  This is a finite shell-level heat candidate only.  It is not a
canonical nonlinear A1 mobility or heat-root law, and it does not construct
conditional replicas, a raw-current spatial intertwiner, or a one-use
nonnegative q-ledger.

The result is therefore a stronger three-dimensional comparison object than the
one-dimensional EXP-000993 candidate, but it still does not complete R-192,
A13, Sector-A or Pre-A.  No physical-empty, OS/KMS, real-time, removal,
thermodynamic or continuum conclusion follows.

## Verification

Primary and independent lanes use exact integer set arithmetic; the integrated
lane reruns both without importing either implementation, checks source/file
hashes, and exercises the eight declared scope mutations. `R206.lean` checks
the finite cardinality factors (2^3=8), (6^3=216), (8^3=512), support
preservation, and the positive quadratic-core lower bound without `sorry`,
`admit`, `axiom` or `unsafe`.

No result ledger entry, gate closure, new negative or PDF is issued here.
