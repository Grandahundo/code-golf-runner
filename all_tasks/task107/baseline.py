def p(i):g=sum(i,[]);z=len({*g})-1;r=range(5*z);return[[i[s:=x//z][t:=y//z]or(g[(t-s)%6::6].count(f:=i[1][1])>>(x-y)%z|g[(t+s)%5::4].count(f)>>(x-~y)%z)&2for y in r]for x in r]
exec(('def p(i):g=sum(i,[]);z=len({*g})-1;return[[i[x//z][y//z]'+'or g[(y%sx)//z%%%s::%s].count(g[6])>>(x-%sy)%%z&2'*2+'for %s in range(5*z)]'*2)%(*'-66++54~yx',))
exec(('def p(i):g=sum(i,[]);z=len({*g})-1;return[[i[x//z][y//z]'+'or(x-%sy==z*0**g[1]%sz*0**g[5]+z%sz)*2'*2+'for %s in range(5*z)]'*2)%(*'~+++--yx',))
exec(('def p(i):g=sum(i,[]);z=len({*g})-1;return[[i[x//z][y//z]'+'or(x-%sy==z*(0**g[1]%s0**g[5]+%s))*2'*2+'for %s in range(5*z)]'*2)%(*'~+2+-0yx',))
exec(('def p(i):z=len({*str(i)})-5;return[[i[x//z][y//z]'+'or(x-%sy==z*(0**i[0][1]%s0**i[1][0]+%s))*2'*2+'for %s in range(5*z)]'*2)%(*'~+2+-0yx',))
