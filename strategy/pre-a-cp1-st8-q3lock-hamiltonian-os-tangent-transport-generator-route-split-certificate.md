# Hamiltonian--OS tangent transport and generator route split

**Candidate:** `PA-CP1-ST8-Q3LOCK-HAMILTONIAN-OS-TANGENT-TRANSPORT-GENERATOR-ROUTE-SPLIT-v0`  
**Result:** `PA-CP1-ST8-Q3LOCK-SECOND-WEIGHTED-ENERGY-MOMENT-AND-COMMON-ALPHA-CAUCHY-GATE-SPLIT` (`R-167 v1.5`)  
**Task / explorations:** `T-054` / `EXP-000801`, with append-only locator/scope correction `EXP-000802`  
**Status:** T0 claim-nonbearing fixed-beta selected-tangent identification theorem and five exact route no-gos

## 1. Question and exact scope

`R-167 v1.4` reconstructed, at each fixed inverse temperature beta, one
canonical OS mixture W-star system whose two ordered phases are normal KMS
states of the same reconstructed group.  That result did not identify the
group with a thermodynamic limit of the registered finite-volume
Hamiltonians.

This checkpoint asks the strongest narrower question already supported by
the registered tangent nets:

> Do the exact finite-volume Hamiltonian KMS word systems along the selected
> `EXP-000781` plus/minus source tangent subsequences converge to the
> `EXP-000800` OS mixture system in a topology that retains bounded real-time
> configuration orbits?

The answer is yes in the following precise sense.  At one externally fixed
beta, fixed-band real-time word kernels converge.  Every limit-independent
finite Gram block has an explicit asymptotically identity polar transport
into the limiting OS Gram space.  A diagonal block exhaustion gives pointed
finite-core Fell/GNS convergence on a countable bandlimited word list.  An
exact finite-volume carre-du-champ identity and a Fejer Liouville filter then
recover each raw rational finite-support configuration character uniformly
in cyclic two-sided L2.

This is a selected-tangent correlation and pointed finite-core Fell/GNS
theorem.  It is not a globally compatible common-Hilbert operator strong-star
theorem, an untransported strong-star Cauchy theorem in one preregistered
local representation, an all-exhaustion result, a zero-source periodic-volume
limit, a canonical momentum reconstruction, or a beta-independent C-star
dynamics.  No C6, CP1, Sector-A or Pre-A claim changes.

## 2. Registered finite systems and limiting mixture

Fix beta greater than zero.  `EXP-000781` supplies two exact finite periodic
Gibbs/path subsequences

\[
  (\Lambda_n,+h_n),\qquad (\Lambda_n,-h_n),\qquad h_n\downarrow0,
\]

whose bounded local Euclidean cylinder laws converge to the ordered path
laws `mu_+` and `mu_-`.  Every finite member is the Gibbs/KMS system of the
exact ST8/Q3LOCK Schrodinger Hamiltonian with the indicated source.  Fix
strictly positive weights

\[
  \lambda_++\lambda_-=1
\]

and form the direct-sum finite word functional

\[
  \Phi_n=\lambda_+\Phi_{n,+}+\lambda_-\Phi_{n,-}.
\]

On the common rational configuration-cylinder labels its Euclidean limit is

\[
  \mu_0=\lambda_+\mu_++\lambda_-\mu_-.
\]

By `EXP-000790` and `EXP-000800`, the full common positive-time cylinder
kernel of `mu_0` reconstructs the canonical fixed-beta mixture W-star system

\[
  (\mathcal M_0,\alpha^0,\Omega_0).
\]

The sequence in this section is frozen data.  It is not replaced by arbitrary
volume shapes or by the zero-source periodic sequence.

## 3. Fixed-band KMS word-kernel convergence

### 3.1 Interior thermal-tube convergence

Let `A_1,...,A_m` be bounded rational finite-support configuration
characters.  On real times first define

\[
 F_n(t_1,\ldots,t_m)
 =\Phi_n\!\left(\alpha^{(n)}_{t_1}(A_1)\cdots
                    \alpha^{(n)}_{t_m}(A_m)\right).
\]

Let the same symbol denote its bounded scalar KMS analytic continuation to
the ordered thermal tube.  No operator-valued complex-time character is
assumed.  The standard KMS estimate gives

