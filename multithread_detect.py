import random
import sys
from threading import Thread
import time
from collections import deque
from imutils.video import VideoStream
import numpy as np
import argparse
import cv2
import imutils
from balises import *
import numpy as np


class detection(Thread):

    """Thread chargé de la detection."""

    def __init__(self, lettre):
        Thread.__init__(self)
        self.lettre = lettre
        self.pos = (0,2)
        self.detection_on = False
        self.teinte_min = 0
        self.teinte_max = 360
        self.saturation_min = 0
        self.saturation_max = 255
        self.lumière_min = 0
        self.lumière_max = 255
        self.video_width = 640
        self.video_height = 480
        self.coeffs = (0,0,0,0,0,0)
    
    
    def get_trackbar_param(self, params):
        """ récupérer les paramètres des trackbar
            params est un tuple de 6 variables :
        """
        self.teinte_min = params[0]
        self.teinte_max = params[1]
        self.saturation_min = params[2]
        self.saturation_max = params[3]
        self.lumière_min = params[4]
        self.lumière_max = params[5]
        
        #print("teinte dans thread", self.teinte_min, self.teinte_max, self.saturation_min, self.saturation_max, self.lumière_min, self.lumière_max)
    
    def calc_pos(self, ptX, coeffs):
        """
        :param ptX: point en coordonnees camera (x,y) dont on veut trouver la lat lon
        :param coeffs: coefficients a,b,c,a',b',c' de changement de repere. Sous la forme lon = ax+by+C, lat = a'x+b'y+c'
        Les coefficient sont calcules par la fonction def_coeffs
        :return: point en coordonnee lat, lon (lat,lon)
        """
        #print("fonction calcul position")
        a = coeffs[0]
        b = coeffs[1]
        c = coeffs[2]
        aprim = coeffs[3]
        bprim = coeffs[4]
        cprim = coeffs[5]

        lon = eval(str(a)) * ptX[0] + eval(str(b)) * ptX[1] + eval(str(c))
        lat = eval(str(aprim)) * ptX[0] + eval(str(bprim)) * ptX[1] + eval(str(cprim))

        return (lat, lon)

    def run(self):
        """Code à exécuter pendant l'exécution du thread."""

        # construct the argument parse and parse the arguments
        ap = argparse.ArgumentParser()
        ap.add_argument("-v", "--video",
            help="path to the (optional) videofile") #video en parametre, ou bien acces a la camera
        ap.add_argument("-b", "--buffer", type=int, default=64,
            help="max buffer size") # longueur de la trainee
        ap.add_argument("-t", "--time", type = int, default = 1,
            help="temps min avant de declencher une information sonore dans le tracking") #parametre de temps min, en s
        ap.add_argument("-d", "--distance", type = int, default = 300,
            help="distance max pour declencher information sonore") #parametre de distance max, en m
        args = vars(ap.parse_args())
        mode_jeu = 0

        calibration_done = False
        nb_pts = [0,0,0] #permet de savoir si on a déjà entré un point pour la calibration. Le point rouge est à l'index 0, et sera incrémenté quand sera renseigné.


        tracking = False #booléen qui permet d'activer la suivi continue du point vert pour déclencher ensuite une info sonore
        last_balise = ""

        def nothing(x):
            pass

        

        # define the lower and upper boundaries of the "green"
        # ball in the HSV color space, then initialize the
        # list of tracked points

        #couleurs = tuple (Bleu,Vert Rouge) = BGR
        #ici, les couleurs sont données en teinte saturation lumière 
        HSVLower = (40, 40, 6) #de 29 a 64, on est dans le vert
        HSVUpper = (90, 200, 200) #on prend une plage de saturation et lumière large
        #rajouter slider pour modifier la plage de couleur
        #

        #couleurs pour tester la calibration


        #cv2.createTrackbar('Saturation','colorWindow',0,100,nothing)
        #cv2.createTrackbar('Lumière','colorWindow',0,100,nothing)


        pts = deque(maxlen=args["buffer"]) #initialiser la trainée. La taille est celle donnée en paramètre. Les élements en trop sortiront tout seul.

        # if a video path was not supplied, grab the reference
        # to the webcam
        if not args.get("video", False): #si pas de vidéo
            vs = VideoStream(0).start() #activer la camera de l'ordi
            

        # otherwise, grab a reference to the video file
        else:
            vs = cv2.VideoCapture(args["video"]) #sinon la vidéo sera celle placée en argument
            self.video_width = vs.get(cv2.CAP_PROP_FRAME_WIDTH)
            self.video_height = vs.get(cv2.CAP_PROP_FRAME_HEIGHT)

        
        maxdist = args["distance"]
        mintime = args["time"]

        # allow the camera or video file to warm up
        time.sleep(2.0)
        
        cv2.namedWindow('mask')
        cv2.namedWindow('Frame')
        #cv2.namedWindow('Reglages')

        #il faut modifier les valeurs limite des trackbar. la saturation et la lumière ne vont pas jusqu'a 360
        

        #cv2.setTrackbarPos('Distance max','Frame', maxdist)
        #cv2.setTrackbarPos('Temps min','Frame', mintime)

        
        # keep looping
        while True:

            

            teinte_min = self.teinte_min
            teinte_max = self.teinte_max

            saturation_min = self.saturation_min
            saturation_max = self.saturation_max

            lumière_min = self.lumière_min
            lumière_max = self.lumière_max

            HSVLower = (teinte_min, saturation_min, lumière_min)
            HSVUpper = (teinte_max, saturation_max, lumière_max)
            
            #print(HSVLower, HSVUpper)
            
            # maxdist = cv2.getTrackbarPos('Distance max','Frame') * 10**-3
            # mintime = cv2.getTrackbarPos('Temps min','Frame')


            # grab the current self.frame
            self.frame = vs.read() #lire une image de la vidéo. contient un tuple, et le premier dit si une image a été capturée. Le deuxième, c'est l'image

            # handle the self.frame from VideoCapture or VideoStream
            self.frame = self.frame[1] if args.get("video", False) else self.frame #gerer la différence entre une vidéo et la caméra

            # if we are viewing a video and we did not grab a self.frame,
            # then we have reached the end of the video
            if self.frame is None: #fin de la vidéo -> quitter
                break

            # resize the self.frame, blur it, and convert it to the HSV
            # color space
            #print("frame : ",self.frame.shape)
            #self.frame = imutils.resize(self.frame, width=600) #on reduit la taille de l'image pour la traiter plus vite -> inutile l'image fait déjà 640 x 480
            blurred = cv2.GaussianBlur(self.frame, (11, 11), 0) #reduire le bruit haute fréquence
            hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV) #passer en codage couleur teinte saturation lumière

            # construct a mask for the color "green", then perform
            # a series of dilations and erosions to remove any small
            # blobs left in the mask
            mask = cv2.inRange(hsv, HSVLower, HSVUpper) #on crée un masque qui va permettre de voir le vert dans notre intervalle défini
            cv2.imshow("mask", mask)

            mask = cv2.erode(mask, None, iterations=2) #permet de supprimer les défauts présents (taches...)
            mask = cv2.dilate(mask, None, iterations=2) #on reduit, puis grossit. Ainsi, les traces disparaissent

            # find contours in the mask and initialize the current
            # (x, y) center of the ball
            cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE) #trouver le contour de la balle
            cnts = imutils.grab_contours(cnts)
            center = None #initialiser les coordonnées du centre, x, y
            # only proceed if at least one contour was found
            if len(cnts) > 0: #si on objet (contour) a été trouvé
                # find the largest contour in the mask, then use
                # it to compute the minimum enclosing circle and
                # centroid
                c = max(cnts, key=cv2.contourArea) #on prend l'objet le plus grand parmis ceux détectés
                ((x, y), radius) = cv2.minEnclosingCircle(c) #on prend le cercle le plus petit qui entoure la tache et on garde les informations dessus (rayon et centre)

                #demander a pagianotis
                M = cv2.moments(c) #cf doc
                center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                self.pos = center
                self.pos_latlong = self.calc_pos(self.pos, self.coeffs)
                
                # only proceed if the radius meets a minimum size
                if radius > 5: #on dessine le cercle seulement si l'objet est suffisament grand
                    # draw the circle and centroid on the self.frame,
                    # then update the list of tracked points
                    cv2.circle(self.frame, (int(x), int(y)), int(radius),
                        (0, 255, 255), 2)
                    cv2.circle(self.frame, center, 5, (0, 0, 255), -1)

            # update the points queue
            pts.appendleft(center) #ajoute le centre a la queue. Les images les plus vieilles sortent automatiquement de la queue

            # loop over the set of tracked points
            for i in range(1, len(pts)): #pour chaque ancienne coordonnées de centre, on va ajouter une tache rouge pour faire la trainée
                # if either of the tracked points are None, ignore
                # them
                if pts[i - 1] is None or pts[i] is None:
                    continue

                # otherwise, compute the thickness of the line and
                # draw the connecting lines
                thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
                cv2.line(self.frame, pts[i - 1], pts[i], (0, 0, 255), thickness) #0,0,255 = rouge
            
            
            #self.frame = cv2.cvtColor(self.frame, cv2.COLOR_HSV2RGB)
            #pour affichage hors thread
                
            self.frame_export = self.frame
            self.mask_export = mask
           
            self.detection_on = True

            # show the self.frame to our screen
            cv2.imshow("Frame", self.frame)
            key = cv2.waitKey(1) & 0xFF

            # if the 'q' key is pressed, stop the loop
            if key == ord("q"): #permet de quitter la boucle si on presse q (alors que fermer la fenetre relance la vidéo)
                break


        # if we are not using a video file, stop the camera video stream
        if not args.get("video", False): #si pas de vidéo en parametre
            vs.stop() #desactiver la camera

        # otherwise, release the camera
        else:
            vs.release() #liberer la vidéo

        # close all windows
        cv2.destroyAllWindows()





# Création des threads
#thread_1 = detection("1")


"""

# Lancement des threads
thread_1.start()

i = 0

while not thread_1.detection_on:
    pass

while i < 100:
    time.sleep(1)
    print(thread_1.pos)
    params = (1,100 + i*5, 15, 110 + i*5, 78, 220 + i*5)
    thread_1.get_trackbar_param(params)
    
    i = i + 1
    #cv2.namedWindow('tkinter')
    #cv2.imshow("tkinter", thread_1.frame)
# Attend que les threads se terminent
thread_1.join()
"""

