# RESULTS-LEDGER — standalone-publishable results

**What this is.** A curated registry of results that emerged while developing
TECT claims but have *standalone* value — reusable lemmas, theorems, and
techniques worth organizing and publishing on their own (several are pure
harmonic-analysis / additive-combinatorics statements independent of TECT
physics). This ledger is the capture point so that nothing publication-worthy
is buried inside a claim's note chain.

**Discipline (binding).** When a development step proves something with reuse
value beyond its host claim, register it here in the SAME turn (one row), with
a stable `R-NNN` id, the one-line statement, where it is proven (claim + note),
the reuse scope, the honest tier, and a publication target. The "where proven"
pointer is the verification anchor — the result is only as strong as the note
it cites. Curated (publication-worthiness is editorial); not generated.

Cross-references: per-claim development arcs in `claims/<ID>/LINEAGE.md`;
policy in `governance/development-history.md`.

| ID | Result | Summary |
|---|---|---|
| [R-043](#r-043) | T-030 CONDITIONAL consolidation: lattice R^eps-loss closed conditionally on R-026 (proof appended); B5 closure = Lemma2+LemmaA (T'<=10 => 11N^2), independent of R-026 & cover-number L; N^2 polylog & E_2/S^2 OPEN (Bourgain-Demeter); treadmill terminated | CONDITIONAL CONSOLIDATION (not a proof certificate); B5 T7-SCOPE_adm unaffected; dr2_t030_consolidation_crosscheck.py 4/4 |
| [R-042](#r-042) | Height-energy bound E_+<=N^2+2 sum nu_k nu_l p(z_k+z_l) + sum-annulus mechanism (disjoint=>T=0); R-033 step 2 | PARTIAL; height additive energy E_h is the parameter; 4-circle incidence core OPEN; T-030 OPEN; dr2_t030_height_energy.py 5/5 |
| [R-041](#r-041) | Sidon-height latitude unions (any radii) E_+<=6N^2 incidence-free (R-033 step 1); non-Sidon residual = open 4-circle incidence | PARTIAL ADVANCE; PROVED Sidon bound; residual = R-033 core; T-030 OPEN; dr2_t030_sidon_decoupling.py 7/7 |
| [R-040](#r-040) | True sphere L-dependence: distinct-radius circles E_+<=(2 p_max+1)N^2 and empirically O(N^2) even at AP heights; linear is a cylinder artifact | PARTIAL ADVANCE; refined bound PROVED + O(N^2) sphere conjecture (T4); residual = 4-circle incidence -> R-033; T-030 OPEN; dr2_t030_height_multiplicity.py 6/6 |
| [R-039](#r-039) | Few-circles bound is LINEAR on a sphere: E_+ <= 6(L+1)N^2 (sharpens R-038's quadratic) | PARTIAL ADVANCE; cover-number lower bound doubled to L >= N^delta/12; sphere-essential; T-030 OPEN; dr2_t030_fewcircles_linear.py 6/6 |
| [R-038](#r-038) | Few-circles (covering-number) bound E_+ <= 3L^2N^2 + [NEST-DEPTH] witness reclassified technique-only | PARTIAL ADVANCE / frontier clarification (T7-within-class = R-021 + Cauchy-Schwarz); T-030 OPEN; dr2_t030_fewcircles.py 8/8 |
| [R-037](#r-037) | Route 3: the non-lattice remainder is non-load-bearing for B5's admissibility-bo … | STRUCTURAL ANALYSIS, operator-ACCEPTED + ENACTED 2026-06-13 as B5-Route3-NonLattice-NonLoa … |
| [R-036](#r-036) | T7 re-proof attempt: poly-separated subclass DR-2 closed modulo continuous decou … | PARTIAL ADVANCE, operator-ACCEPTED 2026-06-13 as DR2-T030-BDDiscrete-ReproofAttempt-260613 … |
| [R-035](#r-035) | R2 multi-scale bookkeeping: power-sum N-counting loss-free + D-loss reduced to o … | PARTIAL ADVANCE, operator-ACCEPTED 2026-06-13 as DR2-T030-R2-Bookkeeping-Reduction-260613 … |
| [R-034](#r-034) | R1 local-to-global bridge (arbitrary-Q DR-2 conditional chain) | ACCEPTED 2026-06-12 … |
| [R-033](#r-033) | Arbitrary-Q sphere additive energy: E_+(Q) <= C N^{9/4} (frontier record) | PROVED MODULO [CIRC-INC] … |
| [R-032](#r-032) | Coherence circle-packing lemma: separation bounds sum-circle occupancy on the sp … | T7 … |
| [R-031](#r-031) | Reading-H C_full extension enacted as T7-SCOPE_{C_full, thin O} (operator-accept … | T7-SCOPE_{C_full} ENACTED + COMFORTABLE-UPGRADED 2026-06-10 … |
| [R-030](#r-030) | Reading-H comparison theorem T7-closed (H-LAYER discharged) within the lattice d … | T7 ENACTED 2026-06-10 … |
| [R-029](#r-029) | SC-SCOPE endpoint floor sharpening (candidate lift) | PARTIAL ADVANCE; LIFT RETRACTED 2026-06-08 … |
| [R-028](#r-028) | H-ADM-COH discharge decision (lattice class) -- the finite margin | ENACTED 2026-06-08 … |
| [R-027](#r-027) | DR-2 -> STEP-5B G1'''-AE integration (amplitude bridge) | T7 … |
| [R-026](#r-026) | DR-2 for the lattice class -- UNCONDITIONAL (decoupling-free, Route A) | T7 … |
| [R-025](#r-025) | Sum-level-circle additive-energy bound (unconditional) | T7 … |
| [R-024](#r-024) | Decoupling-iteration energy inequality | T4+ STRONG EVIDENCE … |
| [R-023](#r-023) | Affine-invariance of additive energy | T7 |
| [R-022](#r-022) | DR-2 via l2-decoupling | T4 … |
| [R-021](#r-021) | Sphere-circle cross-energy bound (corrected) | T7 |
| [R-020](#r-020) | Physical secondary-shell ratio lies in the no-condensate-certified region | T4 |
| [R-019](#r-019) | Controlled-error continuum no-condensate for an enumerated variational selection | T4 |
| [R-018](#r-018) | Exact-Wick off-diagonal correction is O(A^4) and amplitude-aligned | T4 |
| [R-017](#r-017) | Operating-point-faithful multi-shell no-condensate via a validated diagonal eval … | T4 |
| [R-016](#r-016) | Multi-knob controlled-error + continuum no-condensate + orthogonal-shell Hessian | T4 |
| [R-001](#r-001) | P²-representation theorem | T7 … |
| [R-002](#r-002) | Universal single-circle theorem | T7 |
| [R-003](#r-003) | Antipodal-carrier partition | T7 |
| [R-004](#r-004) | ν = μ_C identity | T7 |
| [R-005](#r-005) | Coherence indistinguishability lemma | T4 |
| [R-006](#r-006) | Stereographic incidence transfer | T4 … |
| [R-007](#r-007) | Rectangle reformulation + triple count | T6 |
| [R-008](#r-008) | Amplitude-dyadic lift | T3 |
| [R-011](#r-011) | Sign-decomposition for slaved-variance uniqueness | T4 |
| [R-010](#r-010) | Common-mode dressing cancellation | T4 |
| [R-009](#r-009) | Coherence-resolution admissibility | T3 |
| [R-012](#r-012) | Closed-form Prop-A layer-margin recomputation | T5 … |
| [R-013](#r-013) | Direct dressing-variance endpoint evaluation | T4 |
| [R-015](#r-015) | Curvature-certified controlled-error selection margin | T4 |
| [R-014](#r-014) | Convention-free per-transfer form-factor reduction | T4 |

<a id="r-043"></a>
### R-043 — T-030 consolidation & external-literature closure (treadmill terminated)

**Statement (one line):** CONSOLIDATION (no new theorem). T-030 splits into three precise versions with honest status: (a) LATTICE R^eps-loss, Q subset Z^3 cap {|x|^2=R} => E_+ <<_eps R^eps N^2 = CLOSED CONDITIONALLY on R-026 (Lemma A + Dirichlet class-number/divisor, T7-NTstandard, decoupling-free; the COMPLETE self-contained proof is APPENDED in the note Sec.A: A.1 Lemma A, A.3 [DIV-CIRC] shift-removal/class-number/divisor, A.4 the assembled T-030a theorem -- T-030a is thus paper-grade citable from R-043 modulo textbook number theory), externally corroborated (object only) by Mudgal, "Additive energies on spheres", JLMS 106(4):2927-2958 (2022), arXiv:2105.06925 (d=4 threshold-breaking m^eps|A|^{2+1/3-1/2766}; d=3 improves Benatar-Maffucci; clean R^eps N^2 NOT attributed to a specific d=3 theorem number absent from the abstract); (b) LATTICE N^2 polylog (eps-removal) = OPEN, not a known theorem; (c) ARBITRARY REAL Q in S^2, E_2(Q) <<_eps (#Q)^{2+eps} = OPEN, a Bourgain-Demeter conjecture (Sheffer exposition). NO E_2/S^2 best-known exponent is claimed: the published O(#A^{7/2}) is for E_3 on S^1, a DIFFERENT object (the v1.0 'best ~O(n^{7/3})' is WITHDRAWN as unverified). Internal session results R-038..R-042 (T7-in-class / PARTIAL) sharply localise the (c) obstruction to the non-Sidon overlapping-annulus four-circle incidence energy but do NOT close (b),(c). B5's OWN closure is Lemma 2 (R-032, admissible => T'<=10) + Lemma A (R-025, E_+<=(1+T')N^2) => E_+<=11N^2 -- it uses the sum-circle OCCUPANCY T' and needs NEITHER R-026 (lattice divisor, the separate T-030a result) NOR the few-circles cover-number L (R-038/R-039). The v1.0 'admissible/lattice class closed (R-026 + Lemma-2 cap)' conflated two independent arguments and is CORRECTED. Arbitrary-Q (b),(c) is NON-LOAD-BEARING (H-NONLATTICE-REMAINDER / DR2-SHARE), so B5 = T7-SCOPE_{adm} is UNAFFECTED. Terminates the analytical reduction treadmill: pursuing (c) is pursuing a known open research problem (the external ~140-step R-043..R-189 chain never closed it and is NOT adopted). Verified dr2_t030_consolidation_crosscheck.py 4/4 (single-circle anchor 34668; bound hierarchy; literature constants with provenance).

**Proven in:** B5 / dr2-t030-consolidation v1.0

**Reuse scope:** T-030 status of record; the lattice/real split; external literature anchor (Mudgal 2022; Demeter-Katz); methodological boundary terminating unbounded reduction chains on recognised open problems.

**Tier:** CONDITIONAL CONSOLIDATION -- NOT an independent proof certificate. T-030a CLOSED CONDITIONALLY on R-026 (T7-NTstandard; statement+proof appended); T-030b & E_2/S^2 OPEN (Bourgain-Demeter). B5 closure independent (Lemma2+LemmaA => 11N^2). B5 stays T7-SCOPE_{adm} given A1. No tier/gate/hypothesis flip. Operator review 2026-06-19 ACCEPTED the operational decision with these four corrections.

**Publication target:** S^2 additive-energy paper / T-030 (status section); cites Mudgal 2022.

<a id="r-042"></a>
### R-042 — Height-energy bound + sum-annulus mechanism (R-033 step 2)

**Statement (one line):** Two PROVED structural results localising the open T-030 core, no closure. (1) HEIGHT-ENERGY BOUND: for distinct-radius parallel circles, E_+(Q) <= N^2 + 2 sum_{(k,l)} nu_k nu_l p(z_k+z_l), p(H)=#{(i,j):z_i+z_j=H}; uniform nu => N^2 + 2(N^2/L^2)E_h with E_h=sum_H p(H)^2 the HEIGHT additive energy -- recovers Sidon (E_h~L^2 => O(N^2), matching R-041) and AP (E_h~L^3 => O(LN^2), matching R-039), identifying E_h (a 1-D additive energy) as the controlling parameter (dimension reduction). (2) SUM-ANNULUS MECHANISM: the off-diagonal 4-circle term I_{ijkl}=sum_w r^{ij}(w)r^{kl}(w) has r^{ij}(w)!=0 only for |w| in [|rho_i-rho_j|,rho_i+rho_j], so DISJOINT sum-annuli => I_{ijkl}=0 (rigorous; overlap is necessary-not-sufficient -- discrete sum-sets must also coincide). This is why spread/distinct radii suppress the 4-circle energy to O(N^2) and equal radii (cylinder, all annuli [0,2rho]) maximise it. The height-energy bound is LOOSE for high-E_h heights (measured E_+/bound=0.26 at AP L=7); the gap = the in-plane incidence cancellation = the OPEN R-033 core. Verified dr2_t030_height_energy.py 5/5. Honest correction recorded: "overlap => I>0" was refuted (overlap necessary not sufficient).

**Proven in:** B5 / dr2-t030-height-energy v1.0

**Reuse scope:** arbitrary-Q DR-2 (T-030); the reduction of latitude-union energy to the 1-D height additive energy E_h; the sum-annulus necessary condition for the off-diagonal four-circle incidence energy (the R-033 attack surface).

**Tier:** PARTIAL ADVANCE / R-033 step 2. Both structural results PROVED (elementary). Does NOT close the incidence bound or the sphere O(N^2) conjecture (stays STRONG EVIDENCE T4, R-040); T-030 arbitrary-Q OPEN (record N^{9/4}, R-033). No tier/gate/hypothesis flip; B5 stays T7-SCOPE_{admissibility-bounded} given A1.

**Publication target:** S^2 additive-energy paper / T-030

<a id="r-041"></a>
### R-041 — Sidon-height latitude unions: E_+ <= 6 N^2 incidence-free (R-033 step 1)

**Statement (one line):** (PROVED) A union of L latitude circles (parallel planes, ANY radii) at heights z_i forming a SIDON set has E_+(Q) <= 6 N^2, incidence-free. Proof: the height equation z_a+z_b=z_c+z_d + Sidon => {z_a,z_b}={z_c,z_d} (plane-index multiset matches); each of the two matched arrangements (i,j,i,j) and (i,j,j,i) contributes E_+(C_i,C_j) resp. corr(C_i,C_j), both <= 3 nu_i nu_j (R-021 / Cauchy-Schwarz with E_+(C)<=3 nu^2); sum over ordered (i,j) gives <= 6 N^2. RADIUS-AGNOSTIC (the Sidon condition is on heights only; contrast R-040's (2 p_max+1)N^2 which needs distinct radii). This isolates the incidence-FREE part of the R-040 sphere O(N^2) conjecture; the NON-Sidon residual is the off-diagonal four-circle in-plane incidence energy #{c_a+c_b=c_c+c_d: c_a in C_i,...,{i,j}!={k,l}}, which does NOT reduce to a bounded 2D concentric-circle energy (that grows with L: 3.2,3.9,5.4,6.0 at L=2,4,6,8) -- a height-aware open incidence problem = the R-033 core. Verified dr2_t030_sidon_decoupling.py 7/7 (decoupling exact 0 mismatched; E_+<=6N^2 to L=8; arrangement decomposition; radius-agnostic equal-radius check; non-Sidon residual 1248 at L=5 AP).

**Proven in:** B5 / dr2-t030-sidon-decoupling v1.1

**Reuse scope:** arbitrary-Q DR-2 (T-030); the incidence-free Sidon-height case; the precise reduction of the sphere O(N^2) conjecture to the off-diagonal four-circle incidence energy (R-033).

**Tier:** PARTIAL ADVANCE / R-033 step 1. Sidon-height bound PROVED (T7-within-class, any radii). Sphere O(N^2) conjecture stays STRONG EVIDENCE (T4, R-040). Does NOT close T-030: arbitrary-Q N^{2+eps} OPEN (record N^{9/4}, R-033). No tier/gate/hypothesis flip; B5 stays T7-SCOPE_{admissibility-bounded} given A1. Honest corrections recorded (constant 3->6; 2D-concentric reduction refuted).

**Publication target:** S^2 additive-energy paper / T-030

<a id="r-040"></a>
### R-040 — True sphere L-dependence of the few-circles energy (height-multiplicity refinement)

**Statement (one line):** (PROVED) For L parallel circles with DISTINCT radii at heights z_i (N=|Q|), E_+(Q) <= (2 p_max + 1) N^2, p_max = max_H #{(i,j): z_i+z_j=H} (height additive multiplicity) -- replaces R-039's linear L by p_max (multi-circle Lemma A / R-025 refinement; for m!=0 grouping by plane-pair, the in-plane cross term r^{ij}(M_xy)<=2 by distinct radii, and the M_xy=0 i!=j term vanishes). (EMPIRICAL TRUTH) distinct-radius parallel circles (sphere latitudes have radii sqrt(R-z_i^2), distinct ONLY when z_i^2 pairwise distinct -- z and -z share a radius; the test family 5,10,..,5L is a distinct-radius family, not a sphere-arithmetic family) have E_+/N^2 BOUNDED (~3) EVEN at AP heights (p_max~L): tested to L=12 (Sidon E_+/N^2 2.22-2.60, AP 2.60-2.83) -- E_+ = O(N^2), L-INDEPENDENT; the p_max bound is loose because distinct radii send the colliding plane-pairs to different in-plane sums. (CONTRAST) the LINEAR regime is an EQUAL-radius (cylinder, off-sphere) artifact: same radius + AP heights gives the product C x AP, E_+ ~ 2 L N^2 (E_+/N^2 4.3->22.9, E_+/(LN^2)~1.9 const at L=2..12). Verified dr2_t030_height_multiplicity.py 6/6. CONJECTURE: sphere latitude unions have E_+ = O(N^2 polylog); the residual to a proof is the off-diagonal 4-circle in-plane energy = an incidence problem (-> R-033).

**Proven in:** B5 / dr2-t030-height-multiplicity v1.0

**Reuse scope:** arbitrary-Q DR-2 (T-030); the height-multiplicity refinement of the few-circles bound; the distinct-radius (sphere) vs equal-radius (cylinder) energy dichotomy; motivation for the R-033 incidence route.

**Tier:** PARTIAL ADVANCE / frontier characterisation. Refined bound (2 p_max+1)N^2 PROVED (T7-within-class, distinct radii essential). O(N^2) sphere conjecture STRONG EVIDENCE (T4, scan to L=12 no growth). Does NOT close T-030: arbitrary-Q N^{2+eps} STILL OPEN (record N^{9/4}, R-033). No tier/gate/hypothesis flip; B5 stays T7-SCOPE_{admissibility-bounded} given A1. Honest prediction-correction recorded (initial AP->linear prediction refuted by the data for distinct radii).

**Publication target:** S^2 additive-energy paper / T-030

<a id="r-039"></a>
### R-039 — Few-circles additive-energy bound is LINEAR on a sphere (sharpens R-038)

**Statement (one line):** For Q on an origin-centred S^2 (N=|Q|) covered by L distinct circles, E_+(Q) <= (2+2L)N^2 + 4LN + 4L^3 <= 6(L+1)N^2 -- LINEAR in L, strictly improving R-038's 3 L^2 N^2 (the exact bound for every L>=2; the simplified 6(L+1)N^2 form for L>=3). Proof: a multi-circle refinement of Lemma A (R-025) -- for m!=0, a.m=|m|^2/2 iff |a|=|b| (origin-centred sphere), so r(m) <= t_m=|Q cap C_m|, and two distinct circles meet in <=2 points gives t_m <= 2L off the <=L cover sum-circles C_{m_i}, t_{m_i} <= nu_i+2L. SPHERE-ESSENTIAL: off the sphere (|a|!=|b|) r(m)<=t_m FAILS and R-038's quadratic is the correct general-circle bound (a proof-mechanism guard #{m!=0: r(m)>2L}<=L detected an off-sphere cylinder test config and now passes on the genuine integer sphere x^2+y^2+z^2=1105^2). CONSEQUENCE: E_+ >= N^{2+delta} => cover number L >= N^delta/12 (R-038 gave N^{delta/2}/sqrt3; exponent doubled), pinning the open core from two sides with R-033 Cor.1.2 (rich sum-circle count). Verified dr2_t030_fewcircles_linear.py 6/6 (linear bound holds; A6 mechanism passes on S^2; strict improvement over R-038; estimator audit). TIGHTNESS on S^2 NOT claimed (measured E_+ ~ 3N^2, L-independent on rich-latitude unions -- far below the bound; true energy may be O(N^2 polylog) per R-033).

**Proven in:** B5 / dr2-t030-fewcircles-linear v1.0

**Reuse scope:** arbitrary-Q DR-2 (T-030); the multi-circle Lemma-A occupancy refinement; the sharpened cover-number lower bound on additive-energy extremizers on a sphere.

**Tier:** PARTIAL ADVANCE / frontier sharpening. Theorem T7-WITHIN-CLASS (elementary, sphere-only). Strictly improves R-038's bound (quadratic -> linear). Does NOT close T-030: arbitrary-Q N^{2+eps} STILL OPEN (record N^{9/4}, R-033). No tier/gate/hypothesis flip; B5 stays T7-SCOPE_{admissibility-bounded} given A1. Operator decides any disposition.

**Publication target:** S^2 additive-energy paper / T-030

<a id="r-038"></a>
### R-038 — Few-circles (covering-number) additive-energy bound + [NEST-DEPTH] witness reclassification

**Statement (one line):** For finite Q covered by L circles, E_+(Q) <= 3 L^2 N^2 (Cauchy-Schwarz over the L^2 index pairs + R-021 per-pair E_+(Q_i,Q_j) <= 3|Q_i||Q_j|); hence L <=_eps N^eps => E_+ <=_eps N^{2+eps}, closing arbitrary-Q DR-2 UNCONDITIONALLY for the few-circles class (no decoupling, no incidence bound). The [NEST-DEPTH] lacunary witness (R-036; {2^-j} on a great circle) lies on ONE circle, so E_+ <= 3N^2 (R-021) INDEPENDENT of its nesting depth log2(1/s) -- the exp(depth) fixed-scale telescoping loss is a TECHNIQUE artifact, not bound hardness; the witness is reclassified TECHNIQUE-ONLY. Open core delineated: E_+ <= min(3L^2N^2, (1+T')N^2, C N^{9/4}), so any E_+ >= N^{2+delta} family needs L = N^{Omega(1)} circles AND T' = N^{Omega(1)} simultaneously rich (super-poly-many rich circles; R-033 Cor.1.2). Verified dr2_t030_fewcircles.py 8/8 (single circle E_+=34668 matches R-033 F1/F5; few-circles bound on L=1/3/4; per-pair multiplicity <=2; witness depth 3->6, E_+/N^2 flat ~1.8).

**Proven in:** B5 / dr2-t030-fewcircles v1.0

**Reuse scope:** arbitrary-Q DR-2 (T-030); a covering-number sufficient condition complementary to Lemma A's richness axis; the settled (technique-only) status of the [NEST-DEPTH] witness.

**Tier:** PARTIAL ADVANCE / frontier clarification. Few-circles bound T7-WITHIN-CLASS (elementary: R-021 [T7] + Cauchy-Schwarz over L^2 index pairs). Witness reclassification PROVED (R-021 at L=1 + machine depth-independence). Does NOT close T-030: arbitrary-Q N^{2+eps} STILL OPEN (unconditional record N^{9/4}, R-033). No tier/gate/hypothesis flip; B5 stays T7-SCOPE_{admissibility-bounded} given A1. Operator decides any disposition.

**Publication target:** S^2 additive-energy paper / T-030

<a id="r-037"></a>
### R-037 — Route 3: the non-lattice remainder is non-load-bearing for B5's admissibility-bounded statement

**Statement (one line):** B5's beyond-layer machinery (Lemma A K_floor<=T', rectangle K(n)<=8+4sqrt(14)kappa^4 sqrt(n), R_lead=23.2(1+T')I) depends on the competitor ONLY through (T', n). The coherence circle-packing Lemma 2 (res5_036; PURE geometry, uses only theta_min and q0 -- no lattice/DR-2/decoupling) caps T'(Q) <= floor(2pi/theta_min) <= 10 for EVERY admissible (coherence-resolved) competitor, lattice OR non-lattice; n <= n_pack ~ 49. Hence R_lead <= 23.2*11*I = 0.510 < 1 and K(49) ~ 113 << 5972 for the FULL admissible class with NO arbitrary-Q DR-2. So H-NONLATTICE-REMAINDER-EXCLUDED is NON-LOAD-BEARING for B5's admissibility-BOUNDED statement (A); it is load-bearing ONLY for the strictly stronger admissibility-DISCHARGED (H-ADM-COH removed) lattice-only statement (B). Arbitrary-Q DR-2 (T-030) would only remove the admissibility cap -- a frontier strengthening, not a requirement. Verified dr2_t030_route3_nonloadbearing.py 5/5 (Lemma 2 cap 10 pattern-generic; non-lattice configs obey it; beyond-layer depends only on (T',n)). Parallels synthesis Sec.4b for the C_full head.

**Proven in:** B5 / b5-nonlattice-nonloadbearing-route3 v1.0

**Reuse scope:** B5 hypothesis analysis; the admissibility-bounded vs admissibility-discharged statement distinction.

**Tier:** STRUCTURAL ANALYSIS, operator-ACCEPTED +

**ENACTED 2026-06-13** as B5-Route3-NonLattice-NonLoadBearing-260613: H-NONLATTICE-REMAINDER-EXCLUDED RECLASSIFIED from CONDITIONAL hypothesis to DEFINITIONAL SCOPE; B5 PROMOTED T6-conditional -> T7-SCOPE_{admissibility-bounded} (label B5-BeyondLayer-T7Scope-260613; substantive hypothesis set empty; Attack-4 (T',n)-only chain audit 6/6, script v1.1.0). MANDATORY scope qualifier: B5 does NOT claim unrestricted arbitrary-Q DR-2. T-030 unconditional stays OPEN as a frontier strengthening (removing the admissibility cap).

**Publication target:** Reading-H vacuum-selection paper / B5 tier

<a id="r-036"></a>
### R-036 — T7 re-proof attempt: poly-separated subclass DR-2 closed modulo continuous decoupling only; residual [NEST-DEPTH]

**Statement (one line):** The in-bundle reproof attempt of the [BD-DISCRETE] well-separated reduction: for poly-separated Q subset S^2 (min-sep s >= N^-C, fixed C, after affine R-023 normalization), E_+(Q) <=_{eps,C} N^{2+eps} PROVED modulo ONLY the continuous l2-decoupling theorem [BD-CONTINUOUS] (one frequency per s-cap + the R-034 Besicovitch bridge; delta=s gives E_+ <= s^{-2eps}N^2 = N^{2+2C eps}). This SPLITS the bundled residual: [BD-DISCRETE] = [BD-CONTINUOUS] (textbook, discharges the poly-separated subclass) + [NEST-DEPTH] (nested-cluster recursion depth control; the lacunary witness 2^-j has depth log2(1/s), unbounded; fixed-scale iteration costs exp -- the single genuine open piece). Independent proven-case confirmation: crystallographic shells (poly-separated, s~N^{-1/2}) have E_+/N^2 = 5.27/4.93/3.93 bounded and decreasing. Verified dr2_t030_bd_discrete_reproof.py 5/5.

**Proven in:** B5 / dr2-t030-bd-discrete-reproof-attempt v1.0

**Reuse scope:** arbitrary-Q DR-2 (T-030); the poly-separated subclass closure (clean continuous-decoupling-only hypothesis); reusable.

**Tier:** PARTIAL ADVANCE, operator-ACCEPTED 2026-06-13 as DR2-T030-BDDiscrete-ReproofAttempt-260613 (gate G1; clean-run 5/5): poly-separated subclass T6 PROVED CONDITIONAL on [BD-CONTINUOUS] only; [BD-DISCRETE]=[BD-CONTINUOUS]+[NEST-DEPTH]; arbitrary-Q unconditional NOT achieved; B5 T7 NOT achieved by this route; honest ceiling T6-conditional. [NEST-DEPTH] open (not refuted; broad-narrow/summable-eps routes remain). T-030 unconditional N^{2+eps} stays OPEN (general record N^{9/4}, R-033).

**Publication target:** S^2 additive-energy paper / T-030

<a id="r-035"></a>
### R-035 — R2 multi-scale bookkeeping: power-sum N-counting loss-free + D-loss reduced to one decoupling invocation

**Statement (one line):** The arbitrary-Q DR-2 conditional chain's R2 residual splits into (i) N-counting, PROVED loss-free by the power-sum/superadditivity lemma sum_theta N_theta^p <= (sum N_theta)^p for p=1+eps/2>=1 (so E_+(Q) <= D^2 C N^{2+eps} at ANY split balance -- the unbalanced-tree fear is dissolved); and (ii) D-counting, where a naive fixed-scale tree provably accumulates an exponential D^{2(N-1)} on the maximally-unbalanced tree, but submultiplicativity of the decoupling constant collapses it to a single critical-scale loss s^{-2eps}N^2. The remaining geometry-dependent s^{-eps} is removed by the SINGLE named ingredient [BD-DISCRETE] (the Bourgain-Demeter discrete well-separated reduction) or polynomial separation s>=N^-C. R2 thereby tightens from 'vague multi-scale bookkeeping' to one clean invocation; with R1 (R-034) proved, the chain rests on separated base + [BD-DISCRETE]. Verified dr2_t030_r2_bookkeeping.py 5/5 (power-sum on 400 random + maximally-unbalanced partitions; D^{2G} blow-up exp(40.2) at N=30; one-shot N^{6eps} at s=N^-3; adversarial growth 1.8->10.5->74.9).

**Proven in:** B5 / dr2-t030-r2-bookkeeping v1.0

**Reuse scope:** arbitrary-Q DR-2 conditional chain (T-030); the power-sum loss-free N-counting (reusable in any decoupling-to-energy recursion).

**Tier:** PARTIAL ADVANCE, operator-ACCEPTED 2026-06-13 as DR2-T030-R2-Bookkeeping-Reduction-260613 (gate G1; clean-run 5/5): R2 REDUCED not closed; arbitrary-Q chain = T6-BDconditional, residual set {R1,R2} -> single [BD-DISCRETE]. T-030 unconditional N^{2+eps} stays OPEN; B5 T7 blocker = T-030. Two operator-stated T7 routes: adopt [BD-DISCRETE] as a standard black box (conditional theorem) OR reprove the discrete reduction in-bundle.

**Publication target:** S^2 additive-energy paper / T-030

<a id="r-034"></a>
### R-034 — R1 local-to-global bridge (arbitrary-Q DR-2 conditional chain)

**Statement (one line):** Ball decoupling alone implies E_+(Q) <= D^4 (sum_theta E_+(Q_theta)^{1/2})^2 via the exact Besicovitch limit for trigonometric polynomials (avg_S = sum_v c_v w-hat(v) beta_S(v), envelope S^{-2}) + Minkowski in L^2(dy) + translate-invariance of the decoupling constant -- the cross-scale induction's cited residual R1 is now a WRITTEN PROOF; the conditional arbitrary-Q chain's residual set shrinks {R1,R2} -> {R2} (multi-scale bookkeeping only). Verified dr2_t030_r1_bridge.py 3/3 (operator clean-run

**CONFIRMED 2026-06-12**). NOTE: first registered by the overnight dispatch as 'R-031' WITHOUT the ledger pre-check (collision with the taken R-031); corrected here.

**Proven in:** B5 / dr2-t030-frontier-consolidation v1.1

**Reuse scope:** arbitrary-Q DR-2 conditional chain (T-030); decoupling local-to-global bridges (reusable).

**Tier:** ACCEPTED 2026-06-12 (operator): written proof; chain stays T6-conditional on Bourgain-Demeter + the R2 bookkeeping.

**Publication target:** S^2 additive-energy paper / T-030

<a id="r-033"></a>
### R-033 — Arbitrary-Q sphere additive energy: E_+(Q) <= C N^{9/4} (frontier record)

**Statement (one line):** For EVERY finite Q subset S^2 (no lattice, separation, or amplitude hypothesis), E_+(Q) <= C N^{9/4}: dyadic occupancy classes on Lemma-A sum-circles + the classical Pach-Sharir/CEGSW point-circle incidence bound (n_k <= C N^3/k^5 + C N/k; m -> C_m injectivity proved; stereographic transfer) balanced at k* = N^{1/4}. Beats the prior unconditional N^{5/2}-class record by delta = 1/4; corollary pins any DR-2 counterexample to richness scale k in [N^d, N^{(1-d)/3}] with d < 1/4. Verified dr2_t030_dyadic_richness.py 9/9, worst E_+/N^{9/4} = 1.163 over 7 adversarial families incl. the rich-latitude control (operator clean-run

**CONFIRMED 2026-06-12**). Registration (number corrected from the colliding draft 'R-030'; operator ratification of the corrected name pending): R033-ArbitraryQ-DR2-N9over4-INCstandard-260612.

**Proven in:** B5 / dr2-t030-frontier-consolidation v1.1

**Reuse scope:** arbitrary-Q DR-2 (T-030); sphere incidence/additive-energy methods (standalone harmonic-analysis interest).

**Tier:** PROVED MODULO [CIRC-INC] (classical 1990 incidence geometry import; analogous to the R-026 NT-standard import -- operator decides the import class). T-030 remains OPEN for N^{2+eps}. Aronov-Sharir refinement to N^{20/9+eps} noted.

**Publication target:** S^2 additive-energy paper / T-030

<a id="r-032"></a>
### R-032 — Coherence circle-packing lemma: separation bounds sum-circle occupancy on the sphere

**Statement (one line):** For a theta_min-separated point set Q on a sphere of radius Q0 (pairwise geodesic >= theta_min), every sum-circle C_t={x: x.t=|t|^2/2} (t!=0), a Euclidean circle of radius rho=sqrt(Q0^2-|t|^2/4)<=Q0, has occupancy #(Q cap C_t) <= floor(2pi/theta_min). Proof (elementary): points on C_t are pairwise Euclidean >= 2Q0 sin(theta_min/2); k points on a radius-rho circle pairwise >= d satisfy k<=pi/arcsin(d/2rho), and rho<=Q0 gives d/2rho >= sin(theta_min/2) => k<=2pi/theta_min. No lattice/additive/number-theoretic input; uniform over t. Application: with R-025 (K_floor<=T'=max occupancy), it bounds the TECT off-diagonal additive-energy floor K_floor<=floor(2pi/theta_min)=10 for the full coherence-resolved competitor class, upgrading the Reading-H off-diagonal margin to x1.96. Verified res5_036 (5/5): bound 10 uniform across the window, adversarial max admissible occupancy 8, random 2.

**Proven in:** B1-RH-ENUM / coherence-offdiag-comfortable-bound-260610 v1.0 (res5_036)

**Reuse scope:** Any additive-energy / mode-mixing bound for separated points on a sphere or strictly convex surface; the TECT off-diagonal stability (reusable, elementary -- an alternative to decoupling-based additive-energy bounds for the separated case).

**Tier:** T7 (elementary, proved; res5_036 5/5). General sphere additive-energy (non-separated) unchanged -- decoupling territory (R-022/R-024).

**Publication target:** sphere additive-energy / Reading-H off-diagonal paper

<a id="r-031"></a>
### R-031 — Reading-H C_full extension enacted as T7-SCOPE_{C_full, thin O} (operator-accepted)

**Statement (one line):** The enacted lattice Reading-H T7 (R-030) is extended to the FULL admissible competitor class C_full (lattice + non-lattice real-antipodal, packing-bounded, coherence-resolved) and operator-enacted 2026-06-10 as T7-SCOPE_{C_full, thin O} within R_{C_full}={mu^2 in (0,mu^2_max=3U^2/(20V)=0.0342), I in (0,min(I_c^sel(mu^2), I_off^Cfull))}, given A1-KERNEL-CONV. Mechanism: (i) off-diagonal (O) -- elementary antipodal lemma (x in C_t => -x not in C_t for t!=0 => T'<=N/2) + R-025 (K_floor<=T') + coherence packing (N<=n_pack<=40.88 across the band) => K_floor<=20<20.55=K* => R_lead<=0.974<1 for EVERY admissible competitor incl non-lattice (PROVED, thin x1.026, the universal cap I_off^Cfull=1/(23.2*21)=2.053e-3 binds < I_c^sel=2.50e-3); (ii) (D) diagonal isotropy and (S) selection floor are competitor-agnostic (layer/packing, comfortable). Operating point (2e-3,0.005) interior, thin 2.6% off-diagonal headroom (NOT the Step-1 selection 20%). EXT (max K_floor~3 in arithmetic subclass) is an OPTIONAL T2 margin upgrade (x5.39), NOT a closure blocker. Verified res5_032/033/034/035 (Steps 1-3 + enactment, all PASS).

**Proven in:** B1-RH-ENUM/B2-PROPA-HLAYER / cfull-internal-scope-closure-260610 v1.1 (+ window-certification v1.1, ext-additive-energy-extremal-status, DS-nonlattice-extension, res5_035)

**Reuse scope:** TECT vacuum-selection layer; the Reading-H comparison over the full admissible competitor class; the antipodal-lemma off-diagonal bound (reusable).

**Tier:** T7-SCOPE_{C_full} ENACTED +

**COMFORTABLE-UPGRADED 2026-06-10** (v1.2 ACCEPTED AS CANONICAL; v1.1 thin-O superseded). The coherence circle-packing lemma (R-032) upgraded the off-diagonal margin from thin x1.026 to COMFORTABLE x1.96 (T'<=floor(2pi/theta_min)=10 => R_lead<=0.510<1); selection re-binds (I_off^coh=3.92e-3>I_c^sel) so the region is the FULL Step-1 region R (20% headroom), identical robustness to lattice. EXT no longer needed for comfort. G1+G3 CLOSED; G2 external referee = validation gate (standing). EXT T2 optional. Scope-qualified: thin off-diagonal margin, cap 2.053e-3, given A1; NOT unrestricted/global T7.

**Publication target:** Reading-H C_full closure / vacuum-selection paper

<a id="r-030"></a>
### R-030 — Reading-H comparison theorem T7-closed (H-LAYER discharged) within the lattice domain

**Statement (one line):** F[Q]-F[G_*]>0 for all Q in C_phys\{G_*}: the isotropic Gaussian-Hartree layer G_* is the STRICT comparison infimum over the lattice Reading-H competitor class (real antipodal crystallographic, #Q<=n_pack, angle>=theta_min) at the operating endpoint I=2e-3, mu^2 in [x0.5,x2]. H-LAYER is DISCHARGED as a hypothesis. Assembled from (D) diagonal isotropy strict minimum (T-016) + (O) off-diagonal R_lead<1 class-wide (T-018/020) + the off-shell domination theorem rho_off<=R_lead*r_R/(r_R+c delta^2)<R_lead<1 (T-026, converts the off-shell operator decision to a theorem) + (S) selection floor + SC-SCOPE third-cumulant joint>1 (T-017/021/027). The three T7 blockers A (off-shell admissibility) / B (thin grades R_max/sunset/anchoring, hardened theorem-grade) / C (adversarial margin) all closed. Sole remaining named input A1-KERNEL-CONV (T5, kernel-convention definition). Verified res5_029 5/5 (61/61 chain asserts, 17/17 constants, worst dev/tol 0.49); non-circular rho_off^ext=R_lead(20)*r_R/(r_R+c delta^2)=0.572<1; margins off-diagonal 0.350, selection 0.097>0.

**Proven in:** B1-RH-ENUM/B2-PROPA-HLAYER / t7-enactment-record-260610 v1.0 (+ t7-proposition-assembly v1.1, t7-route-internal-audit v1.0/res5_029)

**Reuse scope:** TECT vacuum-selection layer; the Reading-H/H-LAYER/Proposition-A comparison theorem; the off-shell domination corollary (reusable).

**Tier:** T7

**ENACTED 2026-06-10** (operator sign-off APPROVED + ACCEPTED AS CANONICAL ENACTMENT RECORD). Scope-qualified DISCHARGED-THEOREM (lattice Reading-H, operating endpoint, [x0.5,x2]); H-LAYER discharged; sole named input A1-KERNEL-CONV (T5). NOT full TECT, NOT the TOE; arbitrary-Q (non-lattice) OPEN (legacy fallback). Dual-audit = internal 5-axis route audit + operator adversarial-review chain; fully-external referee pass = standing publication item.

**Publication target:** Reading-H / vacuum-selection comparison-theorem paper

<a id="r-029"></a>
### R-029 — SC-SCOPE endpoint floor sharpening (candidate lift)

**Statement (one line):** The SC-SCOPE all-orders endpoint (I=2e-3) floor rho=2.58 used the kappa-balanced bound K(n_pack)=8+4sqrt(14)sqrt(n_pack)=103.5, which OVERSHOOTS the Lemma-A additive-energy bound 1+T'<=1+n_pack=41.7 at the small endpoint n_pack=40.7 (prefactor c_R~15). Substituting the tighter constant: rho_lat=K_budget/(1+T')>=6.4 (separated T'<=n_pack), paired=rho_lat/2.872>=2.23>1 -- the endpoint CLOSES, completing the 'sharper floor rho>~3.9' route scscope-joint-pairing named. Break-even T'<=92 (paired>=1), T'<=67 (rho>=3.9); lattice T'~tens (R-026) closes. Verified scscope_floor_sharpening.py 5/5. RESIDUAL: exact constant map kappa-balanced K(n) <-> Lemma-A 1+T' (-4I^2/averaging; both bound the lambda'-free (<F^4>-4I^2)/I^2).

**Proven in:** B5 / scscope-floor-sharpening v1.6

**Reuse scope:** SC-SCOPE all-orders endpoint; bears on B1.

**Tier:** PARTIAL ADVANCE;

**LIFT RETRACTED 2026-06-08** (self-caught). The reconciliation K_floor<=T'(M) is PROVED (scscope_constant_map.py 3/3) and the floor is sharpened (rho 2.58->6.55), but the LIFT used the local paired=rho/2.872 formula; the correct additive bookkeeping (sunset saturates) gives only x0.945-1.026 (marginal, threshold rho>=9.85 not 3.9; scscope_joint_correction.py 5/5). SC-SCOPE RESTORED to B1 {H-LAYER}->{H-LAYER,SC-SCOPE}, T6 unchanged. AUDIT-2026-06-08-scscope-lift-overclaim.

**STRONG EVIDENCE 2026-06-08** (scscope_quartic_realized.py 4/4): the REALIZED quartic R_max~0.385 (direct, vs the loose Young estimate 1.019) is < the 0.634 closure threshold -- strong evidence the endpoint closes -- but the absolute Ghat4 factor-2/(2pi)^3 convention is load-bearing (survives +50%, not x2), so NOT certified, NO lift.

**CONVENTION PINNED 2026-06-09** (scscope-quartic-normalisation-certificate v1.0, scscope_quartic_certificate.py 5/5): the Parseval identity (J*J)(0)=(2pi^2)^-1 int q^2 J^2 holds to ratio 1.0000 -- the convolution is standard-normalised, the factor-2 caveat RESOLVED. So R_max=0.385<0.634 is CERTIFIED, and the conservative additive joint = x1.040 (rho=6.55) .. x1.082 (rho=12.6) > 1: the SC-SCOPE all-orders endpoint CLOSES (THIN). NO lift enacted -- presented for operator re-examination.

**OPERATOR DECISION 2026-06-09**: HOLD -> on re-examination LIFTED@THIN-CERTIFIED (operator-authorised; scscope_endpoint_sweep.py 4/4): the thinness is STRUCTURAL (joint sunset-saturates x1.13; sign-stable across I (critical I~2.5e-3 beyond the endpoint) and mu^2 [x0.5,x2] worst x1.034), a near-critical selection boundary. SC-SCOPE LIFTED: B1 {H-LAYER,SC-SCOPE}->{H-LAYER}, tier UNCHANGED T6.

**Publication target:** Reading-H all-orders closure

<a id="r-028"></a>
### R-028 — H-ADM-COH discharge decision (lattice class) -- the finite margin

**Statement (one line):** For Q a subset of a crystallographic momentum shell, G1'''-AE (`sum_t |w_t|^2 <= (1+T'(Q)) I^2`, R-027) holds with the FINITE margin `K_adm = 1+T'(Q) <= K_allowed(n) = 8 + 4 sqrt(14) sqrt(n)` -- verified dr2_hadmcoh_margin.py 3/3 (margin 10.6x-15.8x, GROWING in n since T'~R^0.18 << sqrt(n); worst sub-pattern ratio 0.307). This replaces the subpolynomial-K acceptance JUDGMENT with a numerical inequality (operator point 3). Since H-ADM-COH only secured G1'''-AE by angular separation, it is a DISCHARGE-CANDIDATE: {H-LAYER,H-ADM-COH,SC-SCOPE} -> {H-LAYER,SC-SCOPE} is the proposed B1 reduction for the lattice class.

**Proven in:** B5 / dr2-hadmcoh-discharge-decision v1.2

**Reuse scope:** B1-RH-ENUM hypothesis set; STEP-5B G1'''-AE; physical crystallographic competitor class.

**Tier:** ENACTED 2026-06-08 (operator ACCEPTED): H-ADM-COH DISCHARGED@lattice; B1 active hypotheses {H-LAYER,H-ADM-COH,SC-SCOPE} -> {H-LAYER,SC-SCOPE}, B1 tier UNCHANGED T6

**Publication target:** Reading-H closure / B1 hypothesis reduction

<a id="r-027"></a>
### R-027 — DR-2 -> STEP-5B G1'''-AE integration (amplitude bridge)

**Statement (one line):** WEIGHTED Lemma A: for finite Q in S^2 and any amplitudes c, `sum_t w_t^2 <= (1+T'(Q))||c||_2^4` (w_t=sum_{a+b=t} c_a c_b; Cauchy-Schwarz over the r(t) terms + the t=0 antipodal split w_0^2<=||c||_2^4). With R-026 (lattice T'<<_eps R^eps): for any subset Q of a crystallographic momentum shell and any amplitudes, `sum_t w_t^2 <= (1+C_eps R^eps)||c||_2^4` -- the STEP-5B G1'''-AE bound (the weighted sphere additive energy) with SUBPOLYNOMIAL K~R^eps, with NO angular separation (H-ADM-COH). The chi(P) extraction obstruction is BYPASSED (additive energy bounded directly via Lemma A). Verified dr2_weighted_energy.py 3/3 (worst ratio 0.277 over uniform/gaussian/peaked/signed amplitudes; K=1+T'~R^0.126 subpolynomial).

**Proven in:** B5 / dr2-step5b-integration v1.1

**Reuse scope:** STEP-5B G1'''-AE corner; the physical (lattice) competitor class.

**Tier:** T7 (weighted Lemma A + integration bound). H-ADM-COH discharge NOT enacted -- operator decision (residuals: subpolynomial-K, modeling, corner)

**Publication target:** Reading-H closure / STEP-5B

<a id="r-026"></a>
### R-026 — DR-2 for the lattice class -- UNCONDITIONAL (decoupling-free, Route A)

**Statement (one line):** For `Q = Lambda cap {|x|^2=R}` (a fixed lattice; Z^3/BCC/FCC), `E_+(Q) <= (1 + 6 max_{m!=0} d(4R-|m|^2)) N^2 <= (1+C_eps R^eps)N^2` by Lemma A (R-025) and [DIV-CIRC]. [DIV-CIRC] is now PROVED (v1.1): the substitution `y=2x-m` (sum-circle centre m/2) sends `Z^3 cap C_m` injectively into `{y in Lambda_m : |y|^2=4R-|m|^2}`, a HOMOGENEOUS rank-2 representation count `<= 6 d(4R-|m|^2)` (Dirichlet class-number formula: single class <= sum over classes = w*sum chi(d) <= 6d, UNIFORM in m) `<<_eps R^eps` (divisor bound). For Gauss-typical shells `R~N^2`, `E_+ <=_eps N^{2+eps}` -- DR-2, NO decoupling. Verified EXACTLY: dr2_divcirc_proof.py 4/4 (substitution exact, `T' <= r_Q(R') <= 6d(R')`, `T'/6d<=0.25`); dr2_lattice_divisor.py 5/5 (`T'/N` 0.107->0.024, log-log slope 0.177, `E_+/N^2<=5.3`; Z^3=FCC).

**Proven in:** B5 / dr2-lattice-divisor-closure v1.2

**Reuse scope:** TECT DR-2 carrier (BCC/FCC momentum-shell lattice points); additive-energy DR-2.

**Tier:** T7 (PROVED UNCONDITIONAL modulo textbook number theory: class-number formula + d(n)<<n^eps; operator pre-authorised). Arbitrary-Q DR-2 unchanged OPEN

**Publication target:** `S^2` additive-energy paper / STEP-5B

<a id="r-025"></a>
### R-025 — Sum-level-circle additive-energy bound (unconditional)

**Statement (one line):** For finite `Q in S^2` (N=|Q|), `E_+(Q) <= (1+T'(Q))N^2`, where `T'(Q)` = max occupancy of a PROPER (m!=0) sum-level circle `C_m = S^2 cap {x.m=|m|^2/2}` -- both summands of `a+b=m` lie on `C_m`, and the degenerate m=0 antipodal term is split off (`r(0)^2<=N^2`). UNCONDITIONAL, decoupling-free, conjecture-free. Cor 1: `T'=O(1) => E_+=O(N^2)` -- elementary DR-2 for random/great-circle (T'=2, no decoupling). Cor 2: `T'<=_eps N^eps => DR-2`. Self-tested (dr2_circle_richness.py 5/5: the lemma assert IS the proof check; great-circle tight at 3N^2 = N^2 antipodal + 2N^2 proper). SUFFICIENT-not-tight: the rich latitude circle has T'=N yet E_+~3N^2.

**Proven in:** B5 / dr2-circle-richness-reduction v1.0

**Reuse scope:** The DR2-SHARE carrier-richness obstruction, made exact; any sphere additive-energy bound.

**Tier:** T7 (Lemma A + Cor 1 unconditional; general DR-2 unchanged OPEN)

**Publication target:** `S^2` additive-energy paper / STEP-5B

<a id="r-024"></a>
### R-024 — Decoupling-iteration energy inequality

**Statement (one line):** Conditional on l2-decoupling at p=4, `E_+(Q) <=_eps delta^{-eps} (sum_theta sqrt(E_+(Q_theta)))^2` over delta^{1/2}-caps. The additive energy is the BESICOVITCH MEAN `M(|f_Q|^4)=E_+(Q)` (exact for non-integer `q in S^2`); the iteration follows by applying ball-decoupling on `B_R` and translate-averaging to the mean. (v1.0 used the FALSE identity `||f_theta||_4^4=E_+(Q_theta)` and is WITHDRAWN.) With the R-023 affine rescaling -- caps are uniformly-curved C^2 graph patches handled by decoupling STABILITY, not the literal paraboloid -- it recurses arbitrary finite `Q in S^2` to the separated base case (`-> N^{2+eps}`). Numerics ILLUSTRATIVE only (proxy square-bin partition, not geodesic caps): `K<=1.94`, scale-stable; an exact-E_+ code-audit gate (random `=2N^2-N`) certifies the estimator. TWO cited-not-reproduced ingredients remain: R1 local-to-global translate-averaging, R2 multi-scale eps-bookkeeping over O(log N) levels (Bourgain-Demeter).

**Proven in:** B5 / dr2-cross-scale-induction v1.1

**Reuse scope:** The cross-scale step of any decoupling-based additive-energy bound on a curved surface.

**Tier:** T4+ STRONG EVIDENCE (Besicovitch bridge correct; conditional on decoupling + R1 + R2; T5-candidate pending operator acceptance; v1.0's T5 WITHDRAWN)

**Publication target:** `S^2` additive-energy paper

<a id="r-023"></a>
### R-023 — Affine-invariance of additive energy

**Statement (one line):** Additive energy `E_+(Q)=#{q_i+q_j=q_k+q_l}` is EXACTLY invariant under any affine bijection `T(q)=Aq+b` (since `q_i+q_j-q_k-q_l=0 <=> A(.)=0`); on the paraboloid the parabolic rescaling `(xi,t)->(xi/lam,t/lam^2)` is such a map sending a `lam`-cap to a unit patch, so a cap-cluster UNFOLDS to a unit-scale configuration of IDENTICAL energy -- clustering gives no additive-energy advantage and the worst case is the separated one. Verified exactly (E_+(T(Q))=E_+(Q) for random affine T; rescaling preserves paraboloid+energy; extreme-clustering exponent ~2 down to 0.05-rad caps).

**Proven in:** B5 / dr2-decoupling-closure v1.1

**Reuse scope:** Reducing additive-energy bounds on self-similar/curved surfaces from arbitrary to separated point sets; the key structural step of the DR-2 multi-scale reduction.

**Tier:** T7

**Publication target:** `S^2` additive-energy paper

<a id="r-022"></a>
### R-022 — DR-2 via l2-decoupling

**Statement (one line):** For DELTA-SEPARATED `Q in S^2` the bound `E_+(Q) <=_eps N^{2+eps}` follows from Bourgain-Demeter l2-decoupling for the sphere in R^3 at the critical exponent `p=4` (additive energy = L^4 norm), plus a standard multi-scale reduction (arbitrary sets) and the R-008 dyadic lift (weighted); the curvature mechanism (height-quadratic => sum-of-squares conservation => rectangle rigidity, R-007) sharpens the unconditional `N^{5/2}` to `N^{2+eps}`. Numerically confirmed: exponent ~2 on the sphere (great-circle/cap-grid/random 2.03/1.95/2.01) vs ~3 for the SAME grid kept flat (2.98).

**Proven in:** B5 / dr2-decoupling-closure v1.1

**Reuse scope:** Any additive-energy / discrete-restriction bound for points on a curved surface; closes DR-2 / DR2-SHARE conditional on decoupling.

**Tier:** T4 (SEPARATED case T6 PROVED CONDITIONAL on decoupling; UNRESTRICTED case T4+ STRONG EVIDENCE / T5-candidate. The cross-scale induction is WRITTEN with a CORRECT bridge (dr2-cross-scale-induction v1.1): the additive energy is the BESICOVITCH MEAN M(|f_Q|^4)=E_+(Q), exact for non-integer q; v1.0's ||f_theta||_4^4=E_+ identity was FALSE and is WITHDRAWN with v1.0's T5. Two cited ingredients remain: R1 local-to-global translate-averaging, R2 multi-scale eps-bookkeeping. K<=1.94 numerics ILLUSTRATIVE (proxy partition). Operator authorises any T5/T6 flip)

**Publication target:** `S^2` additive-energy paper / STEP-5B unrestricted closure

<a id="r-021"></a>
### R-021 — Sphere-circle cross-energy bound (corrected)

**Statement (one line):** For finite `A,B` on circles of `S^2`, the off-diagonal additive energy `E_off(A,B) <= 2 min(|A|^2-|A|, |B|^2-|B|)` and the full `E_+(A,B) <= 3|A||B|`, via `r_P(w) <= 2` for `w != 0` (a circle and its translate meet in <= 2 points); holds for parallel AND non-parallel circles. CORRECTS an external `E_+ <= 2|A||B|` that mis-applies `r<=2` to the `w=0` diagonal (witness: `A=B`=16 great-circle points has `E_+=720 > 512`; corrected `E_off=464 <= 480`).

**Proven in:** B5 / dr2-pencil-rigidity-reduction v1.0

**Reuse scope:** Cross additive energy between any two circle-supported sphere sets; the cross-term input to the DR-2 cluster-decomposition reduction.

**Tier:** T7

**Publication target:** DR-2 / `S^2` additive-energy paper

<a id="r-020"></a>
### R-020 — Physical secondary-shell ratio lies in the no-condensate-certified region

**Statement (one line):** For a multi-shell variational selection, the physical secondary-shell response (the amplitude the secondary shell takes when driven by the primary, A2*=argmin over the secondary amplitude + trial mass) is extracted from the exact engine and shown to lie INTERIOR to a region already certified condensate-free -- reducing a `does-the-physical-ratio-condense?' cross-check to a containment check against a whole-domain no-condensate bound; here the {200} response is on the sextic-driven negative branch, suppressed (|rho|<=0.57), with dF_anchored>0 along the trajectory.

**Proven in:** B1 / g3pb3-ratio-closure v1.0

**Reuse scope:** Any multi-shell selection where a whole-domain no-condensate bound exists and a specific physical operating-ratio must be cross-checked.

**Tier:** T4

**Publication target:** methods note (physical-ratio containment cross-check)

<a id="r-019"></a>
### R-019 — Controlled-error continuum no-condensate for an enumerated variational selection

**Statement (one line):** An estimator-grade variational selection `dF>0` is upgraded to a CONTROLLED-ERROR, node-free (continuum) no-condensate statement across all numerical quadrature knobs AND for a multi-shell ensemble's EXACT (off-diagonal-inclusive) free energy, by combining (a) grid-independent curvature certification at two quadrature resolutions, (b) a curvature-chord interval lower bound `dF >= min(v_i,v_{i+1}) - (1/8) M_i delta^2`, and (c) a near-reference PD Hessian covering the thin region where the off-diagonal correction is O(amplitude^4); the exact engine is reused by neuter-import of a frozen legacy script.

**Proven in:** B1 / estimator-upgrade-closure-consolidation v1.0 (+ 4 cited notes)

**Reuse scope:** Any amplitude-even variational selection needing a knob-complete, node-free no-condensate certificate at controlled-error grade.

**Tier:** T4

**Publication target:** methods note (controlled-error continuum no-condensate; gate closed at strong-evidence)

<a id="r-018"></a>
### R-018 — Exact-Wick off-diagonal correction is O(A^4) and amplitude-aligned

**Statement (one line):** The off-diagonal (exact-vs-diagonal) bracket of a dressed-Bloch-Hessian free energy is O(amplitude^4) near the reference (so it never shifts the (0,0) Hessian, which stays equal to the diagonal one) and peaks at LARGE amplitude where the diagonal value is also large -- hence a diagonal no-condensate with margin is not overturned by the bracket; established by REUSING a frozen exact slogdet engine via programmatic neuter-import (truncate before the module-level scan + repoint imports), validated against the engine's own recorded outputs to 5e-8.

**Proven in:** B1 / twoshell-anchored-bracket v1.0

**Reuse scope:** Any diagonal-vs-exact (Hartree-vs-full) correction question where the exact engine exists only as a legacy script; any (0,0)-Hessian argument needing the off-diagonal order.

**Tier:** T4

**Publication target:** methods note (engine-reuse-by-neuter-import + O(A^4) bracket)

<a id="r-017"></a>
### R-017 — Operating-point-faithful multi-shell no-condensate via a validated diagonal evaluator

**Statement (one line):** A multi-shell variational GLOBAL no-condensate is re-established at the CORRECT operating point using a diagonal-continuum evaluator validated against a frozen exact-engine artefact (band-limited moments exact + recorded `anchored - bracket` anchors to 1e-7), with an M-minimised 2D curvature-chord continuum lower bound; the method also exposes that a kernel-offset penalty `C q0^4 > 0` does NOT order DRESSED curvatures (mode-count + loop dressing dominate, so the higher-kernel {200} shell is the SOFTER direction, kappa_{200}=3.86 < kappa_{110}=5.16).

**Proven in:** B1 / twoshell-continuum-bound v1.0

**Reuse scope:** Any multi-shell variational selection whose heavy exact engine exists only at a legacy operating point; any (0,0)-Hessian ordering argument from kernel offsets.

**Tier:** T4

**Publication target:** methods note (operating-point discipline + diagonal-evaluator validation)

<a id="r-016"></a>
### R-016 — Multi-knob controlled-error + continuum no-condensate + orthogonal-shell Hessian

**Statement (one line):** A variational selection's controlled-error grade is extended across ALL loop-integral quadrature knobs (the dressing-variance `M` grid AND the log-difference `dI` grid envelopes are both << the curvature), the grid no-condensate scan is upgraded to a node-free CONTINUUM lower bound via the curvature-chord inequality `dF(A) >= min(v_i,v_{i+1}) - (1/8) M_i delta^2` (value and dip both O(delta^2) near A=0, value coefficient 1/2 > dip coefficient 1/8), and a multi-shell condensate's (0,0) Hessian is certified positive-definite by shell-orthogonality diagonalisation (cross-term = 0; soft eigenvalue = the soft single-shell curvature; stiffer shells add a positive kernel penalty).

**Proven in:** B1 / estimator-upgrade-knobs v1.0

**Reuse scope:** Any amplitude-even variational selection needing knob-complete controlled error + a node-free no-condensate guarantee; any multi-shell order-parameter (0,0) Hessian.

**Tier:** T4

**Publication target:** methods note (with R-015)

<a id="r-001"></a>
### R-001 — P²-representation theorem

**Statement (one line):** The matched second-cumulant off-diagonal transfer operator is `W = λ′(P²−2I·Id)`, `P=Σ A_u S_u` self-adjoint ⇒ `D+W = D₀+λ′P² ≥ D₀ > 0` unconditionally; n-free, pattern-free spectral floor `−2λ′I/r̂`.

**Proven in:** B5 / beyond-layer-gershgorin-reduction v1.7–v1.8

**Reuse scope:** Any matched-cumulant fluctuation operator with a real scalar order parameter; replaces Gershgorin row bounds by an exact structural floor.

**Tier:** T7 (within scope)

**Publication target:** methods note: structural positivity of dressed Bloch Hessians

<a id="r-002"></a>
### R-002 — Universal single-circle theorem

**Statement (one line):** For sphere-circle-supported trig sums, `Σ_{t≠0} w_t² ≤ 14 λ′² I_c²` for ANY amplitudes/n/height; constant 14 sharp (rings attain `14−18/n`).

**Proven in:** B5 / v1.8 + ring proposition

**Reuse scope:** Additive energy of measures on a circle; sharp L⁴ on one curve.

**Tier:** T7

**Publication target:** harmonic-analysis short paper

<a id="r-003"></a>
### R-003 — Antipodal-carrier partition

**Statement (one line):** Every ordered pair `(u,v)`, `u+v≠0`, is an antipodal pair of exactly one sphere-circle (carrier `(u+v)/2`); ordered pairs partition by carriers, `Σ w² = λ′² Σ_C Ψ_C²`.

**Proven in:** B5 / v1.9

**Reuse scope:** Exact additive-energy decomposition of sphere point sets.

**Tier:** T7

**Publication target:** same as R-002/R-006

<a id="r-004"></a>
### R-004 — ν* = μ_C identity

**Statement (one line):** The shifted-shell translate-overlap parameter equals the max number of pattern points on a single sphere-circle.

**Proven in:** B5 / v1.9

**Reuse scope:** Couples transversality (additive) to incidence (geometric) — one parameter, two routes.

**Tier:** T7

**Publication target:** same paper as R-003

<a id="r-005"></a>
### R-005 — Coherence indistinguishability lemma

**Statement (one line):** Sub-resolution restructuring of a variational competitor shifts the free energy by `≤ c_ind I²` (`c_ind=30.1`; exact fiber combinatorics 6/9/(12−6/n) I²) — the admissible class modulo sub-resolution is energy-faithful.

**Proven in:** B5 / coherence-indistinguishability-lemma v1.0

**Reuse scope:** Justifies admissibility quotients in any variational selection with a coherence scale.

**Tier:** T4

**Publication target:** methods note on admissibility classes

<a id="r-006"></a>
### R-006 — Stereographic incidence transfer

**Statement (one line):** Stereographic projection maps sphere-circles to plane circles preserving incidences, so planar point-circle incidence bounds (Aronov–Sharir) apply to sphere additive energy; gives `Σ p_C² = O(N^{20/9} polylog)`.

**Proven in:** B5 / rectangle-constant-closure v1.1 (exponent repaired)

**Reuse scope:** Any discrete sphere L⁴ / additive-energy problem.

**Tier:** T4 (provisional constant)

**Publication target:** harmonic-analysis paper (with R-002/3/4)

<a id="r-007"></a>
### R-007 — Rectangle reformulation + triple count

**Statement (one line):** Off-diagonal carrier energy = weighted count of rectangles inscribed in sphere-circles; three points determine ≤1 circle ⇒ `Σ k_C³ = O(n³)` ⇒ `R = O(n^{5/2})` unconditional.

**Proven in:** B5 / v2.0

**Reuse scope:** Discrete sphere L⁴ extremal combinatorics.

**Tier:** T6

**Publication target:** same paper

<a id="r-008"></a>
### R-008 — Amplitude-dyadic lift

**Statement (one line):** An unconditional-amplitude `Σ w² ≤ C λ′² I² √n log^{3/2}(2n)` bound via dyadic amplitude classes + per-class interpolation + bilinear additive-energy Cauchy–Schwarz + Minkowski.

**Proven in:** B5 / rectangle-constant-closure v1.2; dyadic-lift-log-sharpening

**Reuse scope:** Removing balance hypotheses in additive-energy bounds.

**Tier:** T3

**Publication target:** methods note

<a id="r-011"></a>
### R-011 — Sign-decomposition for slaved-variance uniqueness

**Statement (one line):** For a free energy with $F'(m)=\tfrac12 M'(m)g(m)$ and slaved variance $M(m)$ strictly decreasing, global uniqueness of the minimiser reduces to closed-form sign lemmas on $g$ plus a single anchor inequality, replacing any numerical curve-shape certification.

**Proven in:** B2 / ha0-removal-pathway v2.0

**Reuse scope:** Any Hartree/slaved-variance variational gap equation where a curve-shape uniqueness is wanted without quadrature dependence.

**Tier:** T4

**Publication target:** methods note

<a id="r-010"></a>
### R-010 — Common-mode dressing cancellation

**Statement (one line):** At fixed total intensity the diagonal Hartree dressing is pattern-independent, so the variational free-energy difference `F[P]−F[R_H]` is invariant under the dressing-convention choice; the convention remainder cancels and the structural floor (R-001) protects the selection unconditionally, including the near-gap small-amplitude limit.

**Proven in:** B1 / neargap-common-mode-resolution v1.0

**Reuse scope:** Any Hartree-dressed variational selection where the reference and competitor share total intensity.

**Tier:** T4

**Publication target:** methods note (with R-001)

<a id="r-009"></a>
### R-009 — Coherence-resolution admissibility

**Statement (one line):** The dressed propagator's correlation length `ξ = 2q₀√(C/r̂)` sets an angular resolution `θ_min = 1/(q₀ξ)` and hence a finite admissible mode count `n_adm ~ 4π/θ_min²`; sub-resolution mass reclassifies to the sea sector.

**Proven in:** B5 / coherence-admissibility-cutoff v1.0

**Reuse scope:** Defining variational competitor classes from a physical coherence scale.

**Tier:** T3

**Publication target:** physics methods note

<a id="r-012"></a>
### R-012 — Closed-form Prop-A layer-margin recomputation

**Statement (one line):** The Prop-A band layer margin is closed-form `MARGIN(mu^2)=P_B(M_+(mu^2))-DIP_BAND(mu^2)`; recomputing every mu^2-dependent input over a neighbourhood, with a derivative-sign minimum certificate and a branch-invariance check, certifies parameter-robustness exactly and replaces any frozen-anchor bound.

**Proven in:** B1 / robustness-mu2-margin-recompute v1.1

**Reuse scope:** Any band-floor variational margin whose parameter-robustness must be certified without re-running the full closure.

**Tier:** T5 (within [x0.5,x2]-2nd-cumulant scope)

**Publication target:** methods note

<a id="r-013"></a>
### R-013 — Direct dressing-variance endpoint evaluation

**Statement (one line):** The convexity-honest endpoint coupling `M(r_hat(I))` is evaluated directly by quadrature (two independent quadratures agree ~1%, analytic tail bound), bypassing a factor-2-prone linear-response slope; decides whether a frozen-coupling marginal failure is a real obstruction or a coupling artefact.

**Proven in:** B5 / scscope-mendpoint-evaluation v1.1

**Reuse scope:** Any dressed-coupling endpoint bound where a linearised slope is unreliable.

**Tier:** T4

**Publication target:** methods note

<a id="r-015"></a>
### R-015 — Curvature-certified controlled-error selection margin

**Statement (one line):** A variational selection 'dF>0 for all competitor amplitudes A' is upgraded from estimator-grade to controlled-error by certifying the grid-INDEPENDENT curvature kappa = dF''(0) > 0 (strict minimum) plus a no-deeper-minimum scan, each at two quadrature resolutions (envelope « kappa); the high-res pipeline reuses the production dF via a one-line M-evaluator monkeypatch (no formula re-transcription).

**Proven in:** B1 / estimator-upgrade-enumerated v1.0

**Reuse scope:** Any amplitude-even variational free-energy selection where a naive min-over-A>0 margin is grid-dependent.

**Tier:** T4

**Publication target:** methods note

<a id="r-014"></a>
### R-014 — Convention-free per-transfer form-factor reduction

**Statement (one line):** A sup-kernel budget ratio of the form `max_t Ghat_k(t) * max_t 1/J(t)` is replaced by the realized `max_t [Ghat_k(t)/J(t)]` via the convention-free shape factor `Phi(t)=[Ghat_k(t)/Ghat_k(0)][J(0)/J(t)]` (all measure/normalisation prefactors cancel); the incompatible max-pairing is quantified by `max Phi / (J(0)/J(2q0))`.

**Proven in:** B5 / scscope-endpoint-joint-assessment v1.0

**Reuse scope:** Any per-transfer kernel bound where the absolute normalisation is convention-sensitive but the shape is what matters.

**Tier:** T4

**Publication target:** methods note (with a paired honest-negative: individually-positive channels can jointly fail an additive budget)


## Notes on status

- Tiers above are the results' tiers WITHIN the matched second-cumulant B5
  scope (R-001 etc. are T7 there); a standalone publication would restate
  hypotheses for the general setting and re-derive constants. Publication
  targets are editorial intentions, not commitments.
- R-006's exponent route is provisional (constant unpinned); R-002/3/4/7 are
  the strongest standalone candidates (sharp constants, self-contained).
- This ledger does not duplicate the claim ledger (`CLAIMS.md`): a row here is
  a *reusable artefact extracted from* a claim, pointing back to its proof.
