# Conditional Q3 onsite shifted-potential operator/source bridge

## Scope

EXP-001042 constructed the formal coefficient completion but did not map it to
an operator graph norm.  This checkpoint takes the already declared local
one-sided graph hypotheses as inputs:

```text
||q^m A^(-3/4)|| <= M_m,  m=0,1,2,3.
```

For the actual onsite Q3 difference

```text
D_on(q,a) = g*(q^4-(q-a)^4)/4
           = g*q^3*a - 3g*q^2*a^2/2 + g*q*a^3 - g*a^4/4,
```

the triangle inequality gives the conditional one-step source majorant

```text
||D_on(q,a) A^(-3/4)||
 <= g*(M_3*|a| + 3*M_2*|a|^2/2 + M_1*|a|^3 + |a|^4/4).
```

The same absolute coefficient rate holds for reversing the scalar source
orientation.  This is a one-coordinate, one-sided statement only.

## Exact fixture

Use the declared graph inputs `g=3/5`, `gamma=1/128`, `kappa=2`, source radius
`S=1/4`, and time `t=1/8`.  The ratio `kappa/gamma=256=4^4`, so the derived
moment ladder is

```text
M_0=1, M_1=4, M_2=16, M_3=64.
```

The exact source rate is

```text
B_on = (3/5)*(64/4 + (3/2)*16/4^2 + 4/4^3 + 1/(4*4^4))
      = 10791/1024,
t*B_on = 10791/8192.
```

The primary SymPy lane and independent Fraction lane each pass 20/20.  The
integrated verifier passes 28/28 and Lean R225 passes the rational fixtures.

## Boundary

The graph bounds are hypotheses of this bridge; no unbounded-operator domain
or self-adjointness proof is added here.  The Q3 edge term has two field
coordinates and is not covered.  Even for the onsite term, one-step bounds do
not compose into a Duhamel/history estimate without A-power transport and a
two-sided product theorem.  Spatial first-passage, all-shape exhaustion,
common alpha, KMS/OS reconstruction, GNS gap, continuum, C6, Sector A and
Pre-A remain open.

## Adversarial review

- **Graph hypotheses — UPHELD:** `M_m` are declared inputs, not proved by this
  script.
- **Ordering — UPHELD:** only `q^m A^(-3/4)` in the stated one-sided order is
  used; adjoint and reverse operator orders are not inferred.
- **Edge omission — UPHELD:** no multivariate Q3-edge or spatial-bond map is
  hidden inside the onsite calculation.
- **History composition — UPHELD:** a triangle bound for one factor is not an
  A-power transport or repeated-history theorem.
- **Lean promotion — UPHELD:** R225 checks rational fixtures only.
- **QFT promotion — UPHELD:** no common alpha, OS/KMS, GNS, continuum, C6,
  Sector A or Pre-A conclusion follows.

This is a T0 claim-nonbearing conditional checkpoint and no PDF is issued.
