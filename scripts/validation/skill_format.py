"""Core name/description checks for the supported single-line metadata subset.

This module is not a general YAML parser or an Agent Skills certification tool.
Host extension fields are optional here.
"""
import json
import re
from .manifest import NAME_PATTERN

FRONTMATTER_PATTERN = re.compile(r"\A---(?:\r?\n)(.*?)(?:\r?\n)---(?:\r?\n|\Z)", re.DOTALL)

def _comment_tail(tail: str) -> bool:
    return not tail.strip() or bool(re.fullmatch(r"[ \t]+#[^\r\n]*", tail))


def string_scalar(raw: str) -> str | None:
    """Decode the documented single-line string subset, rejecting other types.

    Double quotes use JSON-compatible escapes; single quotes use YAML's doubled
    apostrophe. Unsupported YAML constructs fail closed rather than being
    coerced to strings. This is intentionally not a general YAML loader.
    """
    raw = raw.strip()
    if not raw:
        return None
    if raw.startswith('"'):
        try:
            value, end = json.JSONDecoder().raw_decode(raw)
        except ValueError:
            return None
        if not isinstance(value, str) or not _comment_tail(raw[end:]):
            return None
    elif raw.startswith("'"):
        match = re.fullmatch(r"'((?:[^']|'')*)'(.*)", raw)
        if not match or not _comment_tail(match.group(2)):
            return None
        value = match.group(1).replace("''", "'")
    else:
        value = re.split(r"[ \t]+#", raw, maxsplit=1)[0].strip()
        if (not value or value[0] in "#[]{}&*!|>@`%"
                or re.search(r":[ \t]|:$", value)
                or value.lower() in ('null', '~', 'true', 'false', 'yes', 'no', 'on', 'off',
                                     '.inf', '+.inf', '-.inf', '.nan')
                or re.fullmatch(r"[-+]?(?:[0-9][0-9_]*(?:\.[0-9_]*)?(?:[eE][-+]?[0-9]+)?|\.[0-9_]+|0[xX][0-9a-fA-F_]+|0[oO][0-7_]+|0[bB][01_]+)", value)
                or re.match(r"[0-9]{4}-[0-9]{2}-[0-9]{2}(?:$|[Tt ])", value)):
            return None
    if any(ord(char) < 32 or 0xD800 <= ord(char) <= 0xDFFF for char in value):
        return None
    return value if value.strip() else None


def frontmatter_value(frontmatter: str, key: str) -> str | None:
    match = re.search(rf"(?m)^{re.escape(key)}[ \t]*:[ \t]*([^\r\n]*)", frontmatter)
    return string_scalar(match.group(1)) if match else None


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
        if len(re.findall(rf"(?m)^{re.escape(key)}[ \t]*:", frontmatter_text)) > 1:
            errors.append(f"{label} has duplicate metadata key {key}")
    return errors
