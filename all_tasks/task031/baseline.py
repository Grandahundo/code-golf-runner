p=lambda m,i=0:m*(i>1)or p([*map(list,filter(sum,zip(*m)))],i+1)
