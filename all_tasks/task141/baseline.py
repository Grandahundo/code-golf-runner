p=lambda m:(R:=range(N:=len(m)))and[[(abs(r-(i:=(a:=sum(m,[])).index(e:=max(a)))//N)==abs(c-i%N))*e for c in R]for r in R]
