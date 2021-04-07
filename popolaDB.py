import re
import os
import sys
import psycopg2
from psycopg2 import Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from formattazione import formattaFile
from formattazione import createFormattedFile

name_db=""
username_db="postgres"
password_db=""
host_db="127.0.0.1"
port_db="5432"


#Funzione che restituisce la tipologia di sensore dato il nome
def typeSensor(sensor):
    if re.findall(r"^BA",sensor):
        return "sensor battery levels"
    if re.findall(r"^D",sensor):
        return "magnetic door sensors"
    if re.findall(r"^LS",sensor):
        return "light sensors"
    if re.findall(r"^L",sensor):
        return "light switches"
    if re.findall(r"^MA",sensor):
        return "wide-area infrared motion sensors"
    if re.findall(r"^M",sensor):
        return "infrared motion sensors"
    if re.findall(r"^T",sensor):
        return "temperature sensors"
     

    return ""

#Funzione per l'inserimento dei sensori sul db e la restituzione di un dizionario che li contiene
def writeSensor(sensorOrd,cursor,house):
    
    #Ottenimento dell'ultimo id inserito per iniziare a lavorare dal successivo
    cursor.execute("select max(id) from activity.sensor;")
    #Controllo che il risultato non sia None
    risp=cursor.fetchone()
    if risp[0] is not None:
        cont=risp[0]+1
    else:
        cont=0

    #Creazione di un dizionario NomeSensore-ID
    sensorDict=dict()
  
    for sensor in sensorOrd:
        
        #Insert nel db
        toSensor="insert into activity.sensor values ("+str(cont)+",\'"+ sensor+"\',\'"+house+"\',\'"+typeSensor(sensor)+"\');\n"
        
        cursor.execute(toSensor)
        
        #Aggiunta del sensore nel dizionario
        sensorDict[sensor]=cont

        cont+=1
    print("Insert completed",end="\n\n")
    return sensorDict


#Funzione per la scrittura dei sensori sul db
def createSensor(cursor, nameFile,house):

    print("Insert of the sensors",end="\n\n")
    fr = open(nameFile,"r")
    sensorSet=set()

    #Individuazione dei sensori ed inserimento in un set
   
    for line in fr:

        res=line.split("\t")
        sensorSet.add(res[2])
      
    fr.close()
    
    #Inserimento ordinato dei sensori nel db
    return writeSensor(sorted(sensorSet),cursor,house)
              


#Funzione per l'inserimento degli eventi nel db
def writeEvent(date,sensor,value,cont,cursor):

    if len(value)>10:
        value="0"
    #Modifica dei valori stringhe discreti in valori numerici 
    if value=="ON" or value=="OPEN" or value=="OK":
        val="1"
    else:
        if value=="OFF" or value=="CLOSE":
            val="0"
        else:
            val="-1"
                
    #Insert nel db
    toWrite="insert into activity.event values ("+str(cont)+",\'"+date+"\',"+sensor+","+val+",\'"+value+"\');\n"
    cursor.execute(toWrite)


#Selezione degli eventi etichettati come attività ed inserimento nel db
def createActivity(sensorDict,cursor, nameFile, house):
    print("Insert of the events and the activities",end="\n\n")
    fr = open(nameFile,"r")

    #Ottenimento degli ultimi id inseriti per iniziare a lavorare dal successivo e controllo sul None
    cursor.execute("select max(id) from activity.event;")
    risp=cursor.fetchone()
    if risp[0] is not None:
        cont=risp[0]+1
    else:
        cont=0
    
    cursor.execute("select max(id) from activity.activity;")
    risp=cursor.fetchone()
    if risp[0] is not None:
        contActivity=risp[0]+1
    else:
        contActivity=0
    
    
    activityStack=list()
    activityQuery=list()
    for line in fr:

        if re.findall(r"begin",line):                            
            #Split per tab
            date, time, sensor, value, activity = line.split("\t")
            #Scrittura evento  
            writeEvent(date+" "+time,str(sensorDict[sensor]),value,cont,cursor)
            
            activityStack.append(activity.split("=")[0])
  
            forQuery=list()
            forQuery.append(activity.split("=")[0])
   
            forQuery.append(str(cont))

            forQuery.append(date+" "+time)

            activityQuery.append(forQuery)

        elif re.findall(r"end",line): 
            if len(activityStack)!=0:
                #Split per tab
                date, time, sensor, value, activity = line.split("\t")
                #Scrittura evento  
                writeEvent(date+" "+time,str(sensorDict[sensor]),value,cont,cursor)
                
                
                activityStack.pop()
                forQuery=activityQuery.pop()
                
                
                toWriteActivity="insert into activity.activity values ("+str(contActivity)+",\'"+forQuery[0]+"\',"+str(forQuery[1])+","+str(cont)+",\'"+forQuery[2]+"\',\'"+date+" "+time+"\',\'"+house+"\');"
                cursor.execute(toWriteActivity)
                contActivity+=1 
        else:
            #Split per tab
            date, time, sensor, value = line.split("\t") 
            #Scrittura evento
            value=re.sub(r"\n","",value)
            writeEvent(date+" "+time,str(sensorDict[sensor]),value,cont,cursor)
        cont+=1

    fr.close()
    print("Insert completed",end="\n\n")


