p=lambda g,k=3,P=[0]:-k*g or[P:=((P>r)*[k]*(P.count(P[0])+k-2)+r)[:len(r)]for r in p(g,k-2)][::-1]
