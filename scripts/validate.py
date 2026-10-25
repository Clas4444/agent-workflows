#!/usr/bin/env python3
"""Validate the portable loop-skills repository without third-party packages."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path


if __package__:
    from .routing_check import check_routes
    from .catalog import check_catalog
    from .skill_resources import check_resources, plain_chain
    from .instruction_history import check_history
    from .validation.manifest import DEFAULT_ROOTS, NAME_PATTERN, Manifest, load_manifest
    from .validation.skill_format import FRONTMATTER_PATTERN, frontmatter_value, check_format
    from .validation.loop_policy import REQUIRED_STATUSES, REQUIRED_SECTIONS, check_loop_policy
else:
    from routing_check import check_routes
    from catalog import check_catalog
    from skill_resources import check_resources, plain_chain
    from instruction_history import check_history
    from validation.manifest import DEFAULT_ROOTS, NAME_PATTERN, Manifest, load_manifest
    from validation.skill_format import FRONTMATTER_PATTERN, frontmatter_value, check_format
    from validation.loop_policy import REQUIRED_STATUSES, REQUIRED_SECTIONS, check_loop_policy

GENERATED_FILES = ("docs/VALIDATION-RESULT.md",)

def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def validate(repo: Path, profile: str = "loop") -> list[str]:
    if profile not in ("loop", "format"):
        raise ValueError("profile must be loop or format")
    manifest, errors = load_manifest(repo)
    if manifest is None or errors:
        return errors

    if (repo / 'skill-groups.json').exists():
        errors.extend(check_catalog(repo))
    if (repo / 'skill-routing.json').exists():
        errors.extend(check_routes(repo))

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
            try:
                plain_chain(repo,path)
            except (OSError,ValueError) as exc:
                errors.append(f"unsafe skill source {root}/{skill}: {exc}")
                continue
            if not path.is_file():
                errors.append(f"missing {path.relative_to(repo)}")
                continue

            label = str(path.relative_to(repo))
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeError) as exc:
                errors.append(f"{label} cannot read UTF-8 instruction: {exc}")
                continue
            errors.extend(check_format(text, skill, label))
            if profile == "loop":
                errors.extend(check_loop_policy(text, skill, label))

        existing = []
        for path in copies:
            try:
                plain_chain(repo,path)
                if path.is_file():
                    existing.append(path)
            except (OSError,ValueError):
                pass  # Already reported before reading the instruction.
        if existing:
            hashes = {sha256(path) for path in existing}
            if len(hashes) != 1:
                errors.append(f"copies of {skill}/SKILL.md are not identical")
        if skill in ("loop-orchestrate", "loop-prompt"):
            runner = repo / "scripts" / "run_loop.py"
            for root in manifest.roots:
                bundled = repo / root / skill / "scripts" / "run_loop.py"
                try:
                    plain_chain(repo,runner)
                    plain_chain(repo,bundled)
                except (OSError,ValueError) as exc:
                    errors.append(f"unsafe runner for {root}/{skill}: {exc}")
                    continue
                if not runner.is_file() or not bundled.is_file():
                    errors.append(f"missing runner for {root}/{skill}")
                elif runner.read_bytes() != bundled.read_bytes():
                    errors.append(f"stale runner for {root}/{skill}")

    errors.extend(check_resources(repo,list(manifest.skills),list(manifest.roots)))
    errors.extend(check_history(repo))
    return errors


def validation_fingerprint(repo: Path) -> str:
    digest = hashlib.sha256()
    digest.update(b"loop-validation-tree-v2\n")
    paths = [
        path
        for path in repo.rglob("*")
        if path.is_file()
        and ".git" not in path.relative_to(repo).parts
        and ".loop" not in path.relative_to(repo).parts
        and "__pycache__" not in path.relative_to(repo).parts
        and str(path.relative_to(repo)).replace("\\", "/") not in GENERATED_FILES
    ]
    for path in sorted(paths, key=lambda item: item.relative_to(repo).as_posix()):
        # Frame records so filename/content boundaries cannot collide, e.g.
        # a='bc' versus ab='c'. JSON escapes filenames containing newlines.
        record = [path.relative_to(repo).as_posix(), sha256(path)]
        digest.update(json.dumps(record, ensure_ascii=True, separators=(",", ":")).encode("ascii"))
        digest.update(b"\n")
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
    parser.add_argument("--profile", choices=("loop", "format"), default="loop",
                        help="loop: full project gate; format: metadata subset plus repository integrity")
    for name in ("tests", "ci", "runtime"):
        parser.add_argument(f"--{name}-status", choices=("PASS", "FAIL", "BLOCKED", "NOT_RUN"), default="NOT_RUN")
    args = parser.parse_args()
    if args.write_summary and args.profile != "loop":
        parser.error("--write-summary requires the full loop profile")
    errors = validate(args.repo.resolve(), profile=args.profile)
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
