# R-167 v2.8 proof certificate: fixed-cluster large-N physical-point local SW and the Cb-multiplier boundary

**Date:** 2026-08-13  
**Task:** T-054  
**Exploration:** EXP-000831, continuing EXP-000828  
**Claim context:** C6-SPACETIME-SIGNATURE  
**Tier:** T0; `claim_bearing: false`  
**Result:** R-167 v2.8, additive to v2.7  
**Manifest:** `strategy/pre-a-cp1-st8-q3lock-fixed-cluster-large-n-physical-point-and-cb-multiplier-c0-boundary-manifest.json`

## 1. Exact conclusion

This certificate closes exactly one additional child:

`PA-CP1-ST8-Q3LOCK-ZERO-SOURCE-FIXED-COMPLETE-SPECTRAL-CLUSTER-RITZ-LARGE-N-PHYSICAL-LAMBDA-ONE-LOCAL-SW-STRETCHED-EXPONENTIAL-EXTENSIVE-REMAINDER`.

On the registered zero-source periodic model corridor
`r=-N^4`, `c=N^-4`, fix one complete finite onsite spectral-cluster Ritz
family.  For all sufficiently large `N`, the exact endpoint `lambda=1` of the
Ritz-restricted interpolation satisfies the R-167 v2.7 local-SW smallness
conditions.  One admissible order proportional to `N` then gives a
volume-extensive error bounded by `exp(-kappa_M N)`.

The certificate also registers

`NG-2026-08-13-PRE-A-ST8-Q3LOCK-NONCONSTANT-CB-CONFIGURATION-MULTIPLIER-FULL-HAMILTONIAN-POINT-NORM-C0`.

For every nonconstant bounded continuous configuration multiplier, the exact
finite-volume full Hamiltonian orbit is not point-norm continuous at zero.
For real multipliers its norm jump has the exact small-time limit equal to the
oscillation.  This strictly strengthens, but does not alter, the immutable
v2.7 raw-configuration-Weyl record.

## 2. Literature and inherited authority

The semiclassical input is B. Simon, *Semiclassical analysis of low lying
eigenvalues I. Non-degenerate minima: asymptotic expansions*, Ann. IHP 38
(1983), 295--308, with its published erratum.  Fixed-eigenvalue asymptotics
and complete harmonic clusters are used; this certificate does not claim a
new operator-norm convergence theorem for spectral projectors.

The local-SW input is S. Bravyi, D. P. DiVincenzo and D. Loss,
*Schrieffer--Wolff transformation for quantum many-body systems*, Annals of
Physics 326 (2011), 2793--2826, arXiv:1105.0675.  Section 4.4, Proposition
4.2 and Lemma 4.2 are used through the fixed-order and admissible
optimal-scale theorem already proved in R-167 v2.7.  The present new step is
to make the proof witnesses uniform in `N` while the spectral-cluster label
`M` remains fixed.

## 3. Complete spectral-cluster Ritz family

Set `g=lambda=chi=hbar=1`, `r=-N^4`, `c=N^-4`, and

```
E_star=N^8,  h=N^-6,
h_site,N=E_star K_h,
K_h=-h^2 Delta/2+W_1.
```

Let `nu_0<=nu_1<=...` be the limiting harmonic excitation levels with the
full two-well multiplicities.  Fix `d_M>=4` at a complete cluster endpoint,
so `nu_(d_M-1)<nu_(d_M)`, and choose
`nu_(d_M-1)<C_M<nu_(d_M)`.  Define

```
Pi_(M,N)=1_[(-infinity,E_star h C_M)]
          (h_site,N-epsilon_(0,N)).
```

For sufficiently large `N`, fixed-eigenvalue asymptotics give
`rank Pi_(M,N)=d_M`.  The projector preserves parity and `Aut(Q3)` and
commutes with the onsite Hamiltonian.  It is the whole finite-dimensional
onsite Ritz Hilbert space used by BDL.  It is not the SW low block.

Inside `ran Pi_(M,N)`, let

```
P_(0,N)=|phi_(0,N)><phi_(0,N)|+|phi_(1,N)><phi_(1,N)|,
Q_(M,N)=Pi_(M,N)-P_(0,N).
```

Thus the retained SW low space has rank two.  The complete first excited
cluster is present because `d_M>=4`.

Let `e_well` be the one-well ground harmonic energy.  Choose
`D_M>e_well+C_M`.  The same fixed-level asymptotics, now including the
absolute ground energy, give an existential `N_M` such that

```
||h_site,N Pi_(M,N)|| <= D_M N^2                  (3.1)
```

for `N>=N_M`.  Equation (3.1), rather than a shifted spectral-width bound, is
load bearing below.

## 4. Gap and uniform BDL proof witnesses

Let `P_(1,N)=|phi_(1,N)><phi_(1,N)|` and set

```
k_(M,N)=Pi_(M,N)
        [h_site,N-epsilon_(0,N)-delta_(1,N)P_(1,N)]
        Pi_(M,N).
```

