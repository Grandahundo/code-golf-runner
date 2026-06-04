#!/usr/bin/env python3
"""
Codex Task Runner — automatically complete programming tasks using Codex SDK.

Usage:
    python3 runner.py <task_directory>
    python3 runner.py test-hello
"""

import asyncio
import json
import os
import sys
import time
import subprocess
from datetime import datetime, timezone
from pathlib import Path

# Fix Windows console encoding for Unicode characters (e.g., ², λ)
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    # Suppress noisy asyncio cleanup warnings on Windows
    import warnings
    warnings.filterwarnings("ignore", category=ResourceWarning)

import yaml
from codex_sdk import (
    Codex,
    CodexOptions,
    ThreadOptions,
    ThreadHooks,
    TurnOptions,
    SandboxMode,
)


# ──────────────────────────────────────────────────────────────────────
# Config helpers
# ──────────────────────────────────────────────────────────────────────


def _load_yaml(path: Path) -> dict:
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}


def load_task_config(task_dir: Path) -> dict:
    """Load task_config.yaml from task directory, with defaults."""
    cfg = _load_yaml(task_dir / "task_config.yaml")
    cfg.setdefault("task_id", task_dir.name)
    cfg.setdefault("budget", {})
    cfg["budget"].setdefault("max_turns", 10)
    cfg["budget"].setdefault("max_tokens", 50000)
    cfg["budget"].setdefault("timeout_seconds", 600)
    cfg["budget"].setdefault("max_retries", 3)
    cfg["budget"].setdefault("turn_timeout_seconds", 1200)
    cfg.setdefault("sandbox_mode", "workspace-write")
    cfg.setdefault("verify", {})
    cfg["verify"].setdefault("command", None)
    cfg["verify"].setdefault("early_stop", True)
    return cfg


# ──────────────────────────────────────────────────────────────────────
# Codex binary discovery
# ──────────────────────────────────────────────────────────────────────


def _find_codex_binary() -> str | None:
    """Find the Codex CLI binary, handling platform quirks."""
    import shutil
    import platform

    candidates = []
    if platform.system().lower() == "windows":
        # codex-sdk looks for codex.exe; npm installs codex.cmd
        candidates = ["codex.exe", "codex.cmd", "codex"]
    else:
        candidates = ["codex"]

    for name in candidates:
        path = shutil.which(name)
        if path:
            return path
    return None


# ──────────────────────────────────────────────────────────────────────
# Task discovery
# ──────────────────────────────────────────────────────────────────────


def _find_task_md(task_dir: Path) -> Path | None:
    """Find task description file, supporting multiple naming conventions."""
    # Exact match first
    exact = task_dir / "task.md"
    if exact.exists():
        return exact
    # Pattern match: task*.md (e.g., task001.md, task_001.md)
    candidates = sorted(task_dir.glob("task*.md"))
    if candidates:
        return candidates[0]
    return None


# ──────────────────────────────────────────────────────────────────────
# Logger
# ──────────────────────────────────────────────────────────────────────


