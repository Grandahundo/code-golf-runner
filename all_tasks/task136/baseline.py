p=lambda m,i=9:-i*m or p(eval(re.sub("(?<=(2.{34}){2})0","2",re.sub("0(?=(.{34}1){2})","1",str(m)))),i-1)
import re
