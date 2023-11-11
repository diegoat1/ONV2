from pulp import *
import sqlite3
from io import *
import os
from datetime import datetime
import math
from flask import *
import numpy as np

### FUNCIÓN QUE AGREGA LOS PERFILES ###

def creadordeperfil(perfil):
    # Base de datos
    basededatos = sqlite3.connect("src/Basededatos")
    cursor = basededatos.cursor()
    try:
        cursor.execute("CREATE TABLE PERFILESTATICO (NOMBRE_APELLIDO VARCHAR(50), DNI INTEGER PRIMARY KEY, NUMERO_TELEFONO INTEGER, EMAIL VARCHAR(50), SEXO VARCHAR(20), FECHA_NACIMIENTO DATE, ALTURA DECIMAL, CIRC_CUELLO DECIMAL, CIRC_MUNECA DECIMAL, CIRC_TOBILLO DECIMAL)")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("INSERT INTO PERFILESTATICO VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", perfil)
        basededatos.commit()
        nameuser = perfil[0]
        success_message = 'El usuario {} ha sido creado.'.format(nameuser)
        flash(success_message)
    except sqlite3.IntegrityError:
        nameuser = perfil[0]
        warning_message = 'El usuario {} ya ha sido creado con anterioridad.'.format(nameuser)
        flash(warning_message)
        pass

## FUNCIÓN QUE EDITA LOS PERFILES ESTATICOS ###

def actualizarperfilest(perfil):
    #Base de datos
    basedatos = sqlite3.connect("src/Basededatos")
    cursor = basedatos.cursor()
    try:
        cursor.execute("UPDATE PERFILESTATICO SET NOMBRE_APELLIDO= ?, NUMERO_TELEFONO=?, EMAIL=?, SEXO=?, FECHA_NACIMIENTO=?, ALTURA=?, CIRC_CUELLO=?, CIRC_MUNECA=?, CIRC_TOBILLO=? WHERE DNI = ?", (perfil[0], perfil[2], perfil[3], perfil[4], perfil[5], perfil[6], perfil[7], perfil[8], perfil[9], perfil[1]))
        basedatos.commit()
        nameuser = perfil[0]
        success_message = 'El usuario {} ha sido actualizado.'.format(nameuser)
        flash(success_message)
    except sqlite3.IntegrityError:
        nameuser = perfil[0]
        warning_message = 'El usuario {} ya ha sido creado con anterioridad.'.format(
            nameuser)
        flash(warning_message)
    
### FUNCIÓN QUE ACTUALIZA LOS PERFILES DINAMICOS ###

