p=lambda i,r=range(12):[[i[a][b]or 2*any([[sum(s[b-j:][:n])/5for s in i[a-k:][:n]]==[n,*[2]*(n-2),n]for n in r for j in r[:n]for k in r[:n]])for b in r]for a in r]
import re;p=lambda i,k=20:-k*i or p(eval(re.sub(f'({(h:=(5,)*-~(n:=k%5))}.{(s:={34-n*3})}(?={(r:=f"5, [^5]{ {n*3}}5.{s}")*n}{h})({r})*5)(, 0)+',"\\1"+",2"*n,str(i))),k-1)
