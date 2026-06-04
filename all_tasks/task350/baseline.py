def p(m):
    M,N=len(m),len(m[0])
    a=sum(m,[])
    for r in range(M):
        for c in range(N):
            if 1 in m[r][:c]and 1 in m[r][c:] or 1 in a[c::N][:r] and 1 in a[c::N][r:]:
                m[r][c] = m[r][c] or 8
    return m
