def p(m):
 n=len(m);(x,*_,X),(y,*_,Y)=map(sorted,zip(*[(r,c)for i in range(n*n)if m[r:=i//n][c:=i%n]]));a=[(x,y,-1,-1),(x,Y,-1,1),(X,y,1,-1),(X,Y,1,1)]
 for r,c,i,j in a:
  while n>c+j>-1<r+i<n:r+=i;c+=j;m[r][c]=min(set(sum(m,[]))-{0,sorted([m[u][v]for u,v,*_ in a])[1]})
 return m
