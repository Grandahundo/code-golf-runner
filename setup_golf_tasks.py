#!/usr/bin/env python3
"""
Build 400 golf task directories from wanderer-cc_golf dataset.

For each task NNN:
  - Extract longest readable solution from sol/taskNNN.py → baseline.py
  - Copy taskNNN.json from wanderer dataset
  - Write verify.py (import-based, auto-detects task file)
  - Write task.md (golf instructions)
  - Write task_config.yaml (unified budget)

Usage:
    python setup_golf_tasks.py --source "<wanderer_path>" --target tasks [--count N] [--all]
"""

import argparse
import json
import re
import shutil
import sys
from pathlib import Path


TASK_MD_TEMPLATE = """# Code Golf — Task {task_id}

## Goal

Write `solve{task_padded}.py` that is **SHORTER** than `baseline.py` while passing all tests.

## How to Work

1. Read `baseline.py` — understand what `p(grid)` does
2. Write `solve{task_padded}.py` with same `p(grid)` → 2D list signature
3. Run `python verify.py solve{task_padded}.py` to test
4. Goal: file smaller than baseline

## Rules

- Must define `p(grid)` function
- Must pass ALL examples
- Smaller = better
- Do NOT read JSON data files — verify.py handles that
"""

VERIFY_PY_TEMPLATE = '''"""Verify solution by importing p() and testing against task data."""
import importlib.util
import glob
import json
import os
import sys


def find_task_file():
    for name in sorted(glob.glob("task*.json")):
        return name
    raise FileNotFoundError("No task*.json found")


def load_examples():
    with open(find_task_file()) as f:
        data = json.load(f)
    examples = []
    for split in ("train", "test"):
        for i, ex in enumerate(data.get(split, [])):
            examples.append((f"{split}[{i}]", ex["input"], ex["output"]))
    return examples


def verify_solution(script_path):
    spec = importlib.util.spec_from_file_location("solution", script_path)
    if spec is None:
        raise RuntimeError(f"Cannot import {script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    if not hasattr(module, "p"):
        raise RuntimeError("Solution must define a p() function")

    func = module.p
    examples = load_examples()
    passed, failed = 0, 0

    for name, inp, expected in examples:
        try:
            actual = func(inp)
            if actual == expected:
                print(f"  [PASS] {name}")
                passed += 1
            else:
                print(f"  [FAIL] {name} — output mismatch")
                failed += 1
        except Exception as e:
            print(f"  [FAIL] {name} — {e}")
            failed += 1

    size = os.path.getsize(script_path)
    return passed, failed, size


def main():
    # Auto-detect solution file
    candidates = sorted(glob.glob("solve*.py"))
    script = sys.argv[1] if len(sys.argv) > 1 else (candidates[0] if candidates else None)
    if not script:
        print("Usage: python verify.py [script.py]")
        return 1
    if not os.path.exists(script):
        print(f"Error: {script} not found")
        return 1

    passed, failed, size = verify_solution(script)
    print(f"\\n{passed}/{passed + failed} passed, {failed} failed")
    print(f"Code size: {size} bytes")

    baseline = "baseline.py"
    if os.path.exists(baseline):
        baseline_size = os.path.getsize(baseline)
        print(f"Baseline: {baseline_size} bytes")
        if size < baseline_size:
            print(f"Shorter by {baseline_size - size} bytes!")
        else:
            print(f"Not shorter (need < {baseline_size}, got {size})")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
'''


# ──────────────────────────────────────────────────────────────
# Sol file parser — extract implementations
# ──────────────────────────────────────────────────────────────


