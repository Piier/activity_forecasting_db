import re
import os
import sys
import psycopg2
from psycopg2 import Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from formattazione import formattaFile
from formattazione import createFormattedFile
from popolaDB import createSensor
from popolaDB import createActivity

name_db=""
username_db="postgres"
password_db=""
host_db="127.0.0.1"
port_db="5432"


#Funzione per la creazione del database
def createDatabase():

    print("Creating database: ",name_db)
    connection = psycopg2.connect(user=username_db,
                            password=password_db,
                            host=host_db,
                            port=port_db,
                            )
    
    connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = connection.cursor()
    sqlCreateDatabase = "create database "+name_db+";"

    cursor.execute(sqlCreateDatabase)

    cursor.close()
    connection.close()
    print("Database created",end="\n\n")

#Funzione per la creazione dello schema e delle tabelle
def createSchema(cursor, connection):
    
    print("Creating schema")

    create="create schema activity"
    cursor.execute(create)
   
    create="create table activity.house(id varchar(10) primary key,type varchar(10) CHECK( type IN (\'Single\',\'Two\')))"
    cursor.execute(create)
    
    create="create table activity.sensor(id SERIAL primary key,name varchar(10) NOT NULL,house varchar(10) NOT NULL references activity.house on delete cascade on update cascade,type varchar(35))"
    cursor.execute(create)
    
    create="create table activity.event(id SERIAL primary key,date timestamp NOT NULL,sensor int NOT NULL references activity.sensor on delete cascade on update cascade,state int NOT NULL,value varchar(10) NOT NULL)"
    cursor.execute(create)
    
    create="create table activity.activity(id SERIAL primary key, name varchar(30) NOT NULL, startID int NOT NULL references activity.event on delete cascade on update cascade, endID int NOT NULL references activity.event on delete cascade on update cascade,startDate timestamp NOT NULL, endDate timestamp NOT NULL,house varchar(10) NOT NULL references activity.house on delete cascade on update cascade)"
    cursor.execute(create)
    
    connection.commit()
    print("Schema created",end="\n\n")



def main():
    
    if name_db=="" or username_db=="" or password_db=="" or host_db=="" or port_db=="":
        print("Error db parameters are missing")
        print("Name db:", name_db)
        print("Username user:", username_db)
        print("Password user:", password_db)
        print("Host db:", host_db)
        print("Port db:",port_db)
        exit()

    #Se ho passato la cartella
    if len(sys.argv)==2:
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
 

    #Creazione del database
    createDatabase()
    
    try:
        connection = psycopg2.connect(user=username_db,
                                    password=password_db,
                                    host=host_db,
                                    port=port_db,
                                    database=name_db)

        cursor = connection.cursor()
        #Creazione schema e tabelle 
        createSchema(cursor,connection)
        
        if len(sys.argv)==2:
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
                    cursor.execute("insert into attivita.casa values(\'"+house+"\',\'"+typeHouse+"\');")#Popolazione della tabella casa 
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
    if len(sys.argv)!=1 and  len(sys.argv)!=2:
        print("Correct use: \n python script.py directory_path\n or\n python script.py")
        exit()
    main()





