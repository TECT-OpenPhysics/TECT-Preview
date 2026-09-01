# R-476 Certificate: PAH-001 Structural Intake

## Result identity

- Result: `R-476`
- Exploration: `EXP-001357`
- Task: `T-062` under `T-054`
- Candidate: `PA-M6-RELATIONAL-APERTURE-TRANSFER-v0`
- Source packet: `strategy/pa-hyp/PAH-001-v1.json`
- Source SHA-256: `03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37`
- Intake manifest: `strategy/pa-hyp/intake-v1.json`
- Tier and scope: T0, claim-nonbearing structural and provenance intake
- Status: `STRUCTURALLY_REGISTERED_RESEARCHER_HYPOTHESIS`
- Run artefacts: `claims/C6-SPACETIME-SIGNATURE/runs/2026-09-02-r476-pah001/`
- PDF: none

## Certified boundary

R-476 certifies that the exact PAH-001 source bytes define one immutable,
reviewable researcher hypothesis with a finite carrier, functional, reversible
generator, state, candidate-internal projection, time boundary, proof-owner
interfaces, common-norm target, ordered limits, falsifiers, and promotion
firewalls.

The packet-level structural state is `OWNER_PACKET_HASHED`. This means only
that the versioned researcher source has a matching hash and declares every
required field. It does not mean that its equations have been proved, that its
dynamics has been admitted for production, or that its projection is a TECT
physical sector. The canonical R-471 snapshot remains
`EMPTY_OWNER_ARTIFACT`; production admission, physical-owner admission,
`F_reg`, `F_lim`, `F_eff`, `F_obs`, scoring, and prospective validation all
remain false.

PAH-001 is a constructed researcher hypothesis, not an external source,
synthetic contract fixture, established TECT law, or physical authority. Any
mathematical change requires `PAH-001-v2` or a new packet ID.

## Verification

The primary lane checks the exact source hash, all pinned authorities, the
nine-slot R-471 order, the eleven-slot R-192 detail order, every declared
scope field, the unchanged R-471 state function, and all promotion locks. It
passes 63/63 assertions. The non-importing independent lane reconstructs the
same state and canonical core digest and passes 52/52 assertions. Both derive
`OWNER_PACKET_HASHED`, `production_admission=NONE`, and core digest
`50e3e5900692b13cbe5f65b7c608a498ed4c1946846836fefd751baac3dcaf69`.

The hostile lane passes 39/39 checks and rejects 36 mutations, including
provenance laundering, every owner/order leak, premature map and physical
promotion, common-core and uniform-contract deletion, limit reordering, and
event-horizon or Reading-H relabelling. The integrated verifier passes 20/20,
and `lake env lean Tect/R476.lean` compiles under the pinned Lean 4.32.1
toolchain. Lean proves only the Boolean registration and promotion firewalls;
it does not prove the model equations or physical interpretation.

Reproduction commands from the repository root are:

```text
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 codes/foundations/pah001_intake.py
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 codes/foundations/pah001_intake_independent.py
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 codes/foundations/pah001_intake_hostile.py
E:\Dev\TECT.venv\Scripts\python.exe -X utf8 verification/scripts/pah001_intake_verify.py
```

## Translation of the motivating intuition

The intuition that spatial distinctions may cease to be operational beyond a
horizon-like boundary is translated into two independent,
coordinate-invariant predicates. The finite object is named only a
`TRAPPED_TRANSFER_CANDIDATE`.

### Predicate 1: low-energy spatial-mode quotient collapse

For the connected low-aperture component (I_{epsilon_c}) containing the
core anchor (C), define

\[
  (D_U\phi)_e=\phi_w-U_e\phi_v,
  \qquad
  K_I=D_U^*\operatorname{diag}(J_e(s))D_U,
  \qquad
  J_e(s)=\frac{2}{s_v+s_w}.
\]

For every fixed finite energy window \(\Lambda\), the target is

\[
  \operatorname{Tr}\mathbf 1_{[0,\Lambda]}(K_I)
  \longrightarrow \dim\ker(D_U|_I).
\]

Equivalently, the first eigenvalue above the gauge, symmetry, and harmonic
kernel must diverge. A sufficient declared target is
\(\gamma_I/\epsilon_c\to\infty\), where \(\gamma_I\) is the first positive
eigenvalue of \(D_U^*D_U\). Nontrivial holonomy or additional harmonic modes
remain explicit surviving topology; they are not forcibly identified with one
mode.

### Predicate 2: directional trapped transfer

For a neutral tagged probe on an active oriented edge, use

\[
  k(v\to w)=\kappa_0 s_v^\nu.
\]

At fixed external time \(T\), the outward first-arrival probability must obey

\[
  p_{\mathrm{out}}(\rho,T)
  =\sup_{v\in I_{\epsilon_c}}\Pr_v(\tau_O\le T)
  \le d_{\max}\kappa_0T\epsilon_c^\nu
  \longrightarrow 0.
\]

For an exterior vertex adjacent to the low-aperture component with
\(s_x\ge s_0>0\), the independently preregistered inward probability must
remain at least