\[
  |F_n(z)|\leq\prod_{j=1}^m\|A_j\|,
\]

uniformly in `n`.  The family is therefore normal on each compact sub-tube.
Every convergent subsequence has a holomorphic limit.  On the ordered
imaginary-time region that limit is the `mu_0` Euclidean cylinder kernel by
the registered tangent convergence.  The registered rational cylinder times
are dense there and continuity fills the full ordered slice.  That slice is
maximally totally real and hence a uniqueness set for the thermal-tube
holomorphic function.  Every subsequential limit is therefore the same, so
`F_n` converges locally uniformly in the tube interior.

### 3.2 Boundary smoothing

The bounded analytic functions have weak-star boundary values.  Interior
convergence fixes every weak-star boundary cluster point.  Consequently, for
fixed `L1` kernels `f_1,...,f_m`, convolution in all physical-time variables
converges pointwise in the translation vector `s`:

\[
 \int_{\mathbb R^m}\prod_j f_j(t_j-s_j)
   F_n(t_1,\ldots,t_m)\,dt
 \longrightarrow
 \int_{\mathbb R^m}\prod_j f_j(t_j-s_j)
   F_0(t_1,\ldots,t_m)\,dt.                         \tag{3.1}
\]

The uniform boundary bound and `L1` translation continuity give, for one
variable and uniformly in `n`,

\[
 |(F_n*f)(s+h)-(F_n*f)(s)|
 \leq C\,\|\tau_hf-f\|_1.
\]

The product-kernel version is identical.  Compact translation sets are thus
equicontinuous, upgrading the weak-star pairings in (3.1) to locally uniform
smoothed convergence.

Use the even Fejer kernels whose physical-frequency multiplier is

\[
  g_R(\omega)=\left(1-\frac{|\omega|}{R}\right)_+,
  \qquad
  f_R(t)=\frac{1-\cos(Rt)}{\pi R t^2}.
\]

They obey `f_R >= 0`, `int f_R = 1`, and have compact Fourier support.
Products add bandwidth, star reverses frequency and rational time shifts
preserve bandwidth.  Taking rational labels, rational bandwidths and
rational shifts gives a countable bandlimited orbit-word list closed under
star, products and rational shifts.  Its complex span is the word algebra
used below.

It follows that every fixed finite Gram matrix of this word list converges
entrywise to the corresponding `EXP-000800` mixture Gram matrix.

## 4. Exact finite-block Gram transport

Enumerate the countable bandlimited words as `X_1,X_2,...`.  Retain a word
only when its limiting GNS vector is independent of the earlier retained
vectors.  For a retained `k`-block let

\[
  (G_n^{(k)})_{ij}=\Phi_n(X_i^*X_j),
  \qquad
  (G_0^{(k)})_{ij}=\Phi_0(X_i^*X_j).
\]

Then `G_0^(k)>0` and `G_n^(k)->G_0^(k)`.  For all sufficiently large `n`,
`G_n^(k)>0` as well.  With the positive square roots define

\[
  M_{n,k}=(G_0^{(k)})^{-1/2}(G_n^{(k)})^{1/2}.
\]

The exact identity

\[
  M_{n,k}^*G_0^{(k)}M_{n,k}=G_n^{(k)}
\]

makes `c -> M_(n,k)c` an isometry from the finite `n` coefficient block to
the limiting coefficient block, and continuity of the positive square root
gives `M_(n,k)->I`.

Before testing any fixed finite family, enlarge the block to contain all
required products, adjoints and rational time shifts.  Gram convergence then
shows finite-word approximate intertwining on each such block.  A diagonal
choice `k=k(n)->infty` gives pointed finite-core Fell/GNS convergence of the
countable bandlimited word system.  The construction does not provide one
globally compatible sequence of complete-Hilbert-space embeddings, so no
common-Hilbert operator strong-star convergence is inferred.

If a limiting Gram block is singular, it is never inverted.  The proof uses
the retained independent pivots above.  Equivalently, one may first compress
to a persistent spectral subspace and discard every vanishing direction; it
must not isometrically inject a higher-rank finite block into a lower-rank
limiting support.  Pointwise Gram convergence alone does not define a label
map between the complete quotient spaces; the counterexample in Section 8.1
shows why this discard step is load-bearing.

