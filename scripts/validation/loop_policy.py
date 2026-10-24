"""Project-specific Loop conventions, separate from the shared skill format."""
import re
from .skill_format import FRONTMATTER_PATTERN

REQUIRED_STATUSES = ("PASS", "FAIL", "BLOCKED", "NOT_RUN")
REQUIRED_SECTIONS = ("Use when", "Inputs", "Workflow", "Output", "Boundaries and evidence", "Example")
BREAK_PATTERNS = (
    r"no (?:suitable )?work",
    r"no new .* remain",
    r"(?:identical|materially identical|duplicate).{0,80}(?:three|3)",
    r"never sleep",
)
STOP_PATTERN = re.compile(r"stop|end|terminate", re.IGNORECASE)

def check_loop_policy(text: str, skill: str, label: str) -> list[str]:
    errors = []
    match = FRONTMATTER_PATTERN.match(text)
    frontmatter_text = match.group(1) if match else ""
    for flag in ("user-invocable", "disable-model-invocation"):
        if not re.search(rf"(?m)^{re.escape(flag)}:[ \t]*(true|false)[ \t]*$", frontmatter_text):
            errors.append(f"{label} has invalid boolean {flag}")
    positions = []
    for section in REQUIRED_SECTIONS:
        matches = list(re.finditer(rf"(?m)^## {re.escape(section)}\s*$", text))
        if len(matches) != 1:
            errors.append(f"{label} requires one {section} section")
        else:
            positions.append(matches[0].start())
    if positions != sorted(positions):
        errors.append(f"{label} has out-of-order contract sections")
    if f"/{skill} " not in text:
        errors.append(f"{label} omits its invocation example")
    if len(text.splitlines()) > 500:
        errors.append(f"{label} exceeds 500 lines")
    for status in REQUIRED_STATUSES:
        if not re.search(rf"\b{status}\b", text):
            errors.append(f"{label} omits {status}")
    if not any(re.search(pattern, text, re.IGNORECASE | re.DOTALL) for pattern in BREAK_PATTERNS):
        errors.append(f"{label} omits a recognizable break condition")
    if not STOP_PATTERN.search(text):
        errors.append(f"{label} omits an explicit stop instruction")
    if not re.search(r"never\s+sleep", text, re.IGNORECASE):
        errors.append(f"{label} omits never-sleep policy")
    return errors
