p=lambda m:[[max(m[y+r][x+c]for x in range(11)for y in range(11)if m[y][x]==5)for c in[-1,0,1]]for r in[-1,0,1]]
