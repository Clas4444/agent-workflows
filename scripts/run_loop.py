#!/usr/bin/env python3
"""Run bounded follow-up prompts through a configured headless agent command."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

STATUSES = ("PASS", "FAIL", "BLOCKED", "NOT_RUN")
MAX_CAPTURE = 100_000


def make_prompt(base: str, iteration: int, previous: str) -> str:
    if iteration == 1:
        return base
    return (
        f"{base}\n\nThis is loop iteration {iteration}. Continue only if useful work "
        "remains. Review the previous iteration output below, verify progress, "
        "and finish with exactly one marker: LOOP_STATUS: PASS, FAIL, BLOCKED, "
        "or NOT_RUN.\n\nPrevious output:\n"
        f"{previous[-MAX_CAPTURE:]}"
    )


def make_follow_up_prompt(previous: str, iteration: int) -> str:
    return (
        f"You are continuing iteration {iteration}. Infer the single most useful "
        "next prompt from the previous result. Do not repeat completed work. "
        "Return exactly one line beginning with NEXT_PROMPT: followed by the "
        "next actionable prompt, then perform that prompt. Finish with exactly "
        "one marker: LOOP_STATUS: PASS, FAIL, BLOCKED, or NOT_RUN.\n\n"
        "Previous result:\n"
        f"{previous[-MAX_CAPTURE:]}"
    )


def extract_next_prompt(output: str) -> str | None:
    for line in output.splitlines():
        if line.startswith("NEXT_PROMPT:"):
            prompt = line.removeprefix("NEXT_PROMPT:").strip()
            if prompt:
                return prompt
    return None


def status_from(output: str, returncode: int) -> str:
    if returncode != 0:
        return "FAIL"
    markers = [
        line.strip()
        for line in output.splitlines()
        if line.strip().startswith("LOOP_STATUS:")
    ]
    if len(markers) != 1:
        return "NOT_RUN"
    marker = markers[0]
    for status in STATUSES:
        if marker == f"LOOP_STATUS: {status}":
            return status
    return "NOT_RUN"


def run_loop(args: argparse.Namespace) -> int:
    command = list(args.command)
    if not command:
        raise ValueError("an agent command is required after --")
    state_path = Path(args.state_file)
    report_path = Path(args.report_file)
    previous = ""
    current_prompt = args.prompt
    self_prompt = getattr(args, "self_prompt", False)
    iterations = []

    for iteration in range(1, args.max_iterations + 1):
        prompt = (
            current_prompt
            if not self_prompt or iteration == 1
            else make_follow_up_prompt(previous, iteration)
        )
        if self_prompt and iteration > 1 and (next_prompt := extract_next_prompt(previous)):
            prompt = (
                f"{next_prompt}\n\nAfter completing this prompt, infer the next "
                "useful prompt if another iteration is allowed. Emit exactly one "
                "NEXT_PROMPT: line and one LOOP_STATUS: marker."
            )
        command_args = [prompt if item == "{prompt}" else item for item in command]
        try:
            result = subprocess.run(
                command_args,
                input=None if "{prompt}" in command else prompt,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=args.timeout_seconds,
                check=False,
                shell=False,
            )
            output = (result.stdout + result.stderr)[-MAX_CAPTURE:]
            returncode = result.returncode
            status = status_from(output, returncode)
        except subprocess.TimeoutExpired as exc:
            output = f"timeout after {args.timeout_seconds}s: {exc}"
            returncode = None
            status = "BLOCKED"
        except OSError as exc:
            output = f"unable to start configured agent command: {exc}"
            returncode = None
            status = "BLOCKED"

        iterations.append(
            {
                "iteration": iteration,
                "status": status,
                "returncode": returncode,
                "output": output,
            }
        )
        previous = output
        if self_prompt and iteration < args.max_iterations:
            current_prompt = extract_next_prompt(output)
            if not current_prompt:
                status = "BLOCKED"
                iterations[-1]["status"] = status
        if status in ("FAIL", "BLOCKED") or (status == "PASS" and not self_prompt):
            break

    state = {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "requested_max_iterations": args.max_iterations,
        "timeout_seconds": args.timeout_seconds,
        "iterations": iterations,
        "final_status": iterations[-1]["status"] if iterations else "NOT_RUN",
    }
    state_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    report_path.write_text(
        "# Loop Run Report\n\n"
        f"- Final status: `{state['final_status']}`\n"
        f"- Iterations: `{len(iterations)}`\n"
        f"- State: `{state_path}`\n"
        f"- Report: `{report_path}`\n\n"
        "The report contains captured agent output. Review it for sensitive data "
        "before sharing.\n",
        encoding="utf-8",
    )
    return 0 if state["final_status"] == "PASS" else 1


def run_batch(args: argparse.Namespace, prompts: list[str]) -> int:
    batch_dir = Path(args.batch_dir)
    batch_dir.mkdir(parents=True, exist_ok=True)
    results = []
    for index, prompt in enumerate(prompts, start=1):
        single_args = argparse.Namespace(
            command=args.command,
            prompt=prompt,
            max_iterations=args.max_iterations,
            timeout_seconds=args.timeout_seconds,
            state_file=str(batch_dir / f"prompt-{index:03d}.json"),
            report_file=str(batch_dir / f"prompt-{index:03d}.md"),
            self_prompt=getattr(args, "self_prompt", False),
        )
        result = run_loop(single_args)
        state = json.loads(Path(single_args.state_file).read_text(encoding="utf-8"))
        results.append(
            {
                "prompt_number": index,
                "status": state["final_status"],
                "iterations": len(state["iterations"]),
                "exit_code": result,
            }
        )
    summary = {
        "prompt_count": len(prompts),
        "results": results,
        "final_status": "PASS" if results and all(item["status"] == "PASS" for item in results) else "FAIL",
    }
    (batch_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    (batch_dir / "summary.md").write_text(
        "# Loop Batch Report\n\n"
        f"- Prompt count: `{summary['prompt_count']}`\n"
        f"- Final status: `{summary['final_status']}`\n\n"
        + "\n".join(
            f"- Prompt {item['prompt_number']}: `{item['status']}`, "
            f"{item['iterations']} iteration(s)"
            for item in results
        )
        + "\n",
        encoding="utf-8",
    )
    return 0 if summary["final_status"] == "PASS" else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prompt")
    parser.add_argument("--prompt-file", help="UTF-8 file with one prompt per non-empty line")
    parser.add_argument("--self-prompt", action="store_true", help="derive each next prompt from the previous output")
    parser.add_argument("--follow-up-count", type=int, default=0, help="number of self-generated prompts after the initial prompt")
    parser.add_argument("--batch-dir", default=".loop/batch")
    parser.add_argument("--max-iterations", type=int, default=3)
    parser.add_argument("--timeout-seconds", type=int, default=600)
    parser.add_argument("--state-file", default=".loop/state.json")
    parser.add_argument("--report-file", default=".loop/report.md")
    parser.add_argument("command", nargs=argparse.REMAINDER, help="agent command after --; use {prompt} for an argument")
    args = parser.parse_args()
    if args.max_iterations < 1 or args.timeout_seconds < 1 or args.follow_up_count < 0:
        parser.error("max-iterations and timeout-seconds must be positive")
    if args.follow_up_count:
        args.self_prompt = True
        args.max_iterations = args.follow_up_count + 1
    if bool(args.prompt) == bool(args.prompt_file):
        parser.error("provide exactly one of --prompt or --prompt-file")
    if args.command and args.command[0] == "--":
        args.command.pop(0)
    try:
        if args.prompt_file:
            prompts = [
                line.strip()
                for line in Path(args.prompt_file).read_text(encoding="utf-8").splitlines()
                if line.strip() and not line.lstrip().startswith("#")
            ]
            if not prompts:
                parser.error("--prompt-file contains no prompts")
            return run_batch(args, prompts)
        return run_loop(args)
    except ValueError as exc:
        parser.error(str(exc))
        return 2


if __name__ == "__main__":
    sys.exit(main())
