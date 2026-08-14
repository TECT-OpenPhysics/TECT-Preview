# R-167 v4.2 certificate: integrated orbit-smear spatial quotient and ground transfer

Date: 2026-08-14  
Task: T-054  
Exploration: EXP-000846  
Claim-bearing: false (T0 route work)  
PDF: none issued

## 1. Exact scoped result

This certificate closes only
`PA-CP1-ST8-Q3LOCK-INTEGRATED-ORBIT-SMEAR-SHELL-CAUCHY-SPATIAL-QUOTIENT-AND-SAME-NET-GROUND-TRANSFER`.

Assume one directed all-shape family of finite zero-source backgrounds for the
ST8/Q3LOCK interaction. A background records every label that changes its
finite Hamiltonian: site activations and onsite Q3 terms, physical interaction
bonds, and explicitly tagged boundary corrections. The family admits admissible
common refinements: for any two backgrounds `F,G`, the auxiliary union
background `F union G` is admitted, and the finite single-toggle insertion
paths from `F` and `G` to this union use only admitted intermediate
backgrounds. The registered periodic zero-source sequence used in R-167 v4.0
is explicitly a cofinal path in this same comparison family. Declare one
common infinite interaction pattern and let `N_R` be the all-shape filter
neighborhood of backgrounds that match it on every label with `r_X<=R`.
Cofinality means that, for every `R`, all sufficiently late periodic
backgrounds lie in `N_R`; it does not mean inclusion of every other shape's
boundary corrections. The periodic path is not compared through a second,
unrelated net.

For temporally integrated finite-support rational Weyl seeds, assume uniform
one-toggle bounds whose weights are summable over all finite-Hamiltonian
labels. Then:

1. the orbit smears, their products, and all unital star-polynomials are
   all-shape norm Cauchy in one spatial quasi-local algebra;
2. their limits generate a spatial C-star subalgebra `B_sp` with a
   point-norm `C0` action `theta_sp`;
3. the R-167 v1.6 categorical carrier has a surjective equivariant
   star-homomorphism `q_sp:A_H^0->B_sp`;
4. `q_sp(k)=0` forces `||pi_L^0(k)||->0` on the same periodic path used by
   R-167 v4.0; and
5. the v4.0 parity-related categorical ground pair factors uniquely through
   `q_sp`, remains a ground pair, and remains separated by the same fixed
   witness.

The conclusion is conditional. This certificate does not prove the required
toggle weights for exact Q3. The target is a spatial quasi-local subalgebra,
not a seed-indexed commuting local net and not the raw oscillator algebra.

## 2. Finite weak operator smears

Let `B_ql` be a unital spatial quasi-local C-star algebra. For every admitted
finite region `Lambda` use a canonical unital isometric embedding

```text
J_Lambda:B(H_Lambda)->B_ql.                               (2.1)
```

A finite background `F` includes a region `Lambda(F)`, its site activations
and onsite Q3 terms, active physical bonds, and tagged boundary corrections.
Let `H_F` be the corresponding zero-source Hamiltonian and

```text
alpha_t^F(A)=exp(i t H_F/hbar) A exp(-i t H_F/hbar).       (2.2)
```

Let `Xi_Q` be exactly the finite-support rational configuration-Weyl label set
of R-167 v1.6. It is not enlarged to momentum or full phase-space Weyl
labels. For `xi in Xi_Q`, put `X=supp(xi)` and restrict the comparison to the
`X`-directed tail

```text
Lambda(F) contains X.                                    (2.3)
```

Let `W_(F,xi)` be the corresponding finite configuration Weyl operator; on a
periodic background `P_L` this is the v1.6 periodized representative. Within
one fixed background abbreviate it by `W_xi`. For `f in C_c^1(R)`, define

```text
G_F(xi,f)
 :=J_(Lambda(F))( weak-int_R f(t) alpha_t^F(W_(F,xi)) dt ). (2.4)
```

The map `t->alpha_t^F(W_(F,xi))` is strong-star continuous. Every value is a
unitary and therefore has norm one. For `u,v in H_(Lambda(F))`,

```text
|int_R f(t)<u,alpha_t^F(W_xi)v>dt|
 <=||f||_1 ||u|| ||v||.                                  (2.5)
```

Thus (2.4) is a well-defined weak operator integral and

```text
||G_F(xi,f)||<=||f||_1.                                  (2.6)
```

This weak-integral construction does not assert norm continuity of the raw
orbit `t->alpha_t^F(W_xi)`.

Fix the translation convention

