import re

def p(grid):
    """Repeatedly rotate and regex-replace to shift non-zero cells."""
    result = grid
    for _ in range(20):
        result = [list(row) for row in zip(*result[::-1])]
        s = str(result)
        s = re.sub(r"0(?=.{34}([^0]), 0.{31})", r"", s)
        result = eval(s)
    return result
