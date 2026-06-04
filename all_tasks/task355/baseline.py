def p(m,E=enumerate):
 s=[]
 for i in{*(a:=sum(m,[]))}-{d:=min(a,key=a.count)}:r,c=zip(*[(r,c)for r,l in E(m)for c,v in E(l)if v==i]);s+=[sum(l[min(c):max(c)+1].count(d)for l in m[min(r):max(r)+1]),i],
 return[max(s)[1:]]
