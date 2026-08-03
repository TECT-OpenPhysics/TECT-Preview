# Pre-A C0-B equivariant causal-selection no-go certificate

**Candidate:** `PA-C0B-EQUIVARIANT-CAUSAL-SELECTION-NOGO-v0`  
**Authority:** T0 C0-B symmetry no-go; no TECT claim or tier change  
**Claim context only:** `C6-SPACETIME-SIGNATURE`  
**Task:** `T-054`  
**Issued:** 2026-08-03

## 1. Question and exact result

C0-B seeks to derive causal order rather than declare it.  The phrase
"structure emerges from a completely symmetric ground state" is incomplete,
because a natural selection rule must respect the state's automorphisms unless
a less symmetric relational state, boundary condition, or sector law is
supplied.

This certificate proves the following exact finite-orbit obstruction:

> A deterministic natural equivariant rule cannot compare two events in the
> same automorphism orbit of a finite substrate state.  In particular, a
> vertex-transitive finite state can select only the empty strict order.

The theorem does not exclude C0-B.  It proves that a viable C0-B model needs a
less symmetric relational state, an asymmetric boundary condition, or a
probabilistic sector-selection law only when its input lies in the excluded
transitive or exact reversal-invariant class.  Its realized order and
continuum meaning must still be derived.

## 2. General equivariant-selection theorem

Let `X` be a finite set with at least two elements, let `s` be a substrate
state, and let `G=Aut(s)` act on `X`.

Let a deterministic selector assign a strict partial order `C(s)` and be
natural under relabeling:

```text
C(g.s)=g.C(s),  g in G.
```

Because every `g` is an automorphism, `g.s=s`, so equivariance makes `C(s)` a
`G`-invariant relation.

### Theorem PA-C0B-E

No two points in the same `G`-orbit are comparable under `C(s)`.  Consequently,
if `G` is vertex-transitive on `X`, then `C(s)` is empty.

### Proof

Suppose `y=g.x` and `x C y`.  Because `g` is a permutation of a finite set, it
has finite order `m`.  Invariance and transitivity of `C` give

```text
x C g.x C g^2.x C ... C g^m.x=x,
```

A strict partial order is irreflexive, so this is impossible.  A transitive
action has one event orbit and hence permits no pair.

The finite hypothesis is load-bearing.  On the infinite set `Z`, translations
act transitively while the usual `<` is a nonempty translation-invariant strict
order.

There is also a stronger corollary that does not require finite `X`: if `G`
acts 2-transitively on ordered distinct pairs, one selected pair forces its
reverse and violates asymmetry.  The original ordered-pair-orbit proof is thus
retained as an infinite-safe special case.

## 3. Reversal-invariant arrow corollary

Suppose a substrate state is invariant under an orientation-reversal operation
and natural covariance requires the selected relation to become its opposite:

```text
C(Rs)=C(s)^op.
```

Under fixed event labels, or after an explicitly declared pullback
identification, if `Rs=s` then `C=C^op`.  A nonempty strict order cannot equal
its opposite, so again `C` is empty.  A unique deterministic time arrow in
this class therefore requires an orientation-bearing state, boundary
condition, or sector choice.

If reversal also applies a nontrivial event permutation `rho`, covariance can
instead read `C(Rs)=rho.C(s)^op`; the fixed-label corollary does not by itself
exclude a nonempty order in that broader setting.

This does not say that reversible microscopic laws cannot have arrow-bearing
states.  It says that the arrow is not uniquely selected by a state that is
itself exactly reversal invariant under the declared naturality rule.

## 4. Exact four-event exhaustion

For `X={0,1,2,3}`, the primary script constructs all 24 permutation matrices
and proves that the orbit of `(0,1)` is all 12 ordered off-diagonal pairs.  The
independent implementation represents every irreflexive relation by a 12-bit
mask and exhausts all

```text
2^12=4096
```

relations.  It independently finds:

```text
219 labelled strict partial orders,
2 S4-invariant irreflexive relations,
1 S4-invariant strict partial order: the empty order,
1 self-opposite strict partial order: the empty order.
```

