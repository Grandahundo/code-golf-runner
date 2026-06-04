def p(m):
    rows, cols = len(m), len(m[0])
    a = []
    for r in range(rows):
        for c in range(cols):
            if m[r][c] == 5:
                w = []
                q = [(r, c)]
                while q:
                    (row,col),*q=q
                    w+=(row, col),
                    for dr, dc in [(0, 1),(1,0)]:
                        nr, nc = row + dr, col + dc
                        if rows>nr>-1<nc<cols!=m[nr][nc]>4:
                            m[nr][nc]=0
                            q+=(nr,nc),
                a+=[len(w),w],
    i=0
    for e in sorted(a)[::-1]:
     for r,c in e[1]:m[r][c]=[1,4,2][i]
     i+=1
    return m