def main():
    
    if name_db=="" or username_db=="" or password_db=="" or host_db=="" or port_db=="":
        print("Error db parameters are missing")
        print("Name db:", name_db)
        print("Username user:", username_db)
        print("Password user:", password_db)
        print("Host db:", host_db)
        print("Port db:",port_db)
        exit()

    #Cambio cartella con quella dove sono presenti i file annotati
    path=sys.argv[1]
    pathDir=path+"\\formatted"

    os.chdir(path)


    #Cartella per la memorizzazione dei file formattati
    if "formatted" in os.listdir():
        os.chdir(pathDir)
        for f in os.listdir():
            os.remove(f)
        os.chdir(path)
    else:
        os.mkdir(pathDir)
    
 
    #Formattazione dei datset
    for fileAnn in os.listdir():
        if fileAnn!="formatted": 
            if os.path.isdir(fileAnn) and re.findall(r"^hh1",fileAnn):
                os.chdir(path+"\\"+fileAnn)
                for fileDirectory in os.listdir():
                    if fileDirectory=="ann.txt" or fileDirectory=="hh105.txt":
                        print("Start formatting the file:",fileAnn ,"\\",fileDirectory,end="\n\n")
                        text=formattaFile(fileDirectory)
                        createFormattedFile(path,fileDirectory,text,fileAnn)
                        print("\nFinish formatting the file: ", fileDirectory,end="\n\n")
                os.chdir(path)

    os.chdir(pathDir)

 
    try:
        connection = psycopg2.connect(user=username_db,
                                    password=password_db,
                                    host=host_db,
                                    port=port_db,
                                    database=name_db)

        cursor = connection.cursor()
        
        #Popolazione del db tramite i file presenti nella cartella passata come parametro
        for fileAnn in os.listdir():
            print("Import ",fileAnn," to the database",end="\n\n")#Print che comunica che file stiamo prendendo in considerazione
            
            house="HH1"+fileAnn.split(".")[0][-2]+fileAnn.split(".")[0][-1]#Creazione nel nome della casa
            
            query="select * from activity.house where id=\'"+house+"\';"
            cursor.execute(query)

        
            if cursor.fetchone() is not None:
                print("House %s already in\n\n" %(house))
            else:
                print("Insert of the house:", house,end="\n\n")
                if house=="HH107" or house=="HH121":
                    typeHouse="Two"
                else:
                    typeHouse="Single"
                cursor.execute("insert into activity.house values(\'"+house+"\',\'"+typeHouse+"\');")#Popolazione della tabella casa 
                print("Insert completed",end="\n\n")
                sensorDict=createSensor(cursor, fileAnn,house)#Popolazione della tabella sensore
                createActivity(sensorDict,cursor,fileAnn,house)#Popolazione delle tabelle attivita e evento
            

                connection.commit()#Commit

    except (Exception, Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        if (connection):
            connection.commit()#Commit
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")


if __name__ == "__main__":
    if len(sys.argv)!=2:
        print("Correct use: python script.py directory_path")
        exit()
    main()


