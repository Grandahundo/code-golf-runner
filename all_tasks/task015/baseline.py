p=lambda i:[i:=eval(re.sub('0(?=.{31}(2)|.{28}(1))',r'6^\1\2',str([*zip(*i[::-1])])))for _ in i][3]
E=enumerate