\[
  p_{\mathrm{in}}(T_0)\ge
  c_0=\frac{s_0^\nu}{d_{\max}}
      \left(1-e^{-\kappa_0s_0^\nu T_0}\right)>0.
\]

Both predicates must hold on the same regulator sequence. Spectral quotient
collapse alone does not prove trapping, and finite-time trapping alone does
not prove collapse of spatial modes. The definitions use incidence,
holonomy, spectrum, anchors, and first-arrival probabilities, so they are
invariant under gauge transformations and anchor-preserving graph
relabellings. They are not coordinate singularities or a general-relativistic
event-horizon definition.

## Exact finite model

The regulator is

\[
  \rho=(G,O,C,K,M_s,M_\psi,R_{\max},\epsilon,a,
        \beta,\nu,\theta,Q).
\]

Here (G=(V,E,P)) is a finite connected oriented bounded-degree two-cell
complex. (O) and (C) are disjoint nonempty anchors. No embedding
coordinates, physical length, physical volume, dimension, lapse, metric, or
Lorentzian cone is inserted.

The microscopic variables are:

- aperture \(s_v\) on a finite grid in \([\epsilon,1]\);
- charged matter
  \(\psi_v=(R_{\max}\ell_v/M_\psi)\zeta_K^{n_v}\), with fixed
  \(Q=\sum_v\ell_v\);
- compact link \(U_e\in\mathbb Z_K\), with
  \(U_{\bar e}=U_e^{-1}\);
- an optional neutral tagged probe used only by the transfer estimand.

The finite symmetry is local \(\mathbb Z_K^V\) gauge invariance together with
the finite relabelling group \(\operatorname{Aut}(G;O,C)\). The
candidate-internal projection is

\[
  P_{\mathrm{cand}}=P_{\mathrm{Aut}}P_G.
\]

This projection acts only on the candidate's finite gauge- and
anchor-automorphism-invariant subspace. It is not a diffeomorphism quotient,
QFT Gauss-law theorem, or admitted TECT physical projection.

The displayed finite functional is

\[
\begin{aligned}
F_\rho={}&\sum_v\left[
 \frac{\lambda_s}{2}(s_v-1)^2
 +\frac{m^2}{2}|\psi_v|^2
 +\frac{\lambda_4}{4}|\psi_v|^4
 +\frac{\eta_6}{6}|\psi_v|^6
 +\frac g2s_v^2|\psi_v|^2\right]\\
&+\frac{\kappa_s}{2}\sum_{e=(v,w)}(s_v-s_w)^2
 +\frac{\kappa_D}{2}\sum_{e=(v,w)}
   J_e(s)|\psi_w-U_e\psi_v|^2\\
&+\kappa_g\sum_pJ_p(s)(1-\operatorname{Re}U_p),
\end{aligned}
\]

where \(J_p\) is the boundary-edge mean of \(J_e\). Counting measure on the
fixed-(Q) finite state space and

\[
  Z_{\rho,Q}=\sum_x e^{-\beta F_\rho(x)}
\]

fix the finite normalization. There are no additional finite counterterms or
free additive constants.

Every local move \(r\) has a declared inverse. With symmetric mobility
\(m_r(x)=m_{r^{-1}}(rx)\), the proposed generator and state are

\[
  (L_\rho f)(x)=\sum_r m_r(x)
  e^{-\beta(F_\rho(rx)-F_\rho(x))/2}[f(rx)-f(x)],
\]

\[
  \pi_{\rho,Q}(x)=Z_{\rho,Q}^{-1}e^{-\beta F_\rho(x)},
  \qquad
  T_\rho(t)=e^{tL_\rho}.
\]

The inserted mobility rules are \(s_v^\nu\) for a matter-phase move,
\((s_vs_w)^{\nu/2}\) for a matter-transfer or link move, and the geometric mean
of the before and after aperture values for an aperture move. The exponent,
move set, and rate scales are dynamics inputs; no static fit selects them.

Time \(t\) is external stochastic time, with local clock accumulation
\(d\tau_v=s_v^\nu dt\). The finite thermal parameter defines the reversible
state. No quantum KMS, proper-time, or Lorentzian-time identity is inferred.

## R-471 and R-192 mapping

PAH-001 declares the nine R-471 slots in the unchanged order:

1. `generator_or_transfer`: \(L_\rho,T_\rho(t)\);
2. `state`: \(\pi_{\rho,Q}\);
3. `physical_projection`: candidate-internal \(P_{\mathrm{cand}}\) only;
4. `time_boundary`: stationary Markov paths on \([0,\infty)\), without
   terminal conditioning;
5. `heat_root_incidence`:
   \((Bf)(x,r)=\sqrt{c_r(x)/2}[f(rx)-f(x)]\), with target
   \(B^*B=-L_\rho\);
6. `root_filtration`: an adapted order keyed by time layer, cell colour,
   cell, and move type;
7. `conditional_replicas`: two conditionally independent exchangeable draws
   from the same next-step kernel;
