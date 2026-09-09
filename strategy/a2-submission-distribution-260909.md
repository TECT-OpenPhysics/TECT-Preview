# A2/R-157/R-158 fixed-checkpoint distribution

Date: 9 September 2026. Scope: document transport and internal verification.
No new mathematical result, tier, source-owner decision or actual submission.

## Decision and source boundary

The operator requested an A2/R-157/R-158 package analogous to the Q3LOCK
submission-preparation distribution, without requiring prior external review.
An existing isolated paper checkpoint already contained v0.1.42 and two
completed transport archives. Reuse that fixed checkpoint rather than
overwrite a different lane or independently redraft the same paper.

The source is commit `903426f3229ff1a5bda3dbe961d37bc13c0a5dd0`.
The small original archive has SHA-256
`4ab649efdcae847fa3023bdaab4ae8066bb6022597ec399bba6b30a0fc297141`;
the full source archive has SHA-256
`f7a4e7c672a0a2a849c6b26cbe921a332c76ba181adeffda386acb273709e501`.
These are provenance inputs, not newly derived mathematical constants.
The original source branch remains clean. No source branch is merged here;
historical exploration IDs inside its supplements belong to that pinned
snapshot and are not reassigned to this lane's ledger entries.

## Distribution and executed checks

Start with `publish/submission-packages/a2/v0142-s1/DELIVERY-README.md`.
The adjacent `v0142-s1.zip` is 400846 bytes with SHA-256
`4a7eafc001f816ea470cbe1a07a2415bf582bb93f57662d25f000d6d5cc96a95`.
Its manifest inventories 56 files, plus the manifest itself. The full-source
companion is 160324093 bytes and retains 9662 inventoried source files plus
its transport manifest. Large transport is locally retained outside Git,
not silently pushed or claimed backed up. Its identity and regeneration
contract are preserved in the public distribution manifest and README.

`verification/scripts/a2_submission_distribution.py` validates the pinned
outer archive hashes, every member hash/size, inventory, CRC, checkpoint and
review/submission disposition. All 43 shared paper members agree exactly
between the original small archive and full source. It refuses an existing
sealed destination, unsafe paths, symlinks and source substitutions. A new
delivery does not overwrite the original v0.1.42 archives or v0.1.41 research.

The newly extracted source replay passes all 14 commands: A2 61/61; R-157
integrated 144/144; R-158 integrated 155/155; assurance-only R-472 22/22 with
Lean PASS; exact coercivity 13/13, Class-II sign 8/8, ensemble 24/24,
analytic dependency 50/50, blank review packet 22/22 and manifest PASS.
The original package identity/body/disclosure audit was rerun at 19/19.
These are executed finite/structural assertions, not a proof by computation
or an independent mathematical/novelty acceptance.

The first two fresh replay attempts failed before any mathematical command
because sandbox access to an existing MiKTeX path was denied. Both failed
receipts are included. A subprocess PATH filter alone did not resolve the
runtime access. The authorized runtime-access retry used the same extracted
bytes and explicitly pinned historical Tectonic 0.16.9, then passed 14/14.
No old expected hash or proof source was changed to obtain PASS.

The unchanged 18-page manuscript and two-page submission notes were freshly
rendered at 120 dpi and all pages visually inspected. Text/geometry checks
find no blank page, off-page glyph or unresolved reference. Visual inspection
finds no clipping/overlap; bibliography spacing remains legible. PDF source
and bytes are reused, not reissued. Current records are under the
distribution's `checks/` directory. The manifest itself is not a signature;
an externally retained ZIP digest is needed for transport trust.

## Adversarial tooling review

1. **Wrong source or uncommitted branch state - mitigated.** Exact original
   archive digests, source commit in metadata and Git archive comment, member
   hashes and 43 cross-archive byte matches pin the source. Mutable source
   worktree files are not used to assemble the delivery.
2. **False external approval - rejected at tooling scope.** Both original
   forms remain blank and hash-current; the 19-check audit confirms that
   status. Archive fixtures reject false approval and submitted=true. No
   review signature is manufactured or required for material preparation.
3. **Corrupt or unsafe ZIP - rejected for tested fixtures.** The self-test
   rejects nine unsafe paths; seven archive fixtures cover valid data,
   changed data, missing/incomplete inventory, wrong commit and false review
   or submission disposition. The verifier rejects duplicate and symlink
   members as additional guards. It checks CRC and every archived byte.
4. **Historical PASS relabelled as current - rejected.** The new 14-command
   replay has its own receipt, original input-manifest hash and actual
   per-command return codes. Initial runtime failures remain visible. Old
   clean replay and PDF receipts stay unchanged and are separately named.
5. **Units, signs, convergence and hardcoded science - no new scientific
   calculation.** The packaging code derives sizes, counts and hashes from
   data. Literal commit/digest identities are declared source inputs. The
   analytic proof, ensemble distinction and limit non-claims are unchanged.

## Reproduction and next action

```text
python -X utf8 verification/scripts/a2_submission_distribution.py --self-test --check publish/submission-packages/a2/v0142-s1.zip
```

The extracted package's `verify-delivery.py` runs without repository/Git
metadata and verifies either ZIP. Follow its delivery README for the full
source replay and explicitly declared Python, SymPy, Lean/Mathlib and TeX
environment. External review and inspection of the tooling are invited.

Next: complete the lane-local release-gated checkpoint and submit its fixed
commit through the integration controller when its existing pending-request
backpressure is resolved. Central integration and remote backup must have
their own receipts. The author may select a venue and confirm personal
declarations; no upload, email, tag, journal compliance or acceptance is
authorized or recorded here. Any changed bytes, failed replay, source/proof
objection, subsuming theorem or new reviewer finding reopens the affected
item. The A2/R-157/R-158 scientific claim state is unchanged.