The value 219 is used only as an enumeration oracle.  The general theorem is
the finite-orbit proof above and does not depend on that count.

The scripts also test the cyclic rotation group `C4` on `Z/4`.  It is
vertex-transitive but not 2-transitive: its three ordered-pair orbits, indexed
by differences `1,2,3`, each have size four.  Their eight possible unions are
exactly the `C4`-invariant irreflexive relations, and exhaustive checking again
finds only the empty invariant strict order.  This fixture proves that
2-transitivity is not needed for the finite theorem.

## 5. Positive symmetry-reduction controls

First take the two-element group `{id,(01)(23)}`.  Its event orbits are
`{0,1}` and `{2,3}`, and

```text
{0,1} x {2,3}
```

is an invariant nonempty strict order.  Thus a state may begin with a smaller
automorphism group; the theorem does not require a dynamical symmetry-breaking
mechanism in that case.

Add distinct relational marks

```text
tau=(0,1,4,9)
```

and define

```text
x C_tau y iff tau_x<tau_y.
```

This is a strict total order.  Both implementations verify its transitivity,
all 24 relabeling covariance identities, and

```text
C_(-tau)=C_tau^op.
```

The control shows that equivariance is not the problem.  A nontrivial
relational state breaks the full stabilizer and permits an order.  But the
marks and their orientation are additional state data.  A C0-B theory must
derive their distribution, phase selection, dynamics, and causal meaning; it
cannot merely rename them "time."

## 6. Random-sector boundary

A permutation-invariant probability distribution over strict orders can be
nontrivial.  The uniform distribution over the 24 total orders on four events
assigns

```text
Pr(x before y)=Pr(y before x)=1/2
```

for every pair.  The scripts verify the exact `12:12` counts.
They also verify that the support contains 24 distinct total orders and is
closed under every `S4` relabeling.

Therefore the no-go excludes deterministic equivariant selection from one
fully symmetric state, not stochastic symmetry breaking.  A random C0-B model
must still prove:

- what selects or conditions on one realized sector;
- why its relation represents intervention or propagation rather than merely
  a random label order;
- acyclicity, stability, and continuum control;
- the emergence of a common Lorentz cone and null boundary;
- independence from arbitrary labels and regulator choices.

## 7. Relation to established approaches

Causal-set sequential growth takes a discrete causal order and sequential
growth conditions as primitives.  It is therefore prior art for C0-A, not a
proof of the C0-B step sought here:

- D. Rideout and R. Sorkin, *A classical sequential growth dynamics for causal
  sets*, https://arxiv.org/abs/gr-qc/9904062 .

Quantum graphity begins with permutation-invariant graph degrees of freedom
and seeks low-energy graph locality.  It is important prior art for emergent
adjacency, but its Hamiltonian evolution is supplied and adjacency alone is
not a derived causal or null structure:

- T. Konopka, F. Markopoulou, and L. Smolin, *Quantum Graphity*,
  https://arxiv.org/abs/hep-th/0611197 .
- S. A. Wilkinson and A. D. Greentree, *Geometrogenesis under Quantum
  Graphity: problems with the ripening Universe*,
  https://arxiv.org/abs/1506.07588 .
- A. Hamma, F. Markopoulou, S. Lloyd, F. Caravelli, S. Severini, and K.
  Markstrom, *A quantum Bose-Hubbard model with evolving graph as toy model for
  emergent spacetime*, https://arxiv.org/abs/0911.5075 .

The latter explicitly studies dynamical local and causal structure, but its
Hamiltonian evolution is supplied.  It therefore calibrates the
`C0-B_spatial/C0-A_time` boundary rather than closing a full C0-B derivation.

Group-field and tensor models provide strong precedent for combinatorial
gluing, condensates, large-`N` behavior, and phase transitions.  Those results
do not by themselves supply a causal order or nullness:

- S. Gielen, D. Oriti, and L. Sindoni, *Cosmology from Group Field Theory
  Formalism for Quantum Gravity*, https://arxiv.org/abs/1303.3576 .
