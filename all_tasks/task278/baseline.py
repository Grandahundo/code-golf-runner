def p(m):
    M,N=len(m),len(m[0])
    for i in range(N*M):
        for nr, nc in[(r:=i//N,(c:=i%N)+1),(r+1,c)]:
            for cell_r, cell_c in [(r,c),(nr,nc)]*(M>nr>-1<nc<N>m[r][c]==m[nr][nc]==2):
                for i in b' @`!a"Bb':
                    i,j =cell_r+i//32-2, cell_c + i%8-1
                    if M>i>-1<j<N and m[i][j]!=2:
                        m[i][j] = 3
    return m
