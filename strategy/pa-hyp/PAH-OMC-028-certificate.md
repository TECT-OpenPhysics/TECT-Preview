# PAH-OMC-028: normal contractions on the R-512 minimal closure

Task T-095. This is an analytic proof repair of R-530, conditional on the
unchanged R-510/R-511/R-512 inputs. Its result does not identify this form
with a limit of finite PAH semigroups. Source bytes and scope are fixed by
`PAH-OMC-028-prereg-v1.json` (SHA-256
`3bb509a383d7b4eba0bb04af1d7d9c37614c3f79f540fd96c09074c34aac81b0`).

## 1. Exact statement and applicability

Let H be the real invariant L2 space of the original probability state.
Let D be the exact R-511 bounded, gauge-invariant, globally
amplitude-l1-Lipschitz finite-prefix cylinders, modulo H-null functions.
Use E(f,g)=(1/2) sum_r nu[c_r Delta_r f Delta_r g]. Its coefficients are
nonnegative and its value on each D vector is finite. R-512 supplies the
minimal closure (Ebar,V), with norm ||v||_V^2=||v||_H^2+Ebar(v,v), dense
core D, and an injective continuous inclusion V -> H. We identify V with
its image only after using that injectivity.

For every scalar normal contraction eta (eta(0)=0 and Lipschitz constant
at most one), and every u in V, the theorem is

    eta(u) belongs to V, and Ebar(eta(u),eta(u)) <= Ebar(u,u).       (1)

Consequently the same closed-form spectral semigroup T_min(t), t>=0,
is positivity preserving, L-infinity contractive, and T_min(t)1=1.

The source assumptions are explicitly inherited, not inferred from a run:

| Input | Status and use |
|---|---|
| R-510 probability-state L2 realization | CONDITIONAL; scalar compositions and 1 in H |
| R-511 dense D, nonnegative root-square identity | CONDITIONAL; contraction on D |
| R-512 closability, minimal completion, injective inclusion | CONDITIONAL; energy lower semicontinuity |
| D stable under eta | SATISFIED from its displayed definition below |
| R-512 spectral representation | CONDITIONAL; operator and semigroup consequences |
| Source-authorized finite-to-target comparison | NOT USED; remains open |

The parameter, strip, all-Q normalization and ordered-state construction
are exactly those in the preregistration. There is no new j or n limit in
this theorem. All recovery sequences below may have growing support.

Literature crosswalk, consulted 2026-09-09: Fukushima, Oshima and Takeda,
*Dirichlet Forms and Symmetric Markov Processes*, second edition (2011),
section 1.1 pp. 3-5 (closed form and minimal extension), Theorem 1.4.1
pp. 25-26 (closed form to Markovian resolvent/semigroup), and Theorem
1.4.2(v) p. 28 (weak form convergence under normal contractions).
Publisher preview: https://api.pageplace.de/preview/DT0400.9783110218091_A15362972/preview-9783110218091_A15362972.pdf .
Only the forward form-to-semigroup implication is used; no locally compact
state topology, Hunt process or converse kernel representation is imported.
This is standard functional analysis. The contribution is repair and
applicability checking of the pinned PAH proof. No novelty claim is made.

## 2. Exact failure of the paired-energy shortcut

R-530's section 'Domain and closure passage' inferred that eta(f_k) is
form-norm Cauchy directly from E(eta(f_k))<=E(f_k). This single-vector
inequality supplies boundedness, but supplies no two-vector difference
estimate. In particular, the would-be bound

    E(eta(f)-eta(g)) <= E(f-g)                                  (2)

is false. As a diagnostic of (2), take two values with probability weights
1/2,1/2, rates 2 in both directions, and the directed-half convention.
Then E(h)=((h_0-h_1)^2). For f=(1,2), g=(0,1), and eta clipped to [0,1],

    f-g=(1,1), eta(f)-eta(g)=(1,0),
    E(f-g)=0, E(eta(f)-eta(g))=1.

