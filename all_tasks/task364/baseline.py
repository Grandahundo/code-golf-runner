def p(m):
    rows, cols = len(m), len(m[0])
    visited = set()
    for r in range(rows):
        for c in range(cols):
            if m[r][c] == 3:
                shape_cells = []
                signature = 0
                q = [(r, c)]
                visited.add((r, c))
                while q:
                    curr_r, curr_c = q.pop(0)
                    shape_cells.append((curr_r, curr_c))
                    b = 0
                    for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                        b *= 2
                        nr, nc = curr_r + dr, curr_c + dc
                        if 0 <= nr < rows and 0 <= nc < cols and m[nr][nc] == 3:
                            b |= 1
                            if (nr, nc) not in visited:
                                visited.add((nr, nc))
                                q.append((nr, nc))
                    if b in [0b0111, 0b1110, 0b1011, 0b1101]:
                        signature += 2
                    if b in [0b0011, 0b0110, 0b1100, 0b1001]:
                        signature += 1
                shape_type = [0,1,6,2][signature]
                for cell_r, cell_c in shape_cells:
                    m[cell_r][cell_c] = shape_type
    return m
