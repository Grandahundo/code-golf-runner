p=lambda a,b=[]:[p(c,d)for*c,in map(zip,[a[2]]+a,a[3:],a[7:])for*d,in map(zip,[a[2]]+b+a,(b+a)[3:],(b+a)[7:11])][5:]or('5'in'%s'%b)*5or int(f'{b}0'[str(a).find('4')])