```text
(tau_s f)(t)=f(t-s).                                     (2.7)
```

Changing variables in (2.4) gives exact finite equivariance:

```text
J_F alpha_s^F(weak-int f(t)alpha_t^F(W_xi)dt)
 =G_F(xi,tau_s f).                                       (2.8)
```

Also

```text
G_F(xi,f)^*=G_F(-xi,bar(f)).                              (2.9)
```

## 3. Conditional integrated-toggle hypothesis

Let `E` be the countable toggle-label set. It includes every finite-Hamiltonian
change: site activation and onsite Q3 terms, each physical interaction bond,
and each boundary correction as a separately tagged label.
Relative to every finite seed `X`, assume an integer shell map

```text
r_X:E->N,
{e:r_X(e)<=R} finite for every R.                         (3.1)
```

The admitted backgrounds are directed by common refinement as specified in
Section 1. In particular, if `e` is absent from `F`, both `F` and `F+e` and
all intermediate backgrounds in an admitted insertion history are members of
the comparison family. Auxiliary union backgrounds need not themselves lie on
the registered periodic path; their purpose is to make the comparison
telescope well-defined.

Here is the load-bearing hypothesis. For every `xi`, `f` and `T>0`, there are
numbers

```text
w_e(xi,f,T)>=0,
sum_(e in E) w_e(xi,f,T)<infinity,                        (3.2)
```

such that, with `X=supp(xi)`, uniformly over every admitted `F` in the
`X`-directed tail not containing `e`, every insertion order and boundary
history, and both time orientations,

```text
sup_(|s|<=T)
 ||G_(F+e)(xi,tau_s f)-G_F(xi,tau_s f)||
 <=w_e(xi,f,T).                                          (3.3)
```

Both time orientations means that the same estimate is available for the
forward and inverse finite dynamics required by the group proof. Define

```text
B_r(xi,f,T)=sum_(e:r_X(e)=r)w_e(xi,f,T).                  (3.4)
```

Local finiteness and (3.2) give

```text
sum_r B_r=sum_e w_e<infinity,
sum_(r>R)B_r->0.                                         (3.5)
```

No exact-Q3 estimate establishing (3.2)--(3.3) is claimed.

## 4. Shell telescope and generator limits

For `X=supp(xi)`, work only in the directed tail whose regions contain `X`.
The honest local-agreement condition at radius `R` is

```text
F triangle G subset {e:r_X(e)>R}.                         (4.1)
```

It says that `F` and `G` match the common infinite interaction pattern on the
`R`-core. Shape-specific boundary corrections lie beyond that core; (4.1)
does not demand that either shape contain the other shape's boundary labels.
Pass from `F` to the admitted auxiliary union `F union G` by inserting the
missing labels, and similarly from `G` to `F union G`. Apply (3.3) at every
intermediate background. The two paths contain exactly the labels in the
symmetric difference, so

```text
sup_(|s|<=T)||G_F(xi,tau_s f)-G_G(xi,tau_s f)||
 <=sum_(e in F triangle G)w_e(xi,f,T)
 <=sum_(r>R)B_r(xi,f,T)->0.                              (4.2)
```

Consequently the complete all-shape net has a unique norm limit

```text
G(xi,f):=lim_F G_F(xi,f) in B_ql,                         (4.3)
```

uniformly for `|s|<=T` and for both orientations. The directed all-shape net
uses the filter neighborhoods `N_R` declared in Section 1. The registered
periodic v4.0 path is required to enter every `N_R`: for each `R`, a late
periodic background and every sufficiently advanced all-shape background
agree with the common pattern on all labels with `r_X<=R`, and hence their
symmetric difference lies only in shells greater than `R`. Applying (4.2) to
this cross-comparison proves that the periodic path converges to the same
`G(xi,f)`, not merely that it is internally Cauchy.

The use of an auxiliary common refinement is essential. Pairwise bounds on
unrelated boundary backgrounds without the admitted union paths would not
imply (4.2).

## 5. Product bound and star-polynomial closure

For data `(xi_j,f_j)`, `1<=j<=m`, take

```text
X=union_(j=1)^m supp(xi_j)                               (5.1)
```

and work on the directed tail `Lambda(F) contains X`. Put

```text
P_F=product_(j=1)^m G_F(xi_j,f_j).                        (5.2)
```

Insert one toggle `e`. The exact product telescope, followed by (2.6) and
(3.3), gives

```text
||P_(F+e)-P_F||
 <=sum_(j=1)^m w_e(xi_j,f_j,T)
                  product_(k!=j)||f_k||_1
 =:w_e(P,T).                                              (5.3)
```

