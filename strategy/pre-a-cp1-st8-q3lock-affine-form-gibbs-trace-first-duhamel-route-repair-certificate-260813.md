# R-167 v3.7 certificate: affine-form Gibbs-trace first-Duhamel route repair

Date: 2026-08-13  
Task: T-054  
Exploration: EXP-000841  
Claim-bearing: false (T0 route work)  
PDF: none issued

## 1. Exact scoped result

This certificate closes only
`PA-CP1-ST8-Q3LOCK-AFFINE-FORM-GIBBS-TRACE-HALF-INTERVAL-L1-FIRST-DUHAMEL-AND-SPECTRAL-RITZ-REMOVAL`.

Let `h>=0` be self-adjoint and suppose `exp(-t h)` is trace class for every
`t>0`. Fix `a,b>=0`, put

```text
B = a h + b I,
V = B^(1/2) C B^(1/2),     C=C*,     ||C||<=1,
```

where the second equality is understood in the quadratic-form sense before
Gibbs dressing. For fixed `beta>0` define

```text
A_beta = Tr[B^(1/2) exp(-beta h/2)],
K_beta(s) = exp[-(beta-s)h] V exp(-s h),   0<s<beta.
```

Then `A_beta<infinity`, `K_beta(s)` is trace class, and

```text
||K_beta(s)||_1
 <= A_beta [sqrt(b)+sqrt(a/(2 e s))]                    (0<s<=beta/2),
 <= A_beta [sqrt(b)+sqrt(a/(2 e (beta-s)))]            (beta/2<=s<beta).
```

Consequently

```text
integral_0^beta ||K_beta(s)||_1 ds
 <= A_beta [beta sqrt(b)+2 sqrt(a beta/e)].             (1.1)
```

If `Pi_M` are increasing finite-rank spectral projections of `h`, strongly
converging to the identity, then

```text
K_(beta,M)(s) := Pi_M K_beta(s) Pi_M -> K_beta(s)
```

both pointwise in trace norm and in `L1((0,beta);S1)`. Hence the compressed
first Duhamel operator integrals converge in trace norm to the full operator
integral. In addition,

```text
Tr K_beta(s) = Tr[C B exp(-beta h)],
Tr integral_0^beta K_beta(s) ds = beta Tr[C B exp(-beta h)].   (1.2)
```

This is a first-insertion theorem, not an all-order contour theorem.

## 2. Finiteness of the Gibbs trace factor

For every `epsilon>0` there is a finite scalar constant `c_epsilon` such that

```text
sqrt(a x+b) <= c_epsilon exp(epsilon x),    x>=0.
```

Taking `epsilon<beta/2` and using the spectral calculus proves
`A_beta<infinity` from the assumed heat-trace property. A more useful explicit
bound follows from

```text
sqrt(a x+b) <= sqrt(a)sqrt(x)+sqrt(b),
sqrt(x) exp(-beta x/2)
 <= sqrt(2/(e beta)) exp(-beta x/4).
```

Therefore, with `Z_h(t)=Tr exp(-t h)`, one has

```text
A_beta <= sqrt(a)sqrt(2/(e beta)) Z_h(beta/4)
          +sqrt(b) Z_h(beta/2).                           (2.1)
```

The factor `2/(e beta)` is not copied: it is the exact maximum of
`x exp(-beta x/2)`, attained at `x=2/beta`.

## 3. The half-interval proof

For `0<s<=beta/2`, write

```text
K_beta(s)=X_s C Y_s,
X_s=exp[-(beta-s)h]B^(1/2),
Y_s=B^(1/2)exp(-s h).
```

Since `beta-s>=beta/2`, positivity and commutation give

```text
||X_s||_1=Tr[B^(1/2)exp[-(beta-s)h]]<=A_beta.
```

The spectral calculus and `sqrt(u+v)<=sqrt(u)+sqrt(v)` give

```text
||Y_s||
 = sup_(x>=0) sqrt(a x+b) exp(-s x)
 <= sqrt(b)+sqrt(a) sup_(x>=0) sqrt(x)exp(-s x)
 = sqrt(b)+sqrt(a/(2 e s)).
```

