"""Core name/description checks for the supported single-line metadata subset.

This module is not a general YAML parser or an Agent Skills certification tool.
Host extension fields are optional here.
"""
import re
from .manifest import NAME_PATTERN

FRONTMATTER_PATTERN = re.compile(r"\A---(?:\r?\n)(.*?)(?:\r?\n)---(?:\r?\n|\Z)", re.DOTALL)

def frontmatter_value(frontmatter: str, key: str) -> str | None:
    match = re.search(rf"(?m)^{re.escape(key)}:[ \t]*([^\r\n]*)", frontmatter)
    return (match.group(1).strip().strip('"').strip("'") or None) if match else None


def check_format(text: str, skill: str, label: str) -> list[str]:
    errors = []
    frontmatter = FRONTMATTER_PATTERN.match(text)
    if not frontmatter:
        errors.append(f"{label} has no YAML frontmatter")
        frontmatter_text = ""
    else:
        frontmatter_text = frontmatter.group(1)
        if text[frontmatter.end():].lstrip().startswith("---"):
            errors.append(f"{label} has an extra frontmatter boundary")
    name = frontmatter_value(frontmatter_text, "name")
    if name != skill or not NAME_PATTERN.fullmatch(name or ""):
        errors.append(f"{label} has mismatched name")
    description = frontmatter_value(frontmatter_text, "description")
    if not description:
        errors.append(f"{label} has no description")
    elif len(description) > 1024:
        errors.append(f"{label} description exceeds 1024 characters")
    for key in ("name", "description", "argument-hint", "user-invocable", "disable-model-invocation"):
        if len(re.findall(rf"(?m)^{re.escape(key)}:", frontmatter_text)) > 1:
            errors.append(f"{label} has duplicate metadata key {key}")
    return errors
