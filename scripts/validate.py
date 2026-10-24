#!/usr/bin/env python3
"""Validate the portable loop-skills repository without third-party packages."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


DEFAULT_ROOTS = (".github/skills", ".agents/skills", ".claude/skills")
GENERATED_FILES = ("docs/VALIDATION-RESULT.md",)
REQUIRED_STATUSES = ("PASS", "FAIL", "BLOCKED", "NOT_RUN")
REQUIRED_SECTIONS = ("Use when", "Inputs", "Workflow", "Output", "Boundaries and evidence", "Example")
NAME_PATTERN = re.compile(r"(?=.{1,64}$)[a-z0-9]+(?:-[a-z0-9]+)*$")
BREAK_PATTERNS = (
    r"no (?:suitable )?work",
    r"no new .* remain",
    r"(?:identical|materially identical|duplicate).{0,80}(?:three|3)",
    r"never sleep",
)
STOP_PATTERN = re.compile(r"stop|end|terminate", re.IGNORECASE)
FRONTMATTER_PATTERN = re.compile(r"\A---(?:\r?\n)(.*?)(?:\r?\n)---(?:\r?\n|\Z)", re.DOTALL)


@dataclass(frozen=True)
class Manifest:
    version: str
    skills: tuple[str, ...]
    roots: tuple[str, ...]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def frontmatter_value(frontmatter: str, key: str) -> str | None:
    match = re.search(rf"(?m)^{re.escape(key)}:[ \t]*([^\r\n]*)", frontmatter)
    return (match.group(1).strip().strip('"').strip("'") or None) if match else None


def load_manifest(repo: Path) -> tuple[Manifest | None, list[str]]:
    errors: list[str] = []
    manifest_path = repo / "skills-manifest.json"
    if not manifest_path.is_file():
        return None, ["missing skills-manifest.json"]

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return None, [f"invalid skills-manifest.json: {exc}"]

    if not isinstance(manifest, dict):
        return None, ["manifest must be a JSON object"]
    version = manifest.get("version")
    if not isinstance(version, str) or not re.fullmatch(r"\d+\.\d+\.\d+(?:-[a-z0-9.-]+)?", version):
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


def validate(repo: Path) -> list[str]:
    manifest, errors = load_manifest(repo)
    if manifest is None or errors:
        return errors

    for root in manifest.roots:
        root_path = repo / root
        actual = sorted(path.name for path in root_path.iterdir() if path.is_dir()) if root_path.is_dir() else []
        if sorted(manifest.skills) != actual:
            errors.append(f"{root} directories do not match manifest")

    for skill in manifest.skills:
        copies: list[Path] = []
        for root in manifest.roots:
            path = repo / root / skill / "SKILL.md"
            copies.append(path)
            if not path.is_file():
                errors.append(f"missing {path.relative_to(repo)}")
                continue

            text = path.read_text(encoding="utf-8")
            lines = text.splitlines()
            frontmatter = FRONTMATTER_PATTERN.match(text)
            if not frontmatter:
                errors.append(f"{path.relative_to(repo)} has no YAML frontmatter")
                frontmatter_text = ""
            else:
                frontmatter_text = frontmatter.group(1)
                if text[frontmatter.end():].lstrip().startswith("---"):
                    errors.append(f"{path.relative_to(repo)} has an extra frontmatter boundary")
            name = frontmatter_value(frontmatter_text, "name")
            if name != skill or not NAME_PATTERN.fullmatch(name or ""):
                errors.append(f"{path.relative_to(repo)} has mismatched name")
            description = frontmatter_value(frontmatter_text, "description")
            if not description:
                errors.append(f"{path.relative_to(repo)} has no description")
            elif len(description) > 1024:
                errors.append(f"{path.relative_to(repo)} description exceeds 1024 characters")
            for key in ("name", "description", "argument-hint", "user-invocable", "disable-model-invocation"):
                if len(re.findall(rf"(?m)^{re.escape(key)}:", frontmatter_text)) > 1:
                    errors.append(f"{path.relative_to(repo)} has duplicate metadata key {key}")
            for flag in ("user-invocable", "disable-model-invocation"):
                if not re.search(rf"(?m)^{re.escape(flag)}:[ \t]*(true|false)[ \t]*$", frontmatter_text):
                    errors.append(f"{path.relative_to(repo)} has invalid boolean {flag}")
            positions = []
            for section in REQUIRED_SECTIONS:
                matches = list(re.finditer(rf"(?m)^## {re.escape(section)}\s*$", text))
                if len(matches) != 1:
                    errors.append(f"{path.relative_to(repo)} requires one {section} section")
                else:
                    positions.append(matches[0].start())
            if positions != sorted(positions):
                errors.append(f"{path.relative_to(repo)} has out-of-order contract sections")
            if f"/{skill} " not in text:
                errors.append(f"{path.relative_to(repo)} omits its invocation example")
            if len(lines) > 500:
                errors.append(f"{path.relative_to(repo)} exceeds 500 lines")
            for status in REQUIRED_STATUSES:
                if not re.search(rf"\b{status}\b", text):
                    errors.append(f"{path.relative_to(repo)} omits {status}")
            if not any(re.search(pattern, text, re.IGNORECASE | re.DOTALL) for pattern in BREAK_PATTERNS):
                errors.append(f"{path.relative_to(repo)} omits a recognizable break condition")
            if not STOP_PATTERN.search(text):
                errors.append(f"{path.relative_to(repo)} omits an explicit stop instruction")
            if not re.search(r"never\s+sleep", text, re.IGNORECASE):
                errors.append(f"{path.relative_to(repo)} omits never-sleep policy")

        existing = [path for path in copies if path.is_file()]
        if existing:
            hashes = {sha256(path) for path in existing}
            if len(hashes) != 1:
                errors.append(f"copies of {skill}/SKILL.md are not identical")
        if skill in ("loop-orchestrate", "loop-prompt"):
            runner = repo / "scripts" / "run_loop.py"
            for root in manifest.roots:
                bundled = repo / root / skill / "scripts" / "run_loop.py"
                if not runner.is_file() or not bundled.is_file():
                    errors.append(f"missing runner for {root}/{skill}")
                elif runner.read_bytes() != bundled.read_bytes():
                    errors.append(f"stale runner for {root}/{skill}")

    return errors


def validation_fingerprint(repo: Path) -> str:
    digest = hashlib.sha256()
    paths = [
        path
        for path in repo.rglob("*")
        if path.is_file()
        and ".git" not in path.parts
        and ".loop" not in path.parts
        and "__pycache__" not in path.parts
        and str(path.relative_to(repo)).replace("\\", "/") not in GENERATED_FILES
    ]
    for path in sorted(paths):
        digest.update(str(path.relative_to(repo)).encode("utf-8"))
        digest.update(path.read_bytes() if path.is_file() else b"<missing>")
    return digest.hexdigest()


def git_value(repo: Path, *args: str) -> str | None:
    try:
        return subprocess.check_output(
            ("git", "-C", str(repo), *args),
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def write_summary(
    repo: Path,
    errors: list[str],
    tests_status: str = "NOT_RUN",
    ci_status: str = "NOT_RUN",
    runtime_status: str = "NOT_RUN",
) -> None:
    status = "PASS" if not errors else "FAIL"
    details = "\n".join(f"- {error}" for error in errors) or "- No validation errors."
    manifest, manifest_errors = load_manifest(repo)
    base_commit = git_value(repo, "rev-parse", "HEAD") or "unavailable"
    dirty = bool(git_value(repo, "status", "--porcelain"))
    fingerprint = validation_fingerprint(repo) if manifest and not manifest_errors else "unavailable"
    revision = f"working-tree:{fingerprint} (base commit {base_commit})" if dirty else base_commit
    output = (
        "# Validation Result\n\n"
        f"- Structural validation: `{status}`\n"
        f"- Validator: `scripts/validate.py`\n"
        f"- Validated source revision: `{revision}`\n"
        f"- Base commit: `{base_commit}`\n"
        f"- Working tree changes present: `{str(dirty).lower()}`\n"
        f"- Automated validator tests: `{tests_status}`\n"
        f"- CI result: `{ci_status}`\n"
        f"- Agent runtime tests: `{runtime_status}` (see `docs/RUNTIME-TEST-MATRIX.md`)\n\n"
        "## Findings\n\n"
        f"{details}\n"
    )
    (repo / "docs" / "VALIDATION-RESULT.md").write_text(output, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--write-summary", action="store_true")
    for name in ("tests", "ci", "runtime"):
        parser.add_argument(f"--{name}-status", choices=("PASS", "FAIL", "BLOCKED", "NOT_RUN"), default="NOT_RUN")
    args = parser.parse_args()
    errors = validate(args.repo.resolve())
    if args.write_summary:
        write_summary(args.repo.resolve(), errors, args.tests_status, args.ci_status, args.runtime_status)
    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PASS: structural validation")
    return 0


if __name__ == "__main__":
    sys.exit(main())