Therefore

```text
sum_e w_e(P,T)
 <=sum_(j=1)^m product_(k!=j)||f_k||_1
                   sum_e w_e(xi_j,f_j,T)
 <infinity.                                               (5.4)
```

The shell proof of Section 4 applies to products. Linearity and (2.9) then
apply it to every unital star-polynomial. Multiplication and star are norm
continuous, so each polynomial limit is the same polynomial in the limits
`G(xi_j,f_j)`.

Define

```text
B_sp=C^*({G(xi,f):xi in Xi_Q,
                      f in C_c^1(R)}) subset B_ql.        (5.5)
```

This is one spatial quasi-local C-star subalgebra. Formula (5.5) alone does
not supply a commuting seed-indexed local net.

## 6. The point-norm C0 spatial action

On generator limits define

```text
theta_sp,s(G(xi,f))=G(xi,tau_s f).                        (6.1)
```

Write a finite polynomial before embedding as

```text
tilde(P)_F in B(H_(Lambda(F))),
P_F=J_F(tilde(P)_F) in B_ql.                              (6.2)
```

Exact finite equivariance says that the embedded polynomial with every `f_j`
replaced by `tau_s f_j` is

```text
P_F^s=J_F(alpha_s^F(tilde(P)_F)).                         (6.3)
```

Both `J_F` and the finite dynamics are isometric. Passing to the all-shape
limits gives

```text
||theta_sp,s(P)||=||P||.                                  (6.4)
```

In particular, if an algebraic polynomial has zero limit, its shift has zero
limit. Hence (6.1) is independent of the presentation of an element. The
finite group identity passes to

```text
theta_sp,s theta_sp,t=theta_sp,s+t,
theta_sp,-s=(theta_sp,s)^(-1).                            (6.5)
```

Thus every `theta_sp,s` extends to an isometric star-automorphism of `B_sp`.
On generators, (2.6) gives

```text
||theta_sp,s(G(xi,f))-G(xi,f)||
 <=||tau_s f-f||_1->0.                                   (6.6)
```

Density and isometry extend (6.6) to all `B_sp`. Therefore `theta_sp` is a
point-norm `C0` automorphism group.

Parity uses the cofinal periodic path, not an unspoken symmetry of every
auxiliary boundary background. The v4.0 periodic zero-source systems have
compatible exact field inversions `Gamma_L` satisfying

```text
Gamma_L H_(P_L) Gamma_L^*=H_(P_L),
Gamma_L G_(P_L)(xi,f) Gamma_L^*=G_(P_L)(-xi,f).           (6.7)
```

Periodic norm convergence to the same all-shape limit and isometry of
`Gamma_L` show that `G(xi,f)->G(-xi,f)` preserves both the zero-limit kernel
and the norm of every polynomial. It consequently defines an isometric
involution `gamma_sp` with

```text
gamma_sp theta_sp,s=theta_sp,s gamma_sp.                  (6.8)
```

## 7. The categorical-to-spatial quotient

Let `A_alg^0` be the dense formal orbit-smear star-algebra used to construct
the R-167 v1.6 categorical carrier. Its norm is

```text
||a||_H=sup_L||pi_L^0(a)||,
A_H^0=completion(A_alg^0/common kernel).                  (7.1)
```

The `C_c^1` smears form a dense generating class: any larger `L1` smear in
the v1.6 presentation is obtained by `L1` approximation, using the uniform
finite bound (2.6). Define on this dense class

```text
q_sp,0(A_(xi,f))=G(xi,f)                                 (7.2)
```

and extend algebraically. Section 5 proves that all relations are respected.
The registered periodic backgrounds are both part of the supremum in (7.1)
and part of the same all-shape comparison. Hence

```text
||q_sp,0(a)||=lim_(registered periodic L)||pi_L^0(a)||
             <=||a||_H.                                  (7.3)
```

Thus (7.2) extends uniquely to a contractive unital star-homomorphism

```text
q_sp:A_H^0->B_sp.                                        (7.4)
```

The image of a C-star homomorphism is closed because it is C-star
isomorphic to the complete quotient by its kernel. Its image contains all
the generators in (5.5), so it is also dense. Therefore

```text
q_sp is surjective.                                      (7.5)
```

The exact finite relations also give

```text
q_sp theta_s=theta_sp,s q_sp,
q_sp gamma=gamma_sp q_sp.                                (7.6)
```

## 8. Completion and same-net kernel annihilation

