p=lambda g,y=-1:[*zip(*[(sorted({*x}-{0})*9)[(y:=y+1):31]for x in g])]