The squared form norms are 1 and 3/2 respectively. Each single-vector
energy inequality still holds. This counterexample rejects (2) and the
purported immediate contraction argument. It does NOT show that a Cauchy
sequence has a non-Cauchy image, does NOT refute conclusion (1), and is NOT
a new PAH carrier or a PAH convergence counterexample. R-530 is preserved
byte for byte; the corrected reasoning below supersedes that paragraph only.

## 3. Core stability and the H-continuous composition

If f in D depends on a finite prefix, eta(f) depends on that same prefix.
Gauge invariance is preserved by scalar composition. If |f|<=M, then
|eta(f)|<=M. Its amplitude-l1 Lipschitz constant is no larger than f's.
Thus eta(D) subset D for every stated eta, not only clipping.

For f,g in H, |eta(f)-eta(g)|<=|f-g| almost everywhere. Integration gives
||eta(f)-eta(g)||_H<=||f-g||_H. The composition is well defined on the
L2 quotient and on the invariant completion: approximate by D and use this
inequality. On D, apply the scalar inequality to each root pair and sum
with the unchanged nonnegative conductance to obtain E(eta(f))<=E(f).
There is no claim that composition contracts the form distance.

## 4. Primary proof: the energy epigraph is closed

Define C={(u,a) in H x R: u in V and Ebar(u)<=a}. Suppose (u_k,a_k) in C
converges strongly to (u,a) in H x R. The H norms and energies of u_k
are bounded, so u_k is bounded in the Hilbert space V. First choose a
subsequence realizing the energy liminf, then a further subsequence with
a weak V limit v (Hilbert reflexivity and weak sequential compactness).
The continuous linear inclusion carries this to a weak H limit v; the
strong H limit is u, so injectivity identifies v with u and u belongs to V.

The energy seminorm is weakly lower semicontinuous on V. For completeness,
its energy balls are convex and norm-closed by form Cauchy-Schwarz, and a
norm-closed convex set is weakly closed by Hilbert separation. Equivalently
one can use weak lower semicontinuity of ||.||_V^2 and subtract the *strongly
convergent* H norms. Therefore Ebar(u)<=liminf Ebar(u_k)<=a. This proves
C closed, including the domain-membership conclusion. In infinite
dimension V itself need not be closed in H; C is the correct closed set.

Now fix ANY u in V. Choose f_k in D converging to u in V, as allowed by
the definition of minimal closure. The energy seminorm triangle inequality
implies E(f_k)->Ebar(u). Section 3 gives eta(f_k)->eta(u) in H and
(eta(f_k),E(f_k)) in C. Closedness of C gives (eta(u),Ebar(u)) in C,
which proves both assertions in (1). No image sequence is presumed Cauchy
in the form norm; no pointwise root energy formula on V is presumed.

The Lean theorem `closed_epigraph_transfer` formalizes this last passage
for arbitrary topological H, arbitrary sequences, continuous eta and an
explicit closed epigraph. The proof of epigraph closedness from the R-512
Hilbert structure remains analytic here; it is not disguised as a finite
test or an already formalized measure construction.

## 5. Independent proof: convex averages in the minimal completion

For the same recovery sequence set w_k=eta(f_k). The single-vector H and
energy bounds make w_k bounded in V. Take a weakly V-convergent subsequence
w_(k_l) with limit v. Its strong H limit is eta(u), so v=eta(u) in H.
For each integer m choose, by Mazur's lemma in the Hilbert space V, a
finite convex combination z_m of the tail {w_(k_l):l>=m} satisfying
||z_m-v||_V<1/m. Each z_m belongs to D, since D is a vector space.
Convexity of E gives

    E(z_m) <= sup_{l>=m} E(w_(k_l))
           <= sup_{l>=m} E(f_(k_l)) -> Ebar(u).

The strong V convergence gives E(z_m)->Ebar(v). Hence v belongs to the
minimal closure and Ebar(v)<=Ebar(u). This proves (1) without using the
epigraph argument or assuming eta(f_k) is form-Cauchy. The convex averages
are proof approximants, not a conditional averaging of PAH rates or states.