For `a in A_alg^0`, the defining common comparison gives

```text
||J_L pi_L^0(a)-q_sp(a)||->0                             (8.1)
```

along the registered periodic path. Let now `a in A_H^0`, and choose
`a_n in A_alg^0` with `||a-a_n||_H->0`. Contractivity of `q_sp`, isometry of
`J_L`, and (7.1) give

```text
||J_L pi_L^0(a)-q_sp(a)||
 <=2||a-a_n||_H+||J_L pi_L^0(a_n)-q_sp(a_n)||.            (8.2)
```

First take `L->infinity`, then `n->infinity`. Therefore (8.1) holds for every
completed `a`.

If `k in ker(q_sp)`, (8.1) and the isometry of `J_L` imply

```text
||pi_L^0(k)||=||J_L pi_L^0(k)||->0.                       (8.3)
```

This is a same-net statement. It would not follow merely from existence of a
spatial quotient built on a different exhaustion.

## 9. Transfer of the v4.0 ground pair

R-167 v4.0 supplies, along one joint subsequence of the registered periodic
path, states

```text
omega_L^sigma(a)
 =<phi_L^sigma,pi_L^0(a)phi_L^sigma>
 ->omega_sigma(a),
sigma in {-1,+1}.                                        (9.1)
```

The limits are ground states of `(A_H^0,theta)` and satisfy

```text
omega_-=omega_+ o gamma.                                 (9.2)
```

For `k in ker(q_sp)`, weak-star convergence and (8.3) give

```text
omega_sigma(k^*k)
 =lim_L omega_L^sigma(k^*k)
 <=lim_L||pi_L^0(k)||^2=0.                               (9.3)
```

Cauchy--Schwarz makes the entire ideal `ker(q_sp)` null for `omega_sigma`.
Surjectivity now gives a unique state `bar(omega)_sigma` on `B_sp` such that

```text
omega_sigma=bar(omega)_sigma o q_sp.                      (9.4)
```

For completeness, groundness is not inferred from invariance alone. Map the
cyclic GNS class of `a` for `omega_sigma` to the cyclic class of `q_sp(a)`
for `bar(omega)_sigma`. Equation (9.3) and surjectivity make this a unitary.
Equivariance (7.6) intertwines the two implementing unitary groups. The
nonnegative implementing generator for the categorical ground state is
therefore the implementing generator for `bar(omega)_sigma`. Hence each
`bar(omega)_sigma` is a `theta_sp`-ground state.

Equations (7.6), (9.2), and surjectivity give

```text
bar(omega)_-=bar(omega)_+ o gamma_sp.                     (9.5)
```

Let `b in A_H^0` be the one fixed odd contractive v4.0 witness and let `d>0`
be its fixed separation constant. The v4.0 eventual bounds survive the joint
cluster:

```text
bar(omega)_+(q_sp(b))=omega_+(b)>=d/2,
bar(omega)_-(q_sp(b))=omega_-(b)<=-d/2.                   (9.6)
```

Because `||q_sp(b)||<=||b||_H<=1`,

```text
||bar(omega)_+-bar(omega)_-||>=d,
q_sp(b)!=0.                                               (9.7)
```

The triangular smear used to define the original witness need not itself be
`C_c^1`: it is an element of the completed categorical algebra and is reached
by `L1` approximation in Section 7. Equations (8.1) and (9.4) therefore apply
to this fixed `b` without changing the witness.

## 10. Nonduplication and exact boundary

R-167 v1.6 constructs the categorical orbit-smear carrier and its action but
does not supply a spatial all-shape realization. R-167 v4.2 adds a conditional
spatial quotient and same-net state transfer. Its new input is precisely the
summable integrated-toggle hypothesis (3.2)--(3.3).

R-167 v3.0 Section 6 already proves the abstract summable
single-toggle-shell to all-shape `C0` reduction. The shell/C0 idea itself is
not new here. R-167 v4.2 specializes and repairs that reduction for embedded
integrated orbit smears with tagged boundary-correction symmetric differences
and admitted common refinements, gives the exact product weight (5.3), and
newly adds the categorical quotient `q_sp`, completed same-periodic-net kernel
annihilation, and transfer of the v4.0 pair. R-167 v4.1 instead establishes
the categorical GNS form core and Poincare reduction. No positive Poincare
constant or GNS spectral gap is proved here. EXP-000790 uses iterated
fixed-source tangent states; the present theorem transfers only the v4.0
diagonal `h_L` same-net clusters and proves no branch identity. Likewise, it
transfers no EXP-000781 DLR tangent, v3.8 fixed-beta KMS state, or v3.4
Yarotskii branch.

