p=lambda m,i=0:exec("m[i][i]=m[i][n-(i:=i+1)]=0;"*(n:=len(m)))or m
