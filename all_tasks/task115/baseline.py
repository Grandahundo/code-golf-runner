p=lambda m:len({*m[0]})>1and[[c for c,d in zip(m[0],[0,*m[0]])if c^d]]or[*zip(*p([*zip(*m)]))]
