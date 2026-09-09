# PAH-OMC-019: minimal closure and the whole radial nullspace

Proof under preregistration SHA-256
`4337e21a140206956ea52ee10e20d04358af868969e3edb9f055e5ea64b055b7`.
Execution, acceptance and source pins are recorded in the result card. This is
a standard functional-analytic construction applied to the exact R-511 form,
not a new microscopic model or an infinite-volume temporal limit theorem.

## 1. Frozen inputs and theorem statement

Use the real invariant Hilbert space H of the R-510 local probability state,
and exactly R-511's bounded, gauge-invariant, globally amplitude-l1-Lipschitz
finite-prefix cylinder domain D. Constants belong to D. Hilbert vectors are
equivalence classes modulo zero state-L2 norm. The following inherited inputs
are used at their stated scopes, not reproved by a finite numerical test:

1. D is a dense real vector subspace of H (R-511, domain section).
2. A is the same PH/LK/AP local sum with the original rates and multiplicities.
   For each g in D, Ag is in H and ||Ag|| <= 2 D_g M_g. The bound depends on g.
3. E(f,g) = -<f,Ag> = (1/2) sum_r nu(c_r Delta_r f Delta_r g) is symmetric,
   nonnegative and finite on D. The root sum for a fixed local pair is finite.
4. For every amplitude-only a in D, Aa=0. The original aperture cylinder s_v
   has E(s_v,s_v)>0, while min(1,r_v) has positive variance and zero energy.

These are specifically equations (7) and the domain, ordered-n-passage and
radial-activity sections of the pinned R-511 certificate. Its proof uses the
R-510 fixed-prefix state theorem and R-509 fixed-n state theorem. The current
argument is conditional on those already registered analytic inputs; it does
not upgrade them to a machine-formalized measure theorem.

Let D_rad be the amplitude-only elements of D and H_rad their H-norm closure.
The scoped conclusion is:

    E is closable on H. Its minimal closed nonnegative extension Ebar has
    dense domain, H_rad is contained in that domain, and
    Ebar(h,h)=Ebar(h,u)=0 for every h in H_rad and u in Dom(Ebar).

The form is not identically zero: Ebar(s_v,s_v)=E(s_v,s_v)>0. No assertion
that ker(Ebar)=H_rad is made; other tail or invariant-label null vectors are
not classified. "Minimal" refers to the smallest closed-extension domain
agreeing with the pre-form, not to an equality with a maximal jump domain.

All original PAH parameters, partial domains and counting labels are fixed.
In particular K=2, M_s=1, epsilon=1/2, beta=nu=1, m2=theta=0 and the other
OMC-016 displayed couplings are one. The two-row G_n has 2(n+2) vertices;
its retained unsplit frontier square and label-only anchors are unchanged.
The all-Q weights are Z_Q/Z, without a new prior, quotient or Jacobian.
The state was obtained with h_j=2^(-j), R_j=2^j, M_j=2^(2j), first j for
fixed n, then the specified anchored n exhaustion. Form closure is a Hilbert
completion on that already fixed state, not another regulator or physical
continuum limit. External Markov time is unchanged and not reinterpreted.

## 2. Literature-first applicability

Primary source: Gerald Teschl, Mathematical Methods in Quantum Mechanics,
second edition, author-hosted text, section 2.3, printed pp. 77--81,
equations (2.47)--(2.49) and Theorem 2.13 (Friedrichs extension), consulted
2026-09-07: https://www.mat.univie.ac.at/~gerald/ftp/book-schroe/schroe2.pdf .
The adjacent definition of closability and point-evaluation example on
pp. 80--81 distinguish positivity from closability. Theorem 2.14 assumes a
closed form and is NOT used to prove this pre-form is closed.

Hypothesis crosswalk: dense domain, symmetry, a nonnegative lower bound and
an H-valued operator S=-A are SATISFIED by the exact inputs in section 1 and
the quotient argument below. Self-adjointness, S(D) subset D, a uniform
operator norm, bounded global exit rate and uniqueness across boundary
states are NOT REQUIRED. Quantum dynamics from the source's application
DOES NOT APPLY. Real-space proofs below avoid any complexification issue.
This is standard theorem reuse; the contribution here is the pinned PAH
applicability and the full radial-subspace consequence, not a new closability
theorem. External review of the inherited state and domain bridge is invited.

## 3. Quotient well-definedness before invoking an operator theorem

Set S=-A. Suppose x in D is zero as a vector in H. For any y in D, symmetry
and the H-valued representer give

    <y,Sx> = E(y,x) = E(x,y) = <x,Sy> = 0.

Density of D in H implies Sx=0. Linearity gives the same conclusion for two
representatives of one H vector. Thus S:D subset H -> H and E descend to the
state-L2 quotient. In particular E(x,x)=0 for H-null x; this fact is not
silently assumed from pointwise configurations. S is densely defined,
symmetric and nonnegative. No iterated application S(Sx) is used.

