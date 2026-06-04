p=lambda m:[m[15-(i:=sum(m,[]).index(0))//16-r][~i%-16::-1][:3]for r in range(3)]
