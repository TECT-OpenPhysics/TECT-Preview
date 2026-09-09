# PAH-OMC-020 fixed-n stationary semigroup passage

This certificate records one bounded proof checkpoint for the unchanged
PAH-001 model. It is a fixed-n, j-to-infinity result only. The anchored
n passage, R-512 minimal-form selection, and every physical interpretation
remain separate open questions.

## Frozen source and scope

The source functional, directed move labels, midpoint rates, labelled Gibbs
state, terminal-square convention, and external Markov time are exactly those
of PAH-001 and the OMC-016/OMC-018 records. The regulator path is
h_j=2^{-j}, R_j=2^j, M_j=2^{2j}; the j limit is taken at fixed
n. No rate, mobility, state, carrier, counterterm, time scale, or limit
order is introduced here.

Pinned parent hashes:

* `strategy/pa-hyp/PAH-001-v1.json`
  `03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37`
* `strategy/pa-hyp/PAH-OMC-016-uniform-result-v1.json`
  `6ba124f6b102022c0e4995c005d9275ce51aaa51a52a6f274ef73254d444bf97`
* `strategy/pa-hyp/PAH-OMC-018-result-v1.json`
  `d34d08c5dda4acf6edb3749c5d18ddd3d98f13a4d52e6049cb373dc055729a65`
* `strategy/pa-hyp/PAH-OMC-018-generator-certificate.md`
  `18dc782cafff8cf8a516fd8366ec7e1f8727a24c9553dba0656a6b4bc84de264`
* `strategy/pa-hyp/PAH-OMC-020-temporal-prereg-v1.json`
  `906e3175d915c46d0323f29bf0e0b363095ec8ff31f4f868fcc0e868283cabc3`

For fixed `n>=2`, let `D` be the bounded globally amplitude-l1-Lipschitz
finite-prefix cylinder domain in the preregistration. Let `P_(n,j)(t)` be
the original finite semigroup, and let `Q_n(t)` be the finite-label fibre
semigroup obtained by retaining precisely the source PH/LK/AP summands of
the same generator at continuous amplitudes. For every `f,g in D` and finite
`T`, the target statement is

    lim_(K->infinity) lim_(j->infinity)
      sup_(0<=t<=T) |
        <S_(n,j) f, P_(n,j)(t) S_(n,j) g>_(mu_(n,j))
        - <f, Q_n(t) g>_(nu_n) | = 0.

The order is literal: first fix an amplitude cutoff `K`, take `j` to
infinity, then remove the cutoff. No diagonal sequence is used.

## Proof of the fixed-n passage

### 1. Compact fibre modulus

At fixed `n`, the PH/LK/AP root set and the label set are finite. A source
rate on a compact amplitude box is

    c_a(r,z)=m_a(z) exp(-(F_n(r,a z)-F_n(r,z))/2).

The mobility is independent of the amplitudes. The displayed PAH functional
is a polynomial in the amplitudes for fixed apertures and labels, with
positive denominators independent of the amplitudes. Hence each `c_a` is
continuous and locally Lipschitz. On `B_(K+1)`, define the source-derived
finite maxima

    ell_(n,K)=max_(a,z,r in B_(K+1)) ||gradient_r c_a(r,z)||_1,
    Lambda_(n,K)=2 |R_n^nr| ell_(n,K).