## 4. Primary proof: energy completion has no ghost vectors

Nonnegative symmetric bilinearity gives form Cauchy--Schwarz by applying
E(x+t y,x+t y)>=0 for every real t. If E(y,y)=0, the linear-in-t expression
forces E(x,y)=0; otherwise minimize the quadratic. Hence E(x,y)^2 is at most
E(x,x) E(y,y). The nullspace of E can be quotiented out. Complete this
pre-inner-product quotient in its energy norm to a Hilbert space K; let
j:D->K denote the natural map, which has dense range. Then

    <j f,j g>_K = E(f,g) = <f,Sg>_H.                    (1)

Consider ANY sequence f_n in D with f_n->0 in H and E(f_n-f_m)->0 as
n,m->infinity. Supports may grow without bound. The second condition says
j f_n is Cauchy, so it converges to v in K. Fix any single g in D. Since
Sg is a fixed H vector, (1) and continuity of inner products give

    <v,j g>_K = lim_n <f_n,Sg>_H = 0.

Density of j(D) implies v=0; therefore E(f_n,f_n)=||j f_n||_K^2->0.
This is exactly the sequential closability criterion. In particular it
does not require a common support or boundedness of ||Sf_n||. The fixed-test
order of quantifiers is essential. Lean formalizes this argument with
arbitrary Hilbert spaces and sequences, not a finite-size surrogate.

## 5. Independent proof: direct fixed-test epsilon estimate

The triangle inequality for the form seminorm implies sqrt(E(f_n,f_n))
is Cauchy and bounded, say by M. If M=0 the conclusion is immediate.
For any epsilon>0 choose N such that sqrt(E(f_n-f_m))<epsilon for n,m>=N.
Fix m>=N, independently of n. Bilinearity and form Cauchy--Schwarz give

    E(f_n,f_n)
      = E(f_n,f_n-f_m)+E(f_n,f_m)
      <= M epsilon + |<f_n,Sf_m>|.

The last term tends to zero by H-convergence against fixed Sf_m in H.
Thus limsup_n E(f_n,f_n)<=M epsilon, and arbitrary epsilon proves zero.
This proof uses no energy-completion orthogonality or external extension
theorem. Replacing m by n would invalidate it: ||f_n|| ||Sf_n|| need not
tend to zero. The hostile checks explicitly reject that shortcut.

## 6. Construction, closedness and minimality

Give D the form norm ||f||_1^2=||f||_H^2+E(f,f), and let V be its Hilbert
completion. The inclusion D->H is contractive and extends to a continuous
linear map i:V->H. If i(v)=0, choose f_n in D converging to v in V. Then
f_n->0 in H and is energy-Cauchy. Section 4 gives E(f_n)->0, so ||f_n||_1->0
and v=0. Thus i is injective; there is no extra completion vector over zero.

Define Dbar=i(V), and for u,v in V set

    Ebar(iu,iv)=<u,v>_V-<iu,iv>_H.                      (2)

Contractivity and approximation show this is a nonnegative symmetric
bilinear form, agreeing with E on D. Its form norm is exactly ||u||_V;
therefore Dbar is complete in the form norm, which is closedness. Dbar
contains D and is dense in H. This proves existence without assuming a
graph core, a self-adjoint generator or a maximal jump-energy domain.

For an independent injectivity test, continuity extends the identity

    <v,g>_V=<iv,(I+S)g>_H,   g in D, v in V.

If iv=0, v is orthogonal to the dense copy of D in V, hence v=0. Lean also
checks this completion-kernel argument; the analytic completion construction
and the model-specific identification of (I+S)g remain in this certificate.

Let F be any closed nonnegative form on H which agrees with E on D. For a
V-Cauchy sequence f_n in D, it is also Cauchy in the F form norm, and hence
converges in Dom(F) to a vector with the same H limit. Consequently
Dbar subset Dom(F), and taking limits in the bilinear forms gives F=Ebar
on Dbar. This is the precise minimal-extension property. It is not a
uniqueness theorem for all closed extensions, Markov extensions or
self-adjoint extensions of S. No such uniqueness is needed here.

Equivalently, the graph {(f,jf):f in D} has a closed linear-span closure W
in H x K. Section 4 excludes a nonzero (0,v) in W. Therefore W is a graph
over its first projection, and its squared second-coordinate norm is (2).
This supplies a separate check on the completion interpretation.

## 7. The whole radial subspace survives, not just a finite witness

For h in H_rad choose a_n in D_rad with a_n->h in H. Since D_rad is a
vector subspace annihilated by A, E(a_n-a_m)=0. Hence a_n is form-norm
Cauchy, h is in Dbar, and Ebar(h,h)=lim_n E(a_n,a_n)=0. Closed-form
Cauchy--Schwarz then gives Ebar(h,u)=0 for all u in Dbar. The form norm on
H_rad equals the H norm; thus H_rad is also form-norm closed. In the graph
description, (a_n,0)->(h,0) and W closed gives the same conclusion; Lean
checks this closed-graph radial-limit step.

