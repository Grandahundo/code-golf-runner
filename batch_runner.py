#!/usr/bin/env python3
"""
Batch Task Runner — run multiple tasks in sequence.

Usage:
    python batch_runner.py <tasks_directory>
    python batch_runner.py tasks
    python batch_runner.py tasks --pattern "task*"
    python batch_runner.py tasks --ids "001,002,005"
"""

import asyncio
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Import the single-task runner
from runner import run_task, _find_task_md


def discover_tasks(root: Path, pattern: str = "task*", ids: str | None = None) -> list[Path]:
    """Find task directories in root. Filter by pattern or explicit IDs."""
    if ids:
        id_list = [x.strip() for x in ids.split(",")]
        candidates = [root / f"task{tid}" for tid in id_list]
        return [d for d in candidates if d.is_dir() and _find_task_md(d)]

    candidates = sorted(root.glob(pattern))
    return [d for d in candidates if d.is_dir() and _find_task_md(d)]


async def run_batch(tasks_root: Path, pattern: str = "task*", ids: str | None = None, delay: int = 60) -> dict:
    """Run all discovered tasks and return batch summary."""
    task_dirs = discover_tasks(tasks_root, pattern, ids)

    if not task_dirs:
        print("No task directories found.")
        return {"total": 0, "passed": 0, "failed": 0, "tasks": []}

    print(f"Found {len(task_dirs)} task(s):")
    for d in task_dirs:
        print(f"  - {d.name}")
    print(f"Cooldown between tasks: {delay}s")
    print()

    results = []
    passed = 0
    failed = 0
    start_time = time.time()

    for i, task_dir in enumerate(task_dirs):
        if i > 0 and delay > 0:
            print(f"\n  [Cooldown] Waiting {delay}s before next task...")
            await asyncio.sleep(delay)

        print(f"\n{'#'*60}")
        print(f"# [{i+1}/{len(task_dirs)}] {task_dir.name}")
        print(f"{'#'*60}")

        try:
            summary = await run_task(task_dir)
            if summary["success"]:
                passed += 1
            else:
                failed += 1
            results.append({
                "task": task_dir.name,
                "success": summary["success"],
                "turns": summary["total_turns"],
                "tokens": summary["total_tokens"],
                "elapsed": summary["total_elapsed_seconds"],
            })
        except Exception as e:
            print(f"[SKIP] {task_dir.name} failed with error: {e}")
            failed += 1
            results.append({
                "task": task_dir.name,
                "success": False,
                "turns": 0,
                "tokens": 0,
                "elapsed": time.time() - start_time,
                "error": str(e),
            })

    total_elapsed = time.time() - start_time

    batch_summary = {
        "batch": str(tasks_root),
        "pattern": pattern,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total": len(task_dirs),
        "passed": passed,
        "failed": failed,
        "total_elapsed_seconds": total_elapsed,
        "tasks": results,
    }

    # Save batch summary alongside tasks
    summary_path = tasks_root / ".batch-summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(batch_summary, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*60}")
    print(f"BATCH COMPLETE: {passed}/{len(task_dirs)} passed, {failed} failed, {total_elapsed:.0f}s")
    print(f"Summary: {summary_path}")
    print(f"{'='*60}")

    return batch_summary


def main():
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <tasks_directory> [--pattern PATTERN] [--ids IDS]")
        print(f"  python {sys.argv[0]} tasks")
        print(f"  python {sys.argv[0]} tasks --ids '001,002,005'")
        sys.exit(1)

    tasks_root = Path(sys.argv[1]).resolve()

    pattern = "task*"
    ids = None
    delay = 60
    args = sys.argv[2:]
    i = 0
    while i < len(args):
        if args[i] == "--pattern" and i + 1 < len(args):
            pattern = args[i + 1]
            i += 2
        elif args[i] == "--ids" and i + 1 < len(args):
            ids = args[i + 1]
            i += 2
        elif args[i] == "--delay" and i + 1 < len(args):
            delay = int(args[i + 1])
            i += 2
        else:
            i += 1

    if not tasks_root.is_dir():
        print(f"Error: {tasks_root} is not a directory")
        sys.exit(1)

    summary = asyncio.run(run_batch(tasks_root, pattern, ids, delay))
    sys.exit(0 if summary["failed"] == 0 else 1)


if __name__ == "__main__":
    main()
