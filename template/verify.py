import glob
import json
import subprocess
import sys


def find_task_file():
    """Auto-detect the task JSON file in the current directory."""
    candidates = sorted(glob.glob("task*.json"))
    if not candidates:
        raise FileNotFoundError("No task*.json found in current directory")
    return candidates[0]


def load_task(path):
    with open(path) as f:
        return json.load(f)


def run_solution(script, input_grid):
    payload = json.dumps({"input": input_grid})
    proc = subprocess.run(
        [sys.executable, script],
        input=payload,
        capture_output=True,
        text=True,
        timeout=30,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"{script} exited with {proc.returncode}:\n{proc.stderr}")
    try:
        result = json.loads(proc.stdout)
        return result.get("output", result.get("answer", result))
    except json.JSONDecodeError:
        raise RuntimeError(f"did not produce valid JSON:\n{proc.stdout[:500]}")


def grids_equal(a, b):
    if len(a) != len(b):
        return False
    return all(r1 == r2 for r1, r2 in zip(a, b))


def main():
    script = sys.argv[1] if len(sys.argv) > 1 else None
    if not script:
        candidates = sorted(glob.glob("solve*.py"))
        if not candidates:
            print("Usage: python3 verify.py <script>")
            return 1
        script = candidates[0]

    task = load_task(find_task_file())

    all_examples = []
    for split in ("train", "test", "arc-gen"):
        for i, ex in enumerate(task.get(split, [])):
            all_examples.append((split, i, ex["input"], ex["output"]))

    passed = 0
    failed = 0

    for split, idx, inp, expected in all_examples:
        try:
            actual = run_solution(script, inp)
            if grids_equal(actual, expected):
                print(f"[PASS] {split}[{idx}]")
                passed += 1
            else:
                print(f"[FAIL] {split}[{idx}] — output mismatch")
                failed += 1
                if failed == 1:
                    print(f"  Input: {inp}")
                    print(f"  Expected: {expected}")
                    print(f"  Actual: {actual}")
        except Exception as e:
            print(f"[FAIL] {split}[{idx}] — {e}")
            failed += 1

    print(f"\n{passed}/{passed + failed} passed, {failed} failed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