def actualizarperfil(nameuser, fdr, peso, cabd, ccin, ccad):
    # Base de datos
    basededatos = sqlite3.connect("src/Basededatos")
    cursor = basededatos.cursor()
    try:
        cursor.execute("CREATE TABLE PERFILDINAMICO (ID INTEGER PRIMARY KEY AUTOINCREMENT, NOMBRE_APELLIDO VARCHAR(50), FECHA_REGISTRO DATE, CIRC_CIN DECIMAL, CIRC_CAD DECIMAL, CIRC_ABD DECIMAL, PESO DECIMAL, BF DECIMAL, IMC DECIMAL, IMMC DECIMAL, PESO_GRASO DECIMAL, PESO_MAGRO DECIMAL, DELTADIA INTEGER, DELTAPESO DECIMAL, DELTADIAPESO DECIMAL, DELTAPG DECIMAL, DELTADIAPG DECIMAL, DELTAPM DECIMAL, DELTADIAPM DECIMAL, DELTAPESOCAT VARCHAR(50), LBMLOSS DECIMAL, LBMLOSSCAT VARCHAR(50), FBMGAIN DECIMAL, FBMGAINCAT VARCHAR (50), SCOREIMMC DECIMAL, SCOREBF DECIMAL, BODYSCORE DECIMAL, INCDAYS INTEGER, DECDAYS INTEGER, DAYS INTEGER, PF DECIMAL, PMF DECIMAL, PGF DECIMAL, ABDF DECIMAL, CINF DECIMAL, CADF DECIMAL, SOLVER_CATEGORY VARCHAR(50))")
    except sqlite3.OperationalError:
        pass
    try:
        #Obtener datos de la tabla perfil estatico - altura, sexo, circunferencia de cuello
        cursor.execute("SELECT ALTURA FROM PERFILESTATICO WHERE NOMBRE_APELLIDO=?", [nameuser])
        altura=cursor.fetchone()[0]
        cursor.execute("SELECT SEXO FROM PERFILESTATICO WHERE NOMBRE_APELLIDO=?", [nameuser])
        sexo=cursor.fetchone()[0]
        cursor.execute("SELECT CIRC_CUELLO FROM PERFILESTATICO WHERE NOMBRE_APELLIDO=?", [nameuser])
        ccu=cursor.fetchone()[0]
        
        #Calculo de porcentaje de grasa corporal
        if sexo=="M":
            bf=495/(1.0324-0.19077*math.log(cabd-ccu,10)+0.15456*math.log(altura,10))-450
        elif sexo=="F":
            bf=495/(1.29579-0.35004*math.log(ccad+ccin-ccu,10)+0.221*math.log(altura,10))-450

        #Calculo del peso graso y magro
        pg=peso*bf/100
        pm=peso-pg
    
        #Calculo de IMC
        imc=peso/((altura/100)**2)

        #Calculo de IMMC (Indice de masa magra corporal)
        immc=pm/((altura/100)**2)

        # CALCULO PESO FINAL LUEGO DEL DEFICIT

        #pesofinal=(pm-factor*peso)/(1-(bfobj/100)-factor)

        #Obtener datos de la base de datos
    
        cursor.execute("SELECT FECHA_REGISTRO, PESO, PESO_GRASO, PESO_MAGRO FROM PERFILDINAMICO WHERE NOMBRE_APELLIDO=? ORDER BY FECHA_REGISTRO DESC LIMIT 1", [nameuser])
        datos=cursor.fetchone()

        deltapeso=0
        deltadia=0
        deltadiapeso=0
        deltapesocat=""
        deltapg=0
        deltadiapg=0
        deltapm=0
        deltadiapm=0
        lbmloss=0
        lbmlosscat=""
        fbmgain=0
        fbmgaincat=""

        if datos!=None:
            #SEPARAR LOS DATOS EN EL ESTADO INICIAL Y FINAL

            estadofinal=fdr,peso,pg,pm
            estadoinicial=datos
            fbmgaincat=""
            lbmlosscat=""

            #TRANSFORMAR LAS FECHAS EN DATOS Y LUEGO SACAR SU DELTA
        
            d0=str(estadofinal[0])
            d0=datetime.strptime(d0, "%Y-%m-%d")
            d1=datetime.strptime(estadoinicial[0], "%Y-%m-%d")
        
            deltadia=d0-d1
            deltadia=deltadia.days

            # SACAR DELTA DE PESO Y CATEGORIZAR

            deltapeso=estadofinal[1]-estadoinicial[1]
            deltadiapeso=deltapeso/deltadia
            if deltapeso>0:
                deltapesocat="Aumento del peso"
            elif deltapeso<0:
                deltapesocat="Disminución del peso"
            elif deltapeso==0:
                deltapesocat="Peso Mantenido"
        
            # SACAR DELTA DE PESO MAGRO Y PESO GRASO POR DÍA Y CATEGORIZAR

            deltapg=(estadofinal[2]-estadoinicial[2])
            deltadiapg=deltapg/deltadia
            deltapm=(estadofinal[3]-estadoinicial[3])
            deltadiapm=deltapm/deltadia

            lbmloss=deltadiapm/(deltadiapm+deltadiapg)
            fbmgain=deltadiapg/(deltadiapm+deltadiapg)

            # CLASIFICACIÓN DEL DESCENSO O AUMENTO DE PESO

            if deltapeso>=0:
                if fbmgain<=.2:
                    fbmgaincat="Excelente"
                elif fbmgain<=.5:
                    fbmgaincat="Correcto"
                elif fbmgain>.5:
                    fbmgaincat="Imprudente"
            elif deltapeso<0:
                if lbmloss>=.5:
                    lbmlosscat="Imprudente"
                elif lbmloss>.36:
                    lbmlosscat="Nada bueno"
                elif lbmloss>.25:
                    lbmlosscat="Correcto"
                elif lbmloss>=.15:
                    lbmlosscat="Excelente"
                elif lbmloss<.15:
                    lbmlosscat="Impresionante"

            # REDONDEOS

            deltapeso=round(deltapeso,2)
            deltadiapeso=round(deltadiapeso,2)
            deltapg=round(deltapg,2)
            deltadiapg=round(deltadiapg,2)
            deltapm=round(deltapm,2)
            deltadiapm=round(deltadiapm,2)
            lbmloss=round(lbmloss,2)
            fbmgain=round(fbmgain,2)
        else:
            pass

        if lbmloss>=10000:
            lbmloss=1
        elif lbmloss<=-10000:
            lbmloss=-1
        if fbmgain>10000:
            fbmgain=1
        elif fbmgain<=-10000:
            fbmgain=-1

        #REDONDEOS
        
        pg=round(pg,2)
        pm=round(pm,2)
        imc=round(imc,2)
        immc=round(immc,2)
        bf=round(bf,2)
        
        perfil=(nameuser, fdr, ccin, ccad, cabd, peso, bf, imc, immc, pg, pm, deltadia, deltapeso, deltadiapeso, deltapg, deltadiapg, deltapm, deltadiapm, deltapesocat, lbmloss, lbmlosscat, fbmgain, fbmgaincat)

        cursor.execute("INSERT INTO PERFILDINAMICO (NOMBRE_APELLIDO, FECHA_REGISTRO, CIRC_CIN, CIRC_CAD, CIRC_ABD, PESO, BF, IMC, IMMC, PESO_GRASO, PESO_MAGRO, DELTADIA, DELTAPESO, DELTADIAPESO, DELTAPG, DELTADIAPG, DELTAPM, DELTADIAPM, DELTAPESOCAT, LBMLOSS, LBMLOSSCAT, FBMGAIN, FBMGAINCAT) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", perfil)
        basededatos.commit()

        basededatos=sqlite3.connect("src/Basededatos")
        cursor=basededatos.cursor()

        #SELECCIONAR ID

        cursor.execute("SELECT ID FROM PERFILDINAMICO WHERE NOMBRE_APELLIDO=? ORDER BY FECHA_REGISTRO DESC LIMIT 1", [nameuser])

        id=cursor.fetchone()[0]

        #DEFINIR OBJETIVO
        cursor.execute("SELECT GOALIMMC, GOALBF FROM OBJETIVO WHERE NOMBRE_APELLIDO=?", [nameuser])
        goal=cursor.fetchone()
        if goal==None:
            if sexo=="M":
                goalimmc=23.7
                goalbf=6
            elif sexo=="F":
                goalimmc=19.4
                goalbf=14
        else:
            goalimmc=goal[0]
            goalbf=goal[1]

        def clean_data(data1, data2):
            # Calcula la media y la desviación estándar para ambas listas
            mean1, std1 = np.mean(data1), np.std(data1)
            mean2, std2 = np.mean(data2), np.std(data2)
            
            # Identifica los índices de los valores dentro de dos desviaciones estándar de la media
            valid_indices1 = ((data1 >= mean1 - 2*std1) & (data1 <= mean1 + 2*std1))
            valid_indices2 = ((data2 >= mean2 - 2*std2) & (data2 <= mean2 + 2*std2))
            
            # Solo conserva los valores que son válidos en ambas listas
            valid_indices = valid_indices1 & valid_indices2
            cleaned_data1 = [val for idx, val in enumerate(data1) if valid_indices[idx]]
            cleaned_data2 = [val for idx, val in enumerate(data2) if valid_indices[idx]]
            
            return cleaned_data1, cleaned_data2

        def calculate_averages(params, db_connection, max_days=None, fbmgain_limit=None, lbmloss_limit=None):
            cursor = db_connection.cursor()

            # Preparar la consulta SQL
            
            if fbmgain_limit is None:
                query = ("SELECT DELTAPM, DELTAPG, DELTADIA FROM PERFILDINAMICO "
                    "WHERE DELTAPESOCAT=? AND NOMBRE_APELLIDO=? ORDER BY FECHA_REGISTRO DESC")
                params = params
            else:
                if params[1] is None:
                    query = ("SELECT DELTAPM, DELTAPG, DELTADIA FROM PERFILDINAMICO "
                    "WHERE DELTAPESOCAT=? AND FBMGAIN<? AND LBMLOSS<? ORDER BY FECHA_REGISTRO DESC")
                    params = [params[0]] + [fbmgain_limit, lbmloss_limit]                    
                else:
                    query = ("SELECT DELTAPM, DELTAPG, DELTADIA FROM PERFILDINAMICO "
                    "WHERE DELTAPESOCAT=? AND NOMBRE_APELLIDO=? AND FBMGAIN<? AND LBMLOSS<? ORDER BY FECHA_REGISTRO DESC")
                    params = params + [fbmgain_limit, lbmloss_limit]

            print("Executing query:", query)
            print("With parameters:", params)

            # Ejecutar la consulta
            cursor.execute(query, params)
            trend_data = cursor.fetchall()

            print("Todos los datos: ", trend_data)

            # Inflar los datos
            inflated_deltadiapm = []
            inflated_deltadiapg = []
            for deltapm, deltapg, deltadia in trend_data:
                deltadiapm=deltapm/deltadia
                deltadiapg=deltapg/deltadia
                for i in range(deltadia):
                    if max_days and len(inflated_deltadiapm) >= max_days:
                        break  # Salir del bucle si se alcanza el límite
                    inflated_deltadiapm.append(deltadiapm)
                    inflated_deltadiapg.append(deltadiapg)
                if max_days and len(inflated_deltadiapm) >= max_days:
                    break  # Salir del bucle principal si se alcanza el límite

            # Limpiar los datos
            cleaned_deltadiapm, cleaned_deltadiapg = clean_data(inflated_deltadiapm, inflated_deltadiapg)

            print("Datos limpiados PG: ", cleaned_deltadiapg)
            print("Datos limpiados PM: ", cleaned_deltadiapm)

            # Calcular los promedios
            def get_average(data):
                return sum(data) / len(data) if data else 0

            ave_deltadiapm = get_average(cleaned_deltadiapm)
            ave_deltadiapg = get_average(cleaned_deltadiapg)

            return ave_deltadiapm, ave_deltadiapg

        #ESTABLECER LAS ECUACIONES DE PUNTAJE
        ScoreFMMI=0
        ScoreBF=0
        if sexo=="M":
            if immc>=23.7:
                ScoreFMMI=100
            elif immc<=17:
                ScoreFMMI=0
            else:
                ScoreFMMI=0.002466321*immc**6-0.24219497*immc**5+9.266704428*immc**4-167.682018*immc**3+1277.535698*immc**2-34999.12222
            if bf<=6:
                ScoreBF=100
            elif bf>=26:
                ScoreBF=0
            else:
                ScoreBF=(-5.12204882)*bf+130.6722689
                if ScoreBF<=0:
                    ScoreBF=0
                else:
                    pass
        elif sexo=="F":
            if immc>=19.4:
                ScoreFMMI=100
            elif immc<=13.6:
                ScoreFMMI=0
            else:
                ScoreFMMI=(-0.074175032)*immc**6+7.431102244*immc**5-309.2054553*immc**4+6840.194429*immc**3-84852.85884*immc**2+559706.116*immc-1533886.926
            if bf<=14:
                ScoreBF=100
            elif bf>=32:
                ScoreBF=0
            else:
                ScoreBF=0.035745253*bf**3-2.41422024*bf**2+45.87549327*bf-167.1547132
        else:
            pass

        BodyScore=0
        #if ratio!=0:
        BodyScore=(ScoreFMMI+ScoreBF)/2
        #else:
        #    pass

        ScoreBF=round(ScoreBF)
        ScoreFMMI=round(ScoreFMMI)
        BodyScore=round(BodyScore)
        
        #PESO FINAL GRASO Y MAGRO, PERIMETROS DE ABDOMEN, CINTURA Y CADERA

        pmf=goalimmc*((altura/100)**2)
        pgf=(goalbf/100*pmf)/(1-(goalbf/100))
        pf=pmf+pgf

        abdf=0
        cinf=0
        cadf=0
        if sexo=='M':
            abdf=ccu+math.exp(5152*math.log(altura)/6359+103240*math.log(10)/19077-16500000*math.log(10)/(6359*(goalbf+450)))
        elif sexo=='F':
            cadf=(10*ccu+10*math.exp((5525*math.log(altura)/8751)+(43193*math.log(10)/11668)-(4125000*math.log(10)/(2917*(goalbf+450)))))/17
            cinf=cadf*.7
        
        #SOLVER FORECAST

        def solver(aveincpm, avedecpm, aveincpg, avedecpg, pm, pmf, pg, pgf):
            incdays=0
            decdays=0
            days=0
            solver_category=""
            
            forecast = LpProblem("Days", LpMinimize)
            IncDays = LpVariable("incdays", 0)
            DecDays = LpVariable("decdays", 0)
            
            forecast += lpSum(IncDays+DecDays)
            forecast += lpSum(IncDays*aveincpm+DecDays*avedecpm+pm) >= pmf, "PM FINAL"
            forecast += lpSum(IncDays*aveincpg+DecDays*avedecpg+pg) <= pgf, "PG FINAL "
            
            status=forecast.solve()

            if status == 1:                
                decdays=round(forecast.variables()[0].varValue)
                incdays=round(forecast.variables()[1].varValue)
                days=round(value(forecast.objective))
                solver_category="Óptimo"
            else: 
                solver_category="No calculable"

            return incdays, decdays, days, solver_category
        
        max_days = 183  # o cualquier número que desees
        
        aveincpm, aveincpg = calculate_averages(["Aumento del peso", nameuser], basededatos, max_days)
        avedecpm, avedecpg = calculate_averages(["Disminución del peso", nameuser], basededatos, max_days)

        print("aveincpm: ",aveincpm, "avedecpm: ",avedecpm,"aveincpg: ", aveincpg,"avedecpg: ", avedecpg,"pm: ", pm,"pmf: ", pmf,"pg: ", pg,"pf: ", pgf)
        
        incdays, decdays, days, solver_category = solver(aveincpm, avedecpm, aveincpg, avedecpg, pm, pmf, pg, pgf)
        
        if solver_category == "No calculable":
            aveincpm, aveincpg = calculate_averages(["Aumento del peso", nameuser], basededatos, max_days, 0.5, 99)
            avedecpm, avedecpg = calculate_averages(["Disminución del peso", nameuser], basededatos, max_days, 99, 0.5)
            
            print("aveincpm: ",aveincpm, "avedecpm: ",avedecpm,"aveincpg: ", aveincpg,"avedecpg: ", avedecpg,"pm: ", pm,"pmf: ", pmf,"pg: ", pg,"pf: ", pgf)

            incdays, decdays, days, solver_category = solver(aveincpm, avedecpm, aveincpg, avedecpg, pm, pmf, pg, pgf)

            if solver_category == "No calculable":
                aveincpm, aveincpg = calculate_averages(["Aumento del peso", None], basededatos, max_days, 0.5, 99)
                avedecpm, avedecpg = calculate_averages(["Disminución del peso", None], basededatos, max_days, 99, 0.5)
                
                print("aveincpm: ",aveincpm, "avedecpm: ",avedecpm,"aveincpg: ", aveincpg,"avedecpg: ", avedecpg,"pm: ", pm,"pmf: ", pmf,"pg: ", pg,"pf: ", pgf)
                
                incdays, decdays, days, solver_category = solver(aveincpm, avedecpm, aveincpg, avedecpg, pm, pmf, pg, pgf)

                if solver_category == "Óptimo":
                    solver_category = "General"
            
            else:
                solver_category = "Positivo"
        else:
            solver_category="Completo"

        print("ID: ", id, "Categoria solver: ", solver_category)

        update=(round(pf), round(pmf), round(pgf), ScoreFMMI, ScoreBF, BodyScore, incdays, decdays, days, round(abdf), round(cinf), round(cadf), solver_category, id)
        cursor.execute("UPDATE PERFILDINAMICO SET PF=?, PMF=?, PGF=?, SCOREIMMC=?, SCOREBF=?, BODYSCORE=?, INCDAYS=?, DECDAYS=?, DAYS=?, ABDF=?, CINF=?, CADF=?, SOLVER_CATEGORY=? WHERE ID=?", update)
        basededatos.commit()

        success_message = 'Los datos del usuario {} han sido registrados y calculados.'.format(nameuser)
        try:
            flash(success_message)
        except:
            pass
    except sqlite3.IntegrityError:
        nameuser = perfil[0]
        warning_message = 'Los datos del usuario {} tienen un error.'.format(nameuser)
        flash(warning_message)

    #Calculo de los objetivos general (deficit, mantenimimiento, ganancia) y especifico (peso objetivo, %bf, imc)

    #Calculo del tiempo que le queda para llegar a su objetivo