The trace-ideal inequality `||X C Y||_1<=||X||_1||C||||Y||` proves the first
half of (1.1). For `beta/2<=s<beta`, instead use
`exp[-(beta-s)h]B^(1/2)` in operator norm and
`B^(1/2)exp(-s h)` in trace norm. This proves the reflected estimate.
Integrating the two square-root singularities gives exactly

```text
2 integral_0^(beta/2) sqrt(a/(2 e s)) ds
 = 2 sqrt(a beta/e),
```

while the two constant pieces total `beta sqrt(b)`. This proves (1.1).

This asymmetric factorization is the essential repair. The symmetric
Schatten-Holder majorant from R-167 v3.6 can behave like `s^-1` and fail to be
integrable even though the one-sided majorant here behaves only like
`s^-1/2`.

## 4. Spectral Ritz removal and trace identity

For every trace-class operator `T`, strong convergence `Pi_M->I` implies

```text
||Pi_M T Pi_M-T||_1 -> 0.
```

Thus the convergence holds pointwise for `T=K_beta(s)`. Moreover

```text
||Pi_M K_beta(s) Pi_M-K_beta(s)||_1<=2||K_beta(s)||_1,
```

and the right side has the integrable majorant in Section 3. Bochner dominated
convergence proves `L1((0,beta);S1)` convergence and therefore convergence of
the operator integrals. Strong `S1` measurability follows first for the finite
spectral compressions and then for `K_beta(s)` from their pointwise trace-norm
limit, so the Bochner integral is fully specified.

All products used in the cyclic trace calculation are trace-ideal products.
Since `B` commutes with `h`, cyclicity gives

```text
Tr[exp[-(beta-s)h]B^(1/2) C B^(1/2)exp(-s h)]
 = Tr[C B exp(-beta h)],
```

which proves (1.2).

## 5. Exact Q3 edge application

For one exact full-oscillator Q3 reference edge at fixed `N`, the inherited
R-167 v1.9 Section 27 relative-form certificate, reused in the v3.5 Section 8
positive-time theorem, supplies

```text
-B_(e,N) <= V_(e,N) <= B_(e,N),
B_(e,N)=alpha_N h^0_(e,N)+beta_N I.
```

The Kato contraction factorization therefore has precisely the affine form in
Section 1 with `a=alpha_N` and `b=beta_N`. The confining reference edge has
compact resolvent and finite heat trace. Hence, for every fixed `N` and every
physical `beta>0`, the full-oscillator first Duhamel edge coefficient is trace
class and is the trace-norm limit of its spectral Ritz compressions. The extra
`g_beta in L1` premise in the v3.6 generic reduction is unnecessary for this
affine Q3 form envelope.

The commuting positive edge terms obey the inherited bound

```text
Z_(0,e,N)(t)<=Z_(k_N)(t/6)^2.
```

Combining this with (2.1) gives the explicit majorant

```text
A_(beta,e,N)
 <= sqrt(alpha_N)sqrt(2/(e beta)) Z_(k_N)(beta/24)^2
    +sqrt(beta_N) Z_(k_N)(beta/12)^2.                    (5.1)
```

The cutoff dimension `M` is absent from (5.1). Uniformity in `N` would require
separate uniform heat-trace and relative-form estimates and is not asserted.

## 6. Exact executable fixture

Take

```text
h=diag(0,1,4),   a=2,   b=3,   beta=log(4),
B=diag(3,5,11),
C e_0=e_2,   C e_2=e_0,   C e_1=-e_1.
```

Then `C=C*`, `C^2=I`, and the only nonzero entries of `V` are

```text
V_02=V_20=sqrt(33),   V_11=-5.
```

Direct singular-value calculation yields

```text
||K_beta(s)||_1
 = sqrt(33)[exp(-4s)+exp(-4(beta-s))]+5exp(-beta),

integral_0^beta ||K_beta(s)||_1 ds
 = 255sqrt(33)/512+5log(4)/4,                            (6.1)

Tr integral_0^beta K_beta(s) ds = -5log(4)/4.           (6.2)
```