class TaskLogger:
    """Records every turn's input/output/reasoning/usage to disk."""

    def __init__(self, log_dir: Path, task_id: str):
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.task_id = task_id
        self.turns: list[dict] = []
        self._turn_counter = 0
        self._start_time = None

    def start(self):
        self._start_time = time.time()

    def next_turn_number(self) -> int:
        self._turn_counter += 1
        return self._turn_counter

    def record_turn(
        self,
        turn_number: int,
        prompt: str,
        turn,  # codex_sdk.Turn
        verification: dict | None = None,
        elapsed: float = 0,
    ):
        items_data = []
        for item in turn.items:
            item_dict = {"type": item.type}
            if hasattr(item, "text"):
                item_dict["text"] = item.text
            if hasattr(item, "command"):
                item_dict["command"] = item.command
                item_dict["aggregated_output"] = getattr(item, "aggregated_output", "")
                item_dict["exit_code"] = getattr(item, "exit_code", None)
                item_dict["status"] = getattr(item, "status", "")
            if hasattr(item, "changes"):
                item_dict["changes"] = [
                    {"path": c.path, "kind": c.kind} for c in item.changes
                ]
                item_dict["status"] = getattr(item, "status", "")
            if hasattr(item, "query"):
                item_dict["query"] = item.query
            if hasattr(item, "message"):
                item_dict["message"] = item.message
            items_data.append(item_dict)

        usage = None
        if turn.usage:
            usage = {
                "input_tokens": turn.usage.input_tokens,
                "cached_input_tokens": turn.usage.cached_input_tokens,
                "output_tokens": turn.usage.output_tokens,
            }

        record = {
            "task_id": self.task_id,
            "turn_number": turn_number,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "elapsed_seconds": elapsed,
            "input_prompt": prompt,
            "items": items_data,
            "final_response": turn.final_response,
            "usage": usage,
            "verification": verification,
        }

        turn_file = self.log_dir / f"turn_{turn_number:03d}.json"
        with open(turn_file, "w", encoding="utf-8") as f:
            json.dump(record, f, ensure_ascii=False, indent=2)

        self.turns.append(record)

    def save_summary(self, success: bool, total_elapsed: float):
        total_input = sum(
            (t.get("usage") or {}).get("input_tokens", 0) for t in self.turns
        )
        total_output = sum(
            (t.get("usage") or {}).get("output_tokens", 0) for t in self.turns
        )
        summary = {
            "task_id": self.task_id,
            "success": success,
            "total_turns": len(self.turns),
            "total_elapsed_seconds": total_elapsed,
            "total_input_tokens": total_input,
            "total_output_tokens": total_output,
            "total_tokens": total_input + total_output,
            "turn_summaries": [
                {
                    "turn": t["turn_number"],
                    "usage": t.get("usage"),
                    "verification": (t.get("verification") or {}).get("passed"),
                }
                for t in self.turns
            ],
        }
        with open(self.log_dir / "summary.json", "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        return summary


# ──────────────────────────────────────────────────────────────────────
# Verification
# ──────────────────────────────────────────────────────────────────────


def run_verification(task_dir: Path, command: str) -> dict:
    """Run the verification command and return result."""
    try:
        proc = subprocess.run(
            command,
            shell=True,
            cwd=str(task_dir),
            capture_output=True,
            text=True,
            timeout=120,
        )
        return {
            "passed": proc.returncode == 0,
            "exit_code": proc.returncode,
            "stdout": proc.stdout.strip()[-2000:],
            "stderr": proc.stderr.strip()[-2000:],
        }
    except subprocess.TimeoutExpired:
        return {"passed": False, "exit_code": None, "stdout": "", "stderr": "Verification timed out"}
    except Exception as e:
        return {"passed": False, "exit_code": None, "stdout": "", "stderr": str(e)}


# ──────────────────────────────────────────────────────────────────────
# Prompt builders
# ──────────────────────────────────────────────────────────────────────


def build_initial_prompt(task_md: str, verify_command: str | None) -> str:
    parts = [
        "You are an automated programming agent. Your task is described below.",
        "",
        "IMPORTANT RULES:",
        "1. Read the task description carefully and complete it.",
        "2. Write code, create files, and run commands as needed.",
        "3. After completing the task, verify your work yourself before finishing.",
        "4. If the task specifies a verification command, run it yourself.",
        "",
        "--- TASK DESCRIPTION (task.md) ---",
        task_md,
        "--- END TASK DESCRIPTION ---",
    ]
    if verify_command:
        parts.extend([
            "",
            f"When you're done, verify your solution by running: `{verify_command}`",
            "Make sure the verification passes before giving your final answer.",
        ])
    return "\n".join(parts)


def build_golf_prompt(task_md: str, baseline_path: Path, task_dir: Path) -> str:
    """Compact prompt for code-golf: produce working code quickly, then optimize."""
    baseline_code = baseline_path.read_text(encoding="utf-8")
    baseline_size = baseline_path.stat().st_size
    task_num = task_dir.name.replace("task", "")

    return f"""Golf this code: write solve{task_num}.py with p(grid) function, SHORTER than {baseline_size} bytes.

CRITICAL: Produce ONE working version within 2 minutes. Do NOT read JSON files — they are for verify.py only, not for you. Do NOT explore or plan extensively. Just write the code.

BASELINE ({baseline_size} bytes):
```python
{baseline_code}
```

STEPS (do this quickly, < 3 iterations total):
1. Read baseline, understand p(grid)
2. Write solve{task_num}.py — compress variable names, collapse loops, use lambdas/comprehensions
3. Run: python verify.py solve{task_num}.py
4. If fail: fix once. If pass and < {baseline_size} bytes: STOP and report.

Do NOT try to achieve the absolute minimum. Just be clearly shorter."""


def build_feedback_prompt(verification: dict) -> str:"


def build_feedback_prompt(verification: dict) -> str:
    status = "PASSED" if verification["passed"] else "FAILED"
    parts = [
        f"Your solution verification {status}.",
        "",
    ]
    if verification.get("stdout"):
        parts.append(f"Verification output:\n```\n{verification['stdout']}\n```")
    if verification.get("stderr"):
        parts.append(f"Verification errors:\n```\n{verification['stderr']}\n```")
    parts.append("Please fix the issues and try again.")
    return "\n".join(parts)


# ──────────────────────────────────────────────────────────────────────
# Main runner
# ──────────────────────────────────────────────────────────────────────


async def run_task(task_dir: Path) -> dict:
    """Run a single task and return the summary."""
    task_dir = task_dir.resolve()
    cfg = load_task_config(task_dir)

    task_id = cfg["task_id"]
    budget = cfg["budget"]
    verify_cmd = cfg["verify"]["command"]
    early_stop = cfg["verify"]["early_stop"]
    sandbox = cfg["sandbox_mode"]

    # Read task.md / task*.md
    task_md_path = _find_task_md(task_dir)
    if not task_md_path:
        raise FileNotFoundError(f"No task.md or task*.md found in {task_dir}")
    task_md = task_md_path.read_text(encoding="utf-8")

    # Detect golf mode: baseline.py exists → use compact golf prompt
    baseline_path = task_dir / "baseline.py"
    golf_mode = baseline_path.exists()

    # Init logger
    log_dir = task_dir / ".codex-logs"
    logger = TaskLogger(log_dir, task_id)

    # Init Codex (uses CLI defaults from ~/.codex/config.toml)
    # On Windows, codex-sdk looks for codex.exe; but npm installs codex.cmd.
    # Resolve the path explicitly.
    codex_path = _find_codex_binary()
    codex = Codex(CodexOptions(codex_path_override=codex_path) if codex_path else CodexOptions())

    thread = codex.start_thread(
        ThreadOptions(
            working_directory=str(task_dir),
            sandbox_mode=sandbox,  # type: ignore[arg-type]
            approval_policy="never",  # auto mode — no human interaction
            skip_git_repo_check=True,
            model_reasoning_effort="high",
        )
    )

    print(f"\n{'='*60}")
    print(f"Task: {task_id}")
    print(f"Budget: max {budget['max_turns']} turns, {budget['max_tokens']} tokens, {budget['timeout_seconds']}s task, {budget.get('turn_timeout_seconds', 1200)}s turn, {budget.get('max_retries', 3)} retries")
    print(f"Sandbox: {sandbox}")
    print(f"Verify: {verify_cmd} (early_stop={early_stop})")
    print(f"{'='*60}\n")

    logger.start()
    start_time = time.time()
    total_tokens = 0
    verification = None

    for turn_num in range(1, budget["max_turns"] + 1):
        elapsed = time.time() - start_time
        if elapsed > budget["timeout_seconds"]:
            print(f"[BUDGET] Timeout reached ({elapsed:.0f}s > {budget['timeout_seconds']}s)")
            break

        if total_tokens >= budget["max_tokens"]:
            print(f"[BUDGET] Token limit reached ({total_tokens} >= {budget['max_tokens']})")
            break

        # Build prompt for this turn
        if turn_num == 1:
            if golf_mode:
                prompt = build_golf_prompt(task_md, baseline_path, task_dir)
            else:
                prompt = build_initial_prompt(task_md, verify_cmd)
        else:
            prompt = build_feedback_prompt(verification)

        print(f"\n--- Turn {turn_num}/{budget['max_turns']} ---")

        # Run turn (with retry for transient streaming errors)
        turn_start = time.time()
        max_retries = budget.get("max_retries", 3)
        turn_timeout = budget.get("turn_timeout_seconds", 1200)
        turn = None
        for attempt in range(1, max_retries + 1):
            try:
                turn = await asyncio.wait_for(thread.run(prompt), timeout=turn_timeout)
                break
            except asyncio.TimeoutError:
                print(f"  [Timeout] Turn exceeded {turn_timeout}s limit")
                if attempt < max_retries:
                    delay = attempt * 5
                    print(f"  [Retry {attempt}/{max_retries}] waiting {delay}s")
                    await asyncio.sleep(delay)
                    thread = codex.start_thread(
                        ThreadOptions(
                            working_directory=str(task_dir),
                            sandbox_mode=sandbox,
                            approval_policy="never",
                            skip_git_repo_check=True,
                            model_reasoning_effort="high",
                        )
                    )
                    continue
                logger.record_turn(
                    turn_num, prompt, type("FakeTurn", (), {
                        "items": [],
                        "final_response": f"Turn timeout after {turn_timeout}s",
                        "usage": None,
                    })(),
                    verification=None,
                    elapsed=time.time() - turn_start,
                )
                break
            except Exception as e:
                msg = str(e)
                is_transient = "Separator" in msg or "chunk exceed" in msg
                if is_transient and attempt < max_retries:
                    delay = attempt * 5
                    print(f"  [Retry {attempt}/{max_retries}] Transient error: {msg[:80]}... waiting {delay}s")
                    await asyncio.sleep(delay)
                    # Create a fresh thread for retry (old one may be in bad state)
                    thread = codex.start_thread(
                        ThreadOptions(
                            working_directory=str(task_dir),
                            sandbox_mode=sandbox,
                            approval_policy="never",
                            skip_git_repo_check=True,
                            model_reasoning_effort="high",
                        )
                    )
                    continue
                print(f"[ERROR] Turn failed: {e}")
                logger.record_turn(
                    turn_num, prompt, type("FakeTurn", (), {
                        "items": [],
                        "final_response": str(e),
                        "usage": None,
                    })(),
                    verification=None,
                    elapsed=time.time() - turn_start,
                )
                break
        if turn is None:
            break

        turn_elapsed = time.time() - turn_start

        # Track tokens
        if turn.usage:
            total_tokens += turn.usage.input_tokens + turn.usage.output_tokens
            print(f"  Usage: {turn.usage.input_tokens} in / {turn.usage.output_tokens} out")

        # Print reasoning
        for r in turn.reasoning():
            print(f"  [Reasoning] {r.text[:200]}...")

        # Print final response
        print(f"  [Response] {turn.final_response[:300]}...")

        # Run verification
        if verify_cmd:
            verification = run_verification(task_dir, verify_cmd)
            status = "PASS" if verification["passed"] else "FAIL"
            print(f"  [Verify] {status}")
        else:
            verification = None

        # Record turn
        logger.record_turn(turn_num, prompt, turn, verification, turn_elapsed)

        # Check early stop
        if early_stop and verification and verification["passed"]:
            print(f"\n[SUCCESS] Verification passed after {turn_num} turn(s)!")
            break
    else:
        print(f"\n[DONE] Budget exhausted after {budget['max_turns']} turns.")

    total_elapsed = time.time() - start_time
    success = (verification or {}).get("passed", False)

    summary = logger.save_summary(success, total_elapsed)
    print(f"\n{'='*60}")
    print(f"Summary: {summary['total_turns']} turns, "
          f"{summary['total_tokens']} tokens, "
          f"{summary['total_elapsed_seconds']:.0f}s, "
          f"success={success}")
    print(f"Logs: {log_dir}")
    print(f"{'='*60}")

    return summary


def main():
    if len(sys.argv) < 2:
        print(f"Usage: python3 {sys.argv[0]} <task_directory>")
        sys.exit(1)

    task_dir = Path(sys.argv[1]).resolve()
    if not task_dir.is_dir():
        print(f"Error: {task_dir} is not a directory")
        sys.exit(1)

    summary = asyncio.run(run_task(task_dir))
    sys.exit(0 if summary["success"] else 1)


if __name__ == "__main__":
    main()