The frozen enumeration, dependence rule and principal roots make the
transport reproducible.  They do not make it a canonical label-preserving
homomorphism from every complete finite GNS representation into
`mathcal M_0`.

## 5. Exact character Dirichlet identity

Let

\[
 W_\xi=\exp\!\left(i\sum_{x,a}\xi_{x,a}q_{x,a}\right),
 \qquad \|\xi\|_2^2=\sum_{x,a}\xi_{x,a}^2,
\]

with rational finite support.  In any finite volume, write the exact
Hamiltonian as

\[
 H=\frac{p^2}{2\chi}+V(q),
\]

where `V(q)` may include any Q3LOCK onsite, q-only source and q-only boundary
term.  On the common Schrodinger form core,

\[
 pW_\xi=W_\xi(p+\hbar\xi)
\]

and hence

\[
 \delta W_\xi
 =\frac{i}{\hbar}[H,W_\xi]
 =iW_\xi\left(\frac{\xi\cdot p}{\chi}
          +\frac{\hbar\|\xi\|_2^2}{2\chi}\right).
\]

Adding the two opposite momentum shifts gives the exact scalar
carre-du-champ identity

\[
 [W_\xi^*,[H,W_\xi]]
 =\frac{\hbar^2}{\chi}\|\xi\|_2^2 I.                 \tag{5.1}
\]

For `rho=Z^(-1)e^(-beta H)` define the normalized Duhamel form

\[
 \|A\|_D^2=\int_0^1
   \operatorname{Tr}(\rho^{1-s}A^*\rho^sA)\,ds.
\]

The Kubo identity and (5.1) yield

\[
 \|\delta W_\xi\|_D^2
 =\frac{1}{\beta\hbar^2}
   \Phi([W_\xi^*,[H,W_\xi]])
 =\frac{\|\xi\|_2^2}{\beta\chi}.                  \tag{5.2}
\]

This equality is independent of volume, source sign and q-only boundary
conditions.  For a finite character sum

\[
  A=\sum_j c_jW_{\xi_j},
\]

the same identity applied to the multiplication gradient, followed by the
triangle inequality, gives

\[
  \|\delta A\|_D
  \leq\frac{\sum_j|c_j|\,\|\xi_j\|_2}{\sqrt{\beta\chi}}. \tag{5.3}
\]

The identities are finite-volume form statements.  Their uniform bounds pass
as limsup estimates; equality of a limiting closed Dirichlet form would
require a separate Mosco/core argument and is not claimed.

## 6. Modular mean and exact Fejer removal

### 6.1 The general W-star mean inequality

Work in the support-reduced faithful normal standard form and let `Delta` be
its modular operator.  For
`X` in the Duhamel form domain of `[log Delta,.]`, the logarithmic-mean
spectral representation of the Duhamel form compares the
arithmetic and logarithmic means through

\[
 \frac{u}{2}\coth\!\left(\frac{u}{2}\right)
 \leq 1+\frac{|u|}{2}.
\]

Spectral Cauchy--Schwarz therefore gives, with the averaged two-sided norm,