For the row-sum matrix `A_n(r)` of the fibre generator,

    ||A_n(r)-A_n(r')||_(infinity->infinity)
       <= Lambda_(n,K) ||r-r'||_1.

Variation of constants and the Markov contraction therefore give, for a
bounded `L_g`-Lipschitz vector-valued test `g` and `0<=t<=T`,

    ||Q_n(t,r)g(r)-Q_n(t,r')g(r')||_infinity
      <= (L_g + T Lambda_(n,K)||g||_infinity)||r-r'||_1.       (A1)

The same bound holds for the floor-sampled fibre matrices on the enlarged
box. This is a finite-label compact estimate; its constant may depend on
`n`, `K`, `T`, and `g`, and no global rate bound is asserted.

### 2. Compact-cutoff Duhamel estimate

Choose a bounded Lipschitz cutoff `chi_K` equal to one on `B_K` and zero
outside `B_(K+1)`, and put `g_K=chi_K g`. The fibre semigroup changes only
labels, so (A1) makes every original radial increment of
`Q_(n,j)(t)S_(n,j)g_K` at most `2 L_(n,K,T,g) h_j`. The R-511 inverse-pair
identity gives, for each directed radial root,

    sum_x mu_(n,j)(x) c_r(x)^2 <= 1.

The finite number `H_(n,K,g)` of roots that can affect the cutoff test and
Cauchy-Schwarz consequently give

    ||R_(n,j) Q_(n,j)(t) S_(n,j)g_K||_2
       <= 2 H_(n,K,g) L_(n,K,T,g) h_j.                 (A2)

At fixed `j` all matrices are finite and reversible. The exact Duhamel
identity and `L2(mu_(n,j))` contraction yield

    sup_(0<=t<=T) ||P_(n,j)(t)S_(n,j)g_K
       -Q_(n,j)(t)S_(n,j)g_K||_2
       <= 2T H_(n,K,g)L_(n,K,T,g)h_j -> 0.             (A3)

No fitted rate, time acceleration, or pointwise infinite-volume estimate is
used.

### 3. Uniform cell passage on the compact cutoff

The exact half-open cell identity, including the retained upper endpoint,
identifies the sampled fibre term with

    Q_n(t,a_j(r))g_K(a_j(r),z)

on every product cell. Equation (A1) makes the family

    Phi_T={f(r,z) Q_n(t,r)g_K(r,z): 0<=t<=T}

uniformly bounded and equicontinuous on the compact box `B_(K+1)`.
The R-509/OMC-016 theorem supplies endpoint-inclusive step-density weak
convergence and the stationary tail bound for the full labelled measure. To
make the time quantifier explicit, cover the compact family `Phi_T` by a
finite sup-norm epsilon-net. Apply the fixed-test weak convergence to the
finite net, then use equicontinuity to bound the remainder uniformly in `t`.
The cell replacement error from `a_j(r)` to `r` is bounded by (A1) times
`|V_n|h_j`. Thus, for fixed `n`, `K`, `f`, `g`, and `T`,

    sup_(0<=t<=T) |
      <S_(n,j)f,Q_(n,j)(t)S_(n,j)g_K>_(mu_(n,j))
      - <f,Q_n(t)g_K>_(nu_n)| -> 0.                 (A4)

This is a compact equicontinuity argument, not an unproved pointwise-rate
envelope and not a diagonal `j,n` limit.

### 4. Removal of the amplitude cutoff

R-509/OMC-016 supplies a fixed-`n`, all-`j` stationary tail estimate. Since
both the original finite semigroup and the fibre semigroup are stationary
Markov contractions, replacing `g` by `g_K` in either correlation costs at
most

    2 ||f||_infinity ||g||_infinity
      sup_j mu_(n,j)(B_K^c),

and the corresponding `nu_n` tail. These quantities vanish as `K` tends to
infinity. Combining this estimate with (A3) and (A4), in the order
`j -> infinity` followed by `K -> infinity`, proves the displayed target.

## Verification boundary

The primary, non-importing independent, and hostile verifiers reconstruct
the finite reversible algebra, source root incidence, compact-modulus
quantifiers, half-open endpoint condition, stationary-tail contraction,
Duhamel order, and the exact source hashes. The existing `PahOmc020.lean`
file checks only finite algebraic consequences; it does not pretend to
formalize the measure-theoretic epsilon-net argument.

This checkpoint proves only the fixed-`n` stationary local-correlation
passage. It does not prove a common completed Hilbert-space map `U_n`, a
varying-space liminf/recovery theorem, boundary escape, R-512 minimal-form
selection, the anchored `n` semigroup limit, or an infinite-volume process.
There is no physical Pre-A, spacetime, QFT, gravity, continuum, mass-gap,
Yang--Mills, or TOE conclusion. Markov time remains external stochastic time.
