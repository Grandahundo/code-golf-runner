p=lambda m,i=3:-i*m or p([*map(list,zip(*([[8]*len(m[0])]+m[1:])[::-1]))],i-1)
