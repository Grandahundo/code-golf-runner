p=lambda m:eval(eval('(m:=re.sub("0(?=..1|..{%d}1)","1",str(m))[::-1]),'%len(m*3)*98)[-1])
import re
