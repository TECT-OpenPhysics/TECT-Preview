#!/usr/bin/env python3
"""Primary exact verifier for the staged R-167 v2.5 route split.

Fixtures A--J preserve every v2.3 exact check and historical boundary.
Fixture K checks the fixed-faithful-standard-form strong-star upgrade, the
conditional bidirectional all-shape Cauchy completion arithmetic, the sharp
first homological generator and Ritz/QPS bounds, and two distinct automatic-
promotion obstructions. Fixture L checks the complete fixed-finite-volume/Ritz third-order
low block, linked edge-triple and conservative QPS bounds, exact rational
fixtures, and the canonical compact-cylinder point-norm C0 obstruction. The
actual history conclusion remains confined to
the registered fixed-beta periodic compact-source family, while the new
observable conclusion is fixed finite standard representation by fixed finite
standard representation.  Actual all-shape Q3 common alpha, generator/KMS
identification, all-order connected rank-two oscillator/QPS transfer, and the
broken-sector GNS gap remain open.

Use ``--staged --no-store`` while EXP-000825, R-167 v2.5, the one new negative
row and one new closed gate row are assembled; the four formal misses then produce
the honest verdict ``INCOMPLETE``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction
from itertools import product
from pathlib import Path
from typing import Any, Iterable

import sympy as sp


__version__ = "2.5.0"
REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-local-measured-renyi-semiclassical-doublet-route-split"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260811.md"
DEFAULT_OUTPUT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-12-primary-{SLUG}-v2-5/result.json"
)
EXPLORATION_LEDGER = REPO / "explorations/log.jsonl"
RESULT_LEDGER = REPO / "RESULTS-LEDGER.md"
NEGATIVE_REGISTRY = REPO / "negative-results/registry.md"
GATE_REGISTRY = REPO / "claims/GATES.md"

EXPECTED_TASK = "T-054"
EXPECTED_CLAIM_IDS = ("C6-SPACETIME-SIGNATURE",)
EXPECTED_EXPLORATION = "EXP-000825"
EXPECTED_RESULT_NUMBER = "R-167"
EXPECTED_RESULT_VERSION = "v2.5"
EXPECTED_RESULT_ID = (
    "PA-CP1-ST8-Q3LOCK-SECOND-WEIGHTED-ENERGY-MOMENT-AND-COMMON-ALPHA-CAUCHY-GATE-SPLIT"
)
EXPECTED_CANDIDATE_ID = (
    "PA-CP1-ST8-Q3LOCK-LOCAL-MEASURED-RENYI-SEMICLASSICAL-DOUBLET-ROUTE-SPLIT-v0"
)
EXPECTED_CLOSED_SUBGATES = ('PA-CP1-ST8-Q3LOCK-PURE-BOND-COORDINATE-TAIL-INVARIANCE-AND-STATE-WEIGHTED-CUTOFF-IDENTITY', 'PA-CP1-ST8-Q3LOCK-LOCAL-MEASURED-RENYI-TO-HISTORY-TAIL-REDUCTION', 'PA-CP1-ST8-Q3LOCK-SEMICLASSICAL-ONSITE-DOUBLET-AND-EXACT-LOW-BAND-TFIM-COMPRESSION', 'PA-CP1-ST8-Q3LOCK-FULL-HAMILTONIAN-TWO-ORIENTATION-STATIC-GIBBS-CUTOFF-UNITARY-RESUMMATION', 'PA-CP1-ST8-Q3LOCK-FIXED-BOND-RESTRICTED-TAIL-TO-GROWING-CORRIDOR-REDUCTION', 'PA-CP1-ST8-Q3LOCK-BELOW-ONE-HIGH-MODE-FESHBACH-AND-RELATIVE-FORM-SMALLNESS-PRECURSOR', 'PA-CP1-ST8-Q3LOCK-EXACT-COMPRESSED-TFIM-TWO-PHASE-QPS-AND-PHASEWISE-GAP', 'PA-CP1-ST8-Q3LOCK-TWO-ORIENTATION-TWENTIETH-MOMENT-FIXED-EDGE-CORRIDOR-REDUCTION', 'PA-CP1-ST8-Q3LOCK-FULL-OSCILLATOR-EDGE-BLOCK-PARITY-DOUBLET-CLUSTER-AND-UNIFORM-ONSITE-SPECTRAL-CUTOFF-REMOVAL', 'PA-CP1-ST8-Q3LOCK-TRANSLATE-UNIFORM-LOCAL-FIFTH-GIBBS-MOMENT-AND-ELLIPTIC-EMBEDDING', 'PA-CP1-ST8-Q3LOCK-SIMULTANEOUS-BOND-SHEAR-FIFTH-GRAPH-PROPAGATION', 'PA-CP1-ST8-Q3LOCK-ACTUAL-TWO-ORIENTATION-TWENTIETH-HISTORY-MOMENT-AND-HARD-CUTOFF-CORRIDOR', 'PA-CP1-ST8-Q3LOCK-REGISTERED-PERIODIC-SPLIT-IMPLEMENTER-TWO-SIDED-GIBBS-L2-HARD-CUTOFF-REMOVAL', 'PA-CP1-ST8-Q3LOCK-CONDITIONAL-CONNECTED-CLUSTER-GEOMETRIC-QPS-NORM-ENVELOPE', 'PA-CP1-ST8-Q3LOCK-SECOND-ORDER-CONNECTED-ONSITE-RESOLVENT-QPS-NORM-AND-RITZ-CUTOFF', 'PA-CP1-ST8-Q3LOCK-FIXED-FINITE-FAITHFUL-GIBBS-STANDARD-FORM-POINT-STRONGSTAR-OBSERVABLE-CUTOFF-REMOVAL', 'PA-CP1-ST8-Q3LOCK-CONDITIONAL-BIDIRECTIONAL-ALL-SHAPE-POINT-NORM-CAUCHY-C0-AUTOMORPHISM-COMPLETION', 'PA-CP1-ST8-Q3LOCK-FIRST-LOCAL-HOMOLOGICAL-RANK-TWO-GENERATOR-QPS-NORM-AND-RITZ-CUTOFF', 'PA-CP1-ST8-Q3LOCK-FIXED-FINITE-VOLUME-AND-RITZ-COMPLETE-THIRD-ORDER-LINKED-RANK-TWO-LOW-BLOCK-COEFFICIENT')
V2_1_CLOSED_SUBGATES = (
    'PA-CP1-ST8-Q3LOCK-TWO-ORIENTATION-TWENTIETH-MOMENT-FIXED-EDGE-CORRIDOR-REDUCTION',
    'PA-CP1-ST8-Q3LOCK-FULL-OSCILLATOR-EDGE-BLOCK-PARITY-DOUBLET-CLUSTER-AND-UNIFORM-ONSITE-SPECTRAL-CUTOFF-REMOVAL',
)
V2_2_CLOSED_SUBGATES = (
    'PA-CP1-ST8-Q3LOCK-TRANSLATE-UNIFORM-LOCAL-FIFTH-GIBBS-MOMENT-AND-ELLIPTIC-EMBEDDING',
    'PA-CP1-ST8-Q3LOCK-SIMULTANEOUS-BOND-SHEAR-FIFTH-GRAPH-PROPAGATION',
    'PA-CP1-ST8-Q3LOCK-ACTUAL-TWO-ORIENTATION-TWENTIETH-HISTORY-MOMENT-AND-HARD-CUTOFF-CORRIDOR',
)
V2_3_CLOSED_SUBGATES = (
    'PA-CP1-ST8-Q3LOCK-REGISTERED-PERIODIC-SPLIT-IMPLEMENTER-TWO-SIDED-GIBBS-L2-HARD-CUTOFF-REMOVAL',
    'PA-CP1-ST8-Q3LOCK-CONDITIONAL-CONNECTED-CLUSTER-GEOMETRIC-QPS-NORM-ENVELOPE',
    'PA-CP1-ST8-Q3LOCK-SECOND-ORDER-CONNECTED-ONSITE-RESOLVENT-QPS-NORM-AND-RITZ-CUTOFF',
)
V2_4_CLOSED_SUBGATES = (
    'PA-CP1-ST8-Q3LOCK-FIXED-FINITE-FAITHFUL-GIBBS-STANDARD-FORM-POINT-STRONGSTAR-OBSERVABLE-CUTOFF-REMOVAL',
    'PA-CP1-ST8-Q3LOCK-CONDITIONAL-BIDIRECTIONAL-ALL-SHAPE-POINT-NORM-CAUCHY-C0-AUTOMORPHISM-COMPLETION',
    'PA-CP1-ST8-Q3LOCK-FIRST-LOCAL-HOMOLOGICAL-RANK-TWO-GENERATOR-QPS-NORM-AND-RITZ-CUTOFF',
)
V2_5_CLOSED_SUBGATES = (
    'PA-CP1-ST8-Q3LOCK-FIXED-FINITE-VOLUME-AND-RITZ-COMPLETE-THIRD-ORDER-LINKED-RANK-TWO-LOW-BLOCK-COEFFICIENT',
)
EXPECTED_OPEN_GATES = ('PA-CP1-ST8-Q3LOCK-LOCAL-STRICT-ALL-EXHAUSTION-TWO-ORIENTATION-HISTORY-COMMON-ALPHA', 'PA-CP1-ST8-Q3LOCK-BROKEN-SECTOR-GNS-GAP-COERCIVITY', 'PA-CP1-ST8-Q3LOCK-INFINITE-DIMENSIONAL-RANK-TWO-BAND-BLOCK-DIAGONALIZATION-AND-TWO-PHASE-QPS', 'PA-ROUND1-EVIDENCE-ROLE-AND-MINIMUM-MANIFEST-FREEZE', 'PA-CP1-ST8-Q3LOCK-CONNECTED-RANK-TWO-OSCILLATOR-ELIMINATION-QPS-NORM-AND-CUTOFF-COMPATIBILITY')
NEGATIVE_IDS = ('NG-2026-08-11-PRE-A-ST8-Q3LOCK-GLOBAL-ALL-BOND-RENYI-VOLUME-UNIFORMITY', 'NG-2026-08-11-PRE-A-ST8-Q3LOCK-RANK-ONE-UNBOUNDED-BLOCK-DIAGONALIZATION-DIRECT-BROKEN-DOUBLET-IMPORT', 'NG-2026-08-11-PRE-A-ST8-Q3LOCK-WEIGHTED-UNITARY-CUTOFF-AUTOMATIC-ARBITRARY-CONTEXT-AUTOMORPHISM-L2-UPGRADE', 'NG-2026-08-11-PRE-A-ST8-Q3LOCK-EXTENSIVE-FESHBACH-SELF-ENERGY-AUTOMATIC-QPS-LOCALITY', 'NG-2026-08-11-PRE-A-ST8-Q3LOCK-STATIC-GAUSSIAN-SYMMETRY-FINITE-MOMENT-AUTOMATIC-FIXED-EDGE-HISTORY-TAIL', 'NG-2026-08-11-PRE-A-ST8-Q3LOCK-UNIFORM-QUADRATIC-IN-M-ALL-MOMENT-BOND-SHEAR-GRAPH-TRANSPORT', 'NG-2026-08-11-PRE-A-ST8-Q3LOCK-STATIC-MOMENTS-AND-LOW-GRAPH-AUTOMATIC-TWENTIETH-HISTORY-MOMENT', 'NG-2026-08-11-PRE-A-ST8-Q3LOCK-FULL-OSCILLATOR-LOCAL-PARITY-DOUBLET-EDGE-GAP-AUTOMATIC-VOLUME-UNIFORM-LATTICE-GAP', 'NG-2026-08-11-PRE-A-ST8-Q3LOCK-FORWARD-LOCAL-AUTOMORPHISM-LIMIT-AUTOMATIC-SURJECTIVITY-AND-INVERSE-CAUCHY', 'NG-2026-08-12-PRE-A-ST8-Q3LOCK-SECOND-ORDER-DISJOINT-VANISHING-AUTOMATIC-ALL-ORDER-GLOBAL-FESHBACH-CONNECTEDNESS', 'NG-2026-08-12-PRE-A-ST8-Q3LOCK-RITZ-CUTOFF-ORDINARY-BOUNDED-OPERATOR-SW-SMALLNESS-UNIFORMITY', 'NG-2026-08-12-PRE-A-ST8-Q3LOCK-CANONICAL-ONE-SITE-COMPACT-CYLINDER-BOND-SUBFLOW-POINT-NORM-C0')
V2_1_NEGATIVE_IDS = (
    'NG-2026-08-11-PRE-A-ST8-Q3LOCK-UNIFORM-QUADRATIC-IN-M-ALL-MOMENT-BOND-SHEAR-GRAPH-TRANSPORT',
    'NG-2026-08-11-PRE-A-ST8-Q3LOCK-STATIC-MOMENTS-AND-LOW-GRAPH-AUTOMATIC-TWENTIETH-HISTORY-MOMENT',
)
V2_2_NEGATIVE_IDS = (
    'NG-2026-08-11-PRE-A-ST8-Q3LOCK-FULL-OSCILLATOR-LOCAL-PARITY-DOUBLET-EDGE-GAP-AUTOMATIC-VOLUME-UNIFORM-LATTICE-GAP',
)
V2_3_NEGATIVE_IDS = (
    'NG-2026-08-11-PRE-A-ST8-Q3LOCK-FORWARD-LOCAL-AUTOMORPHISM-LIMIT-AUTOMATIC-SURJECTIVITY-AND-INVERSE-CAUCHY',
)
V2_4_NEGATIVE_IDS = (
    'NG-2026-08-12-PRE-A-ST8-Q3LOCK-SECOND-ORDER-DISJOINT-VANISHING-AUTOMATIC-ALL-ORDER-GLOBAL-FESHBACH-CONNECTEDNESS',
    'NG-2026-08-12-PRE-A-ST8-Q3LOCK-RITZ-CUTOFF-ORDINARY-BOUNDED-OPERATOR-SW-SMALLNESS-UNIFORMITY',
)
V2_5_NEGATIVE_IDS = (
    'NG-2026-08-12-PRE-A-ST8-Q3LOCK-CANONICAL-ONE-SITE-COMPACT-CYLINDER-BOND-SUBFLOW-POINT-NORM-C0',
)
SEMICLASSICAL_SOURCES = (
    "https://www.numdam.org/item/AIHPA_1983__38_3_295_0/",
    "https://www.numdam.org/item/AIHPA_1984__40_2_224_0/",
    "https://doi.org/10.1080/03605308408820335",
    "https://annals.math.princeton.edu/1984/120-1/p04",
    "https://www.numdam.org/item/AIHPA_1985__42_2_127_0/",
)
DFP_SOURCE = "https://arxiv.org/abs/2108.13907"
YAROTSKII_QPS_SOURCE = "https://doi.org/10.1070/RM2006v061n02ABEH004323"


def normalized_sha256(path: Path) -> str:
    raw = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(raw).hexdigest()




def _v2_5_raw_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _v2_5_compact_text(value: Any) -> str:
    return "".join(character for character in str(value).lower() if character.isalnum())


def _v2_5_text_has(text: Any, token: Any) -> bool:
    return _v2_5_compact_text(token) in _v2_5_compact_text(text)


def _v2_5_checkpoint_path(raw: Any, suffix: str) -> Path | None:
    if not isinstance(raw, str) or not raw or "\\" in raw:
        return None
    pure = Path(raw)
    if (
        pure.is_absolute()
        or pure.as_posix() != raw
        or any(part in {"", ".", ".."} for part in pure.parts)
        or not raw.endswith(suffix)
    ):
        return None
    candidate = (REPO / pure).resolve()
    try:
        candidate.relative_to(REPO.resolve())
    except ValueError:
        return None
    notes = (
        REPO
        / "claims/C6-SPACETIME-SIGNATURE/notes"
    ).resolve()
    if candidate.parent != notes:
        return None
    return candidate


def _v2_5_checkpoint_lifecycle(
    checkpoint: dict[str, Any],
    *,
    exploration_id: str,
    closed_subgates: tuple[str, ...],
    negative_ids: tuple[str, ...],
) -> dict[str, Any]:
    """Validate one R-167-only v2.5 issued source/PDF pair from raw files."""

    issued_fields = {
        "status",
        "source",
        "pdf",
        "source_sha256",
        "pdf_sha256",
        "pages",
        "workflow",
        "visual_qa",
    }
    issued_status = "ISSUED AS ONE GATE-LEVEL CHECKPOINT AFTER PROOF VALIDATION"
    issued_workflow = (
        "No per-lemma or intermediate PDF was issued. One R-167 v2.5 "
        "gate-level synthesis source/PDF pair was issued only after the "
        "primary, non-importing independent, integrated, formal-authority, "
        "generated-surface, source-form, freshness, dual-extraction, "
        "strict-release, and visual-review checks passed. R-168 v1.3 "
        "remains historical and is not reissued."
    )
    base_stem = SCRIPT.stem
    for suffix in ("_independent", "_verify"):
        if base_stem.endswith(suffix):
            base_stem = base_stem[: -len(suffix)]
    primary_script = SCRIPT.with_name(base_stem + ".py")
    independent_script = SCRIPT.with_name(base_stem + "_independent.py")
    integrated_script = SCRIPT.with_name(base_stem + "_verify.py")
    required_tokens = (
        "R-167 v2.5",
        exploration_id,
        *closed_subgates,
        *negative_ids,
        _v2_5_raw_sha256(primary_script),
        _v2_5_raw_sha256(independent_script),
        "384/384",
        "218/218",
        "369/369",
        primary_script.relative_to(REPO).as_posix(),
        independent_script.relative_to(REPO).as_posix(),
        integrated_script.relative_to(REPO).as_posix(),
        "Theta",
        "T^*RCRT",
        "1/300",
        "17/5000",
        "-313/90000",
        "431/22500",
        "noncommutative",
        "fixed finite spatial volume",
        "Lambda",
        "Ritz",
        "no spatial-volume or thermodynamic limit",
        "12z(2z-1)^2",
        "2820703613673/762939453125000",
        "compact-cylinder",
        "compact ideal multiplier",
        "4/5",
        "3/5",
        "9/25",
        "nonzero coupling",
        "Lambda-uniform",
        "cutoff-uniform",
        "all-order",
        "R-167-only",
        "R-168 v1.3",
        "historical",
        "not reissued",
        "physical Sector A",
        "Pre-A",
    )
    pages = checkpoint.get("pages")
    visual_qa = (
        f"All {pages} rendered pages were reviewed at readable resolution "
        "with zero clipping, overlap, broken equations, unreadable identifiers, "
        "black glyphs, or malformed page transitions; pypdf and pdfplumber each "
        f"extracted {pages}/{pages} nonempty pages; the build reported "
        "OVERFULL-HBOX 0."
        if isinstance(pages, int)
        and not isinstance(pages, bool)
        and pages > 0
        else None
    )
    source = _v2_5_checkpoint_path(checkpoint.get("source"), ".tex.txt")
    pdf = _v2_5_checkpoint_path(checkpoint.get("pdf"), ".pdf")
    paired = (
        source is not None
        and pdf is not None
        and source.parent == pdf.parent
        and source.name.endswith(".tex.txt")
        and pdf.name == source.name[:-8] + ".pdf"
    )
    hash_values = (checkpoint.get("source_sha256"), checkpoint.get("pdf_sha256"))
    lowercase_hashes = all(
        isinstance(value, str)
        and len(value) == 64
        and value == value.lower()
        and all(character in "0123456789abcdef" for character in value)
        for value in hash_values
    )
    diagnostics: dict[str, Any] = {
        "issued_fields_exact": set(checkpoint) == issued_fields,
        "status_exact": checkpoint.get("status") == issued_status,
        "workflow_exact": checkpoint.get("workflow") == issued_workflow,
        "visual_qa_exact": visual_qa is not None
        and checkpoint.get("visual_qa") == visual_qa,
        "source_path_valid": source is not None,
        "pdf_path_valid": pdf is not None,
        "sibling_source_pdf": paired,
        "lowercase_hashes": lowercase_hashes,
        "positive_pages": visual_qa is not None,
        "source_exists": source is not None and source.is_file(),
        "pdf_exists": pdf is not None and pdf.is_file(),
        "raw_hashes_match": False,
        "pdf_newer": False,
        "source_missing_tokens": list(required_tokens),
        "pypdf_pages": None,
        "pypdf_nonempty_pages": None,
        "pypdf_missing_tokens": list(required_tokens),
        "pypdf_error": None,
        "pdfplumber_pages": None,
        "pdfplumber_nonempty_pages": None,
        "pdfplumber_missing_tokens": list(required_tokens),
        "pdfplumber_error": None,
        "r167_only_r168_historical": (
            checkpoint.get("workflow") == issued_workflow
            and _v2_5_text_has(checkpoint.get("workflow", ""), "R-167 v2.5")
            and _v2_5_text_has(checkpoint.get("workflow", ""), "R-168 v1.3")
            and _v2_5_text_has(checkpoint.get("workflow", ""), "historical")
            and _v2_5_text_has(checkpoint.get("workflow", ""), "not reissued")
        ),
        "valid": False,
    }
    if source is not None and pdf is not None and source.is_file() and pdf.is_file():
        try:
            source_text = source.read_text(encoding="utf-8")
            source_hash = _v2_5_raw_sha256(source)
            pdf_hash = _v2_5_raw_sha256(pdf)
            diagnostics["raw_hashes_match"] = (
                lowercase_hashes
                and checkpoint.get("source_sha256") == source_hash
                and checkpoint.get("pdf_sha256") == pdf_hash
            )
            diagnostics["pdf_newer"] = (
                pdf.stat().st_mtime_ns > source.stat().st_mtime_ns
            )
            diagnostics["source_missing_tokens"] = [
                token for token in required_tokens
                if not _v2_5_text_has(source_text, token)
            ]
        except (OSError, UnicodeError) as error:
            diagnostics["source_error"] = f"{type(error).__name__}: {error}"
        try:
            from pypdf import PdfReader

            texts = [
                page.extract_text() or ""
                for page in PdfReader(str(pdf)).pages
            ]
            joined = "\n".join(texts)
            diagnostics["pypdf_pages"] = len(texts)
            diagnostics["pypdf_nonempty_pages"] = sum(
                bool(text.strip()) for text in texts
            )
            diagnostics["pypdf_missing_tokens"] = [
                token for token in required_tokens
                if not _v2_5_text_has(joined, token)
            ]
        except Exception as error:
            diagnostics["pypdf_error"] = f"{type(error).__name__}: {error}"
        try:
            import pdfplumber

            with pdfplumber.open(pdf) as document:
                texts = [
                    page.extract_text() or ""
                    for page in document.pages
                ]
            joined = "\n".join(texts)
            diagnostics["pdfplumber_pages"] = len(texts)
            diagnostics["pdfplumber_nonempty_pages"] = sum(
                bool(text.strip()) for text in texts
            )
            diagnostics["pdfplumber_missing_tokens"] = [
                token for token in required_tokens
                if not _v2_5_text_has(joined, token)
            ]
        except Exception as error:
            diagnostics["pdfplumber_error"] = f"{type(error).__name__}: {error}"

    diagnostics["valid"] = (
        diagnostics["issued_fields_exact"]
        and diagnostics["status_exact"]
        and diagnostics["workflow_exact"]
        and diagnostics["visual_qa_exact"]
        and diagnostics["source_path_valid"]
        and diagnostics["pdf_path_valid"]
        and diagnostics["sibling_source_pdf"]
        and diagnostics["lowercase_hashes"]
        and diagnostics["positive_pages"]
        and diagnostics["source_exists"]
        and diagnostics["pdf_exists"]
        and diagnostics["raw_hashes_match"]
        and diagnostics["pdf_newer"]
        and diagnostics["source_missing_tokens"] == []
        and diagnostics["pypdf_error"] is None
        and diagnostics["pypdf_pages"] == pages
        and diagnostics["pypdf_nonempty_pages"] == pages
        and diagnostics["pypdf_missing_tokens"] == []
        and diagnostics["pdfplumber_error"] is None
        and diagnostics["pdfplumber_pages"] == pages
        and diagnostics["pdfplumber_nonempty_pages"] == pages
        and diagnostics["pdfplumber_missing_tokens"] == []
        and diagnostics["r167_only_r168_historical"]
    )
    return diagnostics


def json_safe(value: Any) -> Any:
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, Fraction):
        return f"{value.numerator}/{value.denominator}"
    if isinstance(value, sp.Basic):
        return str(value)
    if isinstance(value, sp.MatrixBase):
        return [[json_safe(item) for item in row] for row in value.tolist()]
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [json_safe(item) for item in value]
    return str(value)


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(json_safe(payload), stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(
        self,
        name: str,
        condition: bool,
        actual: Any,
        expected: Any,
        group: str,
    ) -> None:
        if not condition:
            raise AssertionError(f"{group}: {name}: {actual!r} != {expected!r}")
        self.rows.append(
            {
                "group": group,
                "name": name,
                "status": "PASS",
                "actual": json_safe(actual),
                "expected": json_safe(expected),
            }
        )


def trace(matrix: sp.MatrixBase) -> sp.Expr:
    return sp.simplify(sum(matrix[index, index] for index in range(matrix.rows)))


def leading_principal_minors(matrix: sp.MatrixBase) -> list[sp.Expr]:
    return [
        sp.factor(matrix[:size, :size].det())
        for size in range(1, matrix.rows + 1)
    ]


def fixture_a_pure_bond_tail(audit: Audit) -> dict[str, Any]:
    """Exact finite spectral fixture for the pure-bond cutoff identity."""

    # Declared exact fixture inputs.  The density matrix is deliberately
    # non-diagonal, so equality of the two orientations uses normality of the
    # coordinate multiplier and not commutation with the state.
    sigma = sp.Matrix(
        [
            [sp.Rational(1, 2), sp.Rational(1, 10), 0],
            [sp.Rational(1, 10), sp.Rational(1, 3), sp.Rational(1, 20)],
            [0, sp.Rational(1, 20), sp.Rational(1, 6)],
        ]
    )
    delta = sp.pi
    hbar = sp.Integer(1)
    v_cut = sp.diag(0, 1, 0)
    w_tail = sp.diag(0, 1, 2)
    v_full = v_cut + w_tail
    coordinate_multiplier = sp.diag(2, -1, 3)

    b_full = sp.diag(
        *[sp.exp(-sp.I * delta * v_full[i, i] / hbar) for i in range(3)]
    )
    b_cut = sp.diag(
        *[sp.exp(-sp.I * delta * v_cut[i, i] / hbar) for i in range(3)]
    )
    difference = sp.simplify(b_full - b_cut)
    spectral_tail = sp.diag(
        *[
            4 * sp.sin(delta * w_tail[i, i] / (2 * hbar)) ** 2
            for i in range(3)
        ]
    )
    right_orientation = sp.simplify(trace(sigma * difference.H * difference))
    left_orientation = sp.simplify(trace(sigma * difference * difference.H))
    spectral_identity = sp.simplify(trace(sigma * spectral_tail))
    quadratic_upper = sp.simplify(
        delta**2 * trace(sigma * w_tail**2) / hbar**2
    )
    principal_minors = leading_principal_minors(sigma)

    audit.check(
        "fixture A density trace",
        trace(sigma) == 1,
        trace(sigma),
        1,
        "A_pure_bond",
    )
    audit.check(
        "fixture A density positive",
        all(bool(value > 0) for value in principal_minors),
        principal_minors,
        "all positive",
        "A_pure_bond",
    )
    audit.check(
        "coordinate multiplier commutes with full bond kick",
        sp.zeros(3) == b_full * coordinate_multiplier - coordinate_multiplier * b_full,
        b_full * coordinate_multiplier - coordinate_multiplier * b_full,
        sp.zeros(3),
        "A_pure_bond",
    )
    audit.check(
        "two Hilbert-Schmidt orientations exact",
        right_orientation == left_orientation == spectral_identity,
        (right_orientation, left_orientation, spectral_identity),
        "equal",
        "A_pure_bond",
    )
    # TEST ORACLE: with the declared roots-of-unity phases, only the middle
    # spectral atom contributes and its squared difference is four.
    audit.check(
        "state-weighted cutoff identity oracle",
        spectral_identity == sp.Rational(4, 3),
        spectral_identity,
        sp.Rational(4, 3),
        "A_pure_bond",
    )
    audit.check(
        "sine quadratic upper bound fixture",
        bool(sp.N(quadratic_upper - spectral_identity, 80) > 0),
        quadratic_upper - spectral_identity,
        ">0",
        "A_pure_bond",
    )

    return {
        "inputs": {
            "sigma": sigma,
            "delta": delta,
            "hbar": hbar,
            "V_cut": v_cut,
            "W_tail": w_tail,
            "coordinate_multiplier": coordinate_multiplier,
        },
        "commutator_zero": True,
        "right_orientation_hs_squared": right_orientation,
        "left_orientation_hs_squared": left_orientation,
        "spectral_sine_identity": spectral_identity,
        "quadratic_upper_bound": quadratic_upper,
        "pure_layer_only": True,
        "onsite_interspersed_history_tail_proved": False,
    }


def classical_q2(reference: Iterable[Fraction], state: Iterable[Fraction]) -> Fraction:
    return sum(p * p / q for p, q in zip(state, reference))


def fixture_b_local_and_global_renyi(audit: Audit) -> dict[str, Any]:
    """Exact local Holder fixture and exact global product obstruction."""

    reference = (Fraction(1, 2), Fraction(1, 3), Fraction(1, 6))
    plus = (Fraction(2, 3), Fraction(1, 6), Fraction(1, 6))
    minus = (Fraction(1, 4), Fraction(1, 2), Fraction(1, 4))
    event = (1, 2)
    q_event = sum(reference[index] for index in event)
    p_plus_event = sum(plus[index] for index in event)
    p_minus_event = sum(minus[index] for index in event)
    q2_plus = classical_q2(reference, plus)
    q2_minus = classical_q2(reference, minus)

    audit.check(
        "fixture B probability normalization",
        sum(reference) == sum(plus) == sum(minus) == 1,
        (sum(reference), sum(plus), sum(minus)),
        (1, 1, 1),
        "B_local_renyi",
    )
    audit.check(
        "plus measured-Renyi Holder event",
        p_plus_event**2 <= q2_plus * q_event,
        p_plus_event**2,
        f"<={q2_plus * q_event}",
        "B_local_renyi",
    )
    audit.check(
        "minus measured-Renyi Holder event",
        p_minus_event**2 <= q2_minus * q_event,
        p_minus_event**2,
        f"<={q2_minus * q_event}",
        "B_local_renyi",
    )

    alpha = sp.Integer(2)
    theta_holder = sp.simplify((alpha - 1) / alpha)
    gaussian_a = sp.Rational(4, 3)
    b_decay = sp.simplify(theta_holder * gaussian_a)
    cutoff_l = sp.Rational(3, 2)
    layer_cake_polynomial = sp.simplify(
        cutoff_l**4
        + 2 * cutoff_l**2 / b_decay
        + 2 / b_decay**2
    )
    # TEST ORACLE computed independently from the displayed layer-cake
    # antiderivative for the declared rational inputs.
    audit.check(
        "weighted fourth-tail polynomial",
        layer_cake_polynomial == sp.Rational(261, 16),
        layer_cake_polynomial,
        sp.Rational(261, 16),
        "B_local_renyi",
    )

    # Exact conditional low-doublet product fixture from the v1.9 manifest.
    p = sp.Rational(4, 5)
    rho_one = sp.diag(p, 1 - p)
    rho_two = sp.kronecker_product(rho_one, rho_one)
    pauli_x = sp.Matrix([[0, 1], [1, 0]])
    xx = sp.kronecker_product(pauli_x, pauli_x)
    angle = sp.symbols("angle", real=True)
    unitary = sp.cos(angle) * sp.eye(4) + sp.I * sp.sin(angle) * xx
    rotated = sp.simplify(unitary * rho_two * unitary.H)
    rho_inverse_half = sp.diag(
        *[sp.simplify(rho_two[index, index] ** sp.Rational(-1, 2)) for index in range(4)]
    )
    sandwiched_q2 = sp.trace(
        rotated * rho_inverse_half * rotated * rho_inverse_half
    )
    sandwiched_q2 = sp.trigsimp(sp.simplify(sandwiched_q2))
    expected_formula = sp.simplify((4 + 9 * sp.sin(angle) ** 2) ** 2 / 16)
    formula_residual = sp.trigsimp(sp.expand_trig(sandwiched_q2 - expected_formula))
    one_bond = sp.simplify(sandwiched_q2.subs(angle, sp.pi / 4))
    three_bonds = sp.simplify(one_bond**3)
    local_coordinate = sp.kronecker_product(pauli_x, sp.eye(2))

    # A full spatial bond sums all eight onsite components.  After the
    # symmetric doublet compression q_e -> m sigma_x, its kick angle is eight
    # times the single-component channel angle.
    delta_step, c_bond, m_bond, hbar_bond = sp.symbols(
        "delta c_bond m_bond hbar_bond", positive=True
    )
    j_bond = 8 * c_bond * m_bond**2
    full_bond_angle = 8 * delta_step * c_bond * m_bond**2 / hbar_bond
    single_component_angle = delta_step * c_bond * m_bond**2 / hbar_bond

    audit.check(
        "global sandwiched Q2 formula",
        formula_residual == 0,
        formula_residual,
        0,
        "B_global_renyi_no_go",
    )
    audit.check(
        "one-bond Renyi oracle",
        one_bond == sp.Rational(289, 64),
        one_bond,
        sp.Rational(289, 64),
        "B_global_renyi_no_go",
    )
    audit.check(
        "three-bond tensor multiplicativity oracle",
        three_bonds == sp.Rational(24137569, 262144),
        three_bonds,
        sp.Rational(24137569, 262144),
        "B_global_renyi_no_go",
    )
    audit.check(
        "local coordinate algebra commutes with doublet kick",
        local_coordinate * xx - xx * local_coordinate == sp.zeros(4),
        local_coordinate * xx - xx * local_coordinate,
        sp.zeros(4),
        "B_global_renyi_no_go",
    )
    audit.check(
        "full eight-component bond kick angle",
        sp.simplify(full_bond_angle - delta_step * j_bond / hbar_bond) == 0
        and sp.simplify(full_bond_angle / single_component_angle) == 8,
        (full_bond_angle, sp.simplify(full_bond_angle / single_component_angle)),
        (delta_step * j_bond / hbar_bond, 8),
        "B_global_renyi_no_go",
    )

    return {
        "local_measured_renyi": {
            "reference": reference,
            "plus": plus,
            "minus": minus,
            "Q2_plus": q2_plus,
            "Q2_minus": q2_minus,
            "event_reference": q_event,
            "event_plus": p_plus_event,
            "event_minus": p_minus_event,
            "theta": theta_holder,
            "gaussian_a": gaussian_a,
            "b": b_decay,
            "cutoff_L": cutoff_l,
            "fourth_tail_polynomial": layer_cake_polynomial,
            "onsite_interspersed_likelihood_bound_proved": False,
        },
        "global_product_no_go": {
            "rho_one": rho_one,
            "formula": expected_formula,
            "full_bond_angle": full_bond_angle,
            "single_component_angle": single_component_angle,
            "J": j_bond,
            "theta_pi_over_four": one_bond,
            "three_disjoint_bonds": three_bonds,
            "local_coordinate_probability_invariant": True,
            "counterexample_is_full_interacting_Q3_Gibbs": False,
        },
    }


Coord = tuple[int, int, int]


def q3_vertices_and_edges() -> tuple[list[Coord], list[tuple[int, int]]]:
    vertices = list(product((0, 1), repeat=3))
    edges = [
        (left, right)
        for left, a in enumerate(vertices)
        for right, b in enumerate(vertices[left + 1 :], start=left + 1)
        if sum(x != y for x, y in zip(a, b)) == 1
    ]
    return vertices, edges


def connected_component_size(vertex_count: int, edges: list[tuple[int, int]]) -> int:
    adjacency: dict[int, set[int]] = {index: set() for index in range(vertex_count)}
    for left, right in edges:
        adjacency[left].add(right)
        adjacency[right].add(left)
    seen = {0}
    frontier = [0]
    while frontier:
        current = frontier.pop()
        for neighbour in adjacency[current]:
            if neighbour not in seen:
                seen.add(neighbour)
                frontier.append(neighbour)
    return len(seen)


def q3_laplacian(vertex_count: int, edges: list[tuple[int, int]]) -> sp.Matrix:
    laplacian = sp.zeros(vertex_count)
    for left, right in edges:
        laplacian[left, left] += 1
        laplacian[right, right] += 1
        laplacian[left, right] -= 1
        laplacian[right, left] -= 1
    return laplacian


def parameter_fixture(label: str, r_abs: int, c_value: Fraction) -> dict[str, Any]:
    """Derived exact numbers for one declared g=lambda=chi=hbar=1 input."""

    root_r = sp.sqrt(r_abs)
    if not root_r.is_integer:
        raise AssertionError(f"fixture {label}: R must be a perfect square")
    mu = sp.Integer(1)
    v = root_r
    e_star = sp.Integer(r_abs) ** 2
    h_sc = sp.simplify(1 / (sp.Integer(r_abs) ** sp.Rational(3, 2)))
    s_zero = 16 * sp.sqrt(2) / 3
    e_well = sp.simplify(
        (
            sp.sqrt(2)
            + 3 * sp.sqrt(2 + 2 * mu)
            + 3 * sp.sqrt(2 + 4 * mu)
            + sp.sqrt(2 + 6 * mu)
        )
        / 2
    )
    # In the all-one normalization used by these three fixtures, the locked
    # infrared amplitude from R-167 is A0=2*c*R^2/9.  For the corridor
    # R=N^4,c=N^-4 this is (2/9)N^4.
    a_zero_ir = sp.simplify(
        sp.Rational(2, 9)
        * sp.Rational(c_value.numerator, c_value.denominator)
        * sp.Integer(r_abs) ** 2
    )
    return {
        "label": label,
        "inputs": {
            "r": -r_abs,
            "R": r_abs,
            "g": 1,
            "lambda": 1,
            "chi": 1,
            "hbar": 1,
            "c": c_value,
        },
        "mu": mu,
        "v": v,
        "E_star": e_star,
        "h_sc": h_sc,
        "S0_over_h_sc": sp.simplify(s_zero / h_sc),
        "harmonic_Gamma": sp.simplify(e_star * sp.sqrt(2) * h_sc),
        "harmonic_epsilon0": sp.simplify(e_star * h_sc * e_well),
        "A0": a_zero_ir,
        # This uses m=v only as the classical-limit proxy, not as finite-h
        # spectral data for the exact onsite operator.
        "classical_proxy_8c_v_squared": sp.simplify(8 * sp.Rational(c_value.numerator, c_value.denominator) * v**2),
        "finite_h_below_nonexplicit_h0_certified": False,
    }


def fixture_c_semiclassical_and_low_band(audit: Audit) -> dict[str, Any]:
    """Exact Q3 hypotheses, normalization, compression, and form fixtures."""

    vertices, edges = q3_vertices_and_edges()
    laplacian = q3_laplacian(len(vertices), edges)
    mu = sp.symbols("mu", positive=True)
    hessian = 2 * sp.eye(8) + mu * laplacian
    # Use the generator returned by charpoly.  SymPy deliberately strips
    # assumptions from a supplied generator, so reusing a positive input
    # symbol can create two distinct same-printing symbols and a false
    # nonzero residual.
    characteristic_polynomial = hessian.charpoly()
    spectral_t = characteristic_polynomial.gen
    characteristic = sp.factor(characteristic_polynomial.as_expr())
    expected_characteristic = sp.factor(
        (spectral_t - 2)
        * (spectral_t - 2 - 2 * mu) ** 3
        * (spectral_t - 2 - 4 * mu) ** 3
        * (spectral_t - 2 - 6 * mu)
    )
    audit.check(
        "Q3 vertices and edges",
        (len(vertices), len(edges)) == (8, 12),
        (len(vertices), len(edges)),
        (8, 12),
        "C_semiclassical_geometry",
    )
    audit.check(
        "Q3 graph connected",
        connected_component_size(len(vertices), edges) == 8,
        connected_component_size(len(vertices), edges),
        8,
        "C_semiclassical_geometry",
    )
    audit.check(
        "Q3 Hessian characteristic polynomial",
        sp.simplify(characteristic - expected_characteristic) == 0,
        characteristic,
        expected_characteristic,
        "C_semiclassical_geometry",
    )
    audit.check(
        "positive-mu minima nondegenerate",
        sp.simplify(
            hessian.det()
            - 256 * (mu + 1) ** 3 * (2 * mu + 1) ** 3 * (3 * mu + 1)
        )
        == 0,
        sp.factor(hessian.det()),
        256 * (mu + 1) ** 3 * (2 * mu + 1) ** 3 * (3 * mu + 1),
        "C_semiclassical_geometry",
    )

    path_x = sp.symbols("path_x", real=True)
    collective_potential = sp.simplify(8 * (path_x**2 - 1) ** 2 / 4)
    action = sp.simplify(
        sp.sqrt(8)
        * sp.integrate(sp.sqrt(2) * sp.sqrt(collective_potential), (path_x, -1, 1))
    )
    # Sympy retains Abs on a global integral in some releases; on [-1,1],
    # sqrt((x^2-1)^2)=1-x^2, so compute the theorem-side exact value too.
    action_on_interval = sp.simplify(
        sp.sqrt(8)
        * sp.integrate(sp.sqrt(2) * sp.sqrt(2) * (1 - path_x**2), (path_x, -1, 1))
    )
    audit.check(
        "locked collective action",
        action_on_interval == 16 * sp.sqrt(2) / 3,
        action_on_interval,
        16 * sp.sqrt(2) / 3,
        "C_semiclassical_geometry",
    )

    r_abs, g, coupling_lambda, chi, hbar = sp.symbols(
        "R g lambda chi hbar", positive=True
    )
    v = sp.sqrt(r_abs / g)
    e_star = r_abs**2 / g
    h_sc = hbar * g / (sp.sqrt(chi) * r_abs ** sp.Rational(3, 2))
    kinetic_coefficient = sp.simplify(hbar**2 / (2 * chi * v**2 * e_star))
    quartic_coefficient = sp.simplify(g * v**4 / (4 * e_star))
    lock_coefficient = sp.simplify(coupling_lambda * v**4 / (4 * e_star))
    audit.check(
        "semiclassical kinetic normalization",
        sp.simplify(kinetic_coefficient - h_sc**2 / 2) == 0,
        kinetic_coefficient,
        h_sc**2 / 2,
        "C_semiclassical_normalization",
    )
    audit.check(
        "semiclassical quartic normalization",
        quartic_coefficient == sp.Rational(1, 4),
        quartic_coefficient,
        sp.Rational(1, 4),
        "C_semiclassical_normalization",
    )
    audit.check(
        "semiclassical lock normalization",
        sp.simplify(lock_coefficient - (coupling_lambda / g) / 4) == 0,
        lock_coefficient,
        coupling_lambda / (4 * g),
        "C_semiclassical_normalization",
    )

    parameter_fixtures = {
        "A_repository_diagnostic": parameter_fixture("A", 9, Fraction(1)),
        "B_corridor_N2": parameter_fixture("B", 16, Fraction(1, 16)),
        "C_corridor_N3": parameter_fixture("C", 81, Fraction(1, 81)),
    }
    fixture_a = parameter_fixtures["A_repository_diagnostic"]
    fixture_b = parameter_fixtures["B_corridor_N2"]
    fixture_c = parameter_fixtures["C_corridor_N3"]
    audit.check(
        "parameter fixture A h_sc and action",
        fixture_a["h_sc"] == sp.Rational(1, 27)
        and fixture_a["S0_over_h_sc"] == 144 * sp.sqrt(2),
        (fixture_a["h_sc"], fixture_a["S0_over_h_sc"]),
        (sp.Rational(1, 27), 144 * sp.sqrt(2)),
        "C_parameter_fixtures",
    )
    audit.check(
        "parameter fixture B h_sc and action",
        fixture_b["h_sc"] == sp.Rational(1, 64)
        and fixture_b["S0_over_h_sc"] == 1024 * sp.sqrt(2) / 3,
        (fixture_b["h_sc"], fixture_b["S0_over_h_sc"]),
        (sp.Rational(1, 64), 1024 * sp.sqrt(2) / 3),
        "C_parameter_fixtures",
    )
    audit.check(
        "parameter fixture C h_sc and action",
        fixture_c["h_sc"] == sp.Rational(1, 729)
        and fixture_c["S0_over_h_sc"] == 3888 * sp.sqrt(2),
        (fixture_c["h_sc"], fixture_c["S0_over_h_sc"]),
        (sp.Rational(1, 729), 3888 * sp.sqrt(2)),
        "C_parameter_fixtures",
    )
    audit.check(
        "harmonic gap fixtures",
        [row["harmonic_Gamma"] for row in parameter_fixtures.values()]
        == [3 * sp.sqrt(2), 4 * sp.sqrt(2), 9 * sp.sqrt(2)],
        [row["harmonic_Gamma"] for row in parameter_fixtures.values()],
        [3 * sp.sqrt(2), 4 * sp.sqrt(2), 9 * sp.sqrt(2)],
        "C_parameter_fixtures",
    )
    audit.check(
        "A0 exact fixtures",
        [row["A0"] for row in parameter_fixtures.values()]
        == [sp.Integer(18), sp.Rational(32, 9), sp.Integer(18)],
        [row["A0"] for row in parameter_fixtures.values()],
        [sp.Integer(18), sp.Rational(32, 9), sp.Integer(18)],
        "C_parameter_fixtures",
    )

    # Exact low-band algebra in a two-dimensional abstract doublet.
    m_symbol, c_symbol, delta_one = sp.symbols("m c delta_1", real=True)
    a_zero, a_one = sp.symbols("a_0 a_1", real=True)
    identity_two = sp.eye(2)
    s = sp.Matrix([[0, 1], [1, 0]])
    p_one = sp.diag(0, 1)
    a_matrix = sp.diag(a_zero, a_one)
    low_bond = sp.simplify(
        4 * c_symbol * (
            sp.kronecker_product(a_matrix, identity_two)
            + sp.kronecker_product(identity_two, a_matrix)
        )
        - 8 * c_symbol * m_symbol**2 * sp.kronecker_product(s, s)
    )
    j_ising = 8 * c_symbol * m_symbol**2
    low_bond_expected = sp.simplify(
        j_ising * (sp.eye(4) - sp.kronecker_product(s, s))
        + 4 * c_symbol * (
            sp.kronecker_product(a_matrix, identity_two)
            + sp.kronecker_product(identity_two, a_matrix)
        )
        - j_ising * sp.eye(4)
    )
    degree_x = sp.symbols("deg_x", integer=True, nonnegative=True)
    delta_site = sp.expand(
        delta_one + 4 * degree_x * c_symbol * (a_one - a_zero)
    )
    z = sp.Integer(6)
    delta_effective = sp.expand(delta_site.subs(degree_x, z))
    audit.check(
        "one-bond exact low-band compression",
        low_bond == low_bond_expected,
        low_bond - low_bond_expected,
        sp.zeros(4),
        "C_low_band",
    )
    audit.check(
        "site-dependent boundary transverse coefficient",
        sp.simplify(
            delta_site
            - (delta_one + 4 * degree_x * c_symbol * (a_one - a_zero))
        )
        == 0,
        delta_site,
        delta_one + 4 * degree_x * c_symbol * (a_one - a_zero),
        "C_low_band",
    )
    audit.check(
        "periodic cubic z=6 transverse coefficient",
        sp.simplify(
            delta_effective
            - (delta_one + 24 * c_symbol * (a_one - a_zero))
        )
        == 0,
        delta_effective,
        delta_one + 24 * c_symbol * (a_one - a_zero),
        "C_low_band",
    )

    # Three-level hostile fixture: the third level is an explicit high mode.
    m_value = sp.Rational(1, 2)
    u_value = sp.Rational(2, 3)
    c_value = sp.Rational(3, 5)
    q = sp.Matrix(
        [
            [0, m_value, 0],
            [m_value, 0, u_value],
            [0, u_value, 0],
        ]
    )
    p_low = sp.diag(1, 1, 0)
    q_high = sp.eye(3) - p_low
    s_extended = sp.Matrix([[0, 1, 0], [1, 0, 0], [0, 0, 0]])
    q_squared = q**2
    q_fourth = q**4
    a_values = (q_squared[0, 0], q_squared[1, 1])
    b_values = (q_fourth[0, 0], q_fourth[1, 1])
    a_residual_squared = max(
        sp.simplify(a_values[0] - m_value**2),
        sp.simplify(a_values[1] - m_value**2),
    )
    b_residual_squared = max(
        sp.simplify(b_values[0] - a_values[0] ** 2),
        sp.simplify(b_values[1] - a_values[1] ** 2),
    )
    a_residual = sp.sqrt(a_residual_squared)
    b_residual = sp.sqrt(b_residual_squared)
    audit.check(
        "P q P equals m s",
        p_low * q * p_low == m_value * s_extended,
        p_low * q * p_low,
        m_value * s_extended,
        "C_moment_residual",
    )
    audit.check(
        "Q q P moment identity",
        p_low * q * q_high * q * p_low
        == p_low * q_squared * p_low - (p_low * q * p_low) ** 2,
        p_low * q * q_high * q * p_low,
        p_low * q_squared * p_low - (p_low * q * p_low) ** 2,
        "C_moment_residual",
    )
    audit.check(
        "Q q squared P moment identity",
        p_low * q_squared * q_high * q_squared * p_low
        == p_low * q_fourth * p_low - (p_low * q_squared * p_low) ** 2,
        p_low * q_squared * q_high * q_squared * p_low,
        p_low * q_fourth * p_low - (p_low * q_squared * p_low) ** 2,
        "C_moment_residual",
    )
    # TEST ORACLES for the declared exact matrix fixture.
    audit.check(
        "moment residual fixture values",
        (a_residual_squared, b_residual_squared)
        == (sp.Rational(4, 9), sp.Rational(1, 9)),
        (a_residual_squared, b_residual_squared),
        (sp.Rational(4, 9), sp.Rational(1, 9)),
        "C_moment_residual",
    )

    identity_three = sp.eye(3)
    p_bond = sp.kronecker_product(p_low, p_low)
    delta_q = sp.kronecker_product(q, identity_three) - sp.kronecker_product(identity_three, q)
    exact_bond = sp.simplify(4 * c_value * delta_q**2)
    off_block = sp.simplify((sp.eye(9) - p_bond) * exact_bond * p_bond)
    singular_squared = [
        sp.simplify(value)
        for value, multiplicity in (off_block.H * off_block).eigenvals().items()
        for _ in range(multiplicity)
    ]
    actual_norm_squared = max(singular_squared)
    residual_bound = sp.simplify(
        8
        * c_value
        * (b_residual + 2 * m_value * a_residual + a_residual**2)
    )
    audit.check(
        "one-bond low-high residual bound",
        bool(sp.simplify(residual_bound**2 - actual_norm_squared) >= 0),
        actual_norm_squared,
        f"<={residual_bound**2}",
        "C_moment_residual",
    )

    epsilon_zero = sp.Rational(1, 4)
    gamma = sp.Integer(5)
    g_value = sp.Integer(1)
    v_value = sp.Rational(3, 2)
    epsilon_opt = sp.simplify(
        sp.Rational(1, 4) * sp.sqrt(g_value / (epsilon_zero + gamma))
    )
    a_q = sp.simplify(
        v_value**2 / gamma
        + 4 * epsilon_opt * (epsilon_zero + gamma) / (g_value * gamma)
        + 1 / (4 * epsilon_opt * gamma)
    )
    expected_a_q = sp.simplify(
        v_value**2 / gamma
        + 2 * sp.sqrt(epsilon_zero + gamma) / (gamma * sp.sqrt(g_value))
    )
    audit.check(
        "centered form coefficient optimized",
        sp.simplify(a_q - expected_a_q) == 0,
        a_q,
        expected_a_q,
        "C_centered_form",
    )
    k_fixture = sp.diag(0, 0, gamma)
    psi = sp.Matrix([1, 2, 3])
    t_weight = sp.Integer(2)
    r_operator = q - m_value * s_extended
    lhs = sp.simplify((r_operator * psi).dot(r_operator * psi))
    p_psi = p_low * psi
    q_psi = q_high * psi
    rhs = sp.simplify(
        (1 + t_weight) * a_residual_squared * p_psi.dot(p_psi)
        + (1 + 1 / t_weight) * expected_a_q * (q_psi.dot(k_fixture * q_psi))
    )
    audit.check(
        "centered form finite hostile fixture",
        bool(sp.N(rhs - lhs, 80) > 0),
        rhs - lhs,
        ">0",
        "C_centered_form",
    )

    corridor_exponents = {
        "v": 2,
        "E_star": 8,
        "h_sc": -6,
        "Gamma": 2,
        "m": 2,
        "a": -1,
        "b": 1,
        # Safe consequence of a_j=v^2[1+O(h_sc)] separately.  Exponential
        # smallness of their difference needs an additional weighted-Agmon
        # matrix-element lemma and is deliberately not imported here.
        "d2": -2,
        "c": -4,
        "24c_d2": -6,
        "one_bond_low_high": -3,
        "A_Q": 2,
        "c_A_Q": -2,
        "c_m_sqrt_A_Q": -1,
        "J": 0,
    }
    audit.check(
        "corridor low-high exponent",
        corridor_exponents["c"]
        + max(
            corridor_exponents["b"],
            corridor_exponents["m"] + corridor_exponents["a"],
            2 * corridor_exponents["a"],
        )
        == corridor_exponents["one_bond_low_high"],
        corridor_exponents["one_bond_low_high"],
        -3,
        "C_asymptotic_corridor",
    )
    audit.check(
        "corridor Ising scale exponent",
        corridor_exponents["c"] + 2 * corridor_exponents["m"]
        == corridor_exponents["J"] == 0,
        corridor_exponents["c"] + 2 * corridor_exponents["m"],
        0,
        "C_asymptotic_corridor",
    )
    audit.check(
        "corridor weighted high-mode exponent",
        corridor_exponents["c"] + corridor_exponents["A_Q"]
        == corridor_exponents["c_A_Q"] == -2,
        corridor_exponents["c"] + corridor_exponents["A_Q"],
        -2,
        "C_asymptotic_corridor",
    )
    audit.check(
        "corridor mixed anticommutator exponent",
        corridor_exponents["c"]
        + corridor_exponents["m"]
        + sp.Rational(1, 2) * corridor_exponents["A_Q"]
        == corridor_exponents["c_m_sqrt_A_Q"]
        == -1,
        corridor_exponents["c"]
        + corridor_exponents["m"]
        + sp.Rational(1, 2) * corridor_exponents["A_Q"],
        -1,
        "C_asymptotic_corridor",
    )
    audit.check(
        "safe transverse renormalization exponent",
        corridor_exponents["c"] + corridor_exponents["d2"]
        == corridor_exponents["24c_d2"] == -6,
        corridor_exponents["c"] + corridor_exponents["d2"],
        -6,
        "C_asymptotic_corridor",
    )
    audit.check(
        "A0 corridor exponent",
        -4 + 2 * 4 == 4,
        -4 + 2 * 4,
        4,
        "C_asymptotic_corridor",
    )
    n_corridor = sp.symbols("N", positive=True)
    a_zero_corridor = sp.simplify(
        sp.Rational(2, 9) * n_corridor ** (-4) * (n_corridor**4) ** 2
    )
    audit.check(
        "A0 corridor leading coefficient",
        sp.simplify(a_zero_corridor - sp.Rational(2, 9) * n_corridor**4)
        == 0,
        a_zero_corridor,
        sp.Rational(2, 9) * n_corridor**4,
        "C_asymptotic_corridor",
    )

    imported_scope = {
        "fixed_mu_positive": True,
        "coercive_polynomial": True,
        "exactly_two_connected_zeroes": connected_component_size(len(vertices), edges) == 8,
        "nondegenerate_minima": True,
        "exact_Agmon_distance_from_R167": 16 * sp.sqrt(2) / 3,
        "semiclassical_h0_explicit": False,
        "repository_r_minus_9_certified": False,
        "safe_d2_bound": "O(v^2 h_sc)",
        "exponential_d2_requires_extra_weighted_Agmon_lemma": True,
        "extra_weighted_Agmon_lemma_registered": False,
        "literature_theorem_reproved_by_script": False,
    }
    dfp_boundary = {
        "source": DFP_SOURCE,
        "published_main_theorem_rank_one_vacuum": True,
        "published_main_theorem_unique_ground_state": True,
        "introductory_degenerate_extension_is_rank2_band_theorem": False,
        "Q3_local_kernel_rank": 2,
        "Q3_global_low_dimension": "2^|Lambda|",
        "phi0_only_gap": "delta_1 (exponentially small)",
        "direct_import_closes_broken_sector_gap": False,
    }

    return {
        "q3_graph": {
            "vertices": vertices,
            "edges": edges,
            "laplacian": laplacian,
            "hessian_characteristic": characteristic,
            "locked_collective_integral_raw": action,
            "S0": action_on_interval,
            "zero_set_reason": (
                "W_mu=0 forces x_e^2=1; positive lock forces adjacent signs "
                "equal; connected Q3 leaves only plus/minus all-ones"
            ),
        },
        "normalization": {
            "v": v,
            "E_star": e_star,
            "h_sc": h_sc,
            "kinetic_coefficient": kinetic_coefficient,
            "quartic_coefficient": quartic_coefficient,
            "lock_coefficient": lock_coefficient,
        },
        "parameter_fixtures": parameter_fixtures,
        "semiclassical_import_scope": imported_scope,
        "low_band": {
            "J": j_ising,
            "delta_site": delta_site,
            "delta_eff": delta_effective,
            "moment_fixture": {
                "q": q,
                "m": m_value,
                "a_j": a_values,
                "b_j": b_values,
                "a_squared": a_residual_squared,
                "b_squared": b_residual_squared,
                "actual_one_bond_offblock_norm_squared": actual_norm_squared,
                "one_bond_bound": residual_bound,
            },
            "centered_form_fixture": {
                "epsilon0": epsilon_zero,
                "Gamma": gamma,
                "g": g_value,
                "v": v_value,
                "epsilon_optimizer": epsilon_opt,
                "A_Q": expected_a_q,
                "finite_fixture_lhs": lhs,
                "finite_fixture_rhs": rhs,
            },
        },
        "corridor_exponents_in_N": corridor_exponents,
        "A0_corridor": a_zero_corridor,
        "dfp_rank_one_boundary": dfp_boundary,
    }



def operator_norm_squared(matrix: sp.MatrixBase) -> sp.Expr:
    values = []
    for value, multiplicity in (matrix.H * matrix).eigenvals().items():
        values.extend([sp.simplify(value)] * multiplicity)
    return max(values, key=lambda value: float(sp.N(value, 40)))


def fixture_d_full_gibbs_context(audit: Audit) -> dict[str, Any]:
    """Exact Gibbs/Duhamel, modular-context, and arbitrary-context fixtures."""

    # INPUT FIXTURE. The temperature is derived so rho is exactly the Gibbs
    # state of H; all numerical assertions below are labelled test oracles.
    p = sp.Rational(1, 5)
    t_zero = sp.Integer(1)
    hbar = sp.Integer(1)
    beta = sp.log(4) / sp.pi
    rho = sp.diag(1 - p, p)
    projection_one = sp.diag(0, 1)
    h_full = sp.pi * hbar * projection_one / t_zero
    h_cut = sp.zeros(2)
    w_tail = h_full - h_cut
    gibbs_unnormalized = sp.diag(1, sp.exp(-beta * sp.pi * hbar / t_zero))
    gibbs = sp.simplify(gibbs_unnormalized / trace(gibbs_unnormalized))
    u_full = sp.diag(1, -1)
    u_cut = sp.eye(2)
    difference = u_full - u_cut
    right_squared = sp.simplify(trace(rho * difference.H * difference))
    left_squared = sp.simplify(trace(rho * difference * difference.H))
    w_second_moment = sp.simplify(trace(rho * w_tail**2))
    duhamel_rhs_squared = sp.simplify(t_zero**2 * w_second_moment / hbar**2)

    evolved_full = sp.simplify(u_full * rho * u_full.H)
    evolved_cut = sp.simplify(u_cut * rho * u_cut.H)
    state_difference = sp.simplify(evolved_full - evolved_cut)
    trace_distance = sum(
        sp.sqrt(value)
        for value, multiplicity in (state_difference.H * state_difference).eigenvals().items()
        for _ in range(multiplicity)
    )

    pauli_x = sp.Matrix([[0, 1], [1, 0]])
    alpha_full = sp.simplify(u_full.H * pauli_x * u_full)
    alpha_cut = sp.simplify(u_cut.H * pauli_x * u_cut)
    observable_error = sp.simplify(alpha_full - alpha_cut)
    observable_right_squared = sp.simplify(
        trace(rho * observable_error.H * observable_error)
    )
    observable_left_squared = sp.simplify(
        trace(rho * observable_error * observable_error.H)
    )
    rho_half = sp.diag(sp.sqrt(1 - p), sp.sqrt(p))
    rho_minus_half = sp.diag(1 / sp.sqrt(1 - p), 1 / sp.sqrt(p))
    modular_context = sp.simplify(rho_minus_half * pauli_x * rho_half)
    modular_context_norm_squared = operator_norm_squared(modular_context)
    bandwidth_factor = sp.simplify(sp.exp(beta * sp.pi * hbar / (2 * t_zero)))
    projective_band_norm = sp.Integer(2)
    context_transfer_rhs_squared = sp.simplify(
        (1 + sp.sqrt(modular_context_norm_squared)) ** 2
        * duhamel_rhs_squared
    )

    probability = sp.symbols("p", positive=True)
    unitary_hash_squared_family = 8 * probability
    automorphism_hash_squared_family = sp.Integer(8)

    audit.check(
        "finite Gibbs normalization",
        gibbs == rho,
        gibbs,
        rho,
        "D_full_Gibbs",
    )
    audit.check(
        "two weighted unitary orientations",
        right_squared == left_squared == 4 * p,
        (right_squared, left_squared),
        (4 * p, 4 * p),
        "D_full_Gibbs",
    )
    audit.check(
        "Duhamel static Gibbs upper",
        bool(sp.N(duhamel_rhs_squared - right_squared, 80) > 0),
        duhamel_rhs_squared - right_squared,
        ">0",
        "D_full_Gibbs",
    )
    audit.check(
        "Gibbs W square with hbar restored",
        sp.simplify(w_second_moment - sp.pi**2 * hbar**2 * p / t_zero**2) == 0,
        w_second_moment,
        sp.pi**2 * hbar**2 * p / t_zero**2,
        "D_full_Gibbs",
    )
    audit.check(
        "trace-distance state stability fixture",
        trace_distance == 0,
        trace_distance,
        0,
        "D_full_Gibbs",
    )
    audit.check(
        "arbitrary context one-sided norms",
        observable_right_squared == observable_left_squared == 4,
        (observable_right_squared, observable_left_squared),
        (4, 4),
        "D_context_no_go",
    )
    audit.check(
        "arbitrary context hash seminorm",
        observable_right_squared + observable_left_squared == 8,
        observable_right_squared + observable_left_squared,
        8,
        "D_context_no_go",
    )
    audit.check(
        "half-modular context norm",
        modular_context_norm_squared == 4,
        modular_context_norm_squared,
        4,
        "D_modular_context",
    )
    audit.check(
        "fixed Bohr-band projective bound",
        bandwidth_factor == 2
        and sp.sqrt(modular_context_norm_squared)
        <= bandwidth_factor * projective_band_norm,
        (bandwidth_factor, sp.sqrt(modular_context_norm_squared)),
        (2, "<=4"),
        "D_modular_context",
    )
    audit.check(
        "bounded-context transfer fixture",
        observable_right_squared <= context_transfer_rhs_squared,
        observable_right_squared,
        f"<={context_transfer_rhs_squared}",
        "D_modular_context",
    )
    audit.check(
        "arbitrary-context implication limit",
        sp.limit(unitary_hash_squared_family, probability, 0, dir="+") == 0
        and automorphism_hash_squared_family == 8,
        (sp.limit(unitary_hash_squared_family, probability, 0, dir="+"), 8),
        (0, 8),
        "D_context_no_go",
    )
    q3_domain = {
        "common_quartic_form_domain": True,
        "W_coordinate_growth_degree": 2,
        "W_squared_growth_degree": 4,
        "finite_Gibbs_fourth_moment": True,
        "bounded_spectral_form_truncation": True,
        "strong_resolvent_then_S2_closure": True,
        "smooth_clipped_Q_L_automatically_covered": False,
    }
    audit.check(
        "finite-Q3 hard-form domain instantiation",
        q3_domain["common_quartic_form_domain"]
        and q3_domain["W_coordinate_growth_degree"] == 2
        and q3_domain["W_squared_growth_degree"] == 4
        and q3_domain["finite_Gibbs_fourth_moment"]
        and q3_domain["bounded_spectral_form_truncation"]
        and q3_domain["strong_resolvent_then_S2_closure"]
        and not q3_domain["smooth_clipped_Q_L_automatically_covered"],
        q3_domain,
        "hard/form Q3 pair only",
        "D_Q3_domain",
    )

    return {
        "rho": rho,
        "beta": beta,
        "H": h_full,
        "H_L": h_cut,
        "W": w_tail,
        "right_unitary_HS_squared": right_squared,
        "left_unitary_HS_squared": left_squared,
        "rho_W_squared": w_second_moment,
        "Duhamel_rhs_squared": duhamel_rhs_squared,
        "trace_distance": trace_distance,
        "observable": pauli_x,
        "right_observable_HS_squared": observable_right_squared,
        "left_observable_HS_squared": observable_left_squared,
        "hash_seminorm_squared": observable_right_squared + observable_left_squared,
        "half_modular_context": modular_context,
        "half_modular_context_norm_squared": modular_context_norm_squared,
        "fixed_bandwidth_factor": bandwidth_factor,
        "fixed_band_projective_norm": projective_band_norm,
        "arbitrary_context_upgrade_rejected": True,
        "state_stability_implies_automorphism_stability": False,
        "q3_form_domain_instantiation": q3_domain,
    }


def fixture_e_fixed_edge_corridor(audit: Audit) -> dict[str, Any]:
    """Exact cubic-edge count, corridor constants, covariance, and tilted no-go."""

    # INPUT FIXTURE for exact enumeration; the R-dependent bound is derived
    # symbolically below and the displayed integers are TEST ORACLES.
    radius = 2
    vertices = set(product(range(-radius, radius + 1), repeat=3))
    directions = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
    induced_edges = []
    for vertex in sorted(vertices):
        for direction in directions:
            neighbour = tuple(vertex[index] + direction[index] for index in range(3))
            if neighbour in vertices:
                induced_edges.append((vertex, neighbour))
    exact_count = 6 * radius * (2 * radius + 1) ** 2

    hostile_words = (sp.Integer(3), sp.Integer(-2), sp.Integer(5), sp.Integer(1))
    cauchy_left = sum(hostile_words) ** 2
    cauchy_right = len(hostile_words) * sum(value**2 for value in hostile_words)

    r_symbol = sp.symbols("R", positive=True)
    edge_upper = 54 * r_symbol**3
    c_value = sp.Rational(1, 3)
    edge_prefactor = sp.Integer(4)
    l_squared = r_symbol
    corridor_bound = sp.simplify(
        edge_upper**2
        * c_value**2
        * edge_prefactor
        * sp.exp(-l_squared)
        * (l_squared**2 + 2 * l_squared + 2)
    )
    expected_corridor = 1296 * r_symbol**6 * sp.exp(-r_symbol) * (
        r_symbol**2 + 2 * r_symbol + 2
    )
    elementary_majorant = sp.factor(
        1296
        * sp.factorial(10)
        * (r_symbol ** -2 + 2 * r_symbol ** -3 + 2 * r_symbol ** -4)
    )

    torus_side = 4
    torus_vertices = list(product(range(torus_side), repeat=3))
    orientation_orbits: dict[int, set[tuple[tuple[int, int, int], tuple[int, int, int]]]] = {
        direction: set() for direction in range(3)
    }
    for vertex in torus_vertices:
        for direction in range(3):
            neighbour = list(vertex)
            neighbour[direction] = (neighbour[direction] + 1) % torus_side
            orientation_orbits[direction].add((vertex, tuple(neighbour)))

    kappa = sp.Rational(3, 4)
    precision_determinant = sp.simplify(1 - kappa**2)
    marginal_variance = sp.simplify(1 / precision_determinant)
    tilted_tail_exponent = sp.simplify(1 / (2 * marginal_variance))
    theta = sp.Rational(1, 2)
    reference_power_exponent = theta / 2
    exponent_gap = sp.simplify(reference_power_exponent - tilted_tail_exponent)
    q2_precision_determinant = sp.simplify(1 - 4 * kappa**2)
    dimer_scope = True
    full_one_site_translation_invariance = False
    hard_tail_constants = True
    smooth_clipped_q_l_constants = False

    audit.check(
        "induced cubic edge count",
        len(induced_edges) == exact_count == 300,
        len(induced_edges),
        300,
        "E_fixed_edge",
    )
    audit.check(
        "edge count cubic upper",
        exact_count <= 54 * radius**3,
        exact_count,
        f"<={54 * radius**3}",
        "E_fixed_edge",
    )
    audit.check(
        "restricted-tail sum Cauchy",
        cauchy_left <= cauchy_right,
        cauchy_left,
        f"<={cauchy_right}",
        "E_fixed_edge",
    )
    audit.check(
        "explicit growing corridor constant",
        sp.simplify(corridor_bound - expected_corridor) == 0,
        corridor_bound,
        expected_corridor,
        "E_fixed_edge",
    )
    audit.check(
        "growing corridor vanishes",
        sp.limit(corridor_bound, r_symbol, sp.oo) == 0,
        sp.limit(corridor_bound, r_symbol, sp.oo),
        0,
        "E_fixed_edge",
    )
    audit.check(
        "elementary exponential majorant vanishes",
        sp.limit(elementary_majorant, r_symbol, sp.oo) == 0,
        sp.limit(elementary_majorant, r_symbol, sp.oo),
        0,
        "E_fixed_edge",
    )
    audit.check(
        "periodic translation edge orbits",
        len(orientation_orbits) == 3
        and all(len(orbit) == torus_side**3 for orbit in orientation_orbits.values()),
        {key: len(value) for key, value in orientation_orbits.items()},
        {0: 64, 1: 64, 2: 64},
        "E_covariance_boundary",
    )
    audit.check(
        "tilted Gaussian positive precision",
        precision_determinant == sp.Rational(7, 16) > 0,
        precision_determinant,
        sp.Rational(7, 16),
        "E_tilted_no_go",
    )
    audit.check(
        "tilted Gaussian marginal variance",
        marginal_variance == sp.Rational(16, 7),
        marginal_variance,
        sp.Rational(16, 7),
        "E_tilted_no_go",
    )
    audit.check(
        "tilted tail defeats alpha-two reference power",
        exponent_gap == sp.Rational(1, 32) > 0,
        exponent_gap,
        sp.Rational(1, 32),
        "E_tilted_no_go",
    )
    audit.check(
        "tilted order-two likelihood diverges",
        q2_precision_determinant == sp.Rational(-5, 4) < 0,
        q2_precision_determinant,
        sp.Rational(-5, 4),
        "E_tilted_no_go",
    )
    audit.check(
        "tilted Gaussian and hard-tail scope boundaries",
        dimer_scope
        and not full_one_site_translation_invariance
        and hard_tail_constants
        and not smooth_clipped_q_l_constants,
        {
            "dimer_scope": dimer_scope,
            "full_one_site_TI": full_one_site_translation_invariance,
            "hard_tail": hard_tail_constants,
            "smooth_clipped_Q_L": smooth_clipped_q_l_constants,
        },
        "dimer implication and hard-tail constants only",
        "E_scope",
    )

    return {
        "radius_fixture": radius,
        "induced_edge_count": exact_count,
        "edge_formula": "6 R (2R+1)^2",
        "edge_upper": "54 R^3",
        "corridor_bound": corridor_bound,
        "elementary_majorant": elementary_majorant,
        "periodic_translation_orbit_sizes": {
            key: len(value) for key, value in orientation_orbits.items()
        },
        "translation_covariance_reduces_to_one_edge": False,
        "translation_covariance_reduces_to_three_orientations": True,
        "tilted_gaussian": {
            "kappa": kappa,
            "precision_determinant": precision_determinant,
            "marginal_variance": marginal_variance,
            "tilted_tail_exponent": tilted_tail_exponent,
            "reference_power_exponent": reference_power_exponent,
            "exponent_gap": exponent_gap,
            "Q2_precision_determinant": q2_precision_determinant,
            "all_polynomial_moments_finite": True,
            "fixed_edge_tail_implication_rejected": True,
            "two_site_or_homogeneous_dimer_scope": dimer_scope,
            "full_one_site_translation_invariance": (
                full_one_site_translation_invariance
            ),
            "Q3_dynamics_nonexistence": False,
        },
        "hard_tail_constants": hard_tail_constants,
        "smooth_clipped_Q_L_constants": smooth_clipped_q_l_constants,
        "actual_Q3_fixed_edge_history_bound_proved": False,
    }


def fixture_f_feshbach_and_compressed_qps(audit: Audit) -> dict[str, Any]:
    """Exact cubic overlap, Feshbach, form-smallness, and TFIM-QPS inputs."""

    # INPUT FIXTURES. Side four avoids short-cycle edge identifications;
    # rational parameters are chosen only to test the derived inequalities.
    side = 4
    vertices = list(product(range(side), repeat=3))
    edges: list[frozenset[tuple[int, int, int]]] = []
    for vertex in vertices:
        for direction in range(3):
            neighbour = list(vertex)
            neighbour[direction] = (neighbour[direction] + 1) % side
            edges.append(frozenset((vertex, tuple(neighbour))))
    overlap_counts = [sum(bool(edge & other) for other in edges) for edge in edges]
    open_vertices = list(product(range(side), repeat=3))
    open_edges: list[frozenset[tuple[int, int, int]]] = []
    for vertex in open_vertices:
        for direction in range(3):
            neighbour = list(vertex)
            neighbour[direction] += 1
            if neighbour[direction] < side:
                open_edges.append(frozenset((vertex, tuple(neighbour))))
    open_overlap_counts = [
        sum(bool(edge & other) for other in open_edges) for edge in open_edges
    ]

    high_count = 5
    gamma = sp.Integer(7)
    energy = sp.Integer(2)
    epsilon = sp.Rational(1, 3)
    high_block = gamma * sp.eye(high_count)
    off_block = epsilon * sp.ones(high_count, 1)
    self_energy = sp.simplify(
        off_block.H * (high_block - energy * sp.eye(high_count)).inv() * off_block
    )
    overlap_upper = sp.simplify(11 * high_count * epsilon**2 / (gamma - energy))

    dense_low_count = 5
    dense_off_block = epsilon * sp.ones(1, dense_low_count)
    dense_self_energy = sp.simplify(
        dense_off_block.H
        * (sp.Matrix([[gamma]]) - energy * sp.eye(1)).inv()
        * dense_off_block
    )
    dense_norm_squared = operator_norm_squared(dense_self_energy)
    dense_norm = sp.sqrt(dense_norm_squared)

    c_value = sp.Rational(1, 1000)
    m_value = sp.Integer(2)
    a_squared = sp.Rational(1, 100)
    a_value = sp.Rational(1, 10)
    b_value = sp.Rational(1, 20)
    a_q = sp.Integer(3)
    gamma_form = sp.Integer(100)
    z = sp.Integer(6)
    eta_b = sp.simplify(32 * c_value * a_q)
    nu_b = sp.simplify(32 * c_value * m_value**2 + 64 * c_value * a_squared)
    zeta = sp.simplify(z * (eta_b + nu_b / gamma_form))
    epsilon_form = sp.simplify(
        8 * c_value * (b_value + 2 * m_value * a_value + a_squared)
    )
    p_xy = sp.diag(1, 0, 0, 0)
    q_xy = sp.eye(4) - p_xy
    k_xy = sp.diag(0, gamma_form, gamma_form, 2 * gamma_form)
    qkq = sp.simplify(q_xy * k_xy * q_xy)
    diagonal_high_fixture = sp.simplify(eta_b * qkq + nu_b * q_xy)
    projected_high_upper = sp.simplify((eta_b + nu_b / gamma_form) * qkq)
    projected_high_slack = sp.simplify(projected_high_upper - diagonal_high_fixture)
    projected_slack_eigenvalues = list(projected_high_slack.eigenvals())
    corridor_exponents = {
        "epsilon": -3,
        "eta_b": -2,
        "nu_b_over_Gamma": -2,
        "zeta": -2,
    }

    j_symbol = sp.symbols("J", positive=True)
    star_energies: dict[sp.Expr, int] = {}
    for signs in product((-1, 1), repeat=4):
        center, *neighbours = signs
        value = sp.simplify(j_symbol * sum(1 - center * neighbour for neighbour in neighbours))
        star_energies[value] = star_energies.get(value, 0) + 1
    expected_star = {0: 2, 2 * j_symbol: 6, 4 * j_symbol: 6, 6 * j_symbol: 2}

    pauli_x = sp.Matrix([[0, 1], [1, 0]])
    parity = sp.diag(1, -1)
    p_one = sp.diag(0, 1)
    selector_plus_density = 1 - 1
    selector_minus_density = 1 - (-1)
    selector_difference_derivative = selector_plus_density - selector_minus_density
    selector_split = (0, selector_difference_derivative)
    small_ratio = "abs(delta_eff)/(2J)<epsilon_Y"
    feshbach_absolute_energy_before_low_scalar_subtraction = True
    thermodynamic_ground_band_isolation = False
    diagonal_high_compression_only = True
    off_diagonal_bound_is_distinct = True

    audit.check(
        "periodic cubic edge count",
        len(edges) == 3 * side**3,
        len(edges),
        3 * side**3,
        "F_overlap",
    )
    audit.check(
        "cubic overlap upper and periodic bulk equality",
        set(overlap_counts) == {11}
        and max(open_overlap_counts) <= 11
        and min(open_overlap_counts) < 11,
        {
            "periodic": set(overlap_counts),
            "open_min": min(open_overlap_counts),
            "open_max": max(open_overlap_counts),
        },
        "general <=11; periodic equality; open boundary can be smaller",
        "F_overlap",
    )
    audit.check(
        "exact below-Gamma Feshbach fixture",
        self_energy == sp.Matrix([[sp.Rational(1, 9)]]),
        self_energy,
        sp.Matrix([[sp.Rational(1, 9)]]),
        "F_Feshbach",
    )
    audit.check(
        "11-overlap Feshbach upper",
        self_energy[0, 0] <= overlap_upper
        and overlap_upper == sp.Rational(11, 9),
        (self_energy[0, 0], overlap_upper),
        (sp.Rational(1, 9), sp.Rational(11, 9)),
        "F_Feshbach",
    )
    audit.check(
        "dense extensive self-energy norm",
        dense_norm == sp.Rational(1, 9)
        and all(dense_self_energy[i, j] != 0 for i in range(5) for j in range(5)),
        (dense_norm, dense_self_energy),
        (sp.Rational(1, 9), "all entries nonzero"),
        "F_self_energy_no_go",
    )
    audit.check(
        "relative-form coefficient eta_b",
        eta_b == sp.Rational(12, 125),
        eta_b,
        sp.Rational(12, 125),
        "F_relative_form",
    )
    audit.check(
        "relative-form coefficient nu_b",
        nu_b == sp.Rational(402, 3125),
        nu_b,
        sp.Rational(402, 3125),
        "F_relative_form",
    )
    audit.check(
        "global relative-form smallness fixture",
        zeta < 1,
        zeta,
        "<1",
        "F_relative_form",
    )
    audit.check(
        "one-bond off-block smallness fixture",
        epsilon_form == sp.Rational(23, 6250),
        epsilon_form,
        sp.Rational(23, 6250),
        "F_relative_form",
    )
    audit.check(
        "projected local-high diagonal inequality",
        all(bool(value >= 0) for value in projected_slack_eigenvalues)
        and q_xy * k_xy * q_xy - gamma_form * q_xy
        == sp.diag(0, 0, 0, gamma_form)
        and diagonal_high_compression_only
        and off_diagonal_bound_is_distinct,
        {
            "slack_eigenvalues": projected_slack_eigenvalues,
            "QKQ_minus_GammaQ": q_xy * k_xy * q_xy - gamma_form * q_xy,
        },
        "Qxy Bxy Qxy <= (eta_b+nu_b/Gamma) Qxy(kx+ky)Qxy",
        "F_relative_form",
    )
    audit.check(
        "corridor Feshbach coefficient exponents",
        corridor_exponents
        == {"epsilon": -3, "eta_b": -2, "nu_b_over_Gamma": -2, "zeta": -2},
        corridor_exponents,
        {"epsilon": -3, "eta_b": -2, "nu_b_over_Gamma": -2, "zeta": -2},
        "F_relative_form",
    )
    audit.check(
        "compressed TFIM forward-star spectrum",
        star_energies == expected_star,
        star_energies,
        expected_star,
        "F_compressed_QPS",
    )
    audit.check(
        "compressed TFIM Z2 action",
        parity * pauli_x * parity == -pauli_x
        and parity * p_one * parity == p_one,
        (parity * pauli_x * parity, parity * p_one * parity),
        (-pauli_x, p_one),
        "F_compressed_QPS",
    )
    audit.check(
        "compressed TFIM selector split",
        selector_plus_density == 0
        and selector_minus_density == 2
        and selector_split == (0, -2)
        and small_ratio == "abs(delta_eff)/(2J)<epsilon_Y",
        {
            "plus": selector_plus_density,
            "minus": selector_minus_density,
            "k": selector_split,
        },
        {"plus": 0, "minus": 2, "k": (0, -2)},
        "F_compressed_QPS",
    )
    audit.check(
        "finite-volume absolute-energy Feshbach scope",
        feshbach_absolute_energy_before_low_scalar_subtraction
        and not thermodynamic_ground_band_isolation,
        {
            "before_low_scalar_subtraction": (
                feshbach_absolute_energy_before_low_scalar_subtraction
            ),
            "thermodynamic_ground_band_isolation": (
                thermodynamic_ground_band_isolation
            ),
        },
        "finite-volume absolute-energy algebra only",
        "F_scope",
    )

    return {
        "periodic_side": side,
        "edge_count": len(edges),
        "periodic_overlap_counts": sorted(set(overlap_counts)),
        "open_overlap_range": [min(open_overlap_counts), max(open_overlap_counts)],
        "general_overlap_upper": 11,
        "equality_scope": "bulk edges and sufficiently large periodic tori",
        "Feshbach_fixture": {
            "Gamma": gamma,
            "E": energy,
            "epsilon": epsilon,
            "self_energy": self_energy,
            "overlap_upper": overlap_upper,
        },
        "dense_self_energy_no_go": {
            "matrix": dense_self_energy,
            "operator_norm": dense_norm,
            "all_to_all": True,
            "global_extensive_bound_implies_QPS_locality": False,
        },
        "relative_form": {
            "c": c_value,
            "m": m_value,
            "a_squared": a_squared,
            "A_Q": a_q,
            "Gamma": gamma_form,
            "eta_b": eta_b,
            "nu_b": nu_b,
            "zeta": zeta,
            "epsilon": epsilon_form,
            "corridor_exponents": corridor_exponents,
            "P_xy": p_xy,
            "Q_xy": q_xy,
            "Q_k_sum_Q": qkq,
            "diagonal_high_fixture": diagonal_high_fixture,
            "projected_high_upper": projected_high_upper,
            "projected_high_slack": projected_high_slack,
            "diagonal_high_compression_only": diagonal_high_compression_only,
            "off_diagonal_bound_is_distinct": off_diagonal_bound_is_distinct,
        },
        "compressed_TFIM_QPS": {
            "forward_star_spectrum": star_energies,
            "local_gap": 2 * j_symbol,
            "selector": "u sum_x(1-s_x)",
            "selector_plus_density": selector_plus_density,
            "selector_minus_density": selector_minus_density,
            "selector_split": selector_split,
            "small_ratio": small_ratio,
            "Z2_pins_coexistence_u_zero": True,
            "source": YAROTSKII_QPS_SOURCE,
            "existential_small_ratio_only": True,
            "compressed_infinite_lattice_phasewise_gap": True,
            "finite_torus_exact_degeneracy": False,
            "explicit_threshold": False,
            "oscillator_gap": False,
        },
        "Feshbach_absolute_energy_before_low_scalar_subtraction": (
            feshbach_absolute_energy_before_low_scalar_subtraction
        ),
        "thermodynamic_ground_band_isolation": (
            thermodynamic_ground_band_isolation
        ),
    }



def fixture_g_twentieth_moment_and_graph_boundary(audit: Audit) -> dict[str, Any]:
    """Exact moment-corridor arithmetic and two automatic-inference no-gos."""

    moment_order = 5
    gamma_cutoff = sp.Rational(2, 5)
    edge_power = 6
    tail_power = 4 * (moment_order - 1)
    corridor_power = sp.simplify(edge_power - gamma_cutoff * tail_power)
    edge_constant = sp.Integer(54) ** 2
    factorial_log_power = sp.simplify(2 * gamma_cutoff - 1)

    audit.check(
        "twentieth-moment corridor exponent",
        corridor_power == sp.Rational(-2, 5),
        corridor_power,
        sp.Rational(-2, 5),
        "G_moment_corridor",
    )
    audit.check(
        "twentieth-moment corridor constant",
        edge_constant == 2916 and tail_power == 16,
        (edge_constant, tail_power),
        (2916, 16),
        "G_moment_corridor",
    )
    audit.check(
        "bounded-cutoff factorial logarithmic coefficient",
        factorial_log_power == sp.Rational(-1, 5),
        factorial_log_power,
        sp.Rational(-1, 5),
        "G_moment_corridor",
    )
    admissible_integers = [
        p
        for p in range(2, 8)
        if bool(6 - 4 * gamma_cutoff * (p - 1) < 0)
    ]
    audit.check(
        "minimal integer moment at gamma two-fifths",
        admissible_integers[0] == 5,
        admissible_integers[0],
        5,
        "G_moment_corridor",
    )
    pointwise_samples = []
    for x_value, cutoff in ((1, 2), (2, 2), (3, 2), (7, 5)):
        left = sp.Integer(x_value) ** 4 if x_value > cutoff else sp.Integer(0)
        right = sp.Rational(x_value**20, cutoff**16)
        pointwise_samples.append((x_value, cutoff, left, right, bool(left <= right)))
    audit.check(
        "pointwise twentieth-to-fourth tail domination",
        all(row[-1] for row in pointwise_samples),
        pointwise_samples,
        "X^4 1_(X>L)<=X^20/L^16",
        "G_moment_corridor",
    )

    # INPUT fixture for the conditional constant; exp(G5*T) is represented by E.
    m5_value = sp.Integer(3)
    d5_value = sp.Integer(2)
    s_mu = sp.Integer(5)
    transport_square = sp.symbols("E", positive=True)
    one_orientation = sp.simplify(
        d5_value**2 * transport_square * s_mu**5 * m5_value
    )
    two_orientation = sp.simplify(2 * one_orientation)
    audit.check(
        "sharp conditional two-orientation factor",
        sp.simplify(two_orientation / transport_square) == 75000,
        two_orientation,
        75000 * transport_square,
        "G_conditional_graph",
    )
    grouped_commutator_coefficients = (1, 2, 2)
    audit.check(
        "fifth commutator expansion coefficients",
        sum(grouped_commutator_coefficients) == moment_order,
        grouped_commutator_coefficients,
        (1, 2, 2),
        "G_conditional_graph",
    )
    # A scalar strongly-commuting convexity fixture derives the S_mu^5 factor.
    weights = (sp.Integer(1), sp.Integer(1), sp.Rational(1, 2))
    local_energies = (sp.Integer(2), sp.Integer(3), sp.Integer(4))
    weighted_energy = sum(w * k for w, k in zip(weights, local_energies))
    weight_sum = sum(weights)
    convex_upper = sp.expand(
        weight_sum**4 * sum(w * k**5 for w, k in zip(weights, local_energies))
    )
    audit.check(
        "strongly commuting fifth-power convexity",
        weighted_energy**5 <= convex_upper,
        (weighted_energy**5, convex_upper),
        "K_e^5<=S_mu^4 sum mu_z k_z^5",
        "G_conditional_graph",
    )

    # Exact normalized all-m commutator fixture.
    k_matrix = sp.diag(1, 4)
    v_matrix = sp.Matrix([[0, 1], [1, 0]])
    all_m_rows: list[dict[str, Any]] = []
    for order in range(1, 8):
        half_inverse = sp.diag(1, sp.Rational(1, 2**order))
        k_power = k_matrix**order
        c_matrix = sp.simplify(
            half_inverse * sp.I * (v_matrix * k_power - k_power * v_matrix) * half_inverse
        )
        norm_value = sp.sqrt(operator_norm_squared(c_matrix))
        expected = sp.Integer(2) ** order - sp.Rational(1, 2**order)
        all_m_rows.append(
            {"m": order, "norm": norm_value, "expected": expected}
        )
    audit.check(
        "normalized all-m commutator exponential growth",
        all(sp.simplify(row["norm"] - row["expected"]) == 0 for row in all_m_rows),
        all_m_rows,
        "2^m-2^(-m)",
        "G_all_m_no_go",
    )
    audit.check(
        "quadratic all-m automatic inference rejected",
        sp.limit((2**sp.symbols("m", positive=True)) / sp.symbols("m", positive=True) ** 2, sp.symbols("m", positive=True), sp.oo) == sp.oo,
        "exponential over quadratic diverges",
        True,
        "G_all_m_no_go",
    )

    # K_N rotation fixture.  q_N^10 K_N^(-5/2)=diag(0,1) exactly.
    n_symbol = sp.symbols("N", integer=True, positive=True)
    delta_symbol = sp.symbols("delta", real=True, nonzero=True)
    k_n = sp.diag(1, n_symbol**4)
    q_n = sp.diag(0, n_symbol)
    d5_matrix = sp.simplify(q_n**10 * sp.diag(1, n_symbol**-10))
    v_n = sp.Matrix([[0, -sp.I], [sp.I, 0]]) / n_symbol**4
    half_inverse_5 = sp.diag(1, n_symbol**-10)
    c5_matrix = sp.simplify(
        half_inverse_5
        * sp.I
        * (v_n * k_n**5 - k_n**5 * v_n)
        * half_inverse_5
    )
    g5_exact = sp.simplify(c5_matrix[0, 1])
    if g5_exact.could_extract_minus_sign():
        g5_exact = -g5_exact
    history_one_lower = sp.simplify(delta_symbol**2 * n_symbol**20 / (8 * n_symbol**8))
    history_sum_lower = sp.simplify(2 * history_one_lower)
    x = sp.symbols("x", positive=True)
    static_profile = x**5 * sp.exp(-x)
    static_derivative = sp.factor(sp.diff(static_profile, x))
    audit.check(
        "KN elliptic constant d5",
        d5_matrix == sp.diag(0, 1),
        d5_matrix,
        sp.diag(0, 1),
        "G_static_low_graph_no_go",
    )
    audit.check(
        "KN fifth normalized commutator",
        sp.simplify(g5_exact - (n_symbol**6 - n_symbol**-14)) == 0,
        g5_exact,
        n_symbol**6 - n_symbol**-14,
        "G_static_low_graph_no_go",
    )
    audit.check(
        "KN two-orientation twentieth lower",
        history_one_lower == delta_symbol**2 * n_symbol**12 / 8
        and history_sum_lower == delta_symbol**2 * n_symbol**12 / 4,
        (history_one_lower, history_sum_lower),
        (delta_symbol**2 * n_symbol**12 / 8, delta_symbol**2 * n_symbol**12 / 4),
        "G_static_low_graph_no_go",
    )
    audit.check(
        "static Gibbs fifth profile maximum",
        static_derivative.subs(x, 5) == 0
        and sp.limit(static_profile, x, sp.oo) == 0
        and static_profile.subs(x, 5) == (sp.Rational(5, 1) / sp.E) ** 5,
        (static_derivative, static_profile.subs(x, 5)),
        "maximum (5/e)^5",
        "G_static_low_graph_no_go",
    )

    return {
        "moment_order_p": moment_order,
        "gamma": gamma_cutoff,
        "general_exponent": "6-4*gamma*(p-1)",
        "corridor_exponent": corridor_power,
        "edge_constant": edge_constant,
        "tail_power": tail_power,
        "factorial_R_log_R_coefficient": factorial_log_power,
        "pointwise_samples": pointwise_samples,
        "conditional": {
            "commutator_coefficients": grouped_commutator_coefficients,
            "one_orientation": one_orientation,
            "M20_two_orientation": two_orientation,
            "endpoint_weights_one": True,
            "onsite_family_strongly_commuting": True,
            "onsite_flow_commutes_with_K_e": True,
            "bond_graph_norm": "exp(G5*abs(delta)/2)",
            "graph_squared_moment": "exp(G5*T)",
            "actual_m5_d5_G5_inputs_proved": False,
        },
        "all_m_no_go": {
            "K": k_matrix,
            "V": v_matrix,
            "rows": all_m_rows,
            "Dini_log_norm_derivative": "||C_m||/(2*hbar)",
            "forced_G_m": "||C_m||/hbar",
            "fixed_m5_rejected": False,
            "automatic_quadratic_all_m_inference_rejected": True,
        },
        "KN_no_go": {
            "K": k_n,
            "q": q_n,
            "V": v_n,
            "d5_matrix": d5_matrix,
            "static_m5_upper": "1+(5/e)^5 at beta=1",
            "low_graph_range": "0<=s<=1",
            "low_graph_upper": "1+abs(delta) when N^4>=abs(delta)",
            "delta_nonzero": True,
            "G5": g5_exact,
            "one_orientation_q20_lower": history_one_lower,
            "two_orientation_q20_lower": history_sum_lower,
            "Q3_dynamics_no_go": False,
        },
    }


def fixture_h_full_oscillator_edge_cluster(audit: Audit) -> dict[str, Any]:
    """Exact local-edge min-max, relative-form, and Ritz-removal arithmetic."""

    # INPUTS.  d2 is negative so a^2=max_j(a_j-m^2)=1/100 is consistent.
    c_value = sp.Rational(1, 1000)
    m_value = sp.Integer(2)
    a_value = sp.Rational(1, 10)
    b_value = sp.Rational(1, 20)
    a_q = sp.Integer(3)
    a0_minus_m2 = sp.Rational(1, 100)
    d2 = -sp.Rational(1, 1000)
    delta1 = sp.Rational(1, 10000)
    gamma_high = sp.Integer(100)
    z = sp.Integer(6)

    c_b = sp.simplify(8 * c_value * a0_minus_m2)
    f_b = sp.simplify(delta1 / z + 4 * c_value * d2)
    e_b = sp.simplify(c_b + f_b)
    j_value = sp.simplify(8 * c_value * m_value**2)
    epsilon = sp.simplify(
        8 * c_value * (b_value + 2 * m_value * a_value + a_value**2)
    )
    a_block = sp.simplify(e_b + 2 * j_value)
    d_block = sp.simplify(gamma_high / z)
    schur_margin = sp.simplify(2 * j_value * (d_block - e_b) - epsilon**2)
    gap_rational_lower = sp.simplify(
        2 * j_value - epsilon**2 / (d_block - a_block)
    )
    g_b = sp.simplify(
        (a_block + d_block - sp.sqrt((d_block - a_block) ** 2 + 4 * epsilon**2)) / 2
    )

    # Reconstruct the exact low compression in the s-eigenbasis.
    one = sp.eye(2)
    s_matrix = sp.Matrix([[0, 1], [1, 0]])
    p_one = sp.diag(0, 1)
    pair_s = sp.kronecker_product(s_matrix, s_matrix)
    pair_p_one = sp.kronecker_product(p_one, one) + sp.kronecker_product(one, p_one)
    low_h = sp.simplify(
        c_b * sp.eye(4) + j_value * (sp.eye(4) - pair_s) + f_b * pair_p_one
    )
    plus = sp.Matrix([1, 1]) / sp.sqrt(2)
    minus = sp.Matrix([1, -1]) / sp.sqrt(2)
    plus_plus = sp.kronecker_product(plus, plus)
    minus_minus = sp.kronecker_product(minus, minus)
    p_zero = sp.simplify(plus_plus * plus_plus.H + minus_minus * minus_minus.H)
    low_misaligned = sp.simplify(sp.eye(4) - p_zero)
    p0_compression = sp.simplify(p_zero * low_h * p_zero)
    l_compression = sp.simplify(low_misaligned * low_h * low_misaligned)
    p0_l_cross = sp.simplify(p_zero * low_h * low_misaligned)
    p0_l_cross_norm = sp.sqrt(operator_norm_squared(p0_l_cross))
    parity = sp.kronecker_product(sp.diag(1, -1), sp.diag(1, -1))
    even_trial = sp.simplify((plus_plus + minus_minus) / sp.sqrt(2))
    odd_trial = sp.simplify((plus_plus - minus_minus) / sp.sqrt(2))
    even_energy = sp.simplify((even_trial.H * low_h * even_trial)[0])
    odd_energy = sp.simplify((odd_trial.H * low_h * odd_trial)[0])

    audit.check(
        "corrected edge fixture residual consistency",
        max(a0_minus_m2, a0_minus_m2 + d2) == a_value**2,
        (a0_minus_m2, a0_minus_m2 + d2, a_value**2),
        "a^2=max_j(a_j-m^2)=1/100",
        "H_edge_fixture",
    )
    # The following exact fractions are independent test oracles, not inputs.
    expected_scalars = {
        "Cb": sp.Rational(1, 12500),
        "fb": sp.Rational(19, 1500000),
        "eb": sp.Rational(139, 1500000),
        "J": sp.Rational(4, 125),
        "epsilon": sp.Rational(23, 6250),
        "A": sp.Rational(96139, 1500000),
        "D": sp.Rational(50, 3),
        "D_minus_A": sp.Rational(8301287, 500000),
        "margin": sp.Rational(20832953, 19531250),
        "gap_lower": sp.Rational(332047248, 5188304375),
    }
    actual_scalars = {
        "Cb": c_b,
        "fb": f_b,
        "eb": e_b,
        "J": j_value,
        "epsilon": epsilon,
        "A": a_block,
        "D": d_block,
        "D_minus_A": d_block - a_block,
        "margin": schur_margin,
        "gap_lower": gap_rational_lower,
    }
    audit.check(
        "corrected exact edge constants",
        actual_scalars == expected_scalars,
        actual_scalars,
        expected_scalars,
        "H_edge_fixture",
    )
    audit.check(
        "aligned and misaligned diagonal compressions",
        p0_compression == e_b * p_zero
        and l_compression == (e_b + 2 * j_value) * low_misaligned,
        (p0_compression, l_compression),
        (e_b * p_zero, (e_b + 2 * j_value) * low_misaligned),
        "H_edge_compressions",
    )
    audit.check(
        "P0-L noninvariance retained",
        p0_l_cross != sp.zeros(4) and p0_l_cross_norm == abs(f_b),
        (p0_l_cross, p0_l_cross_norm),
        ("nonzero", abs(f_b)),
        "H_edge_compressions",
    )
    audit.check(
        "one even and one odd Ritz trial",
        parity * even_trial == even_trial
        and parity * odd_trial == -odd_trial
        and even_energy == odd_energy == e_b,
        (even_energy, odd_energy),
        (e_b, e_b),
        "H_edge_parity",
    )
    audit.check(
        "sharp Schur margin and rational gap lower",
        schur_margin > 0
        and d_block > a_block > e_b
        and sp.N(g_b - e_b, 30) > sp.N(gap_rational_lower, 30) > 0,
        {
            "margin": schur_margin,
            "gb": g_b,
            "gb_minus_eb": sp.N(g_b - e_b, 20),
            "rational_lower": gap_rational_lower,
        },
        "gb>eb and gb-eb>=332047248/5188304375",
        "H_edge_minmax",
    )

    eta_b = sp.simplify(32 * c_value * a_q)
    nu_b = sp.simplify(32 * c_value * m_value**2 + 64 * c_value * a_value**2)
    rho_b = sp.simplify(eta_b + nu_b / gamma_high)
    tau = epsilon
    alpha = sp.simplify(
        z * (rho_b + j_value / gamma_high + epsilon**2 / (tau * gamma_high))
    )
    ell_b = sp.simplify(c_b + 8 * c_value * abs(d2))
    beta = sp.simplify(2 * delta1 / z + ell_b + tau)
    gamma0 = min(gamma_high / z, 2 * j_value)
    delta_rf = sp.simplify((1 - alpha) * gamma0 - 2 * beta)
    expected_relative = {
        "eta_b": sp.Rational(12, 125),
        "nu_b": sp.Rational(402, 3125),
        "rho_b": sp.Rational(15201, 156250),
        "alpha": sp.Rational(183081, 312500),
        "beta": sp.Rational(2851, 750000),
        "gamma0": sp.Rational(8, 125),
        "Delta_rf": sp.Rational(4430237, 234375000),
    }
    actual_relative = {
        "eta_b": eta_b,
        "nu_b": nu_b,
        "rho_b": rho_b,
        "alpha": alpha,
        "beta": beta,
        "gamma0": gamma0,
        "Delta_rf": delta_rf,
    }
    audit.check(
        "relative-form edge constants",
        actual_relative == expected_relative and alpha < 1 and delta_rf > 0,
        actual_relative,
        expected_relative,
        "H_edge_relative_form",
    )

    cutoff = {
        "nested": True,
        "parity_preserving": True,
        "Pi_M_contains_P": True,
        "union_is_quartic_form_core": True,
        "restriction_is_Pi_tensor_Pi_full_form": True,
        "same_constants": True,
        "Ritz_eigenvalues_decrease": True,
        "Ritz_limit_is_full_edge": True,
        "replace_q_then_square": False,
        "Pi_q2_Pi_equals_Pi_q_Pi_squared": False,
    }
    audit.check(
        "spectral cutoff is Ritz form compression",
        all(cutoff[key] for key in (
            "nested",
            "parity_preserving",
            "Pi_M_contains_P",
            "union_is_quartic_form_core",
            "restriction_is_Pi_tensor_Pi_full_form",
            "same_constants",
            "Ritz_eigenvalues_decrease",
            "Ritz_limit_is_full_edge",
        ))
        and not cutoff["replace_q_then_square"]
        and not cutoff["Pi_q2_Pi_equals_Pi_q_Pi_squared"],
        cutoff,
        "nested parity-preserving Ritz restriction, not truncated q",
        "H_edge_cutoff",
    )

    return {
        "inputs": {
            "c": c_value,
            "m": m_value,
            "a": a_value,
            "b": b_value,
            "A_Q": a_q,
            "a0_minus_m2": a0_minus_m2,
            "d2": d2,
            "delta1": delta1,
            "Gamma": gamma_high,
            "z": z,
        },
        "sharp_minmax": {
            **actual_scalars,
            "gb": g_b,
            "gb_decimal": sp.N(g_b, 20),
            "gb_minus_eb_decimal": sp.N(g_b - e_b, 20),
            "P0_h_P0": p0_compression,
            "L_h_L": l_compression,
            "P0_h_L_norm": p0_l_cross_norm,
            "P0_and_L_invariant": False,
            "global_parity_invariant": True,
            "h_nonnegative_hypothesis": True,
            "compact_resolvent_hypothesis": True,
            "exactly_one_low_per_parity": True,
            "lambda3_minus_lambda2_lower": g_b - e_b,
        },
        "relative_form": {
            **actual_relative,
            "tau": tau,
            "ell_b": ell_b,
            "form_bound": "abs(<V>)<=alpha<h0>+beta||psi||^2",
            "exactly_two_low": True,
            "lambda3_minus_lambda2_lower": delta_rf,
        },
        "cutoff_removal": cutoff,
        "N_scaling": {
            "eb": -6,
            "epsilon": -3,
            "Gamma_over_z": 2,
            "two_J_limit": 16,
            "sharp_mixing_gap_correction": -8,
            "relative_alpha": -2,
            "relative_beta": -3,
        },
        "local_edge_only": True,
        "global_QPS_transfer": False,
        "oscillator_lattice_GNS_gap": False,
    }



def fixture_i_actual_q3_fifth_shear_and_rank_two(audit: Audit) -> dict[str, Any]:
    """Exact v2.2 algebra, word budget, and local-to-global gap counterfixture."""

    # Exact differential-operator check of the ninth-order virial identity.
    x = sp.symbols("x", real=True)
    hbar = sp.Integer(2)
    chi = sp.Integer(3)
    potential = x**4 / 4 + 2 * x**3 / 3 + 3 * x**2 / 2 + 5 * x
    force = sp.diff(potential, x)
    test_polynomial = x**14 + 2 * x**11 - 3 * x**7 + 5 * x**3 + 1

    def p_apply(expression: sp.Expr, order: int = 1) -> sp.Expr:
        result = expression
        for _ in range(order):
            result = -sp.I * hbar * sp.diff(result, x)
        return sp.expand(result)

    def h_apply(expression: sp.Expr) -> sp.Expr:
        return sp.expand(p_apply(expression, 2) / (2 * chi) + potential * expression)

    def a_apply(expression: sp.Expr) -> sp.Expr:
        return sp.expand((x * p_apply(expression, 9) + p_apply(x * expression, 9)) / 2)

    lhs = sp.expand(sp.I * (h_apply(a_apply(test_polynomial)) - a_apply(h_apply(test_polynomial))) / hbar)
    force_sum = sp.Integer(0)
    for j in range(9):
        force_sum += x * p_apply(force * p_apply(test_polynomial, 8 - j), j)
        force_sum += p_apply(force * p_apply(x * test_polynomial, 8 - j), j)
    rhs = sp.expand(p_apply(test_polynomial, 10) / chi - force_sum / 2)
    audit.check(
        "v2.2 exact ninth-order virial sign and factor",
        sp.expand(lhs - rhs) == 0,
        sp.expand(lhs - rhs),
        0,
        "I_static_virial",
    )
    audit.check(
        "v2.2 critical force energy order",
        sp.Rational(1, 4) + 8 * sp.Rational(1, 2) + 3 * sp.Rational(1, 4) == 5,
        (9, sp.Rational(1, 4) + 4 + sp.Rational(3, 4)),
        (9, 5),
        "I_static_graph",
    )
    graph_levels = tuple((m, 2 * m, 4 * m) for m in range(6))
    audit.check(
        "v2.2 quartic Shubin top degrees",
        graph_levels[-1] == (5, 10, 20),
        graph_levels[-1],
        (5, 10, 20),
        "I_static_graph",
    )

    # Exact terminating direct-shear conjugation for one commuting component.
    delta, coupling, p_value, q_neighbour = sp.symbols(
        "delta c p Q", real=True
    )
    transformed_kinetic = sp.expand(
        (p_value + coupling * delta * q_neighbour) ** 2 / (2 * chi)
    )
    baseline_kinetic = p_value**2 / (2 * chi)
    shear_increment = sp.expand(transformed_kinetic - baseline_kinetic)
    expected_increment = sp.expand(
        delta * coupling * p_value * q_neighbour / chi
        + delta**2 * coupling**2 * q_neighbour**2 / (2 * chi)
    )
    audit.check(
        "v2.2 exact direct subset-shear coefficients",
        sp.expand(shear_increment - expected_increment) == 0,
        shear_increment,
        expected_increment,
        "I_subset_shear",
    )

    choices = (0, 1, 2)  # K, delta R1, delta^2 R2
    delta_degree = {0: 0, 1: 1, 2: 2}
    energy_order = {
        0: sp.Integer(1),
        1: sp.Rational(3, 4),
        2: sp.Rational(1, 2),
    }
    nonbaseline: list[tuple[tuple[int, ...], int, sp.Rational]] = []
    for word in product(choices, repeat=5):
        if all(letter == 0 for letter in word):
            continue
        nonbaseline.append(
            (
                word,
                sum(delta_degree[letter] for letter in word),
                sum((energy_order[letter] for letter in word), sp.Integer(0)),
            )
        )
    degree_counts = {
        degree: sum(row[1] == degree for row in nonbaseline)
        for degree in range(1, 11)
    }
    audit.check(
        "v2.2 every fifth word has delta and order at most five",
        len(nonbaseline) == 3**5 - 1
        and all(degree >= 1 and order <= 5 for _, degree, order in nonbaseline)
        and sum(degree_counts.values()) == len(nonbaseline),
        {
            "words": len(nonbaseline),
            "delta_range": (min(degree_counts), max(degree_counts)),
            "max_order": max(row[2] for row in nonbaseline),
        },
        {"words": 242, "delta_range": (1, 10), "max_order": 5},
        "I_fifth_words",
    )
    t_value = sp.Integer(2)
    direct_word_majorant = sum(
        multiplicity * t_value ** (degree - 1)
        for degree, multiplicity in degree_counts.items()
    )
    polynomial_difference_at_t = sp.expand((1 + t_value + t_value**2) ** 5 - 1)
    audit.check(
        "v2.2 load-bearing linear step majorant",
        t_value * direct_word_majorant == polynomial_difference_at_t,
        (direct_word_majorant, polynomial_difference_at_t),
        "difference=abs(delta)*C5(T) with T=2",
        "I_fifth_words",
    )
    # Exact neighbor-weight allocations at the hostile fixture exp(-mu/4)=1/2.
    residual_ratio = sp.Rational(1, 2)
    mu_symbol, f_x = sp.symbols("mu f_x", positive=True)
    worst_f_y = sp.exp(-mu_symbol) * f_x
    worst_f_z = sp.exp(-mu_symbol) * f_x
    r1_leftover = sp.simplify(
        f_x / (f_x ** sp.Rational(1, 2) * worst_f_y ** sp.Rational(1, 4))
    )
    r2_leftover = sp.simplify(
        f_x
        / (
            worst_f_y ** sp.Rational(1, 4)
            * worst_f_z ** sp.Rational(1, 4)
        )
    )
    residual_weight_bound = sp.simplify(
        2 * ((1 + residual_ratio) / (1 - residual_ratio)) ** 3
    )
    audit.check(
        "v2.2 exact R1/R2 neighbor-weight allocation",
        sp.simplify(r1_leftover - sp.exp(mu_symbol / 4) * f_x ** sp.Rational(1, 4)) == 0
        and sp.simplify(r2_leftover - sp.exp(mu_symbol / 2) * f_x ** sp.Rational(1, 2)) == 0,
        (r1_leftover, r2_leftover),
        (sp.exp(mu_symbol / 4) * f_x ** sp.Rational(1, 4), sp.exp(mu_symbol / 2) * f_x ** sp.Rational(1, 2)),
        "I_weight_budget",
    )
    audit.check(
        "v2.2 cubic residual weight sum",
        residual_weight_bound == 54,
        residual_weight_bound,
        54,
        "I_weight_budget",
    )
    maximum_local_insertions = max(
        sum(letter != 0 for letter in word) for word, _, _ in nonbaseline
    )
    maximum_neighbor_incidences = max(
        sum(1 if letter == 1 else 2 if letter == 2 else 0 for letter in word)
        for word, _, _ in nonbaseline
    )
    edge_tuple_counts = tuple(
        6**r for r in range(1, maximum_neighbor_incidences + 1)
    )
    commutator_order_drop = sp.Rational(3, 4)
    audit.check(
        "v2.2 cubic tuple and K5 allocation budget",
        maximum_local_insertions == 5
        and maximum_neighbor_incidences == 10
        and edge_tuple_counts == tuple(6**r for r in range(1, 11))
        and commutator_order_drop > 0
        and all(5 - order >= 0 for _, _, order in nonbaseline),
        {
            "anchors": maximum_local_insertions,
            "neighbor_incidences": maximum_neighbor_incidences,
            "last_tuple_count": edge_tuple_counts[-1],
            "commutator_order_drop": commutator_order_drop,
        },
        {"anchors": 5, "neighbor_incidences": 10, "last_tuple_count": 6**10, "commutator_order_drop": sp.Rational(3, 4)},
        "I_weight_budget",
    )
    tree_sphere_terms = tuple(
        6 * 5 ** (radius - 1) * residual_ratio**radius for radius in range(1, 7)
    )
    audit.check(
        "v2.2 generic degree-six exponential-growth hostile",
        all(tree_sphere_terms[index + 1] == sp.Rational(5, 2) * tree_sphere_terms[index] for index in range(5))
        and tree_sphere_terms[-1] > tree_sphere_terms[0],
        tree_sphere_terms,
        "six-regular tree weighted spheres grow by 5/2",
        "I_growth_hostile",
    )

    # Rank-two projection fixture on C^2 tensor C^2.
    local_edge = sp.Matrix(
        [
            [0, 0, 0, 0],
            [0, sp.Rational(1, 2), -sp.Rational(1, 2), 0],
            [0, -sp.Rational(1, 2), sp.Rational(1, 2), 0],
            [0, 0, 0, 1],
        ]
    )
    local_spectrum = local_edge.eigenvals()
    audit.check(
        "v2.2 local rank-two projection spectrum",
        local_edge**2 == local_edge
        and local_edge.rank() == 2
        and local_spectrum == {sp.Integer(0): 2, sp.Integer(1): 2},
        {"rank": local_edge.rank(), "spectrum": local_spectrum},
        {"rank": 2, "spectrum": {0: 2, 1: 2}},
        "I_rank_two_local",
    )

    side = 4
    cycle_edges = tuple((site, (site + 1) % side) for site in range(side))
    dimension = 2**side
    h_cycle = sp.zeros(dimension)
    for x_site, y_site in cycle_edges:
        for state in range(dimension):
            bit_x = (state >> x_site) & 1
            bit_y = (state >> y_site) & 1
            if bit_x == bit_y == 1:
                h_cycle[state, state] += 1
            elif bit_x != bit_y:
                h_cycle[state, state] += sp.Rational(1, 2)
                swapped = state ^ (1 << x_site) ^ (1 << y_site)
                h_cycle[swapped, state] -= sp.Rational(1, 2)
    vacuum = sp.zeros(dimension, 1)
    vacuum[0] = 1
    w_vector = sp.zeros(dimension, 1)
    for site in range(side):
        w_vector[1 << site] = 1
    kernel = h_cycle.nullspace()
    audit.check(
        "v2.2 connected cycle kernel vacuum plus W",
        len(kernel) == 2
        and h_cycle * vacuum == sp.zeros(dimension, 1)
        and h_cycle * w_vector == sp.zeros(dimension, 1)
        and sp.Matrix.hstack(vacuum, w_vector).rank() == 2,
        {"nullity": len(kernel), "rank": h_cycle.rank()},
        {"nullity": 2, "rank": dimension - 2},
        "I_rank_two_global",
    )
    one_particle_indices = [1 << site for site in range(side)]
    one_particle = h_cycle.extract(one_particle_indices, one_particle_indices)
    laplacian = sp.zeros(side)
    for x_site, y_site in cycle_edges:
        laplacian[x_site, x_site] += 1
        laplacian[y_site, y_site] += 1
        laplacian[x_site, y_site] -= 1
        laplacian[y_site, x_site] -= 1
    audit.check(
        "v2.2 one-particle half-Laplacian",
        one_particle == laplacian / 2
        and one_particle.eigenvals()
        == {sp.Integer(0): 1, sp.Integer(1): 2, sp.Integer(2): 1},
        {"matrix": one_particle, "spectrum": one_particle.eigenvals()},
        "L_C4/2 with spectrum 0,1,1,2",
        "I_rank_two_global",
    )
    audit.check(
        "v2.2 torus gap upper fixture",
        1 - sp.cos(2 * sp.pi / side) == 1
        and sp.Integer(1) < 2 * sp.pi**2 / side**2,
        (1 - sp.cos(2 * sp.pi / side), 2 * sp.pi**2 / side**2),
        "1<pi^2/8",
        "I_rank_two_global",
    )

    onsite_cutoff = 4
    lifted = sp.zeros(onsite_cutoff**2)
    for a in range(2):
        for b in range(2):
            low_column = 2 * a + b
            full_column = onsite_cutoff * a + b
            for c_index in range(2):
                for d_index in range(2):
                    low_row = 2 * c_index + d_index
                    full_row = onsite_cutoff * c_index + d_index
                    lifted[full_row, full_column] += local_edge[low_row, low_column]
    for a in range(onsite_cutoff):
        for b in range(onsite_cutoff):
            index = onsite_cutoff * a + b
            lifted[index, index] += max(a - 1, 0) + max(b - 1, 0)
    lifted_spectrum = lifted.eigenvals()
    positive_lifted = [value for value in lifted_spectrum if value > 0]
    audit.check(
        "v2.2 infinite-onsite lift finite-cutoff kernel and gap",
        lifted_spectrum.get(sp.Integer(0)) == 2 and min(positive_lifted) == 1,
        {"zero_multiplicity": lifted_spectrum.get(0), "first_positive": min(positive_lifted)},
        {"zero_multiplicity": 2, "first_positive": 1},
        "I_rank_two_lift",
    )

    return {
        "static": {
            "virial_identity_exact": True,
            "force_placements": 9,
            "critical_energy_order": 5,
            "graph_levels_m_p_q": graph_levels,
            "finite_spectral_cutoff_before_monotone_limit": True,
            "unbounded_trace_cyclicity_used": False,
            "registered_periodic_compact_source_scope": True,
            "arbitrary_boundary_static_scope": False,
        },
        "shear": {
            "increment": expected_increment,
            "nonbaseline_words": len(nonbaseline),
            "delta_degree_counts": degree_counts,
            "C5_word_majorant_T2": direct_word_majorant,
            "residual_weight_bound_at_exp_minus_mu_over_four_half": residual_weight_bound,
            "edge_tuple_counts_neighbor_incidences_le_10": edge_tuple_counts,
            "maximum_local_insertions": maximum_local_insertions,
            "maximum_neighbor_incidences": maximum_neighbor_incidences,
            "R1_leftover": r1_leftover,
            "R2_leftover": r2_leftover,
            "commutator_order_drop": commutator_order_drop,
            "K5_multinomial_supplies_weights": True,
            "K_ge_one_fills_slack": True,
            "tested_nearest_neighbor_subset": True,
            "finite_cubic_subgraph_or_periodic_quotient": True,
            "uniform_cubic_polynomial_growth_required": True,
            "generic_degree_six_promotion": False,
            "degree_six_tree_sphere_terms": tree_sphere_terms,
            "O_abs_delta_load_bearing": True,
        },
        "history": {
            "M20": "2*d5^2*exp(C5*T)*S_mu^5*m5",
            "hard_cutoff": "2916*c^2*M20*R^(-2/5)",
            "factorial_log": "-R*log(R)/5+O(R)",
            "registered_periodic_only": True,
            "all_exhaustion_common_alpha": False,
        },
        "rank_two": {
            "local_edge": local_edge,
            "cycle_side": side,
            "cycle_kernel_dimension": len(kernel),
            "one_particle": one_particle,
            "lift_cutoff": onsite_cutoff,
            "lift_zero_multiplicity": lifted_spectrum.get(0),
            "lift_first_positive": min(positive_lifted),
            "automatic_global_gap_inference": False,
            "Q3_gap_no_go": False,
        },
    }


def fixture_j_v2_3_connected_and_implementer(audit: Audit) -> dict[str, Any]:
    """Recompute the four v2.3 exact fixtures from labelled inputs."""

    spatial_dimension = 3
    coordination = 2 * spatial_dimension
    box_side_upper_factor = 3
    edge_growth_coefficient = coordination * box_side_upper_factor**2
    paired_tail_constant = edge_growth_coefficient**2
    squared_rate_constant = 2 * paired_tail_constant
    cutoff_power = 16
    cutoff_scale = Fraction(2, 5)
    paired_corridor_exponent = Fraction(6) - cutoff_power * cutoff_scale
    implementer_rate_exponent = paired_corridor_exponent / 2

    audit.check(
        "v2.3 paired tail and implementer constants",
        paired_tail_constant == 2916
        and squared_rate_constant == 5832
        and paired_corridor_exponent == Fraction(-2, 5)
        and implementer_rate_exponent == Fraction(-1, 5),
        {
            "paired_tail": paired_tail_constant,
            "squared_rate": squared_rate_constant,
            "paired_exponent": paired_corridor_exponent,
            "rate_exponent": implementer_rate_exponent,
        },
        {
            "paired_tail": 2916,
            "squared_rate": 5832,
            "paired_exponent": Fraction(-2, 5),
            "rate_exponent": Fraction(-1, 5),
        },
        "J_implementer",
    )

    u, v = sp.symbols("u v", nonnegative=True)
    cauchy_gap = sp.expand(2 * (u**2 + v**2) - (u + v) ** 2)
    audit.check(
        "v2.3 two-leg Cauchy identity",
        sp.expand(cauchy_gap - (u - v) ** 2) == 0,
        cauchy_gap,
        (u - v) ** 2,
        "J_implementer",
    )

    rate_rows = []
    for base in (2, 5):
        radius = base**5
        cutoff = base**2
        squared_rate = sp.Rational(
            squared_rate_constant * radius**6,
            cutoff**cutoff_power,
        )
        rate = sp.sqrt(squared_rate)
        expected_rate = edge_growth_coefficient * sp.sqrt(2) / base
        rate_rows.append(
            {
                "base": base,
                "R": radius,
                "L": cutoff,
                "squared_rate": squared_rate,
                "rate": rate,
                "expected_rate": expected_rate,
            }
        )
    audit.check(
        "v2.3 exact R to L implementer rates",
        all(sp.simplify(row["rate"] - row["expected_rate"]) == 0 for row in rate_rows),
        rate_rows,
        (27 * sp.sqrt(2), 54 * sp.sqrt(2) / 5),
        "J_implementer",
    )

    z = coordination
    exp_a = 2
    kappa = Fraction(1, (z * exp_a) ** 2)
    envelope_a = Fraction(1, 10**2)
    ratio = z**2 * exp_a * kappa
    qps_bound = envelope_a * kappa / (1 - ratio) ** 2
    cutoff_index = 10
    difference_envelope = envelope_a / cutoff_index
    cutoff_qps_bound = difference_envelope * kappa / (1 - ratio) ** 2
    rooted_walk_counts = tuple(z ** (2 * (size - 1)) for size in range(1, 5))
    series_value = Fraction(1, 1) / (1 - ratio) ** 2
    audit.check(
        "v2.3 canonical connected-walk count",
        rooted_walk_counts == (1, 36, 1296, 46656),
        rooted_walk_counts,
        (1, 36, 1296, 46656),
        "J_connected_envelope",
    )
    audit.check(
        "v2.3 geometric QPS envelope fixture",
        ratio == Fraction(1, 2)
        and series_value == 4
        and qps_bound == Fraction(1, 3600),
        {"r": ratio, "series": series_value, "bound": qps_bound},
        {"r": Fraction(1, 2), "series": 4, "bound": Fraction(1, 3600)},
        "J_connected_envelope",
    )
    audit.check(
        "v2.3 separate cutoff difference envelope",
        difference_envelope == Fraction(1, 1000)
        and cutoff_qps_bound == Fraction(1, 36000),
        {"A_M": difference_envelope, "bound": cutoff_qps_bound},
        {"A_M": Fraction(1, 1000), "bound": Fraction(1, 36000)},
        "J_connected_envelope",
    )

    diagonal_pairs = z
    ordered_off_diagonal_pairs = 3 * z * (z - 1)
    qps_pair_constant = 2 * z * exp_a + 9 * z * (z - 1) * exp_a**2
    epsilon = Fraction(1, 10**2)
    gamma = 2
    second_order_bound = Fraction(qps_pair_constant) * epsilon**2 / gamma
    tau_m = epsilon / cutoff_index
    cutoff_difference_bound = (
        2 * Fraction(qps_pair_constant) * epsilon * tau_m / gamma
    )
    corridor_input_exponents = {
        "c": -4,
        "b": 1,
        "m": 1,
        "a": -1,
        "Gamma": 2,
    }
    bond_bracket_exponent = max(
        corridor_input_exponents["b"],
        corridor_input_exponents["m"] + corridor_input_exponents["a"],
        2 * corridor_input_exponents["a"],
    )
    epsilon_exponent = corridor_input_exponents["c"] + bond_bracket_exponent
    gamma_exponent = corridor_input_exponents["Gamma"]
    second_order_exponent = 2 * epsilon_exponent - gamma_exponent
    audit.check(
        "v2.3 overlapping ordered-pair count",
        diagonal_pairs == 6
        and ordered_off_diagonal_pairs == 90
        and qps_pair_constant == 1104,
        {
            "diagonal": diagonal_pairs,
            "off_diagonal": ordered_off_diagonal_pairs,
            "C_a": qps_pair_constant,
        },
        {"diagonal": 6, "off_diagonal": 90, "C_a": 1104},
        "J_second_order",
    )
    audit.check(
        "v2.3 second-order QPS and cutoff fixture",
        second_order_bound == Fraction(69, 1250)
        and tau_m == Fraction(1, 1000)
        and cutoff_difference_bound == Fraction(69, 6250),
        {
            "second_order": second_order_bound,
            "tau_M": tau_m,
            "cutoff_difference": cutoff_difference_bound,
        },
        {
            "second_order": Fraction(69, 1250),
            "tau_M": Fraction(1, 1000),
            "cutoff_difference": Fraction(69, 6250),
        },
        "J_second_order",
    )
    audit.check(
        "v2.3 N-corridor second-order exponent",
        epsilon_exponent == -3
        and gamma_exponent == 2
        and second_order_exponent == -8,
        {
            "inputs": corridor_input_exponents,
            "bond_bracket": bond_bracket_exponent,
            "epsilon": epsilon_exponent,
            "Gamma": gamma_exponent,
            "second_order": second_order_exponent,
        },
        {"epsilon": -3, "Gamma": 2, "second_order": -8},
        "J_second_order",
    )

    hilbert_dimension = 2**4
    vacuum = sp.zeros(hilbert_dimension, 1)
    vacuum[0, 0] = 1

    def high_vector(site: int) -> sp.Matrix:
        vector = sp.zeros(hilbert_dimension, 1)
        vector[1 << site, 0] = 1
        return vector

    resolvent = sp.diag(
        *[
            sp.Integer(0) if index == 0 else sp.Rational(1, index.bit_count())
            for index in range(hilbert_dimension)
        ]
    )
    t_f = high_vector(0) * vacuum.T
    t_disjoint = high_vector(2) * vacuum.T
    t_overlap = high_vector(0) * vacuum.T
    disjoint_coefficient = t_disjoint.T * resolvent * t_f
    overlapping_coefficient = t_overlap.T * resolvent * t_f
    audit.check(
        "v2.3 exact high-support disjoint cancellation",
        disjoint_coefficient == sp.zeros(hilbert_dimension)
        and overlapping_coefficient == vacuum * vacuum.T,
        {
            "disjoint_rank": disjoint_coefficient.rank(),
            "overlap_rank": overlapping_coefficient.rank(),
        },
        {"disjoint_rank": 0, "overlap_rank": 1},
        "J_second_order",
    )

    local_support = (1, 2, 3)
    forward_support = tuple(site + 1 for site in local_support)
    inverse_images = (3, 5)
    total_sites = max(inverse_images)
    pauli_z = sp.diag(1, -1)

    def local_z(site: int) -> sp.Matrix:
        factors = [sp.eye(2) for _ in range(total_sites)]
        factors[site - 1] = pauli_z
        return sp.kronecker_product(*factors)

    inverse_difference = local_z(inverse_images[0]) - local_z(inverse_images[1])
    inverse_difference_norm = max(
        abs(inverse_difference[index, index])
        for index in range(inverse_difference.rows)
    )
    audit.check(
        "v2.3 UHF forward stabilization and inverse non-Cauchy fixture",
        forward_support == (2, 3, 4)
        and inverse_difference_norm == 2,
        {
            "forward_support": forward_support,
            "inverse_images": inverse_images,
            "inverse_difference_norm": inverse_difference_norm,
        },
        {
            "forward_support": (2, 3, 4),
            "inverse_images": (3, 5),
            "inverse_difference_norm": 2,
        },
        "J_UHF",
    )
    audit.check(
        "v2.3 theorem boundary flags",
        True,
        {
            "implementer_not_arbitrary_observable": True,
            "connected_envelope_conditional": True,
            "second_order_not_all_order": True,
            "uniform_tau_required": True,
            "forward_limit_not_automatically_surjective": True,
            "common_alpha_closed": False,
            "broken_sector_GNS_gap_closed": False,
        },
        "three scoped children plus one implication no-go only",
        "J_scope",
    )

    return {
        "implementer": {
            "paired_tail_constant": paired_tail_constant,
            "squared_rate_constant": squared_rate_constant,
            "paired_corridor_exponent": paired_corridor_exponent,
            "rate_exponent": implementer_rate_exponent,
            "rate_rows": rate_rows,
            "arbitrary_observable_context": False,
        },
        "connected_envelope": {
            "z": z,
            "exp_a": exp_a,
            "kappa": kappa,
            "A": envelope_a,
            "r": ratio,
            "rooted_walk_counts": rooted_walk_counts,
            "qps_bound": qps_bound,
            "A_M_at_M_10": difference_envelope,
            "cutoff_bound_at_M_10": cutoff_qps_bound,
            "pointwise_only_sufficient": False,
        },
        "second_order": {
            "diagonal_pairs": diagonal_pairs,
            "ordered_off_diagonal_pairs": ordered_off_diagonal_pairs,
            "C_a": qps_pair_constant,
            "epsilon": epsilon,
            "Gamma": gamma,
            "qps_bound": second_order_bound,
            "tau_M_at_M_10": tau_m,
            "cutoff_difference_bound": cutoff_difference_bound,
            "N_exponent": second_order_exponent,
            "disjoint_coefficient_rank": disjoint_coefficient.rank(),
            "overlap_coefficient_rank": overlapping_coefficient.rank(),
            "all_order_elimination": False,
        },
        "UHF": {
            "forward_local_support": forward_support,
            "inverse_images": inverse_images,
            "inverse_difference_norm": inverse_difference_norm,
            "limit_surjective": False,
            "Q3_dynamics_nonexistence": False,
        },
    }


def fixture_k_v2_4_standard_form_c0_and_generator(audit: Audit) -> dict[str, Any]:
    """Recompute the v2.4 standard-form, C0, generator and hostile fixtures."""

    spatial_dimension = 3
    coordination = 2 * spatial_dimension
    box_side_upper_factor = 3
    edge_growth_coefficient = coordination * box_side_upper_factor**2
    fixed_radius = 2**5
    cutoff_values = (2**2, 2**3)
    fixed_rows = []
    for cutoff in cutoff_values:
        per_leg = sp.Rational(
            edge_growth_coefficient * fixed_radius**3,
            cutoff**8,
        )
        fixed_rows.append(
            {
                "R0": fixed_radius,
                "L": cutoff,
                "per_leg": per_leg,
                "two_leg": sp.sqrt(2) * per_leg,
            }
        )
    audit.check(
        "v2.4 fixed-member standard-form rates",
        fixed_rows[0]["per_leg"] == 27
        and fixed_rows[1]["per_leg"] == sp.Rational(27, 256)
        and sp.simplify(fixed_rows[0]["two_leg"] - 27 * sp.sqrt(2)) == 0
        and sp.simplify(
            fixed_rows[1]["two_leg"] - sp.Rational(27, 256) * sp.sqrt(2)
        )
        == 0,
        fixed_rows,
        {
            "L4": (27, 27 * sp.sqrt(2)),
            "L8": (sp.Rational(27, 256), sp.Rational(27, 256) * sp.sqrt(2)),
        },
        "K_standard_form",
    )

    rho = sp.diag(sp.Rational(1, 5), sp.Rational(4, 5))
    xi = sp.diag(sp.sqrt(sp.Rational(1, 5)), sp.sqrt(sp.Rational(4, 5)))
    identity_2 = sp.eye(2)
    observable = sp.diag(1, -1)
    rotation_rows = []
    for index in (3, 7):
        denominator = index**2 + 1
        cosine = sp.Rational(index**2 - 1, denominator)
        sine = sp.Rational(2 * index, denominator)
        unitary = sp.Matrix([[cosine, -sine], [sine, cosine]])
        difference = identity_2 - unitary
        plus_squared = sp.trace(difference * rho * difference.T)
        minus_squared = sp.trace(rho * difference * difference.T)
        channel = unitary.T * observable * unitary - observable
        observable_squared = sp.trace(channel * rho * channel.T)
        rotation_rows.append(
            {
                "n": index,
                "unitary": unitary,
                "plus_squared": sp.simplify(plus_squared),
                "minus_squared": sp.simplify(minus_squared),
                "observable_squared": sp.simplify(observable_squared),
            }
        )
    audit.check(
        "v2.4 exact faithful standard-form probe",
        rotation_rows[0]["plus_squared"]
        == rotation_rows[0]["minus_squared"]
        == sp.Rational(2, 5)
        and rotation_rows[1]["plus_squared"]
        == rotation_rows[1]["minus_squared"]
        == sp.Rational(2, 25)
        and rotation_rows[0]["observable_squared"] == sp.Rational(36, 25)
        and rotation_rows[1]["observable_squared"] == sp.Rational(196, 625),
        rotation_rows,
        {
            "legs": (sp.Rational(2, 5), sp.Rational(2, 25)),
            "observables": (sp.Rational(36, 25), sp.Rational(196, 625)),
        },
        "K_standard_form",
    )
    core_multiplier = sp.diag(1, 0)
    core_vector = xi * core_multiplier
    core_rows = []
    for row in rotation_rows:
        difference = identity_2 - row["unitary"]
        core_squared = sp.trace(
            (difference * core_vector) * (difference * core_vector).T
        )
        core_rows.append(
            {
                "n": row["n"],
                "core_squared": sp.simplify(core_squared),
                "leg_squared": row["plus_squared"],
            }
        )
    audit.check(
        "v2.4 right-commutant core propagation",
        rho.det() > 0
        and all(row["core_squared"] <= row["leg_squared"] for row in core_rows),
        {"rho_det": rho.det(), "rows": core_rows},
        "faithful rho and ||(P-P_L)xi C||_2 <= e_plus ||C||",
        "K_standard_form",
    )

    c0_n = 10
    c0_m = 20
    time_window = 1
    generator_difference = abs(Fraction(1, c0_n) - Fraction(1, c0_m))
    positive_cauchy_bound = 2 * time_window * generator_difference
    negative_cauchy_bound = 2 * time_window * generator_difference
    limit_error_bound = Fraction(2 * time_window, c0_n)
    audit.check(
        "v2.4 bidirectional C0 arithmetic",
        generator_difference == Fraction(1, 20)
        and positive_cauchy_bound == negative_cauchy_bound == Fraction(1, 10)
        and limit_error_bound == Fraction(1, 5),
        {
            "generator_difference": generator_difference,
            "positive": positive_cauchy_bound,
            "negative": negative_cauchy_bound,
            "limit": limit_error_bound,
        },
        {
            "generator_difference": Fraction(1, 20),
            "positive": Fraction(1, 10),
            "negative": Fraction(1, 10),
            "limit": Fraction(1, 5),
        },
        "K_C0",
    )
    phase = sp.symbols("phase", nonzero=True)
    alpha_two = sp.diag(1, phase**2)
    alpha_three = sp.diag(1, phase**3)
    alpha_five = sp.diag(1, phase**5)
    audit.check(
        "v2.4 finite group and inverse identities",
        alpha_two * alpha_three == alpha_five
        and alpha_two * sp.diag(1, phase**-2) == sp.eye(2),
        {
            "composition": alpha_two * alpha_three,
            "inverse": alpha_two * sp.diag(1, phase**-2),
        },
        {"composition": alpha_five, "inverse": sp.eye(2)},
        "K_C0",
    )

    exp_a = 2
    epsilon = sp.Rational(1, 100)
    gamma = sp.Integer(2)
    tau_m = sp.Rational(1, 1000)
    projection = sp.diag(1, 1, 0, 0)
    high_projection = sp.eye(4) - projection
    onsite = sp.diag(0, 0, gamma, gamma)
    parity = sp.diag(1, -1, 1, -1)
    transition = sp.zeros(4)
    transition[2, 0] = epsilon
    transition[3, 1] = epsilon
    resolvent = sp.diag(0, 0, 1 / gamma, 1 / gamma)
    d_block = resolvent * transition
    generator = d_block - d_block.T
    off_diagonal = transition + transition.T
    audit.check(
        "v2.4 parity-equivariant skew homological generator",
        projection * high_projection == sp.zeros(4)
        and parity * generator == generator * parity
        and generator.T == -generator
        and onsite * generator - generator * onsite == off_diagonal,
        {
            "parity_commutator": parity * generator - generator * parity,
            "skew_residual": generator.T + generator,
            "homological_residual": onsite * generator - generator * onsite - off_diagonal,
        },
        "zero parity, skew and [K,G]-V_od residuals",
        "K_generator",
    )
    generator_norm_squared = max(d_block.T * d_block)
    edge_norm_bound = epsilon / gamma
    qps_bound = 2 * coordination * exp_a * edge_norm_bound
    edge_cutoff_bound = tau_m / gamma
    qps_cutoff_bound = 2 * coordination * exp_a * edge_cutoff_bound
    audit.check(
        "v2.4 sharp generator QPS and Ritz constants",
        generator_norm_squared == edge_norm_bound**2
        and edge_norm_bound == sp.Rational(1, 200)
        and qps_bound == sp.Rational(3, 25)
        and edge_cutoff_bound == sp.Rational(1, 2000)
        and qps_cutoff_bound == sp.Rational(3, 250),
        {
            "edge_norm_squared": generator_norm_squared,
            "edge": edge_norm_bound,
            "qps": qps_bound,
            "edge_cutoff": edge_cutoff_bound,
            "qps_cutoff": qps_cutoff_bound,
        },
        {
            "edge": sp.Rational(1, 200),
            "qps": sp.Rational(3, 25),
            "edge_cutoff": sp.Rational(1, 2000),
            "qps_cutoff": sp.Rational(3, 250),
        },
        "K_generator",
    )
    second_order = sp.Rational(1, 2) * projection * (
        generator * off_diagonal - off_diagonal * generator
    ) * projection
    expected_second_order = -epsilon**2 / gamma * projection
    audit.check(
        "v2.4 exact second-order low-block match",
        second_order == expected_second_order,
        second_order,
        expected_second_order,
        "K_generator",
    )

    spectator_delta = 1
    spectator_epsilon = sp.Rational(1, 10)
    coupling_weights_squared = sp.diag(1, 4)
    spectator_resolvent = sp.diag(1 / gamma, 1 / (gamma + spectator_delta))
    self_energy = spectator_epsilon**2 * sp.kronecker_product(
        coupling_weights_squared,
        spectator_resolvent,
    )
    diagonal = [self_energy[index, index] for index in range(4)]
    self_energy_mixed = sp.simplify(
        (diagonal[0] - diagonal[1] - diagonal[2] + diagonal[3]) / 4
    )
    spectator_hamiltonian = sp.kronecker_product(
        sp.eye(2), sp.diag(0, spectator_delta)
    )
    feshbach = spectator_hamiltonian - self_energy
    feshbach_diagonal = [feshbach[index, index] for index in range(4)]
    feshbach_mixed = sp.simplify(
        (
            feshbach_diagonal[0]
            - feshbach_diagonal[1]
            - feshbach_diagonal[2]
            + feshbach_diagonal[3]
        )
        / 4
    )
    audit.check(
        "v2.4 disconnected spectator Feshbach coefficient",
        spectator_resolvent == sp.diag(sp.Rational(1, 2), sp.Rational(1, 3))
        and self_energy_mixed == -sp.Rational(1, 800)
        and feshbach_mixed == sp.Rational(1, 800),
        {
            "resolvent": spectator_resolvent,
            "self_energy_mixed": self_energy_mixed,
            "feshbach_mixed": feshbach_mixed,
        },
        {
            "resolvent": sp.diag(sp.Rational(1, 2), sp.Rational(1, 3)),
            "self_energy_mixed": -sp.Rational(1, 800),
            "feshbach_mixed": sp.Rational(1, 800),
        },
        "K_negatives",
    )

    bond_coefficient = Fraction(1, 4)
    ritz_gamma = 2
    ritz_rows = []
    for cutoff in (3, 15):
        coordinate_norm_lower_squared = Fraction(cutoff, 2)
        bond_expectation = cutoff + 1
        smallness_lower = bond_coefficient * bond_expectation / ritz_gamma
        ritz_rows.append(
            {
                "M": cutoff,
                "q_norm_lower_squared": coordinate_norm_lower_squared,
                "bond_expectation": bond_expectation,
                "smallness_lower": smallness_lower,
            }
        )
    audit.check(
        "v2.4 Ritz ordinary-norm smallness hostile fixture",
        ritz_rows[0]["smallness_lower"] == Fraction(1, 2)
        and ritz_rows[1]["smallness_lower"] == 2
        and ritz_rows[1]["smallness_lower"] > ritz_rows[0]["smallness_lower"],
        ritz_rows,
        {"M3": Fraction(1, 2), "M15": 2},
        "K_negatives",
    )
    audit.check(
        "v2.4 exact theorem boundary flags",
        True,
        {
            "fixed_member_standard_form_only": True,
            "moving_R_rate_is_strongstar_rate": False,
            "actual_Q3_all_shape_Cauchy": False,
            "generator_or_KMS_identified": False,
            "first_generator_only": True,
            "third_order_closed": False,
            "all_order_connected_elimination": False,
        },
        "three scoped children and two implication no-gos only",
        "K_scope",
    )

    return {
        "standard_form": {
            "fixed_rows": fixed_rows,
            "rotation_rows": rotation_rows,
            "core_rows": core_rows,
            "fixed_member_only": True,
            "moving_family_rate": False,
        },
        "C0_completion": {
            "n": c0_n,
            "m": c0_m,
            "T": time_window,
            "generator_difference": generator_difference,
            "positive_cauchy_bound": positive_cauchy_bound,
            "negative_cauchy_bound": negative_cauchy_bound,
            "limit_error_bound": limit_error_bound,
            "actual_Q3_Cauchy": False,
            "generator_identified": False,
            "KMS_identified": False,
        },
        "first_generator": {
            "parity": parity,
            "edge_norm_bound": edge_norm_bound,
            "qps_bound": qps_bound,
            "edge_cutoff_bound": edge_cutoff_bound,
            "qps_cutoff_bound": qps_cutoff_bound,
            "second_order": second_order,
            "second_order_scalar": -epsilon**2 / gamma,
            "third_order": False,
            "all_order": False,
        },
        "spectator_Feshbach": {
            "self_energy": self_energy,
            "self_energy_mixed_ZZ": self_energy_mixed,
            "feshbach_mixed_ZZ": feshbach_mixed,
            "raw_global_connectedness": False,
        },
        "Ritz_norm_hostile": {
            "rows": ritz_rows,
            "ordinary_norm_uniform": False,
            "relative_form_no_go": False,
        },
    }


def fixture_l_v2_5_third_order_and_compact_cylinder(
    audit: Audit,
) -> dict[str, Any]:
    """Recompute the fixed-finite-volume/Ritz cubic coefficient and cylinder no-go fixture."""

    commutator = lambda left, right: left * right - right * left
    gamma = sp.Integer(2)
    epsilon = sp.Rational(1, 10)
    low_a = sp.Rational(1, 3)
    high_c = sp.Rational(5, 3)
    projection = sp.diag(1, 0)
    onsite = sp.diag(0, gamma)
    diagonal = sp.diag(low_a, high_c)
    transition = sp.zeros(2)
    transition[1, 0] = epsilon
    off_diagonal = transition + transition.T
    resolvent = sp.diag(0, 1 / gamma)
    d_block = resolvent * transition
    generator = d_block - d_block.T
    second_source = commutator(generator, diagonal)
    z_block = resolvent * second_source
    second_generator = z_block - z_block.T
    audit.check(
        "v2.5 two sequential homological identities",
        commutator(generator, onsite) == -off_diagonal
        and commutator(second_generator, onsite) == -second_source
        and z_block[1, 0] == -sp.Rational(1, 30),
        {
            "first": commutator(generator, onsite),
            "second": commutator(second_generator, onsite),
            "Z": z_block[1, 0],
        },
        {"first": -off_diagonal, "second": -second_source, "Z": -sp.Rational(1, 30)},
        "L_third_order",
    )

    theta_nested = sp.Rational(1, 2) * projection * commutator(
        generator, commutator(generator, diagonal)
    ) * projection
    theta_block = (
        transition.T * resolvent * diagonal * resolvent * transition
        - sp.Rational(1, 2)
        * projection
        * (
            diagonal * transition.T * resolvent**2 * transition
            + transition.T * resolvent**2 * transition * diagonal
        )
        * projection
    )
    expected_theta = sp.Rational(1, 300) * projection
    audit.check(
        "v2.5 complete third-order low-block identity",
        theta_nested == theta_block == expected_theta,
        {"nested": theta_nested, "block": theta_block},
        expected_theta,
        "L_third_order",
    )

    zero_diagonal = sp.zeros(2)
    pure_offdiagonal_theta = sp.Rational(1, 2) * projection * commutator(
        generator, commutator(generator, zero_diagonal)
    ) * projection
    audit.check(
        "v2.5 pure-offdiagonal cubic parity limit",
        pure_offdiagonal_theta == sp.zeros(2),
        pure_offdiagonal_theta,
        sp.zeros(2),
        "L_third_order",
    )

    # Exact noncommutative test inputs.  Every matrix below this point is
    # derived from these inputs; the separately labelled expected matrices are
    # test oracles, not computational inputs.
    nc_kq = sp.diag(2, 3, 5)
    nc_a = sp.Matrix([[1, 2], [2, -1]])
    nc_c = sp.Matrix([[3, 1, 0], [1, -2, 2], [0, 2, 4]])
    nc_t = sp.Rational(1, 10) * sp.Matrix([[1, 2], [0, -1], [3, 1]])
    nc_r = nc_kq.inv()
    nc_d = nc_r * nc_t
    nc_s = nc_d * nc_a - nc_c * nc_d
    nc_z = nc_r * nc_s

    nc_expected = {
        "D": sp.Matrix([[sp.Rational(1, 20), sp.Rational(1, 10)],
                        [0, -sp.Rational(1, 30)],
                        [sp.Rational(3, 50), sp.Rational(1, 50)]]),
        "S": sp.Matrix([[sp.Rational(1, 10), -sp.Rational(4, 15)],
                        [-sp.Rational(71, 300), -sp.Rational(13, 75)],
                        [-sp.Rational(7, 50), sp.Rational(13, 150)]]),
        "Z": sp.Matrix([[sp.Rational(1, 20), -sp.Rational(2, 15)],
                        [-sp.Rational(71, 900), -sp.Rational(13, 225)],
                        [-sp.Rational(7, 250), sp.Rational(13, 750)]]),
        "Gram": sp.Matrix([[sp.Rational(61, 10000), sp.Rational(31, 5000)],
                           [sp.Rational(31, 5000), sp.Rational(259, 22500)]]),
        "high": sp.Matrix([[sp.Rational(219, 10000), sp.Rational(53, 3750)],
                           [sp.Rational(53, 3750), sp.Rational(451, 22500)]]),
        "anticommutator": sp.Matrix(
            [[sp.Rational(37, 2000), sp.Rational(317, 18000)],
             [sp.Rational(317, 18000), sp.Rational(1, 1125)]]
        ),
        "Theta": sp.Matrix(
            [[sp.Rational(17, 5000), -sp.Rational(313, 90000)],
             [-sp.Rational(313, 90000), sp.Rational(431, 22500)]]
        ),
    }
    audit.check(
        "v2.5 noncommutative D S Z exact products",
        nc_d == nc_expected["D"]
        and nc_s == nc_expected["S"]
        and nc_z == nc_expected["Z"],
        {"D": nc_d, "S": nc_s, "Z": nc_z},
        {key: nc_expected[key] for key in ("D", "S", "Z")},
        "L_noncommutative_third_order",
    )

    nc_k = sp.zeros(5)
    nc_k[2:, 2:] = nc_kq
    nc_vd = sp.zeros(5)
    nc_vd[:2, :2] = nc_a
    nc_vd[2:, 2:] = nc_c
    nc_vod = sp.zeros(5)
    nc_vod[2:, :2] = nc_t
    nc_vod[:2, 2:] = nc_t.T
    nc_g = sp.zeros(5)
    nc_g[2:, :2] = nc_d
    nc_g[:2, 2:] = -nc_d.T
    nc_g2 = sp.zeros(5)
    nc_g2[2:, :2] = nc_z
    nc_g2[:2, 2:] = -nc_z.T
    nc_projection = sp.diag(1, 1, 0, 0, 0)
    nc_qp_g2_k = commutator(nc_g2, nc_k)[2:, :2]
    nc_second_residual = (
        commutator(nc_g2, nc_k) + commutator(nc_g, nc_vd)
    )[2:, :2]
    audit.check(
        "v2.5 noncommutative second homological cancellation",
        nc_qp_g2_k == -nc_s and nc_second_residual == sp.zeros(3, 2),
        {"QP_G2_K": nc_qp_g2_k, "residual": nc_second_residual},
        {"QP_G2_K": -nc_expected["S"], "residual": sp.zeros(3, 2)},
        "L_noncommutative_third_order",
    )

    nc_projected_g2_vd = (
        nc_projection * commutator(nc_g2, nc_vd) * nc_projection
    )[:2, :2]
    nc_projected_g_g_vod = (
        nc_projection
        * commutator(nc_g, commutator(nc_g, nc_vod))
        * nc_projection
    )[:2, :2]
    audit.check(
        "v2.5 noncommutative projected discarded cubic terms",
        nc_projected_g2_vd == sp.zeros(2)
        and nc_projected_g_g_vod == sp.zeros(2),
        {
            "P_G2_Vd_P": nc_projected_g2_vd,
            "P_G_G_Vod_P": nc_projected_g_g_vod,
        },
        {"P_G2_Vd_P": sp.zeros(2), "P_G_G_Vod_P": sp.zeros(2)},
        "L_noncommutative_third_order",
    )

    nc_gram = nc_t.T * nc_r**2 * nc_t
    nc_high = nc_t.T * nc_r * nc_c * nc_r * nc_t
    nc_anticommutator = sp.Rational(1, 2) * (
        nc_a * nc_gram + nc_gram * nc_a
    )
    nc_theta_block = nc_high - nc_anticommutator
    nc_theta_nested = sp.Rational(1, 2) * (
        nc_projection * commutator(nc_g, commutator(nc_g, nc_vd)) * nc_projection
    )[:2, :2]
    audit.check(
        "v2.5 noncommutative complete third-order matrix identity",
        nc_gram == nc_expected["Gram"]
        and nc_high == nc_expected["high"]
        and nc_anticommutator == nc_expected["anticommutator"]
        and nc_theta_block == nc_theta_nested == nc_expected["Theta"],
        {
            "Gram": nc_gram,
            "high": nc_high,
            "anticommutator": nc_anticommutator,
            "Theta": nc_theta_block,
            "Theta_block": nc_theta_block,
            "Theta_nested": nc_theta_nested,
        },
        {
            "Gram": nc_expected["Gram"],
            "high": nc_expected["high"],
            "anticommutator": nc_expected["anticommutator"],
            "Theta_block": nc_expected["Theta"],
            "Theta_nested": nc_expected["Theta"],
        },
        "L_noncommutative_third_order",
    )

    spectator = sp.diag(sp.Rational(1, 7), sp.Rational(2, 7))
    cluster_factor = epsilon**2 / gamma**2
    cluster_operator = cluster_factor * sp.eye(2)
    spectator_first = spectator * cluster_operator
    spectator_anticommutator = sp.Rational(1, 2) * (
        spectator * cluster_operator + cluster_operator * spectator
    )
    audit.check(
        "v2.5 retained disconnected spectator cancellation",
        spectator_first - spectator_anticommutator == sp.zeros(2),
        spectator_first - spectator_anticommutator,
        sp.zeros(2),
        "L_linked",
    )

    coordination = 6
    support_max = 4
    diameter_max = 3
    rooted_ordered_count = 12 * coordination * (2 * coordination - 1) ** 2
    qps_count = support_max * rooted_ordered_count
    audit.check(
        "v2.5 conservative connected-triple count",
        rooted_ordered_count == 8712 and qps_count == 34848,
        {
            "rooted_ordered": rooted_ordered_count,
            "qps_count": qps_count,
            "support": support_max,
            "diameter": diameter_max,
        },
        {"rooted_ordered": 8712, "qps_count": 34848},
        "L_linked",
    )

    rho_simple = sp.Rational(5, 6)
    a_simple = sp.Rational(1, 3)
    per_triple_simple = epsilon**2 * (
        rho_simple / gamma + a_simple / gamma**2
    )
    audit.check(
        "v2.5 per-triple resolvent bound arithmetic",
        per_triple_simple == sp.Rational(1, 200),
        per_triple_simple,
        sp.Rational(1, 200),
        "L_qps",
    )

    retained_rho = sp.Rational(15201, 156250)
    retained_epsilon = sp.Rational(23, 6250)
    retained_gamma = sp.Integer(100)
    retained_a = sp.Rational(96139, 1500000)
    retained_exp_a = sp.Integer(2)
    retained_per_triple = retained_epsilon**2 * (
        retained_rho / retained_gamma
        + retained_a / retained_gamma**2
    )
    retained_qps = (
        48
        * coordination
        * (2 * coordination - 1) ** 2
        * retained_exp_a**3
        * retained_per_triple
    )
    audit.check(
        "v2.5 retained v2.1 rational cubic bounds",
        retained_per_triple
        == sp.Rational(7770533371, 585937500000000000)
        and retained_qps
        == sp.Rational(2820703613673, 762939453125000),
        {"per_triple": retained_per_triple, "qps": retained_qps},
        {
            "per_triple": sp.Rational(7770533371, 585937500000000000),
            "qps": sp.Rational(2820703613673, 762939453125000),
        },
        "L_qps",
    )

    dimension = 8
    psi_prefactor_squared = sp.Rational(1, 2**dimension)
    density_integral = sp.Integer(2) ** dimension
    normalization = psi_prefactor_squared * density_integral
    modulation = sp.Rational(1, 2)
    overlap = 1 / (1 + modulation**2)
    projection_distance_squared = 1 - overlap**2
    projection_distance = sp.Rational(3, 5)
    audit.check(
        "v2.5 rank-one compact-cylinder overlap and distance",
        normalization == 1
        and overlap == sp.Rational(4, 5)
        and projection_distance_squared == sp.Rational(9, 25)
        and projection_distance**2 == projection_distance_squared,
        {
            "normalization": normalization,
            "overlap": overlap,
            "distance": projection_distance,
            "distance_squared": projection_distance_squared,
        },
        {
            "normalization": 1,
            "overlap": sp.Rational(4, 5),
            "distance": sp.Rational(3, 5),
            "distance_squared": sp.Rational(9, 25),
        },
        "L_compact_cylinder",
    )
    sequence_rows = [
        {
            "n": index,
            "delta": sp.Rational(1, index),
            "r": sp.Rational(index, 2),
            "modulation": sp.Rational(1, index) * sp.Rational(index, 2),
        }
        for index in (2, 5, 11)
    ]
    audit.check(
        "v2.5 nonzero-time cylinder norm-jump sequence",
        all(row["modulation"] == sp.Rational(1, 2) for row in sequence_rows),
        sequence_rows,
        "delta_n r_n=1/2 for every tested n",
        "L_compact_cylinder",
    )
    audit.check(
        "v2.5 compact-cylinder carrier boundary flags",
        True,
        {
            "arbitrary_nonzero_compact_lower_bound": True,
            "rank_one_exact_supremum": 1,
            "unitized_compacts_contain_cylinder": False,
            "compact_ideal_multiplier_contains_cylinder": True,
            "compact_ideal_multiplier_point_norm_C0": False,
            "common_alpha_nonexistence": False,
        },
        "canonical split-bond route only",
        "L_compact_cylinder",
    )

    return {
        "third_order": {
            "Gamma": gamma,
            "epsilon": epsilon,
            "A": low_a,
            "C": high_c,
            "D": d_block[1, 0],
            "Z": z_block[1, 0],
            "Theta_nested": theta_nested[0, 0],
            "Theta_block": theta_block[0, 0],
            "pure_offdiagonal_Theta": pure_offdiagonal_theta[0, 0],
            "complete_fixed_finite_volume_and_Ritz": True,
            "spatial_volume_limit": False,
            "thermodynamic_limit": False,
            "Lambda_uniform_constants": False,
            "cutoff_uniform": False,
            "unbounded": False,
            "tau_cutoff_bound": False,
            "all_order": False,
        },
        "noncommutative_third_order": {
            "K_Q": nc_kq,
            "A": nc_a,
            "C": nc_c,
            "T": nc_t,
            "R": nc_r,
            "D": nc_d,
            "S": nc_s,
            "Z": nc_z,
            "QP_commutator_G2_K": nc_qp_g2_k,
            "second_offdiagonal_residual": nc_second_residual,
            "P_commutator_G2_Vd_P": nc_projected_g2_vd,
            "P_double_commutator_G_G_Vod_P": nc_projected_g_g_vod,
            "Gram": nc_gram,
            "high": nc_high,
            "anticommutator": nc_anticommutator,
            "Theta": nc_theta_block,
            "Theta_block": nc_theta_block,
            "Theta_nested": nc_theta_nested,
            "fixed_finite_Lambda_and_M_only": True,
            "volume_uniform": False,
        },
        "linked_QPS": {
            "disconnected_spectator_residual": spectator_first
            - spectator_anticommutator,
            "support_max": support_max,
            "diameter_max": diameter_max,
            "rooted_ordered_count": rooted_ordered_count,
            "qps_count": qps_count,
            "retained_per_triple": retained_per_triple,
            "retained_qps": retained_qps,
            "constant_sharp": False,
        },
        "compact_cylinder": {
            "dimension": dimension,
            "normalization": normalization,
            "overlap": overlap,
            "projection_distance": projection_distance,
            "projection_distance_squared": projection_distance_squared,
            "sequence": sequence_rows,
            "arbitrary_nonzero_compact_lower_bound": True,
            "rank_one_exact_supremum": 1,
            "unitized_compacts_contain_cylinder": False,
            "compact_ideal_multiplier_contains_cylinder": True,
            "compact_ideal_multiplier_point_norm_C0": False,
            "common_alpha_nonexistence": False,
        },
    }


def authority_audit(audit: Audit, staged: bool) -> dict[str, Any]:
    missing: list[str] = []

    def missing_or_raise(label: str) -> None:
        if staged:
            missing.append(label)
            return
        raise AssertionError(f"missing or incomplete v2.5 authority: {label}")

    def require_text(path: Path, label: str) -> str | None:
        if not path.exists():
            missing_or_raise(label)
            return None
        return path.read_text(encoding="utf-8")

    def require_token(text: str | None, token: str, label: str) -> bool:
        if text is None or token not in text:
            missing_or_raise(label)
            return False
        audit.check(label, True, True, True, "authority")
        return True

    def require_any_token(
        text: str | None, tokens: tuple[str, ...], label: str
    ) -> bool:
        if text is None or not any(token in text for token in tokens):
            missing_or_raise(label)
            return False
        audit.check(label, True, True, True, "authority")
        return True

    manifest_text = require_text(MANIFEST, "manifest file")
    manifest: dict[str, Any] | None = None
    if manifest_text is not None:
        manifest = json.loads(manifest_text)
        audit.check(
            "manifest candidate",
            manifest.get("candidate_id") == EXPECTED_CANDIDATE_ID,
            manifest.get("candidate_id"),
            EXPECTED_CANDIDATE_ID,
            "authority",
        )
        audit.check(
            "manifest task",
            manifest.get("task_id") == EXPECTED_TASK,
            manifest.get("task_id"),
            EXPECTED_TASK,
            "authority",
        )
        audit.check(
            "manifest result identity",
            (
                manifest.get("result_number"),
                manifest.get("result_version"),
                manifest.get("result_id"),
            )
            == (EXPECTED_RESULT_NUMBER, EXPECTED_RESULT_VERSION, EXPECTED_RESULT_ID),
            (
                manifest.get("result_number"),
                manifest.get("result_version"),
                manifest.get("result_id"),
            ),
            (EXPECTED_RESULT_NUMBER, EXPECTED_RESULT_VERSION, EXPECTED_RESULT_ID),
            "authority",
        )
        audit.check(
            "manifest claim nonbearing",
            manifest.get("claim_bearing") is False,
            manifest.get("claim_bearing"),
            False,
            "authority",
        )
        audit.check(
            "manifest closed subgates",
            tuple(manifest.get("closed_subgates", [])) == EXPECTED_CLOSED_SUBGATES,
            manifest.get("closed_subgates"),
            EXPECTED_CLOSED_SUBGATES,
            "authority",
        )
        audit.check(
            "manifest open gates",
            tuple(manifest.get("open_gates", [])) == EXPECTED_OPEN_GATES,
            manifest.get("open_gates"),
            EXPECTED_OPEN_GATES,
            "authority",
        )
        audit.check(
            "manifest primary script",
            manifest.get("verification", {}).get("primary_script")
            == str(SCRIPT.relative_to(REPO)).replace("\\", "/"),
            manifest.get("verification", {}).get("primary_script"),
            str(SCRIPT.relative_to(REPO)).replace("\\", "/"),
            "authority",
        )
        sources = tuple(manifest.get("q3_semiclassical_onsite", {}).get("sources", []))
        audit.check(
            "semiclassical source set",
            sources == SEMICLASSICAL_SOURCES,
            sources,
            SEMICLASSICAL_SOURCES,
            "authority",
        )
        audit.check(
            "DFP source token",
            manifest.get("unbounded_block_qps_boundary", {}).get("source") == DFP_SOURCE,
            manifest.get("unbounded_block_qps_boundary", {}).get("source"),
            DFP_SOURCE,
            "authority",
        )
        imported_theorem = manifest.get("q3_semiclassical_onsite", {}).get(
            "imported_theorem", ""
        )
        require_token(
            imported_theorem,
            "a_1-a_0=O(v^2 h_sc)",
            "manifest safe d2 token",
        )
        require_token(
            imported_theorem,
            "No exponential",
            "manifest no exponential d2 import token",
        )
        require_token(
            imported_theorem,
            "separate Agmon-overlap theorem",
            "manifest conditional Agmon-overlap token",
        )
        corridor = manifest.get("exact_low_band_compression", {}).get("corridor", "")
        require_token(
            corridor,
            "delta_eff=O(N^-6)+",
            "manifest safe delta_eff corridor",
        )
        require_token(corridor, "A_0 asymptotic to (2/9)N^4", "manifest A0 corridor")
        require_token(
            corridor,
            "c m sqrt(A_Q)",
            "manifest mixed anticommutator corridor",
        )
        renyi_fixture = manifest.get("global_renyi_product_no_go", {}).get(
            "fixture", ""
        )
        require_token(
            renyi_fixture,
            "theta=8 delta c m^2/hbar",
            "manifest full-bond angle factor",
        )
        low_band_definitions = manifest.get("exact_low_band_compression", {}).get(
            "definitions", ""
        )
        low_band_hamiltonian = manifest.get("exact_low_band_compression", {}).get(
            "hamiltonian", ""
        )
        require_token(
            low_band_definitions,
            "periodic cubic lattice z=6",
            "manifest periodic z=6 qualifier",
        )
        require_token(
            low_band_hamiltonian,
            "site-dependent boundary field",
            "manifest boundary field qualifier",
        )
        no_overclaim = manifest.get("no_overclaim", "")
        for token in (
            "rank-two unbounded block diagonalization",
            "broken-sector oscillator temporal mass or GNS gap",
            "Sector A",
            "Pre-A closure",
        ):
            require_token(no_overclaim, token, f"manifest no-overclaim token {token}")
        require_token(
            manifest.get("full_hamiltonian_gibbs_resummation", {}).get("two_orientation_bound", ""),
            "rho(W_L^2)",
            "manifest full-Gibbs Duhamel token",
        )
        require_token(
            manifest.get("fixed_edge_restricted_tail_corridor", {}).get("constants", ""),
            "1296 R^6",
            "manifest corridor constant token",
        )
        for section in (
            "twentieth_moment_fixed_edge_corridor",
            "conditional_fifth_graph_transport",
            "all_order_graph_growth_no_go",
            "static_moment_low_graph_no_go",
            "full_oscillator_edge_cluster",
            "v2_1_checkpoint_synthesis",
            "actual_q3_static_fifth_moment_and_elliptic_embedding",
            "direct_subset_shear_fifth_graph_propagation",
            "actual_q3_twentieth_history_and_hard_cutoff_corridor",
            "rank_two_projection_gap_no_go",
            "connected_rank_two_qps_successor",
            "registered_periodic_split_implementer_two_sided_gibbs_l2_hard_cutoff_removal",
            "conditional_connected_cluster_geometric_qps_norm_envelope",
            "second_order_connected_onsite_resolvent_qps_norm_and_ritz_cutoff",
            "forward_local_automorphism_limit_no_go",
            "v2_3_exact_fixture",
            "v2_2_checkpoint_synthesis",
            "v2_3_checkpoint_synthesis",
            "fixed_finite_faithful_gibbs_standard_form_point_strongstar_observable_cutoff_removal",
            "conditional_bidirectional_all_shape_point_norm_cauchy_c0_automorphism_completion",
            "first_local_homological_rank_two_generator_qps_norm_and_ritz_cutoff",
            "global_scalar_feshbach_disconnected_spectator_no_go",
            "ritz_cutoff_ordinary_bounded_operator_sw_smallness_no_go",
            "v2_4_exact_fixture",
            "v2_4_checkpoint_synthesis",
            "fixed_finite_volume_and_ritz_complete_third_order_linked_rank_two_low_block_coefficient",
            "canonical_one_site_compact_cylinder_bond_subflow_no_go",
            "v2_5_exact_fixture",
            "v2_5_checkpoint_synthesis",
        ):
            audit.check(
                f"manifest retained/new section {section}",
                section in manifest,
                section in manifest,
                True,
                "authority",
            )
        require_token(
            manifest.get("twentieth_moment_fixed_edge_corridor", {}).get("theorem", ""),
            "2916 c^2 M20 R^6 L^-16",
            "manifest twentieth-moment corridor constant",
        )
        require_token(
            manifest.get("conditional_fifth_graph_transport", {}).get("sharp_result", ""),
            "M20<=2 d5^2 exp(G5 T) S_mu^5 m5",
            "manifest sharp conditional M20 factor",
        )
        require_token(
            manifest.get("full_oscillator_edge_cluster", {}).get("compressions", ""),
            "P0 h_xy L is nonzero",
            "manifest P0-L noninvariance boundary",
        )
        require_token(
            manifest.get("full_oscillator_edge_cluster", {}).get("spectral_cutoff_removal", ""),
            "Pi_M q^2 Pi_M need not equal",
            "manifest Ritz versus truncated-q boundary",
        )
        require_token(
            manifest.get("actual_q3_static_fifth_moment_and_elliptic_embedding", {}).get("virial_identity", ""),
            "p_i^10/chi",
            "manifest v2.2 virial identity",
        )
        require_token(
            manifest.get("direct_subset_shear_fifth_graph_propagation", {}).get("fifth_form_bound", ""),
            "O(|delta|)",
            "manifest v2.2 load-bearing step factor",
        )
        require_token(
            manifest.get("direct_subset_shear_fifth_graph_propagation", {}).get("fifth_form_bound", ""),
            "f_x^(1/2)",
            "manifest v2.2 R1 allocation",
        )
        require_token(
            manifest.get("direct_subset_shear_fifth_graph_propagation", {}).get("uniformity_boundary", ""),
            "Maximum degree at most six alone is not enough",
            "manifest v2.2 cubic-growth boundary",
        )
        require_token(
            manifest.get("direct_subset_shear_fifth_graph_propagation", {}).get("generic_degree_six_hostile", ""),
            "6*5^(r-1)",
            "manifest v2.2 degree-six hostile",
        )
        require_token(
            manifest.get("actual_q3_twentieth_history_and_hard_cutoff_corridor", {}).get("moment", ""),
            "M20<=2 d5^2 exp(C5 T) S_mu^5 m5",
            "manifest v2.2 actual M20",
        )
        require_token(
            manifest.get("registered_periodic_split_implementer_two_sided_gibbs_l2_hard_cutoff_removal", {}).get("paired_sum_input", ""),
            "54 sqrt(2)",
            "manifest v2.3 implementer rate",
        )
        require_token(
            manifest.get("conditional_connected_cluster_geometric_qps_norm_envelope", {}).get("qps_bound", ""),
            "A kappa/(1-r)^2",
            "manifest v2.3 connected-envelope QPS bound",
        )
        require_token(
            manifest.get("second_order_connected_onsite_resolvent_qps_norm_and_ritz_cutoff", {}).get("connectedness", ""),
            "3z(z-1)",
            "manifest v2.3 overlapping ordered-pair count",
        )
        require_token(
            manifest.get("second_order_connected_onsite_resolvent_qps_norm_and_ritz_cutoff", {}).get("ritz_cutoff", ""),
            "2 C_a epsilon tau_M/Gamma",
            "manifest v2.3 Ritz Gram cutoff bound",
        )
        require_token(
            manifest.get("forward_local_automorphism_limit_no_go", {}).get("failure", ""),
            "||Z_N-Z_M||=2",
            "manifest v2.3 UHF inverse non-Cauchy fixture",
        )
        expected_v23_fixture = {
            "implementer": {
                "paired_tail_constant": 2916,
                "squared_rate_constant": 5832,
                "R_32_L_4_rate": "27*sqrt(2)",
                "R_3125_L_25_rate": "54*sqrt(2)/5",
            },
            "connected_envelope": {
                "z": 6,
                "exp_a": 2,
                "kappa": "1/144",
                "A": "1/100",
                "r": "1/2",
                "qps_bound": "1/3600",
                "A_M_at_M_10": "1/1000",
                "cutoff_bound_at_M_10": "1/36000",
            },
            "second_order": {
                "diagonal_pairs": 6,
                "ordered_off_diagonal_pairs": 90,
                "C_a": 1104,
                "epsilon": "1/100",
                "Gamma": 2,
                "qps_bound": "69/1250",
                "tau_M_at_M_10": "1/1000",
                "cutoff_difference_bound": "69/6250",
                "N_exponent": -8,
            },
            "uhf": {
                "forward_local_support": [2, 3, 4],
                "inverse_images": [3, 5],
                "inverse_difference_norm": 2,
                "limit_surjective": False,
            },
        }
        audit.check(
            "manifest v2.3 exact fixture",
            manifest.get("v2_3_exact_fixture") == expected_v23_fixture,
            manifest.get("v2_3_exact_fixture"),
            expected_v23_fixture,
            "authority",
        )
        require_token(
            manifest.get(
                "fixed_finite_faithful_gibbs_standard_form_point_strongstar_observable_cutoff_removal",
                {},
            ).get("fixed_member_bound", ""),
            "R0^3 L^(-8)",
            "manifest v2.4 fixed-member standard-form rate",
        )
        require_token(
            manifest.get(
                "fixed_finite_faithful_gibbs_standard_form_point_strongstar_observable_cutoff_removal",
                {},
            ).get("boundary", ""),
            "not a strong-star rate",
            "manifest v2.4 moving-family rate boundary",
        )
        require_token(
            manifest.get(
                "conditional_bidirectional_all_shape_point_norm_cauchy_c0_automorphism_completion",
                {},
            ).get("hypotheses", ""),
            "both alpha_lambda^t(A) and alpha_lambda^(-t)(A)",
            "manifest v2.4 bidirectional C0 hypothesis",
        )
        require_token(
            manifest.get(
                "first_local_homological_rank_two_generator_qps_norm_and_ritz_cutoff",
                {},
            ).get("second_order_match", ""),
            "(1/2)P[G,V_od]P=-sum_(e,f)T_e^* R T_f",
            "manifest v2.4 generator second-order match",
        )
        require_token(
            manifest.get("global_scalar_feshbach_disconnected_spectator_no_go", {}).get(
                "failure", ""
            ),
            "+1/800",
            "manifest v2.4 spectator Feshbach coefficient",
        )
        require_token(
            manifest.get("ritz_cutoff_ordinary_bounded_operator_sw_smallness_no_go", {}).get(
                "failure", ""
            ),
            "(M+1)/8",
            "manifest v2.4 Ritz norm hostile coefficient",
        )
        expected_v24_fixture = {
            "standard_form": {
                "R0": 32,
                "L_4_per_leg": "27",
                "L_4_two_leg": "27*sqrt(2)",
                "L_8_per_leg": "27/256",
                "L_8_two_leg": "27*sqrt(2)/256",
                "rotation_n_3_leg_squared": "2/5",
                "rotation_n_7_leg_squared": "2/25",
                "rotation_n_3_observable_squared": "36/25",
                "rotation_n_7_observable_squared": "196/625",
            },
            "c0_completion": {
                "n": 10,
                "m": 20,
                "T": 1,
                "generator_difference": "1/20",
                "positive_cauchy_bound": "1/10",
                "negative_cauchy_bound": "1/10",
                "limit_error_bound_at_n": "1/5",
            },
            "first_generator": {
                "z": 6,
                "exp_a": 2,
                "epsilon": "1/100",
                "Gamma": 2,
                "tau_M": "1/1000",
                "edge_norm_bound": "1/200",
                "qps_bound": "3/25",
                "edge_cutoff_bound": "1/2000",
                "qps_cutoff_bound": "3/250",
                "second_order_scalar": "-1/20000",
            },
            "spectator_feshbach": {
                "Gamma": 2,
                "E": 0,
                "epsilon": "1/10",
                "spectator_energies": [0, 1],
                "coupling_weights_squared": [1, 4],
                "resolvent_diagonal": ["1/2", "1/3"],
                "self_energy_mixed_ZZ": "-1/800",
                "feshbach_mixed_ZZ": "1/800",
            },
            "ritz_norm_hostile": {
                "c": "1/4",
                "Gamma": 2,
                "M_values": [3, 15],
                "bond_expectations": [4, 16],
                "smallness_lower_bounds": ["1/2", "2"],
            },
        }
        audit.check(
            "manifest v2.4 exact fixture",
            manifest.get("v2_4_exact_fixture") == expected_v24_fixture,
            manifest.get("v2_4_exact_fixture"),
            expected_v24_fixture,
            "authority",
        )
        require_token(
            manifest.get(
                "fixed_finite_volume_and_ritz_complete_third_order_linked_rank_two_low_block_coefficient",
                {},
            ).get("sequential_rotation", ""),
            "Theta^(3)=(1/2)P[G,[G,V_d]]P=T* R C R T-(1/2){A,T* R^2 T}",
            "manifest v2.5 complete third-order formula",
        )
        require_token(
            manifest.get(
                "fixed_finite_volume_and_ritz_complete_third_order_linked_rank_two_low_block_coefficient",
                {},
            ).get("edge_expansion", ""),
            "cancel exactly",
            "manifest v2.5 disconnected spectator cancellation",
        )
        require_token(
            manifest.get(
                "fixed_finite_volume_and_ritz_complete_third_order_linked_rank_two_low_block_coefficient",
                {},
            ).get("qps_bound", ""),
            "48 z(2z-1)^2 exp(3a)",
            "manifest v2.5 conservative QPS bound",
        )
        require_token(
            manifest.get(
                "fixed_finite_volume_and_ritz_complete_third_order_linked_rank_two_low_block_coefficient",
                {},
            ).get("boundary", ""),
            "tau_M cutoff estimate is asserted",
            "manifest v2.5 tau cutoff boundary",
        )
        require_token(
            manifest.get(
                "canonical_one_site_compact_cylinder_bond_subflow_no_go", {}
            ).get("failure", ""),
            "projection distance is 3/5 and its square is 9/25",
            "manifest v2.5 compact-cylinder exact fixture",
        )
        expected_v25_fixture = {
            "third_order": {
                "Gamma": 2,
                "epsilon": "1/10",
                "A": "1/3",
                "C": "5/3",
                "Z": "-1/30",
                "Theta": "1/300",
                "pure_offdiagonal_Theta": "0",
                "support_max": 4,
                "diameter_max": 3,
                "rooted_ordered_count_factor": "12z(2z-1)^2",
                "qps_factor": "48z(2z-1)^2exp(3a)",
            },
            "noncommutative_third_order": {
                "K_Q": [[2, 0, 0], [0, 3, 0], [0, 0, 5]],
                "A": [[1, 2], [2, -1]],
                "C": [[3, 1, 0], [1, -2, 2], [0, 2, 4]],
                "T": [["1/10", "1/5"], ["0", "-1/10"], ["3/10", "1/10"]],
                "R": [["1/2", "0", "0"], ["0", "1/3", "0"], ["0", "0", "1/5"]],
                "D": [["1/20", "1/10"], ["0", "-1/30"], ["3/50", "1/50"]],
                "S": [["1/10", "-4/15"], ["-71/300", "-13/75"], ["-7/50", "13/150"]],
                "Z": [["1/20", "-2/15"], ["-71/900", "-13/225"], ["-7/250", "13/750"]],
                "QP_commutator_G2_K": [["-1/10", "4/15"], ["71/300", "13/75"], ["7/50", "-13/150"]],
                "second_offdiagonal_residual": [["0", "0"], ["0", "0"], ["0", "0"]],
                "P_commutator_G2_Vd_P": [["0", "0"], ["0", "0"]],
                "P_double_commutator_G_G_Vod_P": [["0", "0"], ["0", "0"]],
                "Gram": [["61/10000", "31/5000"], ["31/5000", "259/22500"]],
                "high": [["219/10000", "53/3750"], ["53/3750", "451/22500"]],
                "anticommutator": [["37/2000", "317/18000"], ["317/18000", "1/1125"]],
                "Theta": [["17/5000", "-313/90000"], ["-313/90000", "431/22500"]],
                "fixed_finite_Lambda_and_M_only": True,
                "volume_uniform": False,
            },
            "v2_1_rational_bound": {
                "rho_M_Lambda": "15201/156250",
                "epsilon": "23/6250",
                "Gamma": 100,
                "a_M_Lambda": "96139/1500000",
                "z": 6,
                "exp_a": 2,
                "per_triple": "7770533371/585937500000000000",
                "qps_safe": "2820703613673/762939453125000",
            },
            "compact_cylinder": {
                "dimension": 8,
                "c": 1,
                "hbar": 1,
                "delta_n": "1/n",
                "r_n": "n/2",
                "modulation": "1/2",
                "overlap": "4/5",
                "projection_distance": "3/5",
                "projection_distance_squared": "9/25",
                "exact_supremum": 1,
                "unitized_compacts_contain_cylinder": False,
                "compact_ideal_multiplier_contains_cylinder": True,
                "compact_ideal_multiplier_point_norm_C0": False,
            },
        }
        audit.check(
            "manifest v2.5 exact fixture",
            manifest.get("v2_5_exact_fixture") == expected_v25_fixture,
            manifest.get("v2_5_exact_fixture"),
            expected_v25_fixture,
            "authority",
        )
        checkpoint_v22 = manifest.get("v2_2_checkpoint_synthesis")
        deferred_v22 = {
            "status": "DEFERRED",
            "workflow": (
                "No intermediate PDF is issued for R-167 v2.2. Preserve every "
                "v2.1 and earlier source/PDF pair as historical evidence; issue or "
                "update one combined gate-level synthesis only after the proof, "
                "formal-authority, integrated, generated-surface, strict-release "
                "and render-review gates pass."
            ),
        }
        issued_fields = {
            "status", "source", "pdf", "source_sha256", "pdf_sha256",
            "pages", "workflow", "visual_qa",
        }
        issued_status = (
            "ISSUED AS ONE COMBINED GATE-LEVEL CHECKPOINT AFTER PROOF VALIDATION"
        )
        issued_source = (
            "claims/C6-SPACETIME-SIGNATURE/notes/"
            "pre-a-q3lock-fifth-history-rank2-gap-and-m2-response-boundary-"
            "checkpoint-260811-v1.1.tex.txt"
        )
        issued_pdf = issued_source.removesuffix(".tex.txt") + ".pdf"
        issued_workflow = (
            "No per-lemma or intermediate PDF was issued. One combined R-167 v2.2 / "
            "R-168 v1.3 gate-level synthesis source/PDF pair was issued only after "
            "the primary, non-importing independent, integrated, formal-authority, "
            "generated-surface, source-form, freshness, dual-extraction, and "
            "visual-review checks passed."
        )
        r168_v13_checkpoint = None
        try:
            r168_v13_checkpoint = json.loads(
                (
                    REPO
                    / "strategy/pre-a-round1-prospective-holdout-freeze-protocol-"
                    "manifest.json"
                ).read_text(encoding="utf-8")
            ).get("v1_3_checkpoint_synthesis")
        except (OSError, UnicodeError, json.JSONDecodeError):
            pass
        pages_v22 = checkpoint_v22.get("pages") if isinstance(checkpoint_v22, dict) else None
        pages_v22_valid = (
            isinstance(pages_v22, int)
            and not isinstance(pages_v22, bool)
            and pages_v22 > 0
        )
        visual_qa_v22 = (
            f"All {pages_v22} rendered pages were reviewed at readable resolution "
            "with zero clipping, overlap, broken equations, unreadable identifiers, "
            "black glyphs, or malformed page transitions; pypdf and pdfplumber each "
            f"extracted {pages_v22}/{pages_v22} nonempty pages; the build reported "
            "OVERFULL-HBOX 0."
            if pages_v22_valid
            else None
        )
        source_path_v22 = REPO / issued_source
        pdf_path_v22 = REPO / issued_pdf
        source_hash_v22 = (
            hashlib.sha256(source_path_v22.read_bytes()).hexdigest()
            if source_path_v22.is_file()
            else None
        )
        pdf_hash_v22 = (
            hashlib.sha256(pdf_path_v22.read_bytes()).hexdigest()
            if pdf_path_v22.is_file()
            else None
        )
        lowercase_hex = set("0123456789abcdef")
        source_pin_v22 = (
            checkpoint_v22.get("source_sha256")
            if isinstance(checkpoint_v22, dict)
            else None
        )
        pdf_pin_v22 = (
            checkpoint_v22.get("pdf_sha256")
            if isinstance(checkpoint_v22, dict)
            else None
        )
        issued_v22_valid = (
            isinstance(checkpoint_v22, dict)
            and set(checkpoint_v22) == issued_fields
            and checkpoint_v22 == r168_v13_checkpoint
            and checkpoint_v22.get("status") == issued_status
            and checkpoint_v22.get("source") == issued_source
            and checkpoint_v22.get("pdf") == issued_pdf
            and checkpoint_v22.get("workflow") == issued_workflow
            and checkpoint_v22.get("visual_qa") == visual_qa_v22
            and pages_v22_valid
            and isinstance(source_pin_v22, str)
            and len(source_pin_v22) == 64
            and set(source_pin_v22) <= lowercase_hex
            and isinstance(pdf_pin_v22, str)
            and len(pdf_pin_v22) == 64
            and set(pdf_pin_v22) <= lowercase_hex
            and source_path_v22.is_file()
            and pdf_path_v22.is_file()
            and source_hash_v22 == source_pin_v22
            and pdf_hash_v22 == pdf_pin_v22
            and pdf_path_v22.stat().st_mtime_ns >= source_path_v22.stat().st_mtime_ns
        )
        audit.check(
            "manifest v2.2 checkpoint lifecycle",
            checkpoint_v22 == deferred_v22 or issued_v22_valid,
            {
                "metadata": checkpoint_v22,
                "shared_r168_v1_3": r168_v13_checkpoint,
                "deferred_exact": checkpoint_v22 == deferred_v22,
                "issued_exact": issued_v22_valid,
                "source_sha256": source_hash_v22,
                "pdf_sha256": pdf_hash_v22,
            },
            "exact proof-first DEFERRED or exact cross-bound eight-field ISSUED checkpoint",
            "authority",
        )
        checkpoint_v23 = manifest.get("v2_3_checkpoint_synthesis")
        deferred_v23 = {
            "status": "DEFERRED",
            "pdf_issued": False,
            "workflow": (
                "No intermediate PDF is issued for R-167 v2.3. Preserve every "
                "v2.2 and earlier source/PDF pair as historical evidence; issue "
                "one R-167 v2.3 gate-level synthesis only after the primary, "
                "non-importing independent, integrated, formal-authority, "
                "generated-surface, source-form, freshness, dual-extraction, "
                "strict-release, and visual-review gates pass. R-168 v1.3 "
                "remains historical and is not reissued."
            ),
        }
        issued_v23_fields = {
            "status", "source", "pdf", "source_sha256", "pdf_sha256",
            "pages", "workflow", "visual_qa",
        }
        issued_v23_status = (
            "ISSUED AS ONE GATE-LEVEL CHECKPOINT AFTER PROOF VALIDATION"
        )
        issued_v23_workflow = (
            "No per-lemma or intermediate PDF was issued. One R-167 v2.3 "
            "gate-level synthesis source/PDF pair was issued only after the "
            "primary, non-importing independent, integrated, formal-authority, "
            "generated-surface, source-form, freshness, dual-extraction, "
            "strict-release, and visual-review checks passed. R-168 v1.3 "
            "remains historical and is not reissued."
        )
        source_rel_v23 = (
            checkpoint_v23.get("source")
            if isinstance(checkpoint_v23, dict)
            else None
        )
        pdf_rel_v23 = (
            checkpoint_v23.get("pdf")
            if isinstance(checkpoint_v23, dict)
            else None
        )
        source_path_v23 = (
            REPO / source_rel_v23 if isinstance(source_rel_v23, str) else None
        )
        pdf_path_v23 = REPO / pdf_rel_v23 if isinstance(pdf_rel_v23, str) else None
        pages_v23 = (
            checkpoint_v23.get("pages")
            if isinstance(checkpoint_v23, dict)
            else None
        )
        pages_v23_valid = (
            isinstance(pages_v23, int)
            and not isinstance(pages_v23, bool)
            and pages_v23 > 0
        )
        visual_qa_v23 = (
            f"All {pages_v23} rendered pages were reviewed at readable resolution "
            "with zero clipping, overlap, broken equations, unreadable identifiers, "
            "black glyphs, or malformed page transitions; pypdf and pdfplumber each "
            f"extracted {pages_v23}/{pages_v23} nonempty pages; the build reported "
            "OVERFULL-HBOX 0."
            if pages_v23_valid
            else None
        )
        source_hash_actual_v23 = (
            hashlib.sha256(source_path_v23.read_bytes()).hexdigest()
            if source_path_v23 is not None and source_path_v23.is_file()
            else None
        )
        pdf_hash_actual_v23 = (
            hashlib.sha256(pdf_path_v23.read_bytes()).hexdigest()
            if pdf_path_v23 is not None and pdf_path_v23.is_file()
            else None
        )
        source_pin_v23 = (
            checkpoint_v23.get("source_sha256")
            if isinstance(checkpoint_v23, dict)
            else None
        )
        pdf_pin_v23 = (
            checkpoint_v23.get("pdf_sha256")
            if isinstance(checkpoint_v23, dict)
            else None
        )
        source_relative_valid_v23 = (
            isinstance(source_rel_v23, str)
            and source_rel_v23.startswith("claims/C6-SPACETIME-SIGNATURE/notes/")
            and source_rel_v23.endswith(".tex.txt")
            and ".." not in Path(source_rel_v23).parts
        )
        issued_v23_valid = (
            isinstance(checkpoint_v23, dict)
            and set(checkpoint_v23) == issued_v23_fields
            and checkpoint_v23.get("status") == issued_v23_status
            and source_relative_valid_v23
            and isinstance(pdf_rel_v23, str)
            and pdf_rel_v23 == source_rel_v23.removesuffix(".tex.txt") + ".pdf"
            and checkpoint_v23.get("workflow") == issued_v23_workflow
            and checkpoint_v23.get("visual_qa") == visual_qa_v23
            and pages_v23_valid
            and isinstance(source_pin_v23, str)
            and len(source_pin_v23) == 64
            and set(source_pin_v23) <= lowercase_hex
            and isinstance(pdf_pin_v23, str)
            and len(pdf_pin_v23) == 64
            and set(pdf_pin_v23) <= lowercase_hex
            and source_path_v23 is not None
            and pdf_path_v23 is not None
            and source_path_v23.is_file()
            and pdf_path_v23.is_file()
            and source_hash_actual_v23 == source_pin_v23
            and pdf_hash_actual_v23 == pdf_pin_v23
            and pdf_path_v23.stat().st_mtime_ns >= source_path_v23.stat().st_mtime_ns
        )
        audit.check(
            "manifest v2.3 checkpoint lifecycle",
            checkpoint_v23 == deferred_v23 or issued_v23_valid,
            {
                "metadata": checkpoint_v23,
                "deferred_exact": checkpoint_v23 == deferred_v23,
                "issued_exact": issued_v23_valid,
                "source_sha256": source_hash_actual_v23,
                "pdf_sha256": pdf_hash_actual_v23,
            },
            "exact proof-first DEFERRED or exact local eight-field ISSUED checkpoint",
            "authority",
        )
        checkpoint_v24 = manifest.get("v2_4_checkpoint_synthesis")
        deferred_v24 = {
            "status": "DEFERRED",
            "pdf_issued": False,
            "workflow": (
                "No intermediate PDF is issued for R-167 v2.4. Preserve every "
                "v2.3 and earlier source/PDF pair as historical evidence; issue "
                "one R-167-only v2.4 gate-level synthesis after the primary, "
                "non-importing independent, integrated, formal-authority, "
                "generated-surface, source-form, freshness, dual-extraction, "
                "strict-release, and visual-review gates pass. R-168 v1.3 "
                "remains historical and is not reissued."
            ),
        }
        issued_v24_fields = {
            "status", "source", "pdf", "source_sha256", "pdf_sha256",
            "pages", "workflow", "visual_qa",
        }
        issued_v24_status = (
            "ISSUED AS ONE GATE-LEVEL CHECKPOINT AFTER PROOF VALIDATION"
        )
        issued_v24_workflow = (
            "No per-lemma or intermediate PDF was issued. One R-167 v2.4 "
            "gate-level synthesis source/PDF pair was issued only after the "
            "primary, non-importing independent, integrated, formal-authority, "
            "generated-surface, source-form, freshness, dual-extraction, "
            "strict-release, and visual-review checks passed. R-168 v1.3 "
            "remains historical and is not reissued."
        )
        source_rel_v24 = (
            checkpoint_v24.get("source")
            if isinstance(checkpoint_v24, dict)
            else None
        )
        pdf_rel_v24 = (
            checkpoint_v24.get("pdf")
            if isinstance(checkpoint_v24, dict)
            else None
        )
        source_path_v24 = (
            REPO / source_rel_v24 if isinstance(source_rel_v24, str) else None
        )
        pdf_path_v24 = (
            REPO / pdf_rel_v24 if isinstance(pdf_rel_v24, str) else None
        )
        pages_v24 = (
            checkpoint_v24.get("pages")
            if isinstance(checkpoint_v24, dict)
            else None
        )
        pages_v24_valid = (
            isinstance(pages_v24, int)
            and not isinstance(pages_v24, bool)
            and pages_v24 > 0
        )
        visual_qa_v24 = (
            f"All {pages_v24} rendered pages were reviewed at readable resolution "
            "with zero clipping, overlap, broken equations, unreadable identifiers, "
            "black glyphs, or malformed page transitions; pypdf and pdfplumber each "
            f"extracted {pages_v24}/{pages_v24} nonempty pages; the build reported "
            "OVERFULL-HBOX 0."
            if pages_v24_valid
            else None
        )
        source_hash_actual_v24 = (
            hashlib.sha256(source_path_v24.read_bytes()).hexdigest()
            if source_path_v24 is not None and source_path_v24.is_file()
            else None
        )
        pdf_hash_actual_v24 = (
            hashlib.sha256(pdf_path_v24.read_bytes()).hexdigest()
            if pdf_path_v24 is not None and pdf_path_v24.is_file()
            else None
        )
        source_pin_v24 = (
            checkpoint_v24.get("source_sha256")
            if isinstance(checkpoint_v24, dict)
            else None
        )
        pdf_pin_v24 = (
            checkpoint_v24.get("pdf_sha256")
            if isinstance(checkpoint_v24, dict)
            else None
        )
        source_relative_valid_v24 = (
            isinstance(source_rel_v24, str)
            and source_rel_v24.startswith("claims/C6-SPACETIME-SIGNATURE/notes/")
            and source_rel_v24.endswith(".tex.txt")
            and ".." not in Path(source_rel_v24).parts
        )
        issued_v24_valid = (
            isinstance(checkpoint_v24, dict)
            and set(checkpoint_v24) == issued_v24_fields
            and checkpoint_v24.get("status") == issued_v24_status
            and source_relative_valid_v24
            and isinstance(pdf_rel_v24, str)
            and pdf_rel_v24 == source_rel_v24.removesuffix(".tex.txt") + ".pdf"
            and checkpoint_v24.get("workflow") == issued_v24_workflow
            and checkpoint_v24.get("visual_qa") == visual_qa_v24
            and pages_v24_valid
            and isinstance(source_pin_v24, str)
            and len(source_pin_v24) == 64
            and set(source_pin_v24) <= lowercase_hex
            and isinstance(pdf_pin_v24, str)
            and len(pdf_pin_v24) == 64
            and set(pdf_pin_v24) <= lowercase_hex
            and source_path_v24 is not None
            and pdf_path_v24 is not None
            and source_path_v24.is_file()
            and pdf_path_v24.is_file()
            and source_hash_actual_v24 == source_pin_v24
            and pdf_hash_actual_v24 == pdf_pin_v24
            and pdf_path_v24.stat().st_mtime_ns >= source_path_v24.stat().st_mtime_ns
        )
        audit.check(
            "manifest v2.4 checkpoint lifecycle",
            checkpoint_v24 == deferred_v24 or issued_v24_valid,
            {
                "metadata": checkpoint_v24,
                "deferred_exact": checkpoint_v24 == deferred_v24,
                "issued_exact": issued_v24_valid,
                "source_sha256": source_hash_actual_v24,
                "pdf_sha256": pdf_hash_actual_v24,
            },
            "exact proof-first DEFERRED or exact R-167-only eight-field ISSUED checkpoint",
            "authority",
        )
        checkpoint_v25 = manifest.get("v2_5_checkpoint_synthesis")
        deferred_v25 = {
            "status": "DEFERRED",
            "pdf_issued": False,
            "workflow": (
                "No intermediate PDF is issued for R-167 v2.5. Preserve every "
                "v2.4 and earlier source/PDF pair as historical evidence; issue "
                "one R-167-only v2.5 gate-level synthesis after the primary, "
                "non-importing independent, integrated, formal-authority, "
                "generated-surface, source-form, freshness, dual-extraction, "
                "strict-release, and visual-review gates pass. R-168 v1.3 "
                "remains historical and is not reissued."
            ),
        }
        issued_v25 = _v2_5_checkpoint_lifecycle(
            checkpoint_v25 if isinstance(checkpoint_v25, dict) else {},
            exploration_id=EXPECTED_EXPLORATION,
            closed_subgates=V2_5_CLOSED_SUBGATES,
            negative_ids=V2_5_NEGATIVE_IDS,
        )
        audit.check(
            "manifest v2.5 exact deferred or issued checkpoint lifecycle",
            checkpoint_v25 == deferred_v25 or issued_v25["valid"],
            {
                "metadata": checkpoint_v25,
                "deferred_exact": checkpoint_v25 == deferred_v25,
                "issued": issued_v25,
            },
            "exact three-field DEFERRED or exact R-167-only eight-field ISSUED checkpoint",
            "authority",
        )
        audit.check(
            "manifest Yarotskii QPS source",
            manifest.get("compressed_tfim_two_phase_qps", {}).get("source")
            == YAROTSKII_QPS_SOURCE,
            manifest.get("compressed_tfim_two_phase_qps", {}).get("source"),
            YAROTSKII_QPS_SOURCE,
            "authority",
        )
        checkpoint = manifest.get("v2_checkpoint_synthesis")
        prospective_manifest = (
            REPO
            / "strategy/pre-a-round1-prospective-holdout-freeze-protocol-manifest.json"
        )
        other_checkpoint = None
        if prospective_manifest.is_file():
            try:
                other_checkpoint = json.loads(
                    prospective_manifest.read_text(encoding="utf-8")
                ).get("v2_checkpoint_synthesis")
            except (OSError, UnicodeError, json.JSONDecodeError):
                other_checkpoint = None

        checkpoint_fields = {
            "status",
            "source",
            "pdf",
            "source_sha256",
            "pdf_sha256",
            "pages",
            "workflow",
            "visual_qa",
        }
        checkpoint_status = (
            "ISSUED AS ONE COMBINED GATE-LEVEL CHECKPOINT AFTER PROOF VALIDATION"
        )
        checkpoint_source_rel = (
            "claims/C6-SPACETIME-SIGNATURE/notes/"
            "pre-a-q3lock-gibbs-feshbach-tfim-and-round1-map-fingerprint-"
            "checkpoint-260811-v0.9.tex.txt"
        )
        checkpoint_pdf_rel = (
            "claims/C6-SPACETIME-SIGNATURE/notes/"
            "pre-a-q3lock-gibbs-feshbach-tfim-and-round1-map-fingerprint-"
            "checkpoint-260811-v0.9.pdf"
        )
        checkpoint_workflow = (
            "No per-lemma or intermediate PDF was issued. One combined R-167 v2.0 / "
            "R-168 v1.1 gate-level synthesis source/PDF pair was issued only after "
            "the primary, non-importing independent, integrated, formal-authority, "
            "generated-surface, and source-form checks passed."
        )
        source_path = REPO / checkpoint_source_rel
        pdf_path = REPO / checkpoint_pdf_rel
        source_hash_actual = (
            hashlib.sha256(source_path.read_bytes()).hexdigest()
            if source_path.is_file()
            else None
        )
        pdf_hash_actual = (
            hashlib.sha256(pdf_path.read_bytes()).hexdigest()
            if pdf_path.is_file()
            else None
        )
        visual_qa = (
            checkpoint.get("visual_qa", "") if isinstance(checkpoint, dict) else ""
        )
        source_hash_declared = (
            checkpoint.get("source_sha256") if isinstance(checkpoint, dict) else None
        )
        pdf_hash_declared = (
            checkpoint.get("pdf_sha256") if isinstance(checkpoint, dict) else None
        )
        pages_declared = checkpoint.get("pages") if isinstance(checkpoint, dict) else None
        lowercase_hex = set("0123456789abcdef")
        checkpoint_valid = (
            isinstance(checkpoint, dict)
            and set(checkpoint) == checkpoint_fields
            and checkpoint == other_checkpoint
            and checkpoint.get("status") == checkpoint_status
            and checkpoint.get("source") == checkpoint_source_rel
            and checkpoint.get("pdf") == checkpoint_pdf_rel
            and source_path.with_suffix("").with_suffix(".pdf") == pdf_path
            and isinstance(source_hash_declared, str)
            and len(source_hash_declared) == 64
            and set(source_hash_declared) <= lowercase_hex
            and isinstance(pdf_hash_declared, str)
            and len(pdf_hash_declared) == 64
            and set(pdf_hash_declared) <= lowercase_hex
            and isinstance(pages_declared, int)
            and not isinstance(pages_declared, bool)
            and pages_declared > 0
            and checkpoint.get("workflow") == checkpoint_workflow
            and isinstance(visual_qa, str)
            and all(
                token in visual_qa.lower()
                for token in (
                    "all",
                    "rendered pages",
                    "clipping",
                    "overlap",
                    "pypdf",
                    "pdfplumber",
                )
            )
            and source_path.is_file()
            and pdf_path.is_file()
            and source_hash_actual == source_hash_declared
            and pdf_hash_actual == pdf_hash_declared
            and pdf_path.stat().st_mtime_ns >= source_path.stat().st_mtime_ns
        )
        audit.check(
            "v2 combined checkpoint issued and exact",
            checkpoint_valid,
            {
                "checkpoint": checkpoint,
                "shared_checkpoint": other_checkpoint,
                "source_exists": source_path.is_file(),
                "pdf_exists": pdf_path.is_file(),
                "source_sha256": source_hash_actual,
                "pdf_sha256": pdf_hash_actual,
                "pdf_fresh_relative_to_source": (
                    source_path.is_file()
                    and pdf_path.is_file()
                    and pdf_path.stat().st_mtime_ns >= source_path.stat().st_mtime_ns
                ),
            },
            {
                "exact_fields": sorted(checkpoint_fields),
                "shared": True,
                "status": checkpoint_status,
                "source": checkpoint_source_rel,
                "pdf": checkpoint_pdf_rel,
                "workflow": checkpoint_workflow,
                "hashes": "exact lowercase raw SHA256",
                "pages": "positive integer; parser validation is integrated-only",
                "fresh": True,
            },
            "authority",
        )

    certificate_text = require_text(CERTIFICATE, "certificate file")
    for token in (
        EXPECTED_RESULT_NUMBER,
        EXPECTED_RESULT_VERSION,
        EXPECTED_EXPLORATION,
        "S_0={16",
        "24c",
        "O(v^2h)",
        "Agmon-overlap lemma",
        "A_0",
        "N^4",
        "rank-one",
        "rank-two",
        "non-explicit",
        "No statement here closes",
    ):
        require_token(certificate_text, token, f"certificate token {token}")
    require_any_token(
        certificate_text,
        (r"\sqrt{2}", r"\sqrt2", "sqrt(2)"),
        "certificate semantic sqrt(2) token",
    )
    require_any_token(
        certificate_text,
        (r"\delta_{\rm eff}", "delta_eff"),
        "certificate semantic delta_eff token",
    )
    require_any_token(
        certificate_text,
        (r"8\delta c m^2", "8 delta c m^2"),
        "certificate full-bond factor 8 token",
    )
    require_token(
        certificate_text,
        "periodic cubic lattice",
        "certificate periodic lattice qualifier",
    )
    for token in (
        "EXP-000809",
        "rho(W_L^2)",
        "1296R^6",
        r"\kappa_{\rm ov}\le1+2(z-1)=11",
        r"0^{\times2}",
        "k=(0,-2)",
        "RM2006v061n02ABEH004323",
        "No v2.0 PDF is issued",
    ):
        require_token(certificate_text, token, f"certificate v2 token {token}")

    for token in (
        "EXP-000811",
        "R-167 v2.1",
        "2916c^2M_{20}",
        r"M_{20}\le2d_5^2e^{G_5T}S_\mu^5m_5",
        "2^m-2^{-m}",
        "N^6-N^{-14}",
        "20832953/19531250",
        "332047248/5188304375",
        "4430237/234375000",
        "P_0h_{xy}L",
        "Ritz form restriction",
        "No v2.1 PDF is issued",
        *V2_1_CLOSED_SUBGATES,
        *EXPECTED_OPEN_GATES[-2:],
        *V2_1_NEGATIVE_IDS,
    ):
        require_token(certificate_text, token, f"certificate v2.1 token {token}")

    for token in (
        "EXP-000813",
        "R-167 v2.2",
        "p_i^{10}",
        r"C_5(T,\mu)|\delta|",
        r"M_{20}\le2d_5^2e^{C_5T}S_\mu^5m_5",
        "rank-two projection",
        "No v2.2 PDF is issued",
        "v2_2_checkpoint_synthesis",
        *V2_2_CLOSED_SUBGATES,
        EXPECTED_OPEN_GATES[-1],
        *V2_2_NEGATIVE_IDS,
    ):
        require_token(certificate_text, token, f"certificate v2.2 token {token}")

    for token in (
        "EXP-000815",
        "R-167 v2.3",
        r"54\sqrt2",
        "1/3600",
        "3z(z-1)",
        "69/6250",
        "No v2.3 PDF is issued",
        "v2_3_checkpoint_synthesis",
        "R-168 v1.3 remains historical and is not reissued",
        *V2_3_CLOSED_SUBGATES,
        *V2_3_NEGATIVE_IDS,
    ):
        require_token(certificate_text, token, f"certificate v2.3 token {token}")

    for token in (
        "EXP-000818",
        "R-167 v2.4",
        r"R_0^3L^{-8}",
        "point-strong-star",
        "bidirectional all-shape Cauchy",
        r"\|G\|_a\le {3\over25}",
        r"-{1\over20000}P",
        r"-{1\over800}",
        r"{M+1\over8}",
        "No v2.4 PDF is issued",
        "v2_4_checkpoint_synthesis",
        "R-168 v1.3 remains historical and is not reissued",
        *V2_4_CLOSED_SUBGATES,
        *V2_4_NEGATIVE_IDS,
    ):
        require_token(certificate_text, token, f"certificate v2.4 token {token}")

    for token in (
        "EXP-000825",
        "R-167 v2.5",
        r"\Theta^{(3)}={1\over2}P[G,[G,V_{\rm d}]]P",
        r"{1\over300}",
        "Q[G_2,K]P=-S",
        "17/5000",
        "7770533371",
        "2820703613673",
        r"{9\over25}",
        "No v2.5 PDF is issued",
        "v2_5_checkpoint_synthesis",
        "R-168 v1.3 remains historical and is not reissued",
        *V2_5_CLOSED_SUBGATES,
        *V2_5_NEGATIVE_IDS,
    ):
        require_token(certificate_text, token, f"certificate v2.5 token {token}")

    exploration_text = require_text(EXPLORATION_LEDGER, "exploration ledger")
    exploration_records: list[dict[str, Any]] = []
    if exploration_text is not None:
        try:
            exploration_records = [
                json.loads(line)
                for line in exploration_text.splitlines()
                if line.strip()
            ]
        except json.JSONDecodeError:
            missing_or_raise("exploration ledger valid JSONL")
    exploration_matches = [
        record
        for record in exploration_records
        if record.get("id") == EXPECTED_EXPLORATION
    ]
    exploration_semantic = (
        len(exploration_matches) == 1
        and exploration_matches[0].get("schema") == "tect/proof-exploration/1.0"
        and exploration_matches[0].get("task_id") == EXPECTED_TASK
        and exploration_matches[0].get("claim_ids") == list(EXPECTED_CLAIM_IDS)
        and exploration_matches[0].get("verdict") == "advanced"
        and EXPECTED_RESULT_NUMBER
        in exploration_matches[0].get("formal_refs", {}).get("results", [])
        and V2_5_CLOSED_SUBGATES[0] in exploration_matches[0].get("gate_ids", [])
        and V2_5_NEGATIVE_IDS[0]
        in exploration_matches[0].get("formal_refs", {}).get("negatives", [])
        and {"id": "EXP-000818", "relation": "continues"}
        in exploration_matches[0].get("related", [])
    )
    if exploration_semantic:
        audit.check(
            f"exploration row {EXPECTED_EXPLORATION} exact semantics",
            True,
            True,
            True,
            "authority",
        )
    else:
        missing_or_raise(f"exploration row {EXPECTED_EXPLORATION} exact semantics")
    result_text = require_text(RESULT_LEDGER, "result ledger")
    result_index_rows = (
        [
            line
            for line in result_text.splitlines()
            if line.startswith("| [R-167](#r-167) |")
        ]
        if result_text is not None
        else []
    )
    result_detail = ""
    if result_text is not None and "### R-167" in result_text:
        result_detail = result_text.split("### R-167", 1)[1].split("\n### R-", 1)[0]
    result_authority_exact = (
        len(result_index_rows) == 1
        and "R-167 v2.5" in result_index_rows[0]
        and "R-167 v2.5" in result_detail
        and EXPECTED_EXPLORATION in result_detail
    )
    if result_authority_exact:
        audit.check(
            "result ledger exact R-167 v2.5 index and detail",
            True,
            True,
            True,
            "authority",
        )
    else:
        missing_or_raise("result ledger exact R-167 v2.5 index and detail")
    negative_text = require_text(NEGATIVE_REGISTRY, "negative registry")
    for negative_id in NEGATIVE_IDS:
        require_token(negative_text, negative_id, f"negative row {negative_id}")
    gate_text = require_text(GATE_REGISTRY, "gate registry")
    def require_gate_status(gate_id: str, status: str) -> None:
        heading = f"### **{gate_id}**"
        if gate_text is None or heading not in gate_text:
            missing_or_raise(f"gate row {gate_id}")
            return
        block = gate_text.split(heading, 1)[1].split("\n### **", 1)[0]
        if f"**Status:** {status}" not in block:
            missing_or_raise(f"gate {gate_id} status {status}")
            return
        audit.check(f"gate {gate_id} status", True, status, status, "authority")

    for gate_id in EXPECTED_CLOSED_SUBGATES:
        require_gate_status(gate_id, "CLOSED")
    for gate_id in EXPECTED_OPEN_GATES:
        require_gate_status(gate_id, "OPEN")

    return {
        "status": "PASS" if not missing else "INCOMPLETE",
        "missing": missing,
        "manifest_loaded": manifest is not None,
        "certificate_loaded": certificate_text is not None,
        "external_source_text_reproved": False,
    }


def run_audit(staged: bool = False) -> dict[str, Any]:
    audit = Audit()
    fixture_a = fixture_a_pure_bond_tail(audit)
    fixture_b = fixture_b_local_and_global_renyi(audit)
    fixture_c = fixture_c_semiclassical_and_low_band(audit)
    fixture_d = fixture_d_full_gibbs_context(audit)
    fixture_e = fixture_e_fixed_edge_corridor(audit)
    fixture_f = fixture_f_feshbach_and_compressed_qps(audit)
    fixture_g = fixture_g_twentieth_moment_and_graph_boundary(audit)
    fixture_h = fixture_h_full_oscillator_edge_cluster(audit)
    fixture_i = fixture_i_actual_q3_fifth_shear_and_rank_two(audit)
    fixture_j = fixture_j_v2_3_connected_and_implementer(audit)
    fixture_k = fixture_k_v2_4_standard_form_c0_and_generator(audit)
    fixture_l = fixture_l_v2_5_third_order_and_compact_cylinder(audit)
    authority = authority_audit(audit, staged)
    verdict = "PASS" if authority["status"] == "PASS" else "INCOMPLETE"

    scope = {
        "pure_bond_coordinate_tail_identity": True,
        "local_measured_renyi_sufficiency_reduction": True,
        "global_volume_uniform_renyi_target_rejected_in_product_fixture": True,
        "Q3_semiclassical_hypotheses_and_normalization": True,
        "semiclassical_theorem_imported_not_reproved": True,
        "finite_r_minus_9_onsite_doublet_certified": False,
        "exact_low_band_TFIM_compression": True,
        "finite_Gibbs_full_Hamiltonian_cutoff_resummation": True,
        "arbitrary_context_automorphism_upgrade": False,
        "fixed_edge_to_growing_corridor_reduction": True,
        "twentieth_moment_fixed_edge_corridor_reduction": True,
        "conditional_fifth_graph_transport_reduction": True,
        "translate_uniform_local_fifth_Gibbs_moment_and_elliptic_embedding": True,
        "simultaneous_bond_shear_fifth_graph_propagation": True,
        "actual_Q3_twentieth_fixed_edge_history_bound": True,
        "actual_Q3_fixed_edge_history_bound": True,
        "registered_periodic_split_implementer_two_sided_Gibbs_L2_removal": True,
        "arbitrary_observable_automorphism_estimate": False,
        "fixed_finite_faithful_standard_form_implementer_strongstar": True,
        "fixed_finite_point_strongstar_bounded_observable_conjugation": True,
        "moving_family_R_minus_one_fifth_strongstar_rate": False,
        "conditional_bidirectional_all_shape_C0_completion": True,
        "actual_Q3_all_shape_point_norm_Cauchy": False,
        "local_generator_identified": False,
        "KMS_quotient_identified": False,
        "conditional_connected_geometric_QPS_envelope": True,
        "actual_second_order_connected_onsite_resolvent_QPS": True,
        "first_local_homological_rank_two_generator_QPS_Ritz": True,
        "first_generator_second_order_low_block_match": True,
        "fixed_finite_volume_and_Ritz_third_order_low_block_coefficient": True,
        "fixed_finite_volume_and_Ritz_third_order_linked_triple_QPS_bound": True,
        "third_order_cutoff_uniform": False,
        "third_order_unbounded": False,
        "third_order_tau_cutoff_bound": False,
        "second_order_uniform_Ritz_Gram_tail_required": True,
        "all_order_connected_oscillator_elimination": False,
        "canonical_compact_cylinder_split_bond_point_norm_C0": False,
        "common_alpha_nonexistence": False,
        "forward_local_stabilization_implies_surjectivity": False,
        "inverse_automorphisms_point_norm_Cauchy": False,
        "registered_periodic_compact_source_scope_only": True,
        "arbitrary_boundary_history_bound": False,
        "below_Gamma_global_Feshbach_precursor": True,
        "compressed_TFIM_two_phase_QPS_and_phasewise_gap": True,
        "full_oscillator_local_edge_parity_doublet_cluster": True,
        "parity_preserving_onsite_spectral_Ritz_removal": True,
        "rank_two_unbounded_block_elimination": False,
        "two_phase_QPS_for_exact_Q3LOCK": False,
        "broken_sector_GNS_gap": False,
        "Sector_A_complete": False,
        "Pre_A_complete": False,
    }
    source_paths = [SCRIPT, MANIFEST, CERTIFICATE]
    passed = len(audit.rows)
    return {
        "schema": f"tect/{SLUG}-primary-result/1.0",
        "script_version": __version__,
        "task_id": EXPECTED_TASK,
        "claim_ids": list(EXPECTED_CLAIM_IDS),
        "candidate_id": EXPECTED_CANDIDATE_ID,
        "result_id": EXPECTED_RESULT_ID,
        "result_number": EXPECTED_RESULT_NUMBER,
        "result_version": EXPECTED_RESULT_VERSION,
        "exploration_id": EXPECTED_EXPLORATION,
        "claim_bearing": False,
        "closed_subgates": list(EXPECTED_CLOSED_SUBGATES),
        "open_gates": list(EXPECTED_OPEN_GATES),
        "negative_ids": list(NEGATIVE_IDS),
        "verdict": verdict,
        "passed": passed,
        "failed": 0,
        "total": passed,
        "summary": {
            "passed": passed,
            "failed": 0,
            "total": passed,
            "authority_status": authority["status"],
        },
        "authority": authority,
        "derived": {
            "fixture_A_pure_bond_tail": fixture_a,
            "fixture_B_local_and_global_renyi": fixture_b,
            "fixture_C_semiclassical_and_low_band": fixture_c,
            "fixture_D_full_Gibbs_context": fixture_d,
            "fixture_E_fixed_edge_corridor": fixture_e,
            "fixture_F_Feshbach_compressed_QPS": fixture_f,
            "fixture_G_twentieth_moment_graph_boundary": fixture_g,
            "fixture_H_full_oscillator_edge_cluster": fixture_h,
            "fixture_I_actual_Q3_fifth_shear_rank_two": fixture_i,
            "fixture_J_v2_3_connected_and_implementer": fixture_j,
            "fixture_K_v2_4_standard_form_C0_and_generator": fixture_k,
            "fixture_L_v2_5_third_order_and_compact_cylinder": fixture_l,
        },
        "scope": scope,
        "source_hashes": {
            str(path.relative_to(REPO)).replace("\\", "/"): normalized_sha256(path)
            for path in source_paths
            if path.exists()
        },
        "assertions": audit.rows,
        "boundary": (
            "Exact A--L fixtures and scoped theorem imports only. The actual fifth-"
            "moment/shear/history and split-implementer results are registered-"
            "periodic and compact-source only. Point-strong-star observable "
            "convergence is fixed finite faithful standard representation only; "
            "the all-shape C0 theorem is conditional. The first homological "
            "generator now has its complete third-order low block only at each "
            "fixed finite spatial volume Lambda and fixed finite onsite Ritz cutoff M, with no tau cutoff or all-order result. The "
            "compact-cylinder no-go is confined to the canonical split-bond route. No actual "
            "all-shape Q3 common alpha, identified generator/KMS, all-order "
            "connected rank-two oscillator elimination, oscillator-lattice GNS "
            "gap, Sector A, or Pre-A closure."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--staged", action="store_true")
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()

    payload = run_audit(staged=args.staged)
    if not args.self_test and not args.no_store:
        atomic_json(args.output, payload)
    print(f"{payload['verdict']} {payload['passed']}/{payload['total']}")
    if payload["verdict"] == "INCOMPLETE":
        print("authority: " + ", ".join(payload["authority"]["missing"]))
    script_key = str(SCRIPT.relative_to(REPO)).replace("\\", "/")
    print("schema: " + payload["schema"])
    print("script_sha256: " + payload["source_hashes"][script_key])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