### FUNCIÓN QUE EDITA LOS DATOS DEL PERFIL DINAMICO ###

def actualizarperfildin(perfil):
    #Base de datos
    basedatos = sqlite3.connect("src/Basededatos")
    cursor = basedatos.cursor()
    #Obtener datos de la tabla perfil estatico - altura, sexo, circunferencia de cuello
    cursor.execute("SELECT ALTURA FROM PERFILESTATICO WHERE NOMBRE_APELLIDO=?", [perfil[1]])
    altura=cursor.fetchone()[0]
    cursor.execute("SELECT SEXO FROM PERFILESTATICO WHERE NOMBRE_APELLIDO=?", [perfil[1]])
    sexo=cursor.fetchone()[0]
    cursor.execute("SELECT CIRC_CUELLO FROM PERFILESTATICO WHERE NOMBRE_APELLIDO=?", [perfil[1]])
    ccu=cursor.fetchone()[0]

    peso=perfil[3]
    cabd=perfil[4]
    ccad=perfil[6]
    ccin=perfil[5]
    
    #Calculo de porcentaje de grasa corporal
    if sexo=="M":
        bf=495/(1.0324-0.19077*math.log(cabd-ccu,10)+0.15456*math.log(altura,10))-450
    elif sexo=="F":
        bf=495/(1.29579-0.35004*math.log(ccad+ccin-ccu,10)+0.221*math.log(altura,10))-450

    #Calculo del peso graso y magro
    pg=peso*bf/100
    pm=peso-pg

    #Calculo de IMC
    imc=peso/((altura/100)**2)

    #Calculo de IMMC (Indice de masa magra corporal)
    immc=pm/((altura/100)**2)

    cursor.execute("SELECT FECHA_REGISTRO, PESO, PESO_GRASO, PESO_MAGRO FROM PERFILDINAMICO WHERE NOMBRE_APELLIDO=? ORDER BY FECHA_REGISTRO DESC LIMIT 1", [perfil[1]])
    datos=cursor.fetchone()

    deltapeso=0
    deltapesocat=""
    deltadia=0
    deltadiapeso=0
    deltapg=0
    deltadiapg=0
    deltapm=0
    deltadiapm=0
    lbmloss=0
    fbmgain=0

    if datos!=None:
        #SEPARAR LOS DATOS EN EL ESTADO INICIAL Y FINAL

        estadofinal=perfil[2],peso,pg,pm
        estadoinicial=datos
        fbmgaincat=""
        lbmlosscat=""

        #TRANSFORMAR LAS FECHAS EN DATOS Y LUEGO SACAR SU DELTA
    
        d0=str(estadofinal[0])
        d0=datetime.strptime(d0, "%Y-%m-%d")
        d1=datetime.strptime(estadoinicial[0], "%Y-%m-%d")
    
        deltadia=d0-d1
        deltadia=deltadia.days

        # SACAR DELTA DE PESO Y CATEGORIZAR

        deltapeso=estadofinal[1]-estadoinicial[1]
        deltadiapeso=deltapeso/deltadia
        if deltapeso>=0:
            deltapesocat="Aumento del peso"
        elif deltapeso<0:
            deltapesocat="Disminución del peso"
    
        # SACAR DELTA DE PESO MAGRO Y PESO GRASO POR DÍA Y CATEGORIZAR

        deltapg=(estadofinal[2]-estadoinicial[2])
        deltadiapg=deltapg/deltadia
        deltapm=(estadofinal[3]-estadoinicial[3])
        deltadiapm=deltapm/deltadia

        lbmloss=deltadiapm/deltadiapeso
        fbmgain=deltadiapg/deltadiapeso

        # CLASIFICACIÓN DEL DESCENSO O AUMENTO DE PESO

        if deltapeso>=0:
            if fbmgain<=.2:
                fbmgaincat="Excelente"
            elif fbmgaincat<=.5:
                fbmgaincat="Correcto"
            elif fbmgaincat>.5:
                fbmgaincat="Imprudente"
        elif deltapeso<0:
            if lbmloss>=.5:
                lbmlosscat="Imprudente"
            elif lbmloss>.36:
                lbmlosscat="Nada bueno"
            elif lbmloss>.25:
                lbmlosscat="Correcto"
            elif lbmloss>=.15:
                lbmlosscat="Excelente"
            elif lbmloss<.15:
                lbmlosscat="Impresionante"

        # REDONDEOS

        deltapeso=round(deltapeso,2)
        deltadiapeso=round(deltadiapeso,2)
        deltapg=round(deltapg,2)
        deltadiapg=round(deltadiapg,2)
        deltapm=round(deltapm,2)
        deltadiapm=round(deltadiapm,2)
        lbmloss=round(lbmloss,2)
        fbmgain=round(fbmgain,2)
    else:
        pass

    # REGISTRAR EN UNA TABLA DE ANALISIS

    # CALCULO PESO MUSCULAR MAXIMO Y CALCULADORA DE MEDIDAS

    #REDONDEOS
    
    pg=round(pg,2)
    pm=round(pm,2)
    imc=round(imc,2)
    immc=round(immc,2)
    bf=round(bf,2)

    if lbmloss>=10000:
        lbmloss=1
    elif lbmloss<=-10000:
        lbmloss=-1
    if fbmgain>10000:
        fbmgain=1
    elif fbmgain<=-10000:
        fbmgain=-1

    cursor.execute("UPDATE PERFILDINAMICO SET NOMBRE_APELLIDO=?, FECHA_REGISTRO=?, PESO=?, CIRC_ABD=?, CIRC_CIN=?, CIRC_CAD=?, BF=?, IMC=?, IMMC=?, PESO_GRASO=?, PESO_MAGRO=?, DELTADIA=?, DELTAPESO=?, DELTADIAPESO=?, DELTAPG=?, DELTADIAPG=?, DELTAPM=?, DELTADIAPM=?, DELTAPESOCAT=?, LBMLOSS=?, LBMLOSSCAT=?, FBMGAIN=?, FBMGAINCAT=? WHERE ID = ?", (perfil[1], perfil[2], peso, cabd, ccin, ccad, bf, imc, immc, pg, pm, deltadia, deltapeso, deltadiapeso, deltapg, deltadiapg, deltapm, deltadiapm, deltapesocat, lbmloss, lbmlosscat, fbmgain, fbmgaincat, perfil[0]))

    nameuser = perfil[1]
    basedatos.commit()
    
    basededatos=sqlite3.connect("src/Basededatos")
    cursor=basededatos.cursor()

    #SELECCIONAR ID

    cursor.execute("SELECT ID FROM PERFILDINAMICO WHERE NOMBRE_APELLIDO=? ORDER BY FECHA_REGISTRO DESC LIMIT 1", [nameuser])

    id=cursor.fetchone()[0]

    #DEFINIR OBJETIVO
    cursor.execute("SELECT GOALIMMC, GOALBF FROM OBJETIVO WHERE NOMBRE_APELLIDO=?", [nameuser])
    goal=cursor.fetchone()
    if goal==None:
        if sexo=="M":
            goalimmc=23.7
            goalbf=6
        elif sexo=="F":
            goalimmc=19.4
            goalbf=14
    else:
        goalimmc=goal[0]
        goalbf=goal[1]

    #TENDENCIAS SUBIDA DE PESO
    go=0
    cursor.execute("SELECT DELTADIAPM, DELTADIAPG FROM PERFILDINAMICO WHERE DELTAPESOCAT=? AND NOMBRE_APELLIDO=? ORDER BY FECHA_REGISTRO DESC LIMIT 7", ["Aumento del peso", nameuser])
    increasetrend=cursor.fetchall()
    if len(increasetrend)>0:
        deltadiapg=0
        deltadiapm=0
        for i in range(len(increasetrend)):
            deltadiapg=deltadiapg+increasetrend[i][1]
            deltadiapm=deltadiapm+increasetrend[i][0]
        aveincpg=deltadiapg/(len(increasetrend))
        aveincpm=deltadiapm/(len(increasetrend))
        go=1
    else:
        pass

    #TENDENCIAS BAJADA DE PESO
    cursor.execute("SELECT DELTADIAPM, DELTADIAPG FROM PERFILDINAMICO WHERE DELTAPESOCAT=? AND NOMBRE_APELLIDO=? ORDER BY FECHA_REGISTRO DESC LIMIT 7", ["Disminución del peso", nameuser])
    decreasetrend=cursor.fetchall()
    global avedecpm
    global avedecpg
    if len(decreasetrend)>0:
        deltadiapg=0
        deltadiapm=0
        for i in range(len(decreasetrend)):
            deltadiapg=deltadiapg+decreasetrend[i][1]
            deltadiapm=deltadiapm+decreasetrend[i][0]
        avedecpg=deltadiapg/(len(decreasetrend))
        avedecpm=deltadiapm/(len(decreasetrend))
        go=go*1
    else:
        pass

    #RELACIÓN DE RENDIMIENTOS
    
    #ratio=0
    #if go==1:
    #    ratio=-avedecpg/aveincpm
    #else:
    #    pass

    #PUNTAJE CORPORAL

    #ESTABLECER LAS ECUACIONES DE PUNTAJE
    ScoreFMMI=0
    ScoreBF=0
    if sexo=="M":
        if immc>=23.7:
            ScoreFMMI=100
        elif immc<=17:
            ScoreFMMI=0
        else:
            ScoreFMMI=0.002466321*immc**6-0.24219497*immc**5+9.266704428*immc**4-167.682018*immc**3+1277.535698*immc**2-34999.12222
        if bf<=6:
            ScoreBF=100
        elif bf>=26:
            ScoreBF=0
        else:
            ScoreBF=(-5.12204882)*bf+130.6722689
            if ScoreBF<=0:
                ScoreBF=0
            else:
                pass
    elif sexo=="F":
        if immc>=19.4:
            ScoreFMMI=100
        elif immc<=13.6:
            ScoreFMMI=0
        else:
            ScoreFMMI=(-0.074175032)*immc**6+7.431102244*immc**5-309.2054553*immc**4+6840.194429*immc**3-84852.85884*immc**2+559706.116*immc-1533886.926
        if bf<=14:
            ScoreBF=100
        elif bf>=32:
            ScoreBF=0
        else:
            ScoreBF=0.035745253*bf**3-2.41422024*bf**2+45.87549327*bf-167.1547132
    else:
        pass

    BodyScore=0
    #if ratio!=0:
    BodyScore=(ScoreFMMI+ScoreBF)/2
    #else:
    #    pass

    ScoreBF=round(ScoreBF)
    ScoreFMMI=round(ScoreFMMI)
    BodyScore=round(BodyScore)
    
    #PESO FINAL GRASO Y MAGRO

    pmf=goalimmc*((altura/100)**2)
    pgf=(goalbf/100*pmf)/(1-(goalbf/100))
    pf=pmf+pgf

    abdf=0
    cinf=0
    cadf=0
    if sexo=='M':
        abdf=ccu+math.exp(5152*math.log(altura)/6359+103240*math.log(10)/19077-16500000*math.log(10)/(6359*(goalbf+450)))
    elif sexo=='F':
        cadf=(10*ccu+10*math.exp((5525*math.log(altura)/8751)+(43193*math.log(10)/11668)-(4125000*math.log(10)/(2917*(goalbf+450)))))/17
        cinf=cadf*.7

    #SOLVER FORECAST

    incdays=0
    decdays=0
    days=0
    if go==1:
        forecast = LpProblem("Days", LpMinimize)
        IncDays = LpVariable("incdays", 0)
        DecDays = LpVariable("decdays", 0)
        forecast += lpSum(IncDays+DecDays)
        forecast += lpSum(IncDays*aveincpm+DecDays*avedecpm+pm) == pmf, "PM FINAL"
        forecast += lpSum(IncDays*aveincpm+DecDays*avedecpg+pg) == pgf, "PG FINAL "
        forecast.solve()

        decdays=round(forecast.variables()[0].varValue)
        incdays=round(forecast.variables()[1].varValue)
        days=round(value(forecast.objective))
    else:
        pass

    update=(pf, pmf, pgf, ScoreFMMI, ScoreBF, BodyScore, incdays, decdays, days, round(abdf), round(cinf), round(cadf), id)

    cursor.execute("UPDATE PERFILDINAMICO SET PF=?, PMF=?, PGF=? SCOREIMMC=?, SCOREBF=?, BODYSCORE=?, INCDAYS=?, DECDAYS=?, DAYS=?, ABDF=?, CINF=?, CADF=? WHERE ID=?", (update))
    basededatos.commit()
    
    success_message = 'El usuario {} ha sido actualizado.'.format(nameuser)
    flash(success_message)

