import sqlite3
from datetime import datetime
import forms
import functions


# import pandas lib as pd
import pandas as pd
 
# read by default 1st sheet of an excel file
df = pd.read_excel('./src/Perfil estático.xlsx')

#for i in df.index:
    #print(i.index)
#    pass

#print(c)

i = list(df.index)
#print(i)

for i in i:
    list=[]
    for j in range(0,9):
        data=df.iloc[i,j]
        list.append(data)
    nameuser=str(list[0])
    dni=int(list[1])
    if list[2]=="Femenino":
        sexo='F'
    else:
        sexo='M'
    fdn=list[3].date()
    try:
        tel=int(list[4])
    except:
        tel=int(3624123456)
    altura=list[5]
    if str(list[6])=='nan':
        email='test@gmail.com'
    else:
        email=str(list[6])
    ccuello=list[8]        
    perfil = (nameuser, dni, tel, email, sexo, str(fdn), altura, ccuello, 15, 22)
    print(perfil)
    functions.creadordeperfil(perfil)
    
#data=df.iloc[1,3]
#print(data)