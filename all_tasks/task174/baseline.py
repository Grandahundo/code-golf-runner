p=lambda g,c=3,t=[]:c%3//2*t*((a:=[r for r in zip(*c%3*t or g)if c//3in r])==a[::-1])or p(g,c+1,a)  # <- this seems promising
