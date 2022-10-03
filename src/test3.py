from ast import increment_lineno
from gekko import GEKKO

import numpy as np
import matplotlib.pyplot as plt

m = GEKKO(remote=True)
y = m.Var(value=1)
x = m.Var(value=1)
m.Equation(x+2*y==0)
m.Equation(x**2+y**2==1)
#m.options.SOLVER = 1 # IPOPT - 1 = APOPT
m.solve(display=False)

print(x.value,y.value)
