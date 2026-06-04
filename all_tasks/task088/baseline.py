p=lambda i,k=3,t=0:-k*i[1:]or p([*zip(*[[v and t for v in c]for*c,in i if(t:=t or max(c))][k<3:][::-1])],k-1)
