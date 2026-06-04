def p(m):
 m=[[8]*(n:=len(m[0]))for _ in m];r,c,d=len(m),0,1
 while r:r-=1;m[r][c]=1;d*=~-(0<=c+d<n)|1;c+=d
 return m
