"""Manifest parsing and repository path policy (not Agent Skills metadata)."""
import re
from dataclasses import dataclass
from pathlib import Path
from .json_data import loads_json

DEFAULT_ROOTS = (".github/skills", ".agents/skills", ".claude/skills")
NAME_PATTERN = re.compile(r"(?=.{1,64}$)[a-z0-9]+(?:-[a-z0-9]+)*$")
_NUMBER = r"(?:0|[1-9][0-9]*)"
_PRERELEASE = r"(?:0|[1-9][0-9]*|[0-9A-Za-z-]*[A-Za-z-][0-9A-Za-z-]*)"
_BUILD = r"[0-9A-Za-z-]+"
VERSION_PATTERN = re.compile(
    rf"{_NUMBER}\.{_NUMBER}\.{_NUMBER}(?:-{_PRERELEASE}(?:\.{_PRERELEASE})*)?"
    rf"(?:\+{_BUILD}(?:\.{_BUILD})*)?"
)

@dataclass(frozen=True)
class Manifest:
    version: str
    skills: tuple[str, ...]
    roots: tuple[str, ...]


def load_manifest(repo: Path) -> tuple[Manifest | None, list[str]]:
    errors: list[str] = []
    manifest_path = repo / "skills-manifest.json"
    if not manifest_path.is_file():
        return None, ["missing skills-manifest.json"]

    try:
        manifest = loads_json(manifest_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return None, [f"invalid skills-manifest.json: {exc}"]

    if not isinstance(manifest, dict):
        return None, ["manifest must be a JSON object"]
    version = manifest.get("version")
    if not isinstance(version, str) or not VERSION_PATTERN.fullmatch(version):
        errors.append("manifest version must use semantic version syntax")
    skills = manifest.get("skills")
    if not isinstance(skills, list) or not all(isinstance(item, str) for item in skills):
        return None, errors + ["manifest skills must be a list of strings"]
    if len(skills) != len(set(skills)):
        errors.append("manifest skills contains duplicate entries")
    if not skills:
        errors.append("manifest skills must not be empty")
    if any(not NAME_PATTERN.fullmatch(skill) for skill in skills):
        errors.append("manifest contains an invalid skill name")

    roots = manifest.get("project_skill_roots")
    if not isinstance(roots, list) or not all(isinstance(root, str) for root in roots):
        return None, errors + ["manifest project_skill_roots must be a list of strings"]
    if len(roots) != len(set(roots)) or not roots:
        errors.append("manifest project_skill_roots must be non-empty and unique")
    if any(Path(root).is_absolute() or ".." in Path(root).parts for root in roots):
        errors.append("manifest project_skill_roots must contain safe relative paths")
    if tuple(roots) != DEFAULT_ROOTS:
        errors.append("manifest project_skill_roots must match supported native roots")

    return Manifest(
        version=version if isinstance(version, str) else "",
        skills=tuple(skills),
        roots=tuple(roots),
    ), errors
