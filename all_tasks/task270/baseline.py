import re
p=lambda m,i=7,S=re.sub:-i*m or p([*zip(*eval(S('7([^[(]*), 0, 1','0\\1, 7, 1',S('3([^[(]*), 0, 2','0\\1, 3, 2',str(m)))))][::-1],i-1)
