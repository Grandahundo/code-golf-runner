def p(m):
    f=lambda m:[*map(list,zip(*m))]
    t=8 in m[0]
    m = m if t else f(m)
    rows, cols = len(m), len(m[0])
    a=sum(m,[])
    for i in range(rows*cols):
        if a[i] != 2:
            continue
        r = i//cols
        c = i%cols
        def splash(a):
            for e in a:
                if m[r][e] == 8:
                    for j in range(min(c,e),max(c,e) + 1):
                        m[r][j] = 2
                    for dr in [-1,0,1]:
                        for dc in [-1,0,1]:
                            if dr|dc:m[r+dr][e+dc] = 8
                    break
        splash(range(c, 0, -1))
        splash(range(c + 1, cols))
    return m if t else f(m)
