p=lambda m,R=range(4):[[m[r][c+4]or m[r+4][c]or m[r+4][c+4]or m[r][c]for c in R]for r in R]
