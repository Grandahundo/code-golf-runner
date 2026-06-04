# Code Golf Task — Pattern Discovery

## Your Job

You are given a task data file (`task*.json`) containing training examples and test examples. Each example has an **input** grid and an **output** grid.

Your job is to:
1. **Discover the transformation rule** by examining the train examples
2. **Write a Python script** that implements this rule
3. **Verify it passes all examples**

## How to Discover the Pattern

DO NOT read the entire JSON file at once — it may be very large.

Instead, use Python one-liners to peek at the data:

```bash
# See structure
python -c "import json; d=json.load(open('taskNNN.json')); print('keys:', list(d.keys())); print('train count:', len(d.get('train',[])))"

# Examine first train example
python -c "import json; d=json.load(open('taskNNN.json')); e=d['train'][0]; print('input:', e['input']); print('output:', e['output'])"

# Compare multiple examples to confirm the pattern
python -c "import json; d=json.load(open('taskNNN.json')); [print(f'ex{i}: in={e[\"input\"]} out={e[\"output\"]}') for i,e in enumerate(d['train'][:5])]"
```

## Requirements

- Script filename: `solveNNN.py` (match the task number)
- Read JSON from **stdin**: `{"input": <grid>}`
- Write JSON to **stdout**: `{"output": <grid>}`
- **Code length must be < 1000 bytes** (check with `wc -c`)
- Verify with: `python3 verify.py solveNNN.py`

## Strategy

1. First peek at 2-3 train examples to understand the pattern
2. Write a first version of your solution
3. Run `python3 verify.py solveNNN.py` to test
4. If it fails, examine the failing example and fix
5. Once all pass, you're done