def extract_baseline(sol_path: Path) -> str | None:
    """Extract the best readable baseline implementation from a sol file."""
    text = sol_path.read_text(encoding="utf-8")

    # Split into blocks: everything between section headers
    # A block is a run of code lines (not starting with # or ##)
    blocks = []
    current = []
    in_code = False

    for line in text.split("\n"):
        stripped = line.strip()

        # Skip empty lines, headers, and separators (order matters: ### before ## before #)
        if not stripped:
            continue

        if stripped.startswith("###"):
            # Subsection header like "### att (83 bytes)"
            if current:
                blocks.append("\n".join(current))
                current = []
            in_code = False
            continue

        if stripped == "##" or stripped.startswith("## "):
            # Separator
            if current:
                blocks.append("\n".join(current))
                current = []
            in_code = False
            continue

        if stripped.startswith("#"):
            # Section header or comment like "# ovs (73 bytes, gold)"
            if current:
                blocks.append("\n".join(current))
                current = []
            in_code = False
            continue

        # Code line
        current.append(line)
        in_code = True

    if current:
        blocks.append("\n".join(current))

    # Filter: keep blocks that define p() function (not variable assignments like p = [...])
    def has_p(block: str) -> bool:
        return bool(re.search(r"(\bdef p\b|\bp\s*=\s*lambda)", block))

    code_blocks = [b for b in blocks if has_p(b)]
    if not code_blocks:
        return None

    # Split blocks into individual solutions
    solutions = []
    for block in code_blocks:
        current = []
        for line in block.split("\n"):
            stripped = line.strip()
            if re.match(r"(p\s*=|def\s+p\()", stripped):
                if current:
                    solutions.append("\n".join(current))
                current = [line]
            elif current:
                # Append continuation lines (indented, or part of multi-line def)
                current.append(line)
        if current:
            solutions.append("\n".join(current))

    # Filter valid solutions
    valid = []
    for s in solutions:
        stripped = s.strip()
        if not stripped:
            continue
        if stripped.startswith("exec(") or "p=eval(" in stripped[:20] or "p = eval(" in stripped[:20]:
            continue
        # Remove leading comment lines
        lines = stripped.split("\n")
        code_lines = [l for l in lines if not l.strip().startswith("#")]
        if not code_lines:
            continue
        clean = "\n".join(code_lines).strip()
        # Must define p as function or lambda (not variable assignment)
        if re.search(r"(\bdef p\b|\bp\s*=\s*lambda)", clean):
            valid.append(clean)

    if not valid:
        return None

    # Pick LONGEST solution
    baseline = max(valid, key=len)
    return baseline


# ──────────────────────────────────────────────────────────────
# Task creator
# ──────────────────────────────────────────────────────────────


def create_task(task_num: int, source_dir: Path, target_dir: Path, max_test: int = 5):
    task_padded = f"{task_num:03d}"
    task_id = f"task{task_padded}"
    task_dir = target_dir / task_id

    # Extract baseline from sol file
    sol_path = source_dir / "sol" / f"{task_id}.py"
    if not sol_path.exists():
        print(f"  [SKIP] {task_id}: no sol file")
        return False

    baseline_code = extract_baseline(sol_path)
    if not baseline_code:
        print(f"  [SKIP] {task_id}: no extractable baseline")
        return False

    task_dir.mkdir(parents=True, exist_ok=True)

    # Write baseline.py
    (task_dir / "baseline.py").write_text(baseline_code + "\n", encoding="utf-8")

    # Write verify.py
    (task_dir / "verify.py").write_text(VERIFY_PY_TEMPLATE, encoding="utf-8")

    # Write task.md
    (task_dir / "task.md").write_text(
        TASK_MD_TEMPLATE.format(task_id=task_num, task_padded=task_padded),
        encoding="utf-8",
    )

    # Write task_config.yaml
    config = f"""# Task config for {task_id}
task_id: "{task_id}"

budget:
  max_turns: 10
  max_tokens: 300000
  timeout_seconds: 1200
  turn_timeout_seconds: 600
  max_retries: 2

sandbox_mode: "danger-full-access"

verify:
  command: "python verify.py"
  early_stop: true
"""
    (task_dir / "task_config.yaml").write_text(config, encoding="utf-8")

    # Copy and trim task JSON
    src_json = source_dir / "tasks" / f"{task_id}.json"
    if src_json.exists():
        data = json.loads(src_json.read_text(encoding="utf-8"))
        for key in ("test", "arc-gen"):
            if key in data and len(data[key]) > max_test:
                data[key] = data[key][:max_test]
        (task_dir / f"{task_id}.json").write_text(
            json.dumps(data), encoding="utf-8"
        )

    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, help="wanderer-cc_golf directory")
    parser.add_argument("--target", default="tasks", help="Target directory")
    parser.add_argument("--count", type=int, default=10, help="Number of tasks")
    parser.add_argument("--all", action="store_true", help="Create all 400 tasks")
    parser.add_argument("--ids", help="Comma-separated IDs, e.g. '004,005,010'")
    parser.add_argument("--max-test", type=int, default=5)
    args = parser.parse_args()

    source_dir = Path(args.source).resolve()
    target_dir = Path(args.target).resolve()

    if args.ids:
        task_nums = [int(x.strip()) for x in args.ids.split(",")]
    elif args.all:
        task_nums = list(range(1, 401))
    else:
        task_nums = list(range(1, args.count + 1))

    print(f"Building {len(task_nums)} golf tasks...")
    print(f"Source: {source_dir}")
    print(f"Target: {target_dir}")
    print()

    ok = 0
    for num in task_nums:
        if create_task(num, source_dir, target_dir, args.max_test):
            print(f"  [OK] task{num:03d}")
            ok += 1
        else:
            print(f"  [SKIP] task{num:03d}")

    print(f"\nDone: {ok}/{len(task_nums)} created.")
    print(f"Run: python batch_runner.py {target_dir}")


if __name__ == "__main__":
    main()