- T. Delepouve and R. Gurau, *Phase Transition in Tensor Models*,
  https://arxiv.org/abs/1504.05745 .

This bounded comparison is not a claim that no later or unexamined model has
a stronger result.  The finite invariant-order lemma is elementary and is not
claimed as scientific novelty.

## 8. Conditional escape contract and independent TECT gates

A future candidate whose input is finite and vertex-transitive or exactly
fixed-label reversal invariant must specify:

1. the premetric degrees of freedom without importing a causal or null
   vocabulary into their definition;
2. the exact relational state, boundary, or sector law that escapes the
   applicable no-go; a candidate with a smaller automorphism group must prove
   that actual group rather than invent a symmetry-breaking history;
3. whether the selected object is deterministic, quotient-valued, set-valued,
   conditioned, stochastic, or a coherent quantum sector.

Independently of the symmetry theorem, integration into the TECT Pre-A
programme requires:

4. an operational influence relation and a theorem proving its acyclicity or
   controlled exceptions;
5. a continuum limit with a unique stable Lorentz cone and null boundary;
6. a map from the resulting characteristic data to the PA-H1 algebra and state;
7. a common parent law from which PA-M2 appears only as a controlled
   low-energy effective functional.

Graph adjacency plus an externally supplied update tick is at most a
`C0-B_spatial/C0-A_time` hybrid.  It must not be counted as complete causal
emergence.

## 9. Scope and consequence for Pre-A

Proved:

- no two events in one finite automorphism orbit can be comparable under a
  deterministic natural strict-order selector, so a finite transitive input
  selects only the empty order;
- the 2-transitive ordered-pair corollary remains valid without finiteness;
- exact reversal invariance cannot uniquely select a nonempty strict arrow;
- a marked symmetry-broken control can select an equivariant total order;
- an invariant random ensemble can exist while leaving each pair unbiased
  before sector realization.

Not proved:

- that C0-B is impossible;
- that symmetry breaking alone gives physical causality;
- a microscopic relational dynamics, continuum spacetime, null boundary, or
  light speed;
- a physical state, gravity, event horizon, cooling history, or phase
  transition;
- the PA-H1-to-PA-M2 interface or completion of Pre-A.

The immediate constructive baseline is the separate C0-A reflection-positive
transfer certificate.  It is a temporal calibration with no spatial causal
structure, not a physical selection of C0-A and not evidence that C0-A is more
probable.  C0-B remains live; it currently bears the additional construction
burden stated above.

## 10. Devil's-advocate review

1. **The full permutation group or 2-transitivity is too strong.**
   **DISMISSED FOR THE FINITE THEOREM.**  Only event-orbit finiteness is used.
   The exact `C4` fixture is transitive but not 2-transitive.
2. **Spontaneous symmetry breaking can select an order.**
   **VALID AND RETAINED CONDITIONALLY.**  A transitive input needs an escape,
   while a state whose actual automorphism group already has multiple orbits
   need not possess a dynamical symmetry-breaking history.
3. **A symmetric probability law over orders is a counterexample.**
   **DISMISSED BY SCOPE.**  The theorem concerns a deterministic selector.  The
   random ensemble is explicitly retained and audited.
4. **A total order is not a Lorentzian causal order.**
   **UPHELD.**  The marked control demonstrates selection only; no cone,
   locality, or nullness follows.
5. **Graph adjacency is already causal influence.**
   **UPHELD AS AN OVERCLAIM RISK.**  Influence requires an update/intervention
   rule and continuum theorem; adjacency alone is spatial relation data.
6. **The result rules out causal sets or graphity.**
   **REJECTED.**  Causal sets choose order as primitive, while graphity supplies
   relational states and an external Hamiltonian.  Neither is invalidated.
7. **The four-event enumeration proves the general theorem.**
   **REJECTED.**  The general proof is the ordered-pair orbit argument; the
   enumeration is an independent finite certificate.

## 11. Reproducible evidence

```text
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_c0b_equivariant_causal_selection_nogo.py
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_c0b_equivariant_causal_selection_nogo_independent.py
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_c0b_equivariant_causal_selection_nogo_verify.py
```