## 6. Resolvent, semigroup, and the constant one

Write q=Ebar on V and let K>=0 be its associated self-adjoint operator.
For lambda>0, J_lambda=(I+lambda K)^(-1) is characterized as the unique
minimizer in V of q(v)+||v-h||_H^2/lambda. Strict convexity gives uniqueness.
If 0<=h<=1, the scalar clipping p to [0,1] decreases both terms, by (1)
and the pointwise nearest-point inequality. Therefore p(J_lambda h) is
also a minimizer and equals J_lambda h. Thus J_lambda preserves [0,1].

The spectral formula gives (J_(t/m))^m h -> exp(-tK)h in H. Since the
order interval [0,1] is H-closed, T_min(t) preserves it. Linearity and
positive bounded truncation extend positivity to every nonnegative H
vector. For bounded h with ||h||_infty<=M, order preservation and the
constant identity below imply |T_min(t)h|<=M. The case t=0 is immediate.

The probability state puts 1 in H, and the original D contains 1. Every
root difference of 1 is zero, so q(1)=0. Form Cauchy-Schwarz gives
Ebar(1,v)=0 for all v in V. In the closed-form representation this states
1 in Dom(K) and K1=0 (the representing H vector is zero). Hence the
spectral calculus yields T_min(t)1=1 for every t>=0. Merely knowing that
the resolvent preserves [0,1] would not establish this equality.

## 7. Independent and hostile evidence boundary

The primary executable evaluates the preregistered example with exact
fractions and the full directed-half weighted sum. The independent
executable uses the reversible generator matrix and -<h,Lh> instead.
Hostile controls reject: (2), negative conductances, a 2-Lipschitz map,
positivity without closedness, and conservation without zero energy of 1.
The point-evaluation nonclosable control is from R-512, not a new model.
For s_n(x)=max(1-n*x,0) on [0,1], the evaluation energy is q(s_n)=1
while ||s_n||_2^2=1/(3*n) and q(s_n-s_m)=0. To test lower semicontinuity
itself, use u_n=1-s_n: u_n -> 1 in L2 but q(u_n)=0<q(1)=1.
The spikes alone test closability, not a lower-semicontinuity violation
at zero. Both implications are kept distinct in the hostile check.

The Lean file checks the exact paired-energy and form-norm counterexamples,
the universal single-root inequality, and the arbitrary-sequence closed
epigraph transfer. Tool output certifies those statements and exact-byte
replay only. Hilbert weak compactness, the probability-state crosswalk,
Mazur approximation, the form representation and spectral passage above
are analytic arguments open to independent external review. No signed
external referee report is claimed.

Sign/factor: both directed edges with state weights 1/2 and rates 2 yield
the energy coefficient one; the independent matrix computation checks it.
Domain: a finite energy liminf must prove membership in V, not simply
evaluate an undefined q(u). Limit: f_k recovery is a Hilbert completion,
with no exchange of the PAH j/n order. Hardcoding: fixture values come from
the preregistration and are recomputed; expected rational values are test
oracles only. Weak versus strong: only the H norm is subtracted after
strong convergence; no strong V convergence of w_k is assumed.

## 8. Scope and next gate

Classification is auxiliary_support, with a proof-level negative against
the paired contraction shortcut and a repaired conditional proof of the
same R-530 conclusion. R-512's inherited assumptions are not discharged.
T-054's active gate and the PAH-OMC-020 HOLD_FOR_EVIDENCE remain unchanged.

Next one scientific question: can the exact R-511 initial operator be
shown to have a unique Markov extension on the same invariant L2 space,
or does an additional boundary extension survive? This requires a separate
domain/extension contract; no equivalence to finite-to-target convergence
is asserted. Re-review immediately if an inherited assumption in section 1
fails. No physical Pre-A, spacetime, QFT, gravity, continuum, Yang-Mills,
mass gap, common causal cone or TOE conclusion follows.
