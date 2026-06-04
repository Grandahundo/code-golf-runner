p=lambda a,s=[],*r:a+~a*any(any(s)*r)%3if r else[*map(p,a,[a]*20,*s)]
