"""Verify solution by importing p() and testing against task data."""
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
    print(f"\n{passed}/{passed + failed} passed, {failed} failed")
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
