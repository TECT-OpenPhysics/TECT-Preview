# R-362 finite local-Q2 replica-folding certificate

Date: 2026-08-27  
Exploration: EXP-001204  
Task: T-054  
Host claim: C6-SPACETIME-SIGNATURE  
Status: T0 claim-nonbearing exact finite reduction; no parent gate closes

## 1. Question

EXP-001203 proposed folding the forward/backward real-time history before
estimating its local likelihood. The first question is whether this folding
already requires a positive Euclidean path measure, or whether the measured
collision quantity has a direct positive operator realization.

## 2. Exact finite theorem

Let `rho` be a faithful finite-dimensional reference state, `sigma` an output
state, and `{E_j}` a finite local PVM. Set

```text
p_j = Tr(E_j rho) > 0,
q_j = Tr(E_j sigma),
K_(rho,E) = sum_j p_j^(-1) E_j tensor E_j.
```

Then

```text
Q2(q||p)
  = sum_j q_j^2 / p_j
  = Tr[K_(rho,E) (sigma tensor sigma)].
```

The equality follows outcome by outcome from

```text
Tr[(E_j tensor E_j)(sigma tensor sigma)] = Tr(E_j sigma)^2.
```

`K_(rho,E)` is positive. If `sigma=U W rho W* U*`, cyclicity gives the exact
Heisenberg form

```text
Q2 = Tr[(rho tensor rho)
        (W*U* tensor W*U*) K_(rho,E) (UW tensor UW)].
```

The equality constant is one. No path-count, Hilbert-dimension, volume, or
history-length factor is introduced by the folding itself. For `sigma=rho`,
the value is exactly one.

## 3. Common-weight phase mixture

For two common nonnegative weights `w1,w2`, positive reference probabilities
`p1,p2`, and output probabilities `q1,q2`, the pointwise convexity gap is

```text
w1 q1^2/p1 + w2 q2^2/p2
  - (w1 q1+w2 q2)^2/(w1 p1+w2 p2)
= w1 w2 (p2 q1-p1 q2)^2
  / [p1 p2 (w1 p1+w2 p2)] >= 0.
```

Summing outcomes proves common-weight mixture convexity of measured Q2. This
does not prove that the actual limiting Q3 history preserves phase weights.
If it does not, the phase-label likelihood remains a separate obligation.

## 4. Diagonal peel and the surviving interaction

An outermost unitary commuting with every `E_j` leaves all measured
probabilities unchanged. Hence a pure coordinate source or pure coordinate
bond history peels exactly.

This statement cannot be iterated blindly through onsite layers. After the
collision witness is conjugated by an onsite kinetic unitary, the bond need
not commute with the moved witness. The actual Q3 fixture has a minimum
two-copy interspersed commutator Frobenius witness

```text
0.04815793620932884 > 0.
```

Thus R-362 removes the artificial real-time positivity problem and terminal
diagonal suffixes, but it does not remove the onsite/bond collar problem.

## 5. Verification

The primary lane checks every prefix of both term orders, both time signs,
both history adjoints, both source supports and signs, two beta values, both
sites, and oscillator cutoffs 3 and 4. The independent lane rebuilds the
oscillator, Q3 Hamiltonian, Gibbs states, split products, PVM, partial traces,
replica witness, and mixture identities without importing the primary.

Key stored values:

- 512 history contexts and 1024 local site rows;
- primary 2069/2069 assertions PASS;
- independent 2067/2067 assertions PASS;
- integrated 48/48 assertions PASS;
- Lean R362 PASS;
- maximum direct-versus-replica error `3.3306690738754696e-15`;
- maximum Heisenberg-form error `2.220446049250313e-16`;
- maximum source invariance error `3.3306690738754696e-16`;
- maximum pure-bond invariance error `4.440892098500626e-16`;
- maximum primary/independent compared-field difference `1.554e-15`;
- two-reference common-weight mixture slack at least
  `2.1153745421997883e-11` on the declared fixture.

Reproduce with:

```powershell
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_local_q2_replica_folding.py
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_local_q2_replica_folding_independent.py
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_local_q2_replica_folding_verify.py
```

## 6. Adversarial review

1. **Euclidean positivity objection — VALID with correction.** The exact
   positive object is a two-copy operator witness. No positive Euclidean path
   measure or reflection-positive collar has been constructed.
2. **Hidden dimension factor — DISMISSED for folding only.** The identity has
   equality constant one. The evolved witness may still have cutoff-dependent
   norm or state-weighted tails.
3. **All bonds disappear — UPHELD as false.** Only an outermost diagonal layer
   peels. The nonzero interspersed commutator proves that an onsite-conjugated
   witness can feel a later bond.
4. **Finite-to-uniform promotion — UPHELD.** Cutoffs 3 and 4 and volume 2 do
   not prove a uniform collar estimate.
5. **Phase theorem — UPHELD.** The mixture inequality assumes common weights;
   phase-weight preservation and within-phase influence contraction are open.
6. **Lean promotion — UPHELD.** Lean proves the finite-sum algebra, not the
   Q3 matrix spectra, partial traces, thermodynamic limit, or QFT interfaces.

## 7. Boundary and next gate

R-362 closes FI-2a only: positive finite operator folding. FI-2b remains the
load-bearing target. Center the witness by its reference expectation, peel
terminal diagonal layers, and prove a state-weighted shell commutator or
conditional-expectation estimate for the onsite-interspersed doubled witness
with constants uniform in source, cutoff, volume, prefix, and allowed
exhaustion shape. No common core, common alpha, OS/KMS/GNS identification,
mass gap, continuum, C6, Sector-A, or Pre-A closure follows here.

