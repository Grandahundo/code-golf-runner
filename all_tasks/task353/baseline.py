def p(m):
    find_coords = lambda val: next(
        (r, c) for r, row in enumerate(m) for c, v in enumerate(row) if v == val
    )
    r3, c3 = find_coords(3)
    r4, c4 = find_coords(4)
    dr, dc = r4 - r3, c4 - c3
    m[r3][c3] = 0
    m[r3 + (dr > 0) - (dr < 0)][c3 + (dc > 0) - (dc < 0)] = 3
    return m