\[
 \|X\|_{\#,\mathrm{avg}}^2
 \leq \|X\|_D^2
  +\frac12\|X\|_D\,\|[\log\Delta,X]\|_D.           \tag{6.1}
\]

For the convention
`delta=(i/hbar)[H,.]` and `sigma_s=alpha_(-beta hbar s)`, a beta-KMS dynamics
obeys exactly

\[
 [\log\Delta,X]=i\beta\hbar\,\delta X,
\]

and in the unaveraged v1.4 convention

\[
 \|X\|_{\#,\mathrm{sum}}^2
 =\Phi(X^*X)+\Phi(XX^*),
\]

(6.1) reads

\[
 \|X\|_{\#,\mathrm{sum}}^2
 \leq 2\|X\|_D^2
   +\beta\hbar\|X\|_D\,\|\delta X\|_D.             \tag{6.2}
\]

This is a modular spectral theorem in a faithful normal standard form, not a
finite-matrix-only assertion.

### 6.2 Removing a fixed physical-frequency band

Let

\[
  W_\xi^{(R)}=\int_{\mathbb R}f_R(t)\alpha_t(W_\xi)\,dt,
  \qquad Y_R=W_\xi-W_\xi^{(R)},
\]

where `R` is physical Liouville frequency.  In the Duhamel spectral measure,

\[
 |1-g_R(\omega)|\leq\min\!\left(1,\frac{|\omega|}{R}\right).
\]

Put

\[
  a_\xi=\frac{\|\xi\|_2}{\sqrt{\beta\chi}}.
\]

Equation (5.2) gives, exactly,

\[
 \|Y_R\|_D\leq\frac{a_\xi}{R},
 \qquad
 \|\delta Y_R\|_D\leq a_\xi.                      \tag{6.3}
\]

Combining (6.2) and (6.3),

\[
 \|Y_R\|_{\#,\mathrm{sum}}
 \leq a_\xi
  \sqrt{\frac{2}{R^2}+\frac{\beta\hbar}{R}}.       \tag{6.4}
\]

The bound is uniform in volume, source and q-only boundary terms.  It is
`O(R^(-1/2))` and is sufficient to recover the cyclic two-sided L2 vector of
each raw character: first take the selected tangent limit at fixed `R`, then
take `R` to infinity.  The local `p^2` estimate in `EXP-000781` gives an
optional cyclic two-sided spectral estimate of order `R^(-1)`, but that
stronger rate is not needed for the theorem.

Equation (6.4) alone does not control multiplication of `Y_R` by arbitrary
bandlimited left and right contexts.  It therefore does not upgrade the raw
characters to operator strong-star convergence on the whole word core; that
would require an additional modular/right-multiplier lemma.

The filter is an `L1` convolution, so `W_xi^(R)` remains bounded by one.  No
possibly unbounded sharp spectral projection is used.

## 7. Generator statement and the first coordinate-tail rung

Raw configuration characters are bounded orbit seeds but not bounded
generator-domain elements.  The correct bounded smooth core is obtained by
time convolution.  For a smooth compactly supported `f`,

\[
 A_f=\int f(t)\alpha_t(A)\,dt,
 \qquad
 \delta(A_f)=-A_{f'}.                               \tag{7.1}
\]

The union of these temporal smears is strong-star dense in the fixed-beta
limit system.

There is also an exact algebraic local-jet checkpoint.  On the finite-support
polynomial CCR core write

\[
 \delta_h=\delta_0+hD,
 \qquad D(q_x)=0,\qquad D(p_x)=u.
\]

Every fixed iterate of `delta_h` on `W_xi` is a finite-neighbourhood
polynomial times `W_xi` and becomes independent of the outer volume once that
neighbourhood is included.  In particular,

\[
 \delta_hW_\xi=\delta_0W_\xi,
 \qquad
 \delta_h^2W_\xi-\delta_0^2W_\xi
 =\frac{ih}{\chi}\left(\sum_x\xi_x\cdot u\right)W_\xi. \tag{7.2}
\]

If `H=K+W_L(q)` differs by a coordinate multiplication tail, then

\[
 \delta_HW_\xi=\delta_KW_\xi,
\]

and the first nonzero rung is

\[
 (\delta_H^2-\delta_K^2)W_\xi
 =-\frac{i}{\chi}W_\xi\,\xi\cdot\nabla W_L.         \tag{7.3}
\]

Consequently,

\[
 \|(\delta_H^2-\delta_K^2)W_\xi\|_{D,H}
 \leq\frac{\|\xi\|_2}{\chi}
       \Phi_H(|\nabla W_L|^2)^{1/2}.                \tag{7.4}
\]

The registered coordinate-tail estimate makes (7.4) super-Gaussian in the
cutoff.  Equations (7.2)--(7.4) do not sum the higher orbit rungs and do not
identify a canonical momentum operator in the OS envelope.

## 8. Exact embedding and generator no-gos

### 8.1 Pointwise Gram convergence does not define a label map

Let `v_n` be unit vectors in `C^2` converging to `e_1` without ever being
parallel to it, and set

\[
 q_n(x)=|\langle v_n,x\rangle|^2,
 \qquad q_0(x)=|x_1|^2.
\]

Then `q_n(x)->q_0(x)` for every `x`, but

\[
 N_n=v_n^\perp\not\subset e_1^\perp=N_0.
\]

Thus the formula `[x]_n -> [x]_0` is not well-defined.  A faithful diagonal
state tending to a rank-one state gives the complementary dimension-collapse
fixture: the finite GNS spaces have dimension two while the limiting support
has dimension one.  These examples reject a naive label-preserving complete
GNS embedding.  They do not reject the support-reduced finite-block polar
transport of Section 4.

### 8.2 Configuration cylinders do not select canonical momentum

For one exact Schrodinger system set

\[
 H=\frac{p^2}{2\chi}+V(q),
 \qquad U_a=e^{ia\cdot q/\hbar},
 \qquad H_a=U_aHU_a^*=\frac{(p-a)^2}{2\chi}+V(q).
\]

Every bounded Euclidean cylinder trace made only from functions of `q` is
identical for `H` and `H_a`, because `U_a` commutes with every such insertion.
Nevertheless,

\[
 \delta_H(q)=\frac{p}{\chi},
 \qquad
 \delta_{H_a}(q)=\frac{p-a}{\chi}.
\]

Therefore configuration-cylinder OS data alone do not determine the
canonical momentum or the registered polynomial CCR derivation.  A kinetic
or CCR anchor must be supplied independently.

### 8.3 A raw character is not a bounded generator-core element

For nonzero `xi`,

\[
 [H,W_\xi]
 =W_\xi\left(\frac{\hbar}{\chi}\xi\cdot p
       +\frac{\hbar^2\|\xi\|_2^2}{2\chi}\right)
\]

is unbounded.  Thus raw rational configuration characters belong to the
bounded orbit algebra and to the Duhamel form domain, but not to the bounded
W-star generator domain.  The temporal-smear core (7.1) is the valid
replacement.

## 9. Exact parity and cross-beta no-gos

### 9.1 An asymmetric phase mixture is not a zero-source periodic limit

Every finite periodic zero-source Gibbs/path law is invariant under the
registered parity.  The two ordered laws are distinct and exchanged by
parity.  Therefore

\[
  \lambda\mu_++(1-\lambda)\mu_-
\]

is parity invariant if and only if `lambda=1/2`.  No asymmetric v1.4 mixture
can be the weak limit of the zero-source periodic sequence.  The symmetric
mixture is only an admissible candidate; proving it is the periodic limit
still requires phase exhaustiveness or a direct convergence theorem.

### 9.2 Fixed-beta envelopes do not glue automatically

On `M_2` with the diagonal configuration algebra, take

\[
 (\beta_1,H_1)=(1,-\sigma_x),
 \qquad
 (\beta_2,H_2)=(2,-2\sigma_x).
\]

Each is a faithful stochastically positive finite KMS system.  If one inner
dynamics generated by `H` had both Gibbs states at their displayed inverse
temperatures, then

\[
 H=-\beta_j^{-1}\log\rho_j+\text{scalar}
\]

would hold for both `j`.  The two right-hand sides differ by the nonscalar
operator `sigma_x`, so no such `H` exists.  Fixed-beta common envelopes do not
automatically determine a beta-independent dynamics.

## 10. Closed subgate and remaining analytic gate

This checkpoint closes exactly

`PA-CP1-ST8-Q3LOCK-FIXED-BETA-TANGENT-NET-BANDLIMITED-HAMILTONIAN-OS-POINTED-GNS-IDENTIFICATION`.

The closed statement is:

1. the selected `EXP-000781` plus/minus tangent finite Hamiltonian KMS word
   kernels converge, after fixed physical-time bandlimiting, to the
   `EXP-000800` mixture kernels;
2. explicit independent-pivot finite-block polar transports give pointed
   finite-core Fell/GNS convergence of every fixed word family; and
3. the uniform exact estimate (6.4) recovers each raw rational configuration
   character as a cyclic two-sided L2 vector.

The next open gate is

`PA-CP1-ST8-Q3LOCK-ALL-EXHAUSTION-MIXTURE-L2-LOCALITY-AND-BETA-INDEPENDENT-CSTAR-DYNAMICS`.

It requires, at minimum, an all-shape pairwise-union estimate in one
preregistered locally normal mixture representation, for example

\[
 \sup_{\Lambda,\Lambda'\supset B_R(X)}
 \|X_\Lambda-X_{\Lambda'}\|_{\#,\beta}\longrightarrow0,
\]

together with exhaustion independence, a beta-independent invariant C-star
algebra and generator, the zero-source symmetric anchoring needed for the
periodic sequence, and the missing canonical momentum/full-Weyl bridge.
Selected-tangent pointed-GNS convergence is not this estimate.

The historical gates

- `PA-CP1-ST8-Q3LOCK-HAMILTONIAN-THERMODYNAMIC-IDENTIFICATION-IN-CANONICAL-OS-MIXTURE`, and
- `PA-CP1-ST8-Q3LOCK-PROJECTED-DUHAMEL-MODULAR-C1-MULTIPLIER-LOCALITY`

remain recorded as route history and are not silently deleted.

## 11. Reproducible verification contract

The five exact negative-result identifiers are:

- `NG-2026-08-10-PRE-A-ST8-Q3LOCK-POINTWISE-OS-GRAM-NAIVE-LABEL-EMBEDDING`;
- `NG-2026-08-10-PRE-A-ST8-Q3LOCK-CONFIGURATION-CYLINDER-CANONICAL-MOMENTUM-GENERATOR`;
- `NG-2026-08-10-PRE-A-ST8-Q3LOCK-RAW-CONFIGURATION-CHARACTER-BOUNDED-GENERATOR-CORE`;
- `NG-2026-08-10-PRE-A-ST8-Q3LOCK-ASYMMETRIC-MIXTURE-ZERO-SOURCE-PERIODIC-LIMIT`; and
- `NG-2026-08-10-PRE-A-ST8-Q3LOCK-FIXED-BETA-ENVELOPE-AUTOMATIC-CROSS-BETA-GLUING`.

The closed subgate and the exact successor are, respectively,

- `PA-CP1-ST8-Q3LOCK-FIXED-BETA-TANGENT-NET-BANDLIMITED-HAMILTONIAN-OS-POINTED-GNS-IDENTIFICATION`; and
- `PA-CP1-ST8-Q3LOCK-ALL-EXHAUSTION-MIXTURE-L2-LOCALITY-AND-BETA-INDEPENDENT-CSTAR-DYNAMICS`.

`EXP-000802` corrects only the append-only authority chain by adding the
integrated-verifier locator and the exact cyclic/all-exhaustion boundary
tokens. It changes no theorem, constant, gate or negative result.

The primary verifier must independently compute or symbolically reconstruct:

1. the momentum shift, double commutator and exact Kubo constant;
2. the Fejer multiplier bounds and the unaveraged modular-mean coefficient;
3. positive-root Gram transports and a singular-support fixture;
4. the rotating-null and GNS-dimension-collapse counterexamples;
5. the momentum-gauge cylinder equality and generator mismatch;
6. the raw-character unbounded momentum term;
7. the parity `lambda=1/2` condition and the two-temperature `M_2` mismatch;
8. the source jet and first coordinate-tail rung; and
9. every scope and no-overclaim boundary.

The independent verifier must not import the primary verifier or consume its
stored result.  The integrated verifier must execute both engines freshly,
check deterministic equality with their stored JSON artefacts, cross-check
their exact invariants, and verify all manifest, certificate, exploration,
negative-result, gate, ledger and generated-map links.

Under the repository PDF-efficiency policy, this development checkpoint uses
this source certificate, manifest, run JSONs and the append-only exploration
record.  It does not issue or render an intermediate note PDF.  A single
gate-level synthesis PDF is deferred until the larger gate reaches its
declared checkpoint.

## 12. No-overclaim boundary

This package proves a fixed-beta selected phase-tangent Hamiltonian-to-OS
finite-word correlation and pointed finite-core Fell/GNS identification,
plus exact cyclic character topology reductions.  It does not prove:

- a canonical label-preserving embedding of complete finite GNS spaces;
- globally compatible common-Hilbert operator strong-star convergence;
- raw-character operator convergence after arbitrary left/right contexts;
- direct untransported mixture-L2 Cauchy on the inductive local algebra;
- all-volume-shape, all-boundary or all-exhaustion convergence;
- convergence of the zero-source periodic volumes to the symmetric mixture;
- a canonical momentum or full Weyl/CCR embedding in the OS envelope;
- a beta-independent common C-star automorphism group;
- algebraic ground states or a beta-to-infinity passage;
- a GNS gap or a physical mass gap;
- regulator removal, a continuum, physical empty space or a below-empty
  energy sign; or
- Pre-A selection, C6, CP1 or Sector-A closure.

The five negative results reject only the named naive embedding, generator,
parity and cross-beta shortcuts.  They do not prove that the remaining common
dynamics does not exist.
