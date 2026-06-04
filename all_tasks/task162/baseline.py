def p(m,R=range):
 for r in R(len(m)-2):
  for c in R(len(m[0])-2):
   if sum(sum(m[r+i][c:c+3])for i in R(3))<1:
    for i in R(3):m[r+i][c:c+3]=[1]*3
 return m
