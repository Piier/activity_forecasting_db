import re
import os

#Funzione per la creazione del nuovo file
def createFormattedFile(filePath, fileAnn, textLine, name):
    fileName="formatted"+name+".txt"
    print("Start writing formatted file", fileName, "in ",filePath+"\\formatted")
    os.chdir(filePath+"\\formatted")
    f1=open(fileName,"w+")
    textLen=len(textLine)
    cont=0
    for line in textLine:
        f1.write(line)

        if cont!=textLen-1:  
             f1.write("\n")
            
        cont+=1
    f1.close()
    os.chdir(filePath)


def tabAndSpace(testo):
    #Tab e varie cose
    testo=re.sub(r" ","\t",testo, flags=re.MULTILINE)
    testo=re.sub(r"\t$","",testo,flags=re.MULTILINE)
    testo=re.sub(r"\t\t","\t",testo,flags=re.MULTILINE)
    testo=re.sub(r"\t\t","\t",testo,flags=re.MULTILINE)
    testo=re.sub(r"\t$","",testo,flags=re.MULTILINE)
    testo=re.sub(r"^\t","",testo,flags=re.MULTILINE)
    return testo

def controllData(righeTesto):
    cont=0
    #Eliminazione etichette non begin or end e cose in piu
    for riga in righeTesto:
        x = riga.split("\t")

        if not re.findall(r"^2",x[0]) and x[0]!="":
            print("Error date format:", riga)
            x[0]=x[0][1:]
            righeTesto[cont]=x[0]+"\t"+x[1]+"\t"+x[2]+"\t"+x[3]

        #Sensore system
        for y in x:
            if y=="system":
                print("System value:", x)
                righeTesto[cont]=righeTesto[cont-1]
                x=righeTesto[cont].split("\t")
        
        #Mancanza di dati
        if len(x)<4  :
            print("Missing fields:",x)
            righeTesto[cont]=righeTesto[cont-1]
        

        #Sensore sbagliato
        if len(x)>=3 and len(x[2])>10:
            print("Wrong sensor:",x)
            righeTesto[cont]=righeTesto[cont-1]
        
        
        #Troppe etichette
        if len(x)>5:
            print("Removing fields:",x)
            for i in range(len(x)-5):
                x.pop()
            righeTesto[cont]=x[0]+"\t"+x[1]+"\t"+x[2]+"\t"+x[3]+"\t"+x[4]
        #Etichette !begin and !home
        if len(x)==5:
        
            if not(re.findall(r"begin",x[-1])) and not(re.findall(r"end",x[-1])):
    
                x.pop()
                righeTesto[cont]=x[0]+"\t"+x[1]+"\t"+x[2]+"\t"+x[3]
        cont+=1

    return righeTesto


def formattaFile(fileAnn):
    f=open(fileAnn,"r")
    testo=f.read()
    f.close()
    testo=tabAndSpace(testo)
    righeTesto=testo.split("\n")
    righeTesto=controllData(righeTesto)
    return righeTesto


