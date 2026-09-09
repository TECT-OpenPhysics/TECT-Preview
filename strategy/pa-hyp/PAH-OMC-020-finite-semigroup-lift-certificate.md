# R-550 finite semigroup lift checkpoint

## Question and scope

R-550 asks whether the exact finite pointwise identity registered by R-493,

`L_(n+1) I_(n,n+1) f = I_(n,n+1) L_n f`,

already gives

`P_(n+1)(t) I_(n,n+1) f = I_(n,n+1) P_n(t) f`.

The PAH-001 functional, directed roots, midpoint rates, labelled Gibbs
components, grade-blind lift, carriers, normalization, external Markov time
and limit order are unchanged.  Only one finite successor pair is considered;
no j limit, anchored-n limit or physical interpretation is taken.

## Exact conditional bridge

For finite function spaces, let `A=L_(n+1)`, `B=L_n` and let `I` be the lift.
If `A I=I B` holds on the entire coarse function space, induction gives
`A^k I=I B^k` for every `k`.  The finite-dimensional exponential series then
has identical coefficients term by term, hence `exp(t A) I=I exp(t B)`.

For a proper local subspace `C`, the same conclusion for `f` requires
`B^k f` to remain in `C` and the first-order identity to hold for every such
iterate.  The Lean file formalizes this induction and the finite partial
exponential coefficient identity.

## Audit of R-493

R-493 declares `N(f)=max(2,m_f+1)` and proves its equality only for each
support-stabilized grade-blind cylinder.  Its packet has no source-authorized
invariant-core field, no all-iterate statement and no all-function operator
identity.  The R-484 hidden-diagonal defect `16/9` remains retained; first-order
support separation is not iteration closure.

Therefore the result is `HOLD_FOR_EVIDENCE`, not a negative result: the finite
bridge is proved conditionally, while its PAH premise is not present.  The
next evidence target is one source-authorized invariant/iterate packet or a
stronger all-function finite operator identity.

## Adversarial boundary

The derivative-at-zero shortcut, the replacement of the local cylinder by the
full finite function space, fixed-`N(f)` iteration, boundary-defect erasure and
anchored-n/physical promotion are all rejected.  The exact matrix examples in
the run JSON are regression oracles only and do not introduce a new PAH model.

No physical Pre-A, spacetime, event horizon, gravity, QFT, Yang--Mills,
continuum, mass-gap, cosmic-origin or TOE conclusion follows.