### CREA UNA LISTA CON TODOS LOS USUARIOS ###

def creadordelista():
    basededatos = sqlite3.connect("src/Basededatos")
    cursor = basededatos.cursor()
    cursor.execute(
        "SELECT NOMBRE_APELLIDO, DNI FROM PERFILESTATICO ORDER BY NOMBRE_APELLIDO ASC")
    lista = []
    for i in cursor.fetchall():
        i = [i[0], i[0]]
        lista.append(i)
    return lista

### FUNCIÓN PARA DEFINIR OBJETIVOS ###

def goal(goal):
    
    #Conectar con la base de datos
    basededatos=sqlite3.connect("src/Basededatos")
    cursor=basededatos.cursor()

    #Guardar datos
    try:
        cursor.execute("INSERT INTO OBJETIVO VALUES(?, ?, ?)", (goal.nameuser.data, goal.goalimmc.data, goal.goalbf.data))
        basededatos.commit()
        success_message = 'Los objetivos de {} han sido definidos.'.format(goal.nameuser.data)
        flash(success_message)
    except sqlite3.IntegrityError:
        cursor.execute("UPDATE OBJETIVO SET GOALIMMC=?, GOALBF=? WHERE NOMBRE_APELLIDO=?", (goal.goalimmc.data, goal.goalbf.data, goal.nameuser.data))
        basededatos.commit()
        success_message = 'Los objetivos de {} se han actualizados.'.format(goal.nameuser.data)
        flash(success_message)

