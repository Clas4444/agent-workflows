#!/usr/bin/env python3
"""Validate the portable loop-skills repository without third-party packages."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path


ROOTS = (".github/skills", ".agents/skills", ".claude/skills")
REQUIRED_STATUSES = ("PASS", "FAIL", "BLOCKED", "NOT_RUN")
BREAK_PATTERNS = (
    r"no (?:suitable )?work",
    r"no new .* remain",
    r"(?:identical|materially identical|duplicate).{0,80}(?:three|3)",
    r"never sleep",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def frontmatter_value(text: str, key: str) -> str | None:
    match = re.search(rf"(?m)^{re.escape(key)}:\s*(.+?)\s*$", text)
    return match.group(1).strip().strip('"') if match else None


def validate(repo: Path) -> list[str]:
    errors: list[str] = []
    manifest_path = repo / "skills-manifest.json"
    if not manifest_path.is_file():
        return ["missing skills-manifest.json"]

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"invalid skills-manifest.json: {exc}"]

    skills = manifest.get("skills")
    if not isinstance(skills, list) or not all(isinstance(item, str) for item in skills):
        return ["manifest skills must be a list of strings"]

    expected_roots = list(ROOTS)
    if manifest.get("project_skill_roots") != expected_roots:
        errors.append("manifest project_skill_roots does not match repository roots")

    actual = sorted(
        path.name
        for path in (repo / ROOTS[0]).iterdir()
        if path.is_dir()
    ) if (repo / ROOTS[0]).is_dir() else []
    if sorted(skills) != actual:
        errors.append(f"manifest skills do not match .github/skills: {sorted(skills)} != {actual}")

    for skill in skills:
        copies: list[Path] = []
        for root in ROOTS:
            path = repo / root / skill / "SKILL.md"
            copies.append(path)
            if not path.is_file():
                errors.append(f"missing {path.relative_to(repo)}")
                continue

            text = path.read_text(encoding="utf-8")
            lines = text.splitlines()
            if not text.startswith("---\n") and not text.startswith("---\r\n"):
                errors.append(f"{path.relative_to(repo)} has no YAML frontmatter")
            if frontmatter_value(text, "name") != skill:
                errors.append(f"{path.relative_to(repo)} has mismatched name")
            description = frontmatter_value(text, "description")
            if not description:
                errors.append(f"{path.relative_to(repo)} has no description")
            if len(lines) > 500:
                errors.append(f"{path.relative_to(repo)} exceeds 500 lines")
            for status in REQUIRED_STATUSES:
                if status not in text:
                    errors.append(f"{path.relative_to(repo)} omits {status}")
            if not any(re.search(pattern, text, re.IGNORECASE | re.DOTALL) for pattern in BREAK_PATTERNS):
                errors.append(f"{path.relative_to(repo)} omits a recognizable break condition")

        existing = [path for path in copies if path.is_file()]
        if existing:
            hashes = {sha256(path) for path in existing}
            if len(hashes) != 1:
                errors.append(f"copies of {skill}/SKILL.md are not identical")

    return errors


def write_summary(repo: Path, errors: list[str]) -> None:
    status = "PASS" if not errors else "FAIL"
    details = "\n".join(f"- {error}" for error in errors) or "- No validation errors."
    try:
        commit = subprocess.check_output(
            ("git", "-C", str(repo), "rev-parse", "HEAD"),
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        commit = "unavailable"
    try:
        dirty = bool(
            subprocess.check_output(
                ("git", "-C", str(repo), "status", "--porcelain"),
                text=True,
                stderr=subprocess.DEVNULL,
            ).strip()
        )
    except (OSError, subprocess.CalledProcessError):
        dirty = False
    output = (
        "# Validation Result\n\n"
        f"- Result: `{status}`\n"
        f"- Validator: `scripts/validate.py`\n"
        f"- Repository commit: `{commit}`\n\n"
        f"- Working tree changes present: `{str(dirty).lower()}`\n\n"
        "## Findings\n\n"
        f"{details}\n"
    )
    (repo / "docs" / "VALIDATION-RESULT.md").write_text(output, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--write-summary", action="store_true")
    args = parser.parse_args()
    errors = validate(args.repo.resolve())
    if args.write_summary:
        write_summary(args.repo.resolve(), errors)
    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PASS: structural validation")
    return 0


if __name__ == "__main__":
    sys.exit(main())