8. `raw_current_spatial_intertwiner`:
   \(Be^{-tB^*B}=e^{-tBB^*}B\) on the finite common core after projection;
9. `production_one_use_q_ledger`:
   \(q_r(t)=\|B_re^{-tB^*B}f\|^2\), keyed exactly once by the complete root
   label.

All nine are researcher-hypothesis definitions, axioms, or theorem targets.
None is a proved production owner or physical owner.

The unchanged R-192 detail order is also declared:

`common_heat`, `root_1`, `root_2`, `future_residual`, `covariance_bases`,
`complement`, `historical_low`, `forest`, `returned_mean`, `source`, and
`sextic`.

Each binding has status
`CANDIDATE_DEFINITION_NOT_A13_COMPATIBILITY`. Consequently PAH-001 does not
fill the historical A13 production cylinder, repair R-192, or permit any A13
reserve or gate promotion.

## Common core and limit order

The proposed common core is the algebraic union
\(\mathcal A_{\mathrm{cyl}}^{\mathrm{inv}}\) of bounded gauge- and
anchor-automorphism-invariant cylinder observables under declared
anchor-preserving refinements. The common norm is the supremum norm. The
finite Markov target gives the candidate constant \(C_T=1\) in

\[
  \|T_\rho(t)f\|_\infty\le C_T\|f\|_\infty.
\]

This finite contraction is not the missing common-core compatibility or a
continuum-uniform estimate. Refinement compatibility, generator agreement,
boundary-defect decay, Cauchy convergence, and the completed common space are
unproved.

No limit interchange is claimed. The declared order is:

1. remove any numerical split-step \(\delta_t\), if one is introduced;
2. remove local state cutoffs \((K,M_s,M_\psi,R_{\max})\) at fixed finite
   complex and fixed \(\epsilon,a,\beta\), and selector;
3. take the named anchor-preserving refinement \(a\to0\) at fixed target
   volume;
4. take nested anchored volume and exhaustion to infinity;
5. remove the phase selector after volume and exhaustion;
6. take aperture collapse \(\epsilon\to0\), with
   \(\gamma_I/\epsilon_c\to\infty\);
7. take \(\beta\to\infty\) only if a ground-state proposition is requested;
8. take observation time \(T_{\mathrm{obs}}\to\infty\) last.

Aperture collapse must precede infinite observation time. Reversing that order
is a different proposition and carries no horizon-like credit.

## Preregistered falsifiers

PAH-001 is rejected or narrowed if any applicable condition fires:

- finite gauge invariance, detailed balance, transfer positivity, Markov
  conservation, or \(P_{\mathrm{cand}}\)-commutation fails;
- the finite functional or partition normalization is not well-defined;
- \(\gamma_I/\epsilon_c\) fails to diverge or unaccounted low modes survive;
- the outward probability lacks a uniform aperture-power bound, or the inward
  probability also vanishes;
- trapping requires infinite observation time before aperture collapse or an
  undeclared exchange of limits;
- the result depends on arbitrary labels or incompatible refinement choices;
- no volume-independent exterior causal-influence envelope exists;
- static-equivalent choices of \(\nu\) or rates change the frozen two-time
  estimand, leaving a mobility equivalence class;
- the branch disappears when its selector is removed after volume and
  exhaustion;
- the same-owner branch sign overlaps zero, is nonnegative or scheme
  dependent, or the branch is nonstationary or transversely unstable;
- generator compatibility or boundary-error decay fails on
  \(\mathcal A_{\mathrm{cyl}}^{\mathrm{inv}}\);
- Lorentzian, effective, observational, scorer, or holdout reconstruction is
  absent or fails.

Failure is local to PAH-001 or the stated proposition. It is not a
falsification of every TECT candidate.

## Nonclaims

- Structural completeness does not prove gauge invariance, detailed balance,
  factorization, stability, either collapse predicate, or any limit.
- The candidate projection is not an admitted TECT physical sector.
- `TRAPPED_TRANSFER_CANDIDATE` is not an event horizon, black-hole interior,
  Lorentzian spacetime, or gravity model.
- No physical-empty branch is admitted. No Reading-H sign, stationarity, or
  transverse-stability verdict has been evaluated.
- No Pre-A, Sector-A, C6, QFT, Yang--Mills, continuum, observation,
  cosmic-origin, mass-gap, or theory-of-everything conclusion follows.
- No parameter is fitted, no observation is scored, and no prospective
  prediction is credited.
- Existing T-054, T-059, and T-061 methods and the R-471 and R-192 orders are
  unchanged.

## Next single proof question

Do the finite reversible generator, gauge projection, and root incidence define
one common-core-compatible finite transfer under the exact PAH-001 source
bytes?

The next audit must prove or refute finite gauge invariance, detailed balance,
candidate-projection commutation, \(B^*B=-L_\rho\) on the finite invariant
core, and compatibility of the declared cylinder embeddings. No branch,
physical-empty, continuum, or observation calculation is admissible before
that question is resolved.
