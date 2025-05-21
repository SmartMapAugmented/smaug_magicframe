from threading import Thread
import time
from dbupdate import *



class ToDb(Thread):
    """
    thread pour envoyer la position du bateau à dans une base de donnée spatialite
    en paramètres
    db : chemin complet de la base de donnée
    table : nom de la table dans laquelle est stockée la position du bateau
    pour test, le faire tourner 10 fois
    """
    
    def __init__(self,thread_detect,db,table):
        Thread.__init__(self)
        self.thread_detect = thread_detect
        self.db = db
        self.table = table
        self.connector, self.cursor =  init_db(self.db, self.table)
        insert_position(self.thread_detect.pos_latlong[0],self.thread_detect.pos_latlong[1],self.db, self.table)
        self.execution = True
        
        
    def run(self):
        i = 0
        print("etat de l execution :", self.execution)
        while True :
            if self.execution == True:
                print('envoi vers spatialite de ' + str(self.thread_detect.pos_latlong) + 'chemin' + self.db, self.table )
                lat = str(self.thread_detect.pos_latlong[0])
                lon = str(self.thread_detect.pos_latlong[1])
                updateBoatPosition(lat,lon,self.db,self.table)
                time.sleep(1)
                
            else:
                print('arret de la mise à jour de la base')
                break
