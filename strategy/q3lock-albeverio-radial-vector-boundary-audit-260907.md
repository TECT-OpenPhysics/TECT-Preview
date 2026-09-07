# Q3LOCK radial-vector theorem boundary audit

Date: 2026-09-07. Exploration: EXP-001619. Task: T-054.
Status: T0, claim_bearing=false, bounded literature comparison only.
This note does not change the theorem tier, add a proof premise, or authorize
PDF generation. The paper remains INTERNAL_REVIEW_ONLY and PDF DEFERRED.

## Primary source and exact scope

The comparison source is S. Albeverio, Y. Kozitsky, Y. Kondratiev and
M. R\"ockner, *Phase transitions and quantum effects in anharmonic crystals*,
arXiv:1204.6279v1, https://arxiv.org/pdf/1204.6279. The relevant source
locations are:

* the vector model and its scalar product interaction, equations (2)--(9),
  PDF pages 4--5;
* the three potential classes, equations (13)--(16), PDF pages 5--6;
* the definition of the static correlation and order parameter, equations
  (64)--(66), PDF pages 13--14;
* the infrared comparison and Griffiths implication, Theorem 2 and equations
  (71)--(75), PDF pages 15--16;
* the arbitrary-component radial quartic phase theorem, equations (76)--(82)
  and Theorem 3, PDF pages 16--17.

This is a primary author source used as a comparison record. It is not added
to the EXP-000780 -> EXP-000781 -> EXP-000782 proof authority chain.

## Hypothesis-level comparison

| Source statement | Requirement in the source | Q3LOCK comparison | Disposition |
|---|---|---|---|
| Model (2)--(9) | A finite-component displacement vector with ferromagnetic scalar-product spatial interaction and a one-site potential | Q3LOCK has \(\nu=8\), the same type of spatial dot-product coupling, and a fixed-lattice finite range | Satisfied structurally |
| Potential class (13) | For arbitrary \(\nu\), \(V(q)=-\alpha\lvert q\rvert^2+b\lvert q\rvert^4\), hence full \(O(\nu)\) invariance | The Q3 onsite polynomial is quartic but non-radial: equal-norm internal vectors can have different energies | Failed for direct import |
| Theorem 2 | \(O(\nu)\)-symmetric potential and the scalar order parameter obtained by selecting one component of the field | Q3 has only the cube-graph symmetry and uses a collective diagonal direction; the source's rotational reduction is unavailable | Does not apply directly |
| Theorem 3 | \(d\ge3\), nearest-neighbor \(J>0\), radial quartic (13), condition (78), and \(\beta>\beta_*\); conclusion includes \(|\operatorname{ex}(\mathcal G)|>1\) | The dimension and spatial sign match, but radiality and the source-specific lower bound (80)--(81) are not established for Q3 | Does not apply directly |
| Source comparison mechanism | Local bound \(D^L_{xx}\ge\beta\nu\vartheta_*f(\beta/(4m\vartheta_*))\) from the radial collective Hessian, followed by the infrared subtraction | Q3LOCK must supply its own collective Hessian/Falk--Bruch estimate with the Q3 polynomial and then verify the separate loop/DLR passage | Residual model-specific proof |
| Scalar asymmetric class (16) | \(\nu=1\), asymmetric scalar potential with a superquadratic lower bound | Q3 is eight-component and parity-even, not a scalar asymmetric model | Does not apply |

The source therefore confirms a close vector comparator, but it does not
cover an arbitrary non-radial \(\nu\)-component quartic potential. The phrase
“\(\nu\) arbitrary” in Theorem 3 modifies the radial family (13); it does
not remove the \(O(\nu)\) hypothesis.

## What can and cannot be imported

The source's finite-volume Duhamel notation, infrared subtraction strategy,
and the radial threshold shape are standard comparison material. They do not
certify the Q3LOCK claim. In particular:

1. The source's \(\vartheta_*\) is a parameter of the radial potential and
   cannot be replaced by Q3LOCK's \(A_0\), \(I_3\), or \(\lambda\) without a
   separately proved inequality.
2. The source's \(J\) is the spatial interaction intensity. It is not the
   internal Q3 locking coefficient \(\lambda\).
3. The source's phase theorem uses its own order-parameter and Gibbs-state
   framework. It does not supply the typed collective-source tangent, the
   continuous-loop FKG passage, or the parity-intertwined zero-source DLR pair
   required here.
4. The source's radial symmetry cannot be recovered by merely projecting the
   Q3 model onto the diagonal direction: the transverse coordinates and the
   non-bilinear internal edge terms remain in the Hamiltonian.

The current manuscript's proposed contribution is consequently narrower than
“a phase theorem for vector quantum crystals”: it is the conditional Q3-specific
collective lower bound and its composition with the loop/DLR construction.
Whether that composition is publication-level novelty remains for a specialist
to decide.

## Adversarial checks and disposition

* **Arbitrary-component trap:** treating arbitrary \(\nu\) as arbitrary
  potential is rejected; the source explicitly restricts the arbitrary-
  \(\nu\) phase theorem to (13). UPHELD as a firewall.
* **Parameter-identification trap:** identifying \(\lambda\) with the source
  \(J\) or \(\vartheta_*\) is rejected; they enter different terms. UPHELD.
* **Symmetry-reduction trap:** replacing the Q3 polynomial by its radial
  envelope would change the model and cannot be used as a theorem premise.
  UPHELD.
* **Priority trap:** this boundary audit is not an exhaustive search and does
  not establish novelty or priority. UPHELD.

Disposition: **DOES-NOT-APPLY directly; RETAIN AS THE CLOSEST RADIAL-VECTOR
COMPARATOR.** The external literature review and signed specialist opinion
remain open. No manuscript theorem, claim tier, or PDF status is changed.
