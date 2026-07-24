"""Shared deterministic discovery rules for claim evidence paths."""

from pathlib import Path


def lineage_note_paths(claim_dir: Path) -> list[Path]:
    """Return exactly the notes represented by build_lineage.py."""
    paths: list[Path] = []
    notes_dir = claim_dir / "notes"
    if notes_dir.exists():
        paths.extend(sorted(notes_dir.glob("*.tex.txt"), key=lambda path: path.as_posix()))
    paths.extend(
        sorted(claim_dir.glob("*/notes/*.tex.txt"), key=lambda path: path.as_posix())
    )
    return list(dict.fromkeys(paths))


def unordered_root_note_paths(claim_dir: Path) -> list[Path]:
    """Return legacy root notes intentionally outside the ordered lineage."""
    return sorted(claim_dir.glob("*.tex.txt"), key=lambda path: path.as_posix())


def auditable_note_paths(claim_dir: Path) -> list[Path]:
    """Return every non-bundle note subject to the footer policy."""
    return list(
        dict.fromkeys(lineage_note_paths(claim_dir) + unordered_root_note_paths(claim_dir))
    )


def manifest_paths(claim_dir: Path) -> dict[str, list[Path]]:
    """Classify manifests without filesystem case-sensitivity assumptions."""
    claim_level: list[Path] = []
    bundle_top: list[Path] = []
    bundle_embedded: list[Path] = []
    for path in claim_dir.rglob("*"):
        if not path.is_file() or path.suffix.casefold() != ".json":
            continue
        relative_parts = path.relative_to(claim_dir).parts
        in_bundle = any(part.casefold() == "bundle" for part in relative_parts[:-1])
        name = path.name.casefold()
        if "manifest" not in name:
            continue
        if in_bundle and name == "manifest.json":
            bundle_top.append(path)
        elif in_bundle:
            bundle_embedded.append(path)
        else:
            claim_level.append(path)
    key = lambda path: path.as_posix()
    return {
        "claim_level": sorted(claim_level, key=key),
        "bundle_top": sorted(bundle_top, key=key),
        "bundle_embedded": sorted(bundle_embedded, key=key),
    }