### FUNCIÓN PARA ARMAR PLANES ###

def plannutricional(planner):

    #Conectar con la base de datos
    basededatos=sqlite3.connect("src/Basededatos")
    cursor=basededatos.cursor()

    #Obtener datos de la base de datos
    cursor.execute("SELECT PESO FROM PERFILDINAMICO WHERE NOMBRE_APELLIDO=? ORDER BY FECHA_REGISTRO DESC LIMIT 1", [planner.nameuser.data])
    peso=cursor.fetchone()[0]
    cursor.execute("SELECT PESO_MAGRO FROM PERFILDINAMICO WHERE NOMBRE_APELLIDO=? ORDER BY FECHA_REGISTRO DESC LIMIT 1", [planner.nameuser.data])
    pm=cursor.fetchone()[0]
    cursor.execute("SELECT PESO_GRASO FROM PERFILDINAMICO WHERE NOMBRE_APELLIDO=? ORDER BY FECHA_REGISTRO DESC LIMIT 1", [planner.nameuser.data])
    pg=cursor.fetchone()[0]
    
    #Calculo de la tasa metabolica basal

    #Calcular las proteinas, grasas y carbohidratos por día
    proteina=2.513244*pm
    #grasa=.65*peso
    grasa=planner.cal.data*.3/9
    ch=(planner.cal.data-(proteina*4)-(grasa*9))/4

    #Divisor de comidas
    comidas=[]
    if planner.desplan.data==True:
        comidas.append("Desayuno")
    if planner.mmplan.data==True:
        comidas.append("Media-mañana")
    if planner.almplan.data==True:
        comidas.append("Almuerzo")
    if planner.merplan.data==True:
        comidas.append("Merienda")
    if planner.mtplan.data==True:
        comidas.append("Media-tarde")
    if planner.cenplan.data==True:
        comidas.append("Cena")

    for i in range (0, len(comidas)):
        comidas[i]=[comidas[i]]
        for o in range (3):
            comidas[i].append(1)

    #Tamaño de las porciones - Función
    def tamaño(tamaño, comidas):
        if tamaño==0:
            coetam=0.5
        elif tamaño==1:
            coetam=0.75
        elif tamaño==2:
            coetam=1
        elif tamaño==3:
            coetam=1.33
        elif tamaño==4:
            coetam=2
        for o in range (1, 4):
            comidas[i][o]=comidas[i][o]*coetam

    for i in range (len(comidas)):
        if comidas[i][0]=="Desayuno":
            tamaño(int(planner.tamdes.data), comidas)
        if comidas[i][0]=="Media-mañana":
            tamaño(int(planner.tammm.data), comidas)
        if comidas[i][0]=="Almuerzo":
            tamaño(int(planner.tamalm.data), comidas)
        if comidas[i][0]=="Merienda":
            tamaño(int(planner.tammer.data), comidas)
        if comidas[i][0]=="Media-tarde":
            tamaño(int(planner.tammt.data), comidas)
        if comidas[i][0]=="Cena":
            tamaño(int(planner.tamcen.data), comidas)

    if planner.entreno.data!="6":
        def indice(theList, item):
            return [(ind, theList[ind].index(item)) for ind in range(len(theList)) if item in theList[ind]]
        comch=indice(comidas, planner.entreno.data)
        comch=comch[0][0]
        for i in range (len(comidas)):
            if i==comch or i==comch+1:
                comidas[i][3]=comidas[i][3]*2
            else:
                comidas[i][2]=comidas[i][2]*2

    inprot=0
    ingras=0
    incarb=0

    for i in range (len(comidas)):
        inprot+=comidas[i][1]
        incarb+=comidas[i][3]
        ingras+=comidas[i][2]
		
    for i in range (len(comidas)):
        comidas[i][1]=comidas[i][1]/inprot
        comidas[i][2]=comidas[i][2]/ingras
        comidas[i][3]=comidas[i][3]/incarb

    libertad=int(planner.libertad.data)

    #Todo el codigo de arriba lo copie del primer programa Mondo que habia creado, pero no me acuerdo como funciona. Solo parece funcionar.

    #Lo que tengo que hacer aca es desglosar comidas para poder guardar en la base de datos

    dp=0; dg=0; dc=0; mmp=0; mmg=0; mmc=0; ap=0; ag=0; ac=0; mp=0; mg=0; mc=0; mtp=0; mtg=0; mtc=0; cp=0; cg=0; cc=0

    for i in range (len(comidas)):
        if comidas[i][0]=='Desayuno':
            dp=comidas[i][1]
            dg=comidas[i][2]
            dc=comidas[i][3]
        elif comidas [i][0]=='Media-mañana':
            mmp=comidas[i][1]
            mmg=comidas[i][2]
            mmc=comidas[i][3]
        elif comidas [i][0]=='Almuerzo':
            ap=comidas[i][1]
            ag=comidas[i][2]
            ac=comidas[i][3]
        elif comidas [i][0]=='Merienda':
            mp=comidas[i][1]
            mg=comidas[i][2]
            mc=comidas[i][3]
        elif comidas [i][0]=='Media-tarde':
            mtp=comidas[i][1]
            mtg=comidas[i][2]
            mtc=comidas[i][3]
        elif comidas [i][0]=='Cena':
            cp=comidas[i][1]
            cg=comidas[i][2]
            cc=comidas[i][3]

    #REDONDEOS
    proteina=round(proteina,2)
    grasa=round(grasa,2)
    ch=round(ch,2)
    
    #Guardar en base de datos las ultimas divisiones de macros, calorias, etc.
    try:
        cursor.execute("CREATE TABLE DIETA (NOMBRE_APELLIDO  VARCHAR(50) UNIQUE, CALORIAS DECIMAL, PROTEINA DECIMAL, GRASA DECIMAL, CH DECIMAL, DP DECIMAL, DG DECIMAL, DC DECIMAL, MMP DECIMAL, MMG DECIMAL, MMC DECIMAL, AP DECIMAL, AG DECIMAL, AC DECIMAL, MP DECIMAL, MG DECIMAL, MC DECIMAL, MTP DECIMAL, MTG DECIMAL, MTC DECIMAL, CP DECIMAL, CG DECIMAL, CC DECIMAL, LIBERTAD INTEGER)")
    except sqlite3.OperationalError:
        pass
    
    #Primero intenta registrar la dieta, pero si esta ya fue realizada actualiza nada mas los valores.
    try:    
        cursor.execute("INSERT INTO DIETA (NOMBRE_APELLIDO, CALORIAS, PROTEINA, GRASA, CH, DP, DG, DC, MMP, MMG, MMC, AP, AG, AC, MP, MG, MC, MTP, MTG, MTC, CP, CG, CC, LIBERTAD) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (planner.nameuser.data, planner.cal.data, proteina, grasa, ch, dp, dg, dc, mmp, mmg, mmc, ap, ag, ac, mp, mg, mc, mtp, mtg, mtc, cp, cg, cc, libertad))
    except:
        cursor.execute("UPDATE DIETA SET CALORIAS=?, PROTEINA=?, GRASA=?, CH=?, DP=?, DG=?, DC=?, MMP=?, MMG=?, MMC=?, AP=?, AG=?, AC=?, MP=?, MG=?, MC=?, MTP=?, MTG=?, MTC=?, CP=?, CG=?, CC=?, LIBERTAD=? WHERE NOMBRE_APELLIDO=?", (planner.cal.data, proteina, grasa, ch, dp, dg, dc, mmp, mmg, mmc, ap, ag, ac, mp, mg, mc, mtp, mtg, mtc, cp, cg, cc, libertad, planner.nameuser.data))
        
    basededatos.commit()
    
#En este espacio tiene que estar el creador de la lista de receta similar al creador de la lista de nombres para los formularios
#Copie las recetas creadas anteriormente en MONDO, hace falta armar el creador de recetas

### FUNCIÓN QUE AGREGA ALIMENTOS ###

def creadordealimento(alimento):
    # Base de datos
    basededatos = sqlite3.connect("src/Basededatos")
    cursor = basededatos.cursor()
    try:
        cursor.execute("INSERT INTO ALIMENTOS (Largadescripcion, P, G, CH, F, Gramo1, Medidacasera1, Gramo2, Medidacasera2) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)", alimento)
        basededatos.commit()
        namefood = alimento[0]
        success_message = 'El alimento {} ha sido creado.'.format(namefood)
        flash(success_message)
    except sqlite3.IntegrityError:
        nameuser = alimento[0]
        warning_message = 'El alimento {} ya ha sido creado con anterioridad.'.format(
            nameuser)
        flash(warning_message)

## FUNCIÓN QUE EDITA LOS PERFILES ESTATICOS ###

def editfood(alimento):
    #Base de datos
    basedatos = sqlite3.connect("src/Basededatos")
    cursor = basedatos.cursor()
    try:
        cursor.execute("UPDATE ALIMENTOS SET Largadescripcion=?, P=?, G=?, CH=?, F=?, Gramo1=?, Medidacasera1=?, Gramo2=?, Medidacasera2=? WHERE ID = ?", (alimento[1], alimento[2], alimento[3], alimento[4], alimento[5], alimento[6], alimento[7], alimento[8], alimento[9], alimento[0]))
        basedatos.commit()
        namefood = alimento[1]
        success_message = 'El alimento {} ha sido actualizado.'.format(namefood)
        flash(success_message)
    except sqlite3.IntegrityError:
        nameuser = alimento[0]
        warning_message = 'El alimento {} ya ha sido actualizado.'.format(
            namefood)
        flash(warning_message)

### FUNCIÓN QUE CREA UNA LISTA CON TODAS LAS RECETAS ###

def listadereceta():
    basededatos = sqlite3.connect("src/Basededatos")
    cursor = basededatos.cursor()
    cursor.execute("SELECT NOMBRERECETA, NOMBRERECETA FROM RECETAS ORDER BY NOMBRERECETA ASC")
    lista = []
    for i in cursor.fetchall():
        i = [i[0], i[0]]
        lista.append(i)
    return lista

### FUNCIÓN QUE CREA UNA LISTA CON TODOS LOS ALIMENTOS ###

def listadealimentos():
    basededatos=sqlite3.connect("src/Basededatos")
    cursor=basededatos.cursor()
    cursor.execute("SELECT Largadescripcion, Largadescripcion FROM ALIMENTOS ORDER BY Largadescripcion ASC")
    lista=[('','')]
    for i in cursor.fetchall():
        i=[i[0],i[0]]
        lista.append(i)
    return lista

### CREA UNA LISTA DE LA PRESENTACIÓN DE LAS PORCIONES ###

def listadeporciones(alimento):
    basededatos=sqlite3.connect("src/Basededatos")
    cursor=basededatos.cursor()
    cursor.execute("SELECT Medidacasera1, Medidacasera2 FROM ALIMENTOS WHERE Largadescripcion=?", [alimento])
    listaporciones=[]
    porciones=cursor.fetchall()
    porcionObj={}
    porcionObj['id']=-1
    porcionObj['porcion']=''
    listaporciones.append(porcionObj)
    porcionObj={}
    porcionObj['id']=0
    porcionObj['porcion']=porciones[0][0]
    listaporciones.append(porcionObj)
    porcionObj={}
    porcionObj['id']=1
    porcionObj['porcion']=porciones[0][1]
    listaporciones.append(porcionObj)
    return listaporciones

### FUNCIÓN RECETARIO ###

def recetario(receta):
    basededatos=sqlite3.connect('src/Basededatos')
    cursor=basededatos.cursor()
    cursor.execute("INSERT INTO RECETAS (NOMBRERECETA, ALIIND1, PORIND1, ALIIND2, PORIND2, ALIIND3, PORIND3, ALIDEP1, PORDEP1, RELFIJ1, RELALI1, VALOR1, ALIDEP2, PORDEP2, RELFIJ2, RELALI2, VALOR2, ALIDEP3, PORDEP3, RELFIJ3, RELALI3, VALOR3, ALIDEP4, PORDEP4, RELFIJ4, RELALI4, VALOR4, ALIDEP5, PORDEP5, RELFIJ5, RELALI5, VALOR5, ALIDEP6, PORDEP6, RELFIJ6, RELALI6, VALOR6, ALIDEP7, PORDEP7, RELFIJ7, RELALI7, VALOR7, ALIDEP8, PORDEP8, RELFIJ8, RELALI8, VALOR8, ALIDEP9, PORDEP9, RELFIJ9, RELALI9, VALOR9, ALIDEP10, PORDEP10, RELFIJ10, RELALI10, VALOR10) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (receta.recipename.data, receta.foodi1.data, receta.foodisize1.data, receta.foodi2.data, receta.foodisize2.data, receta.foodi3.data, receta.foodisize3.data, receta.food1.data, receta.foodsize1.data, receta.relfood1.data, receta.reffood1.data, receta.valfood1.data, receta.food2.data, receta.foodsize2.data, receta.relfood2.data, receta.reffood2.data, receta.valfood2.data, receta.food3.data, receta.foodsize3.data, receta.relfood3.data, receta.reffood3.data, receta.valfood3.data, receta.food4.data, receta.foodsize4.data, receta.relfood4.data, receta.reffood4.data, receta.valfood4.data, receta.food5.data, receta.foodsize5.data, receta.relfood5.data, receta.reffood5.data, receta.valfood5.data, receta.food6.data, receta.foodsize6.data, receta.relfood6.data, receta.reffood6.data, receta.valfood6.data, receta.food7.data, receta.foodsize7.data, receta.relfood7.data, receta.reffood7.data, receta.valfood7.data, receta.food8.data, receta.foodsize8.data, receta.relfood8.data, receta.reffood8.data, receta.valfood8.data, receta.food9.data, receta.foodsize9.data, receta.relfood9.data, receta.reffood9.data, receta.valfood9.data, receta.food10.data, receta.foodsize10.data, receta.relfood10.data, receta.reffood10.data, receta.valfood10.data ))
    basededatos.commit()

### CALCULA LAS CANTIDADES QUE HAY QUE COMER DE CADA ALIMENTO PARA UNA RECETA ESPECIFICA ###

def recipe(recipeform, nameuser):
    basededatos=sqlite3.connect('src/Basededatos')
    cursor=basededatos.cursor()
    cursor.execute("SELECT PROTEINA, GRASA, CH, LIBERTAD FROM DIETA WHERE NOMBRE_APELLIDO=?", [nameuser])
    dieta=cursor.fetchall()
    proteina=dieta[0][0]
    grasa=dieta[0][1]
    ch=dieta[0][2]
    libertad=dieta[0][3]

    if recipeform.menues.data=='Desayuno':
        cursor.execute("SELECT DP, DG, DC FROM DIETA WHERE NOMBRE_APELLIDO=?", [nameuser])
        menu=cursor.fetchall()
        rp=menu[0][0]
        rg=menu[0][1]
        rc=menu[0][2]
    elif recipeform.menues.data=='Media-mañana':
        cursor.execute("SELECT MMP, MMG, MMC FROM DIETA WHERE NOMBRE_APELLIDO=?", [nameuser])
        menu=cursor.fetchall()
        rp=menu[0][0]
        rg=menu[0][1]
        rc=menu[0][2]
    elif recipeform.menues.data=='Media-mañana':
        cursor.execute("SELECT MMP, MMG, MMC FROM DIETA WHERE NOMBRE_APELLIDO=?", [nameuser])
        menu=cursor.fetchall()
        rp=menu[0][0]
        rg=menu[0][1]
        rc=menu[0][2]
    elif recipeform.menues.data=='Almuerzo':
        cursor.execute("SELECT AP, AG, AC FROM DIETA WHERE NOMBRE_APELLIDO=?", [nameuser])
        menu=cursor.fetchall()
        rp=menu[0][0]
        rg=menu[0][1]
        rc=menu[0][2]
    elif recipeform.menues.data=='Merienda':
        cursor.execute("SELECT MP, MG, MC FROM DIETA WHERE NOMBRE_APELLIDO=?", [nameuser])
        menu=cursor.fetchall()
        rp=menu[0][0]
        rg=menu[0][1]
        rc=menu[0][2]
    elif recipeform.menues.data=='Cena':
        cursor.execute("SELECT CP, CG, CC FROM DIETA WHERE NOMBRE_APELLIDO=?", [nameuser])
        menu=cursor.fetchall()
        rp=menu[0][0]
        rg=menu[0][1]
        rc=menu[0][2]
    
    #FUNCIÓN QUE AJUSTA LAS CANTIDADES - TRATAR DE INDEPENDIZAR DE LA FUNCIÓN "RECIPE"
    
    def solver(p0, g0, ch0, libertad, nombrereceta):
        
        basededatos = sqlite3.connect("src/Basededatos")
        cursor = basededatos.cursor()
        cursor.execute("SELECT * FROM RECETAS WHERE NOMBRERECETA=?", [nombrereceta])
        receta = cursor.fetchall()[0]
        alimentos = []
        alimentosnovar = []
        proteina = {}
        grasa = {}
        carbos = {}
        medida_casera = {}
        porcionesnovar = {}
        mcdescripcion = {}
        met = 0

        for i in range(5, 10, 2):
            if receta[i] != "" and receta[i] != " ":
                cursor.execute("SELECT P FROM ALIMENTOS WHERE Largadescripcion=?", [receta[i]])
                pi = cursor.fetchone()[0]
                cursor.execute("SELECT G FROM ALIMENTOS WHERE Largadescripcion=?", [receta[i]])
                gi = cursor.fetchone()[0]
                cursor.execute("SELECT CH FROM ALIMENTOS WHERE Largadescripcion=?", [receta[i]])
                ci = cursor.fetchone()[0]
                if receta[i+1] == 0:
                    cursor.execute("SELECT Gramo1 FROM ALIMENTOS WHERE Largadescripcion=?", [receta[i]])
                    mi = cursor.fetchone()[0]
                    cursor.execute("SELECT Medidacasera1 FROM ALIMENTOS WHERE Largadescripcion=?", [receta[i]])
                    mc = cursor.fetchone()[0]
                elif receta[i+1] == 1:
                    cursor.execute("SELECT Gramo2 FROM ALIMENTOS WHERE Largadescripcion=?", [receta[i]])
                    mi = cursor.fetchone()[0]
                    cursor.execute("SELECT Medidacasera2 FROM ALIMENTOS WHERE Largadescripcion=?", [receta[i]])
                    mc = cursor.fetchone()[0]

                alimentos.append(receta[i])
                proteina[receta[i]] = pi
                grasa[receta[i]] = gi
                carbos[receta[i]] = ci
                medida_casera[receta[i]] = mi
                mcdescripcion[receta[i]] = mc

        porciones = LpVariable.dicts("Alim", alimentos, 0)

        for i in range(11, 57, 5):
            if receta[i] != "" and receta[i] != " ":
                cursor.execute("SELECT P FROM ALIMENTOS WHERE Largadescripcion=?", [receta[i]])
                pi = cursor.fetchone()[0]
                cursor.execute("SELECT G FROM ALIMENTOS WHERE Largadescripcion=?", [receta[i]])
                gi = cursor.fetchone()[0]
                cursor.execute("SELECT CH FROM ALIMENTOS WHERE Largadescripcion=?", [receta[i]])
                ci = cursor.fetchone()[0]
                if receta[i+1] == 0:
                    cursor.execute("SELECT Gramo1 FROM ALIMENTOS WHERE Largadescripcion=?", [receta[i]])
                    mi = cursor.fetchone()[0]
                    cursor.execute("SELECT Medidacasera1 FROM ALIMENTOS WHERE Largadescripcion=?", [receta[i]])
                    mc = cursor.fetchone()[0]
                elif receta[i+1] == 1:
                    cursor.execute("SELECT Gramo2 FROM ALIMENTOS WHERE Largadescripcion=?", [receta[i]])
                    mi = cursor.fetchone()[0]
                    cursor.execute("SELECT Medidacasera2 FROM ALIMENTOS WHERE Largadescripcion=?", [receta[i]])
                    mc = cursor.fetchone()[0]
                if receta[i+2] == 0:
                    porcionesnovar[receta[i]] = porciones[alimentos[receta[i+3]-1]]*receta[i+4]
                elif receta[i+2] == 1:
                    porcionesnovar[receta[i]] = receta[i+4]

                alimentosnovar.append(receta[i])
                proteina[receta[i]] = pi
                grasa[receta[i]] = gi
                carbos[receta[i]] = ci
                medida_casera[receta[i]] = mi
                mcdescripcion[receta[i]] = mc

        metodo1 = LpProblem("metodo1", LpMaximize)
        metodo1 += lpSum([medida_casera[i]*porciones[i]*(proteina[i]*4+carbos[i]*4+grasa[i]*9)/100 for i in alimentos])+lpSum([medida_casera[i]*porcionesnovar[i]*(proteina[i]*4+carbos[i]*4+grasa[i]*9)/100 for i in alimentosnovar]), "Total de calorias"
        
        metodo1 += lpSum([medida_casera[i]*porciones[i]*(proteina[i]*4+carbos[i]*4+grasa[i]*9)/100 for i in alimentos])+lpSum([medida_casera[i]*porcionesnovar[i]*(proteina[i]*4+carbos[i]*4+grasa[i]*9)/100 for i in alimentosnovar]) <= p0*4+g0*9+ch0*4
        metodo1 += lpSum([medida_casera[i]*porciones[i]*proteina[i]/100 for i in alimentos])+lpSum([medida_casera[i] * porcionesnovar[i]*proteina[i]/100 for i in alimentosnovar]) <= p0*(1+(libertad/100)), "Limite superior de proteinas"
        metodo1 += lpSum([medida_casera[i]*porciones[i]*proteina[i]/100 for i in alimentos])+lpSum([medida_casera[i] * porcionesnovar[i]*proteina[i]/100 for i in alimentosnovar]) >= p0*(1-(libertad/100)), "Limite inferior de proteinas"
        metodo1 += lpSum([medida_casera[i]*porciones[i]*grasa[i]/100 for i in alimentos])+lpSum([medida_casera[i] * porcionesnovar[i]*grasa[i]/100 for i in alimentosnovar]) <= g0*(1+(libertad/100)), "Limite superior de grasas"
        metodo1 += lpSum([medida_casera[i]*porciones[i]*grasa[i]/100 for i in alimentos])+lpSum([medida_casera[i] * porcionesnovar[i]*grasa[i]/100 for i in alimentosnovar]) >= g0*(1-(libertad/100)), "Limite inferior de grasas"
        metodo1 += lpSum([medida_casera[i]*porciones[i]*carbos[i]/100 for i in alimentos])+lpSum([medida_casera[i] * porcionesnovar[i]*carbos[i]/100 for i in alimentosnovar]) <= ch0*(1+(libertad/100)), "Limite superior de carbos"
        metodo1 += lpSum([medida_casera[i]*porciones[i]*carbos[i]/100 for i in alimentos])+lpSum([medida_casera[i] * porcionesnovar[i]*carbos[i]/100 for i in alimentosnovar]) >= ch0*(1-(libertad/100)), "Limite inferior de carbos"
        
        metodo1.writeLP("src/metodo1Model.lp")
        
        metodo1.solve()

        if LpStatus[metodo1.status] != "Optimal":
            metodo2 = LpProblem("metodo2", LpMaximize)

            metodo2 += lpSum([medida_casera[i]*porciones[i]*(proteina[i]*4+carbos[i]*4+grasa[i]*9)/100 for i in alimentos])+lpSum([medida_casera[i]*porcionesnovar[i]*(proteina[i]*4+carbos[i]*4+grasa[i]*9)/100 for i in alimentosnovar]), "Total de calorias"
            
            metodo2 += lpSum([medida_casera[i]*porciones[i]*(proteina[i]*4+carbos[i]*4+grasa[i]*9)/100 for i in alimentos])+lpSum([medida_casera[i]*porcionesnovar[i]*(proteina[i]*4+carbos[i]*4+grasa[i]*9)/100 for i in alimentosnovar]) <= p0*4+g0*9+ch0*4
            metodo2 += lpSum([medida_casera[i]*porciones[i]*(proteina[i]*4+carbos[i]*4+grasa[i]*9)/100 for i in alimentos])+lpSum([medida_casera[i]*porcionesnovar[i]*(proteina[i]*4+carbos[i]*4+grasa[i]*9)/100 for i in alimentosnovar]) <= (p0*4+g0*9+ch0*4)*(1-libertad/100)
            #metodo2 += lpSum([medida_casera[i]*porciones[i]*proteina[i]/100 for i in alimentos])+lpSum([medida_casera[i]*porcionesnovar[i]*proteina[i]/100 for i in alimentosnovar]) <= p0*(1+libertad/100), "Limite superior de proteinas"
            metodo2 += lpSum([medida_casera[i]*porciones[i]*proteina[i]/100 for i in alimentos])+lpSum([medida_casera[i] * porcionesnovar[i]*proteina[i]/100 for i in alimentosnovar]) >= p0*(1-libertad/100), "Limite inferior de proteinas"

            metodo2.writeLP("src/metodo2Model.lp")

            metodo2.solve()

            if LpStatus[metodo2.status] != "Optimal":
                metodo3 = LpProblem("metodo3", LpMaximize)

                metodo3 += lpSum([medida_casera[i]*porciones[i]*(proteina[i]*4+carbos[i]*4+grasa[i]*9)/100 for i in alimentos])+lpSum([medida_casera[i]*porcionesnovar[i]*(proteina[i]*4+carbos[i]*4+grasa[i]*9)/100 for i in alimentosnovar]), "Total de calorias"

                metodo3 += lpSum([medida_casera[i]*porciones[i]*(proteina[i]*4+carbos[i]*4+grasa[i]*9)/100 for i in alimentos])+lpSum([medida_casera[i]*porcionesnovar[i]*(proteina[i]*4+carbos[i]*4+grasa[i]*9)/100 for i in alimentosnovar]) <= p0*4+g0*9+ch0*4
                metodo3 += lpSum([medida_casera[i]*porciones[i]*(proteina[i]*4+carbos[i]*4+grasa[i]*9)/100 for i in alimentos])+lpSum([medida_casera[i]*porcionesnovar[i]*(proteina[i]*4+carbos[i]*4+grasa[i]*9)/100 for i in alimentosnovar]) <= (p0*4+g0*9+ch0*4)*(1-libertad/100)

                metodo3.writeLP("src/metodo3Model.lp")

                metodo3.solve()
                if LpStatus[metodo3.status] == "Optimal":
                    met = 3
            elif LpStatus[metodo2.status] == "Optimal":
                met = 2
        elif LpStatus[metodo1.status] == "Optimal":
            met = 1

    
        '''cwd=os.getcwd()
        archivo_texto=open(cwd+"\\Pacientes\\"+nameuser+".txt", "a")
        archivo_texto.write("\n" + str(nombrereceta) + "\n")'''

        Texto=""

        if met == 1:
            flash("\nMetodo aplicado: Completo","block-title mb-0") 
            flash("Calorias totales: " + str(round(value(metodo1.objective), 2)), "mb-0 font-size-sm")
            flash("La calidad es: " + str(round(float(str(((lpSum([medida_casera[i]*value(porciones[i])*proteina[i]/100 for i in alimentos]+[medida_casera[i]*value(porcionesnovar[i])*proteina[i]/100 for i in alimentosnovar]))/(value(metodo1.objective)))/((p0)/(p0*4+ch0*4+g0*9))*10)+"\n"))), "mb-0 font-size-sm font-w600")
            flash("Alimentos", "mb-0 font-w600")
            for i in alimentos:
                flash("\n" + str(i), "mb-0 font-w500")
                flash("Nº de porciones: " + str(round(porciones[i].varValue, 2)) + "(" + str(mcdescripcion[i]) + ") - " + " Total: " + str(round(porciones[i].varValue*medida_casera[i], 2)) + " gr.", "mb-0 font-size-sm")
            for i in alimentosnovar:
                flash("\n" + str(i), "mb-0 font-w500")
                flash("Nº de porciones: " + str(round(value(porcionesnovar[i]), 2)) + "(" + str(mcdescripcion[i]) + ") - " + " Total: " + str(round(value(porcionesnovar[i]*medida_casera[i]), 2)) + " gr.", "mb-0 font-size-sm")

        elif met == 2:
            flash("\nMetodo aplicado: Proteinas", "block-title mb-0")
            flash("Calorias totales: " + str(round(value(metodo2.objective), 2)), "mb-0 font-size-sm")
            flash("La calidad es: " + str(round(float(str(((lpSum([medida_casera[i]*value(porciones[i])*proteina[i]/100 for i in alimentos]+[medida_casera[i]*value(porcionesnovar[i])*proteina[i]/100 for i in alimentosnovar]))/(value(metodo2.objective)))/((p0)/(p0*4+ch0*4+g0*9))*10)+"\n"))), "mb-0 font-size-sm font-w600")
            flash("Alimentos", "mb-0 font-w600")
            for i in alimentos:
                flash("\n" + str(i), "mb-0 font-w500")
                flash("Nº de porciones: " + str(round(porciones[i].varValue, 2)) + "(" + str(mcdescripcion[i]) + ") - " + " Total: " + str(round(porciones[i].varValue*medida_casera[i], 2)) + " gr.", "mb-0 font-size-sm")
            for i in alimentosnovar:
                flash("\n" + str(i), "mb-0 font-w500")
                flash("Nº de porciones: " + str(round(value(porcionesnovar[i]), 2)) + "(" + str(mcdescripcion[i]) + ") - " + " Total: " + str(round(value(porcionesnovar[i]*medida_casera[i]), 2)) + " gr.", "mb-0 font-size-sm")

        elif met == 3:
            flash("\nMetodo aplicado: Calorias", "block-title mb-0")
            flash("Calorias totales: " + str(round(value(metodo3.objective), 2)), "mb-0 font-size-sm")
            flash("La calidad es: " + str(round(float(str(((lpSum([medida_casera[i]*value(porciones[i])*proteina[i]/100 for i in alimentos]+[medida_casera[i]*value(porcionesnovar[i])*proteina[i]/100 for i in alimentosnovar]))/(value(metodo3.objective)))/((p0)/(p0*4+ch0*4+g0*9))*10)+"\n"))), "mb-0 font-size-sm font-w600")
            flash("Alimentos", "mb-0 font-w600")
            for i in alimentos:
                flash("\n" + str(i), "mb-0 font-w500")
                flash("Nº de porciones: " + str(round(porciones[i].varValue, 2)) + "(" + str(mcdescripcion[i]) + ")" + " Total: " + str(round(porciones[i].varValue*medida_casera[i], 2)) + " gr.", "mb-0 font-size-sm")
            for i in alimentosnovar:
                flash("\n" + str(i), "mb-0 font-w500")
                flash("Nº de porciones: " + str(round(value(porcionesnovar[i]), 2)) + "(" + str(mcdescripcion[i]) + ")" + " Total: " + str(round(value(porcionesnovar[i]*medida_casera[i]), 2)) + " gr.", "mb-0 font-size-sm")
            
    try:
        solver(rp*proteina, rg*grasa, rc*ch, libertad, recipeform.receta.data)
    except:
        error_message= "NO FUNCIONA - AVISE POR FAVOR"
        flash(error_message)
        redirect ( url_for('recipe') )