Its kernel is exactly `ran P_(0,N)`.  The inherited semiclassical estimate
gives, after increasing `N_M`,

```
Gamma_N=epsilon_(2,N)-epsilon_(0,N) >= N^2/sqrt(2).
```

Subtracting the positive exponentially small first splitting and
(3.1) give

```
||k_(M,N)|| <= D_M N^2,
||k_(M,N)||/Gamma_N <= sqrt(2)D_M.                (4.1)
```

Normalize the augmented edge interaction by its local strength
`J_(M,N)`.  The normalized interaction has locality two, degree six and
strength one.  Rerun the BDL Proposition 4.2/Lemma 4.2 majorant with the
right side of (4.1).  Every proof constant is then bounded in terms of the
fixed data `M`, `D_M`, locality, degree and decomposition.  Hence one may
choose `alpha_M,beta_M>0` common to all sufficiently large `N`.  This is a
uniformization of the displayed BDL proof, not an inference from unrelated
pointwise existential constants.  No uniformity in `M` is asserted.

## 5. Exact coordinate and bond bounds

For `y>=0`,

```
(y-1)^2+5/4-y=(y-3/2)^2 >= 0.
```

Summing the eight coordinate inequalities and using the nonnegative lock
term gives

```
|x|^2 <= 4W_1+10.                                  (5.1)
```

Because `W_1<=K_h` as forms and `Pi_(M,N)` is a spectral subspace of `K_h`,
(3.1) and (5.1) imply

```
||Pi_(M,N)|q|^2Pi_(M,N)||
 <= N^4[10+4D_M N^-6].                             (5.2)
```

For one spatial bond
`B_e=(c/2)|q_x-q_y|^2`, the elementary form inequality
`|q_x-q_y|^2<=2|q_x|^2+2|q_y|^2` gives

```
||B_(e,M,N)|| <= 20+8D_M N^-6.                     (5.3)
```

On the periodic graph with `z=6`, allocate the onsite splitting with the
same incident weights `omega=1/6` as R-167 v2.6.  The two endpoint shares add
at most `delta_(1,N)/3` to (5.3).  Therefore

```
J_(M,N)
 <= 6[20+8D_M N^-6+delta_(1,N)/3]
 = 120+48D_M N^-6+2delta_(1,N)
 <= 121                                                   (5.4)
```

after one final increase of the existential `N_M`.

## 6. The physical interpolation endpoint and the large-N remainder

At `lambda=1`, the augmented edge allocation restores the exact zero-source
Ritz-restricted Hamiltonian. With
`Pi_Lambda=Pi_(M,N)^(tensor Lambda)`, the identity is

```
H_(M,N)(1)=Pi_Lambda[H_N-|Lambda|epsilon_(0,N)]Pi_Lambda.
```

The scaled coupling is `eta=J_(M,N)<=121`. If

```
N^2 > 3872sqrt(2) max(alpha_M,beta_M^-1),           (6.1)
```

then (4.1) and (5.4) imply both strict v2.7 smallness inequalities

```
J_(M,N)<beta_M Gamma_N/32,
J_(M,N)<Gamma_N/(32alpha_M).
```

Use the v2.7 admissible order

```
n_N=floor sqrt[beta_M Gamma_N/(8J_(M,N))].          (6.2)
```

It obeys

```
n_N >= floor[N sqrt(beta_M/(968sqrt(2)))].          (6.3)
```

The v2.7 remainder and `J_(M,N)<=121` now yield

```
|E_0(H_(M,N)(1))-E_0(H_eff,loc^(n_N))|
 <= 1936alpha_M|Lambda|
    exp[-(ln 8)N sqrt(beta_M/(968sqrt(2)))].         (6.4)
```

This is the new closed child.  Here `physical lambda=1` means only the exact
interpolation endpoint of the zero-source Ritz-restricted Hamiltonian along
the registered asymptotic model corridor `r=-N^4,c=N^-4`.  It is not a
physical-world parameter claim, not a certified finite-`N` instance, and not
full-oscillator cutoff removal.

## 7. Exact arithmetic fixture

For a synthetic worst-case theorem oracle set

```
alpha=beta=1, J=121, N=74, Gamma_lower=5476/sqrt(2).
```

The strict-threshold margin is

```
1369^2-2(968^2)=113>0.
```

Equation (6.2) gives `n_*=2`, while

```
rho=Gamma_lower/4=1369/sqrt(2),
J/rho=121sqrt(2)/1369<1/8.
```

The exact fixed-order BDL bound, not the exponential envelope, is

```
2J(J/rho)^2 |Lambda|
 = 7086244/1874161 |Lambda|.                        (7.1)
```

This fixture does not certify `alpha_M=beta_M=1` for Q3 and does not certify
`N_M<=74`.

## 8. Every nonconstant Cb configuration multiplier has a norm jump

Fix a finite Q3 volume and write

```
H=P^2/(2chi)+V(Q),
U_t=exp(-itH/hbar),
alpha_t(A)=U_t^*AU_t,
```

