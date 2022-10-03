from pulp import *
from scipy.optimize import *
import scipy.special as sc
import numpy as np

#SCORES

squat=24
floorpull=30
horizontalpress=26
verticalpress=40
pulluprow=35
error=0

diasdeentrenamiento=6
numerodeejercicios=4
multiplier=0

scores=(squat,floorpull,horizontalpress,verticalpress,pulluprow)

maxscore=max(scores)

def objective(x):
    varsquat = x[0]
    varfloorpull = x[1]
    varhorizontalpress = x[2]
    varverticalpress = x[3]
    varpulluprow = x[4]
    multiplier = x[5]

    return (varsquat-squat)**2+(varfloorpull-floorpull)**2+(varhorizontalpress-horizontalpress)**2+(varverticalpress-verticalpress)**2+(varpulluprow-pulluprow)**2

def constraint1(x):
    cons1 = diasdeentrenamiento*numerodeejercicios
    print(cons1)
    x0=sc.round(x0)
    for i in range(5):
        cons1 = cons1 - (maxscore*x[5]/x[i],0)
        print(cons1)
    return cons1

def constraint2(x):
    for i in range(5):
        return round(maxscore*x[5]/x[i],1)+diasdeentrenamiento

# initial guesses
n=6
x0=np.zeros(n)
x0[0] = squat
x0[1] = floorpull
x0[2] = horizontalpress
x0[3] = verticalpress
x0[4] = pulluprow
x0[5] = 1

# show initial objective

# optimize
#b = (1.0,5.0)
#bnds = (b, b, b, b)
con2 = {'type': 'ineq', 'fun': constraint2}
con1 = {'type': 'eq', 'fun': constraint1}
cons = [con1,con2]
solution = minimize(objective,x0, constraints=cons)
x = solution.x

# show final objective
print('Final Objective: ' + str(objective(x)))

# print solution
print('Solution')
print('Squat = ' + str(x[0]))
print('Levantamiento del Suelo = ' + str(x[1]))
print('Press horizontal = ' + str(x[2]))
print('Press vertical = ' + str(x[3]))
print('Remo = ' + str(x[4]))
print('Multiplier = ' + str(x[5]))

print('Entrenamientos a la semana: ' + str(round(maxscore/x[0]*x[5],0)+round(maxscore/x[1]*x[5],0)+round(maxscore/x[2]*x[5],0)+round(maxscore/x[3]*x[5],0)+round(maxscore/x[4]*x[5],0)))