If H_rad is described as all measurable amplitude-only L2 functions, the
density identification is as follows. The consistent R-510 finite-prefix
amplitude marginals are probabilities on a countable product of standard
Borel half-lines. Their spatial probability extension is unique on the
cylinder sigma algebra. Finite-prefix measurable functions are L2-dense:
the closed class they span contains indicators of the generating cylinder
sets and, by the monotone-class argument with dominated convergence,
all measurable-set indicators, then simple functions and all L2 functions.
For each finite prefix, bounded Lipschitz functions are L2-dense by Radon
regularity, compact truncation and continuous/Lipschitz approximation.
An amplitude-only function is automatically gauge invariant. Thus this
description yields exactly H_rad, not a restricted list of test witnesses.
No Gibbs conditional embedding or conditional averaging of a generator is
introduced by this spatial density argument.

The source witness s_v stays in the original D, so its strictly positive
aperture energy is unchanged by (2). The positive variance of min(1,r_v)
and all radial zero energies coexist with this. No spectral gap, ergodicity,
uniqueness of invariant measure or recovery of radial motion follows.

## 8. Hostile review and falsification boundaries

1. Positivity alone implies closability: UPHELD objection. On C[0,1] in
   L2[0,1], q(f)=f(0)^2 is nonnegative. f_n(x)=max(1-nx,0) satisfies
   ||f_n||_2^2=1/(3n)->0, q(f_n-f_m)=0 and q(f_n)=1. There cannot be an
   H-valued fixed representer for this evaluation form. This is a control,
   NOT a PAH counterexample or newly substituted carrier.
2. An H-null vector may have nonzero representative energy: DISMISSED for
   the pinned inputs by section 3. Removing symmetry or density would break
   that argument; the verifier does not infer them from fixture agreement.
3. E(fn)=<fn,Sfn>->0 follows just from fn->0: UPHELD against the shortcut.
   For S e_n=n^2 e_n on finite sequences, fn=e_n/n has H norm ->0 but energy
   one and energy-distance squared two for distinct n. It fails the required
   energy-Cauchy premise. The proof always pairs with a fixed test vector.
4. S must map D to D or be uniformly bounded: DISMISSED. Equations (1) and
   the epsilon proof require only each fixed Sg in H; no iterate is taken.
5. Operator closability is enough without checking form closability: UPHELD
   against that logical substitution. Sections 4 and 5 prove the form's
   precise null/Cauchy criterion, not merely the operator graph criterion.
6. A selected closed extension could add boundary vectors: VALID with
   mitigation. Section 6 uses the minimal form completion and proves its
   containment property. Maximal-domain equality is explicitly unproved.
7. A positive-variance radial witness could regain energy in closure:
   DISMISSED by the zero energy of every difference a_n-a_m and the exact
   form norm, not by finite-matrix analogy. Entire H_rad is covered.
8. Radial retention classifies the complete nullspace: UPHELD objection.
   An abstract form may have additional invariant-label or tail zero modes;
   no equality of kernels is asserted. Strict aperture positivity only proves
   the form is nonzero.

The primary and independent executable checks are analytic-identity audits,
not proofs of all inherited probability statements. They do not import each
other. Lean proves the abstract universal sequence, quotient and completion
consequences. Hostile controls test missing hypotheses and quantifier errors.
This is internal independent verification, not an external signed referee
report. No new PAH finite carrier, parameter fit or dynamics is evaluated.

## 9. Remaining single question and non-claims

Next single question, requiring a separately activated bounded contract:
does the original finite stationary semigroup, in the fixed j-before-n
order, converge on local observables to the semigroup selected by this
minimal closed form? A theorem of abstract form closure alone cannot answer
that selection/convergence question. Its contract must fix the comparison
maps and topology before a calculation; no time acceleration or new rates.

REVIEW_REQUIRED after this one closability attempt under DCTRL-000012.
Continuation requires this accepted proof and unchanged source pins, a
separate one-question budget and an explicit temporal comparison contract.
Re-review immediately for a defect in density, H-valued representers,
symmetry, quotient compatibility, the state theorem or the closure argument.
Do not repeat the same finite root tables as new progress.

This is auxiliary_support with no change to T-054's active gate, C6 T1 or
PAH-OMC-014. It does not prove essential self-adjointness, a graph core,
minimal/maximal jump-domain equality, finite-semigroup convergence, a path
law, physical infinite-volume dynamics, quantum real time, common causal
cone, continuum, physical Pre-A, spacetime, horizon, QFT, gravity,
Yang--Mills, mass gap or TOE. No Q3LOCK evidence is imported.
