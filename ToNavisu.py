from threading import Thread
import requests
import time
import random
from datetime import datetime, timezone

class ToNavisu(Thread):
    """
    thread pour envoyer la position du bateau à Navisu
    pour test, le faire tourner 10 fois
    """
    
    def __init__(self,thread_detect,host,port,cmd,origin,target):
        Thread.__init__(self)
        self.thread_detect = thread_detect
        self.execution = True
        
        self.host = host
        self.port = port
        self.cmd = cmd
        self.origin = origin
        self.target = target
        
        """
        self.host = "93.90.200.21"
        self.port = "3003"
        self.cmd = "track"
        self.origin = "SMAP"
        self.target = "ship"
        """
    def run(self):
        i = 0
        print("etat de l execution :", self.execution)
        while True :
            if self.execution == True:
                heure = str(datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))
                print('envoi vers navisu de ' + str(self.thread_detect.pos_latlong))
                lat = str(self.thread_detect.pos_latlong[0])
                lon = str(self.thread_detect.pos_latlong[1])
                marequete = 'http://'+ self.host + ':' + self.port + \
                                 '/control?cmd=' + self.cmd + \
                                 '&origin=' + self.origin + \
                                 '&timestamp=' + heure + \
                                 '&target=' + self.target + \
                                 '&latitude=' + lat + \
                                 '&longitude=' + lon
                print("envoi requête : " + marequete)
                try:
                    r = requests.put(marequete)
                except:
                    print('pb de requete')
                time.sleep(1)
                
            else:
                print('arret du thread navisu')
                break
