def p(m):a,b=sorted(set(r:=m[0]),key=r.count);return[-~r.count(a)*[b]]*-~m.count([a]*len(r))
