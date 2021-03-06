##IMPORT
import requests
import json
import datetime
from datetime import date
from datetime import datetime
from datetime import timedelta
import mysql.connector

##DOC
__author__ = 'Elia Semprebon'
__description__ = 'Generatore della tabella centrale per marconitt'


##VARIABILI
global boolD
boolD = True


##FUNZIONI


def fn_getclassi(obj):
    '''
    Funzione che ritorna un vettore con le classi, prendendo l'oggetto in json
    '''
    classi = obj["classes"]

    for i in classi:
        if(i == "" or i == None):
            classi.remove(i)

    classi.remove(classi[len(classi) - 1])
    classi.remove(classi[len(classi) - 2])
    classi.remove(classi[len(classi) - 3])

    return classi


def fn_getstanze(obj):
    '''
    Funzione che ritorna un vettore con le stanze, prendendo l'oggetto in json
    '''
    stanze = obj["rooms"]

    for i in stanze:
        if(i == "" or i == None):
            stanze.remove(i)
        
    stanze.append("Aula Magna")
        
    return stanze


def fn_getgiorniscuola(nomefile):
    '''
    Funzione che genera i giorni di scuola, escludendo quindi le vacanze(prese da file), e li ritorna in un vettore
    '''
    start = date(2017, 04, 01)
    end = date(2017, 05, 31)
    actual = start
    giorni = []
    ifile = open(nomefile, "r")
    inizio_vac = []
    fine_vac = []
    line = ifile.readline()
    line = ifile.readline()
    line = line.replace("\n", "")
    
    while(line != "" and line != None):
        vett = line.split(";")
        dati = vett[0].split("-")
        inizio_vac.append(date(int(dati[0]), int(dati[1]), int(dati[2])))
        dati = vett[1].split("-")
        fine_vac.append(date(int(dati[0]), int(dati[1]), int(dati[2])))
        line = ifile.readline()
        line = line.replace("\n", "")


    while(actual <= end):
        agg = True
        
        for i in range(0, len(inizio_vac)):
            if(actual >= inizio_vac[i] and actual <= fine_vac[i]):
                agg = False
            if(actual.weekday() == 6):
                agg = False

        if(agg):
            giorni.append(actual)
        actual += timedelta(1)

    return giorni


def fn_generaconnessione():
    '''
    Funzione che genera e ritorna la connessione a mysql
    '''
    connessione = mysql.connector.connect(user='root', password='',host='127.0.0.1',database='marconitt')
    return connessione
    

def fn_generarighe():
    '''
    Funzione che elimina, poi rigenera ed invia le righe al database mysql
    '''
    req = requests.get("http://localhost:80/api.php")
    obj = json.loads(req.text)
    classi = fn_getclassi(obj)
    stanze = fn_getstanze(obj)
    nomefile = "vacanze.csv"
    giorni = fn_getgiorniscuola(nomefile)
    ore = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    cont = 0
    appo = 500
    connessione = fn_generaconnessione()
    cursore = connessione.cursor()
    query = "DELETE FROM timetable;"
    cursore.execute(query)
    connessione.commit()

    if(boolD):
        print(len(ore))
        print(len(giorni))
        print(len(stanze))
    
    for g in giorni:
        for o in ore:
            for s in stanze:
                str_giorno = g.strftime("%Y-%m-%d")
                query = "INSERT INTO timetable(giorno, ora, stanza, giorno_settimana) VALUES (%s, %s, %s, %s);"
                dati = (str_giorno, str(o), s, str(g.weekday() + 1))
                cursore.execute(query, dati)
                cont += 1

                if (cont == appo):
                    if(boolD):
                        print("Cont= " + str(cont) + "     appo= " + str(appo))
                        
                    appo += 500
                    cursore.close()
                    connessione.commit()
                    connessione.close()
                    connessione = fn_generaconnessione()
                    cursore = connessione.cursor()
                    

    #query = "DELETE FROM timetable WHERE stanza IS NULL or stanza = ''"
    cursore.close()
    connessione.commit()
    connessione.close()


##ELABORAZIONE
if __name__ == "__main__":
    if(boolD):
        print("inizio programma")

    fn_generarighe()
    
    if(boolD):
        print("Fine programma")
