def p(m,R=range):r,c=zip(*[(r,c)for r in R(9)for c in R(9)if m[r][c]]);return sum([[sum([[v,v]for v in m[r][min(c):max(c)+1]],[])]*2for r in R(min(r),max(r)+1)],[])