The upstream trace factor and theorem bound are

```text
A_beta=sqrt(3)+sqrt(5)/2+sqrt(11)/16,
A_beta[log(4)sqrt(3)+2sqrt(2log(4)/e)].                 (6.3)
```

The latter strictly exceeds (6.1). The rank-two spectral compression retains
only the middle diagonal entry, so its exact integrated tail is
`255sqrt(33)/512`; the rank-three tail is zero. Both the symbolic and the
stdlib-only verifiers derive these values from the input spectrum and matrix,
not from copied outputs.

## 7. Relation to the v3.6 negative result

The registered negative
`NG-2026-08-13-PRE-A-ST8-Q3LOCK-POINTWISE-POSITIVE-TIME-TRACE-CLASS-AUTOMATIC-SHORT-TIME-L1-DOMINATION`
remains correct and immutable. Its fixture proves that the symmetric
Schatten-Holder function
`sqrt(F_B(2s)F_B(2(beta-s)))` need not be integrable. It explicitly did not
rule out a sharper transition-resolved estimate. The present half-interval
factorization supplies such an estimate for `B=a h+bI` and therefore repairs
the route without contradicting the negative.

The older
`NG-2026-08-13-PRE-A-ST8-Q3LOCK-FIXED-POSITIVE-TIME-ENERGY-DRESSED-TRACE-CONTROL-AUTOMATIC-DFFR-CONTOUR-ENTRY`
also remains correct: first-coefficient integrability alone supplies neither
the higher time-simplex estimates nor the contour entropy summation required
by DFFR.

## 8. Devil's-advocate audit

1. **Objection: the endpoint singularity is merely hidden in `A_beta`.**
   **DISMISSED.** `A_beta` is evaluated at fixed positive time `beta/2` and is
   finite by the heat-trace hypothesis. All endpoint dependence is explicitly
   `s^-1/2` or `(beta-s)^-1/2`, both integrable.

2. **Objection: the proof silently uses an HS-HS estimate and loses spectral
   multiplicity.** **DISMISSED.** The load-bearing inequality is the
   `S1-operator-S1` ideal product `||X C Y||_1<=||X||_1||C||||Y||` on each half
   interval. Spectral multiplicity is fully retained inside `A_beta`.

3. **Objection: form-bounded `V` need not be an operator.** **DISMISSED with
   scope.** The Kato factorization defines the Gibbs-dressed product through
   `B^(1/2) C B^(1/2)`. Sections 2-3 prove that the dressed factors form a
   trace-class product. No undressed boundedness of `V` is claimed.

4. **Objection: first order implies the DFFR contour expansion.** **UPHELD.**
   Higher insertions, transition-resolved sums, small-simplex combinatorics and
   contour entropy remain unproved. This is why all parent gates remain OPEN.

5. **Code-discipline objection: constants or units could be copied.**
   **DISMISSED for the fixture.** The fixture is dimensionless exact test data.
   Both computation lanes derive `B`, `V`, singular values, integrals, trace
   identity, rank tails and the factor `2/(e beta)` from labelled inputs. The
   integrated verifier adds an AST/import firewall and rejects copied derived
   assignments; those checks supplement rather than replace this proof.

## 9. Scope and next gate

EXP-000841 establishes R-167 v3.7 as an additive T0, claim-nonbearing route
repair. It proves no all-order Duhamel or contour convergence, no DFFR
transition-norm entry or phase-branch identification, no `N`-uniform heat
trace, no common phase-independent real-time alpha, no algebraic ground-state
identity for the time-zero candidates, no purity or complete phase
classification, no broken-sector GNS gap, no continuum or regulator removal,
no mass gap, physical vacuum or empty-space comparison, Round-1, C6, CP1,
physical Sector A or Pre-A. All five active parent gates and the historical
beta-infinity gate remain OPEN. No v3.7 PDF is issued.

The next analytic step is either an all-order energy-weighted Duhamel/simplex
majorant, or the independent construction of the common spatial dynamics and
the algebraic-ground identification needed by the already registered
full-oscillator tangent candidates.