Exactly three registered negative boundaries are reused:

- `NG-2026-08-12-PRE-A-ST8-Q3LOCK-ORBIT-SMEAR-SEED-SUPPORT-AUTOMATIC-SPATIAL-LOCAL-NET`;
- `NG-2026-08-13-PRE-A-ST8-Q3LOCK-CATEGORICAL-UNIFORM-CONTINUOUS-ELEMENT-KMS-ENVELOPE-AUTOMATIC-ALL-SHAPE-CAUCHY-AND-UNIQUE-PHASE-QUOTIENT`; and
- `NG-2026-08-13-PRE-A-ST8-Q3LOCK-NONESSENTIALLY-CONSTANT-LINFINITY-CONFIGURATION-MULTIPLIER-FULL-HAMILTONIAN-POINT-NORM-C0`.

They remain compatible with this theorem because the all-shape result is
assumed through explicit weights, `B_sp` is not promoted to a seed-local net,
and raw full-Hamiltonian Weyl orbits are not asserted to be norm continuous.
No new negative result is registered.

This theorem proves no exact-Q3 toggle-weight estimate, DLR/OS identification,
beta-infinity limit, GNS gap, purity, factoriality, disjointness, phase
exhaustion, regulator removal, continuum, physical mass gap, physical vacuum,
empty-space comparison, Round-1, C6, CP1, physical Sector A, or Pre-A closure.
Both historical gates and all five active parent gates remain OPEN.

## 11. Devil's-advocate and code-discipline audit

The executable numbers in this package are exact dimensionless audit
fixtures. They are not measured or proved Q3 toggle weights. Before citation,
the following adversarial checks are mandatory and are implemented in both
derivation lanes and the integrated verifier.

- **Sign and triangle factors.** The two paths from `F` and `G` to
  `F union G` traverse disjoint halves of `F triangle G`; they must not be
  replaced by twice the symmetric-difference sum. The scripts check one exact
  symmetric-difference fixture against the full shell tail.
- **Convention and involutions.** The translation is
  `(tau_s f)(t)=f(t-s)`, forced by the change of variables in (2.8).
  Adjoint uses `W_xi^*=W_(-xi)` and complex conjugation of `f`. Parity acts on
  the configuration label and commutes with the zero-source dynamics; it is
  not an unrecorded time reversal.
- **Units and provenance.** Shell, weak-sum, quotient, and four-dimensional
  ground fixtures are dimensionless proof diagnostics. None is inserted into
  an exact-Q3 Hamiltonian or cited as a physical coupling, mass, or gap.
- **Convergence.** The generator tail is controlled only after
  `sum_e w_e<infinity`; the product tail uses the derived weight (5.3). The
  periodic limit is identified only by cross-comparison through every `N_R`,
  not by pairwise periodic Cauchy convergence.
- **Hardcode masking.** Each nontrivial reported value is recomputed from one
  labelled exact input block and then compared with a separately labelled
  `TEST_ORACLE` string. The independent lane uses only stdlib `Fraction`; the
  integrated AST audit rejects hidden SymPy, float, complex, and dynamic
  execution in that lane.
- **Limit and failure cases.** The unital empty product has zero toggle weight;
  zero individual weights cause no difficulty; `q_sp(k)=0` is tested through
  a decaying representation fixture. If the weights are nonsummable, the
  background family lacks admitted union paths, or the periodic path fails to
  enter every `N_R`, the corresponding theorem step is unavailable and no
  spatial quotient or ground transfer is inferred.

External adversarial review is invited specifically on the union-path factor,
translation sign, product norms, categorical completion estimate, same-net
kernel limit, and parity-ground factorization.

## 12. Proof-first lifecycle

The proof-first package consists of this certificate, its manifest, and three
executable verifiers. Before formal integration, run only

```text
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_integrated_orbit_smear_spatial_quotient_ground_transfer_route_split.py --staged --no-store
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_integrated_orbit_smear_spatial_quotient_ground_transfer_route_split_independent.py --staged --no-store
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_integrated_orbit_smear_spatial_quotient_ground_transfer_route_split_verify.py --staged --no-store
```

The frozen formal contract is EXP-000846, R-167 v4.2, event 638 with ID
`20260814-r-167-v4-2-integrated-orbit-smear-spatial-quoti`, theorem-map
version 1.34.0, and post-formal counts
`49/168/196/367/847/638/55/catalog3971`. No v4.2 PDF is issued.
