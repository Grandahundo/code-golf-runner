p=lambda i,k=0,s=[0]*99:[s+0*(s:=x)for*x,in zip(*k or p(i,i))if-~-any(x)*(s:=[*map(max,s,x)])]+[s]
r=[0]*99;p=lambda i,k=0,s=r:[s+0*(s:=x)for*x,in zip(*k or p(i,i))if r+(s:=[*map(max,s,x)])>x]+[s]
r=[0]*99;p=lambda i,k=0,s=r:[s+0*(s:=x)for*x,in[*zip(*k or p(i,i)),r]if r+(s:=[*map(max,s,x)])>x]
