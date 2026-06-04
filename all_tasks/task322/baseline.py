p=lambda m,r=[0]*3:m and[s:=[*map(sum,zip(m.pop(0),r))]]+p(m,s)