where `V` is the exact real semibounded coercive Q3 polynomial.  Let
`f in C_b(R^d)` and let `M_f` denote multiplication by `f`.

Fix `x,y` and a normalized Gaussian `phi_(x,sigma)` centered at `x`.  For
`t!=0`, boost it by

```
p_t=chi(y-x)/t.
```

Under the free flow, its center at time `t` is `y`; its variance differs from
the initial fixed variance by `O(t^2)`.  For `|s|<=|t|`, the Galilean centers
remain on the compact segment joining `x` and `y`.  Polynomial multiplication
on this translated Gaussian family has a uniform `L2` bound.  Duhamel's
formula therefore gives

```
||(U_t-U_t^0) exp(ip_t.Q/hbar)phi_(x,sigma)||=O(|t|).
```

Since `M_f` is bounded, the same estimate transfers its expectation.  Thus
the moving-vector expectation of
`alpha_t(M_f)-M_f` tends to

```
(f*g_sigma)(y)-(f*g_sigma)(x).
```

First let `t->0`, then `sigma->0`, and then take the supremum over `x,y`.
This proves

```
liminf_(t->0,t!=0)||alpha_t(M_f)-M_f||
 >= diam f(R^d).                                    (8.1)
```

For real `f`, subtract the scalar midpoint
`c=(sup f+inf f)/2`.  Automorphisms fix scalars, so

```
||alpha_t(M_f)-M_f||
 <= 2||f-c||_infinity=osc(f).
```

Together with (8.1),

```
lim_(t->0,t!=0)||alpha_t(M_f)-M_f||=osc(f)          (8.2)
```

for every bounded continuous real nonconstant `f`.

Taking `f(q)=exp(i xi.q)` gives range diameter two, so (8.1) and the unitary
upper bound recover the v2.7 sharp Weyl limit.  The new negative strictly
strengthens that special case while preserving the old record as immutable
history.

## 9. Boundaries and surviving routes

The fixed-cluster result does not contradict the registered ordinary-norm
Ritz-cutoff obstruction.  That negative concerns automatic uniformity as
`M->infinity`; this theorem keeps `M` fixed and lets `N` grow.

The following remain open:

- an arbitrary Ritz family or `M`-uniform/full-oscillator cutoff removal;
- a standard-SW growing-order theorem or a convergent all-order transform;
- fifth/all-order oscillator QPS control, phase transfer, and a GNS gap;
- an actual all-shape common alpha, KMS identification, or spatial local net;
- a certified physical finite-`N` instance or a physical-world parameter;
- regulator removal, continuum, physical empty-space comparison, Round-1,
  C6, CP1, physical Sector A, and Pre-A.

The multiplier obstruction is finite-volume and point-norm only.  It does not
reject strong or strong-star dynamics, local-strict or energy topology,
temporal/energy/resolvent smears, smaller continuous-element algebras,
fixed-beta OS envelopes, or common-alpha existence on another carrier.

All five parent gates remain OPEN.

## 10. Devil's-advocate audit

1. **Objection:** a shifted Ritz-width bound was used as an absolute bound on
   `W_1`. **DISMISSED after repair.**  The theorem defines
   `D_M>e_well+C_M` and uses the absolute estimate (3.1).
2. **Objection:** `Pi_(M,N)` was confused with the rank-two SW low block.
   **DISMISSED after repair.**  `Pi_(M,N)` is the complete finite onsite Ritz
   space; `P_(0,N)` is the rank-two low projector inside it.
3. **Objection:** pointwise BDL constants need not be uniform in `N`.
   **DISMISSED with an explicit proof uniformization.**  The recurrence is
   rerun with fixed locality, degree and strength and the common ratio bound
   `sqrt(2)D_M`.
4. **Objection:** the `N=74` fixture certifies an actual Q3 parameter point.
   **UPHELD as a wording risk and mitigated.**  It is labelled a synthetic
   theorem-arithmetic oracle; all Q3 witnesses and onsets remain existential.
5. **Objection:** a moving high-momentum vector contradicts ordinary strong
   continuity. **DISMISSED.**  Operator norm permits a `t`-dependent unit
   vector; no fixed-vector strong-continuity claim is contradicted.
6. **Objection:** (8.1) proves common-alpha nonexistence. **UPHELD as an
   overclaim and rejected.**  It removes sharp nonconstant coordinate
   multipliers from a point-norm-C0 full-Hamiltonian carrier only.

## 11. Reproduction

Run from the repository root:

```powershell
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_fixed_cluster_large_n_physical_point_and_cb_multiplier_c0_boundary.py --self-test --no-store
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_fixed_cluster_large_n_physical_point_and_cb_multiplier_c0_boundary_independent.py --self-test --no-store
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_fixed_cluster_large_n_physical_point_and_cb_multiplier_c0_boundary_verify.py --staged --no-store
```

No per-lemma or intermediate v2.8 PDF is issued.  The checkpoint synthesis is
deferred until the next logical gate-level checkpoint.
