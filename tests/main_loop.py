# importer les librairies necessaires au programme
from collections import deque
from imutils.video import VideoStream
import numpy as np
import argparse
import cv2
import imutils
import os
import time
from fonctions import *
from balises import *
import numpy as np
import interactions as it

global config
config = dict()

fic_param = "param.txt"

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

cam = trouve_cam()
print("camera : ", cam)

if not args.get("video", False): #si pas de video
    vs = VideoStream(src = int(cam) ).start() #activer la camera de l'ordi
else:
    vs = cv2.VideoCapture(args["video"]) #sinon la video sera celle placee en argument

maxdist = args["distance"]
mintime = args["time"]

pts = deque(maxlen=args["buffer"]) #initialiser la trainee. La taille est celle donnee en parametre. Les elements en trop sortiront tout seul.

# allow the camera or video file to warm up
time.sleep(2.0)

#on cree une fenetre mask dans laquelle on met chaque trackbar de couleur et le masque
cv2.namedWindow('mask')
#la fenetre frame contient l'image perçue par la camera et sur laquelle on rajoute un point rouge pour l'objet le plus gros qui passe le masque.
cv2.namedWindow('Frame')

teinte_min = 0
teinte_max = 0
saturation_min = 0
saturation_max = 0
lumiere_min = 0
lumiere_max = 0
HSVLower = (teinte_min, saturation_min, lumiere_min)
HSVUpper = (teinte_max, saturation_max, lumiere_max)


# chargement de la config si le fichier param existe

if os.path.exists(fic_param) :
    print("chargement du fichier de configuration")
    teinte_min, teinte_max, saturation_min, saturation_max, lumiere_min, lumiere_max, HSVLower, HSVUpper, maxdist, mintime, a, aprim, b, bprin, c, cprim = load_param(fic_param)

# on cree les objets trackbars.
cv2.createTrackbar('Teinte Min','mask',teinte_min,180,nothing)
cv2.createTrackbar('Teinte Max','mask',teinte_max,180,nothing)

cv2.createTrackbar('Saturation Min','mask',saturation_min,255,nothing)
cv2.createTrackbar('Saturation Max','mask',saturation_max,255,nothing)

cv2.createTrackbar('Lumiere Min','mask',lumiere_min,255,nothing)
cv2.createTrackbar('Lumiere Max','mask',lumiere_max,255,nothing)

cv2.createTrackbar('Distance max','Frame',0,1000,nothing)
cv2.createTrackbar('Temps min','Frame',0,5,nothing)

# on initialise les trackbars.
cv2.setTrackbarPos('Distance max','Frame', int(maxdist))
cv2.setTrackbarPos('Temps min','Frame', mintime)

# video recorder
w = 600
h = 450
#lignes qui servaient a voir si on pouvait enregistrer la video captee par la camera
#fourcc = cv2.VideoWriter_fourcc('X', '2', '6', '4')
#video_writer = cv2.VideoWriter("~/ttc/test.avi", fourcc, 25, (w, h))

try:
    load_param()
    change_calibration_done()
except:
    pass

# keep looping
while True:

    #on recupere les valeurs de tout les trackbars crees
    teinte_min = cv2.getTrackbarPos('Teinte Min','mask')
    teinte_max = cv2.getTrackbarPos('Teinte Max','mask')

    saturation_min = cv2.getTrackbarPos('Saturation Min','mask')
    saturation_max = cv2.getTrackbarPos('Saturation Max','mask')

    lumiere_min = cv2.getTrackbarPos('Lumiere Min','mask')
    lumiere_max = cv2.getTrackbarPos('Lumiere Max','mask')

    HSVLower = (teinte_min, saturation_min, lumiere_min)
    HSVUpper = (teinte_max, saturation_max, lumiere_max)

    maxdist = cv2.getTrackbarPos('Distance max','Frame') * 10**-3
    mintime = cv2.getTrackbarPos('Temps min','Frame')

    # creation d'une configuration pour enregistrement dans fichier
    config["teinte_min"] = teinte_min
    config["teinte_max"] = teinte_max
    config["saturation_min"] = saturation_min
    config["saturation_max"] = saturation_max
    config["lumiere_min"] = lumiere_min
    config["lumiere_max"] = lumiere_max
    config["HSVLower"] = HSVLower
    config["HSVUpper"] = HSVUpper
    config["maxdist"]  = maxdist
    config["mintime"] = mintime

    # grab the current frame
    frame = vs.read() #lire une image de la video. contient un tuple, et le premier dit si une image a ete capturee. Le deuxieme, c'est l'image

    # handle the frame from VideoCapture or VideoStream
    frame = frame[1] if args.get("video", False) else frame #gerer la difference entre une video et la camera

    # if we are viewing a video and we did not grab a frame,
    # then we have reached the end of the video
    if frame is None: #fin de la video -> quitter
        break

    # resize the frame, blur it, and convert it to the HSV
    # color space
    frame = imutils.resize(frame, width=600) #on reduit la taille de l'image pour la traiter plus vite
    frame = flip(frame)
    blurred = cv2.GaussianBlur(frame, (11, 11), 0) #reduire le bruit haute frequence
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV) #passer en codage couleur teinte saturation lumiere

    # construct a mask for the color "green", then perform
    # a series of dilations and erosions to remove any small
    # blobs left in the mask
    mask = cv2.inRange(hsv, HSVLower, HSVUpper) #on cree un masque qui va permettre de voir le vert dans notre intervalle defini
    cv2.imshow("mask", mask)

    mask = cv2.erode(mask, None, iterations=2) #permet de supprimer les defauts presents (taches...)
    mask = cv2.dilate(mask, None, iterations=2) #on reduit, puis grossit. Ainsi, les traces disparaissent

    # find contours in the mask and initialize the current
    # (x, y) center of the ball
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE) #trouver le contour de la balle
    cnts = imutils.grab_contours(cnts)
    center = None #initialiser les coordonnees du centre, x, y
    # only proceed if at least one contour was found
    if len(cnts) > 0: #si on objet (contour) a ete trouve
        # find the largest contour in the mask, then use
        # it to compute the minimum enclosing circle and
        # centroid
        c = max(cnts, key=cv2.contourArea) #on prend l'objet le plus grand parmis ceux detectes
        ((x, y), radius) = cv2.minEnclosingCircle(c) #on prend le cercle le plus petit qui entoure la tache et on garde les informations dessus (rayon et centre)

        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

        # only proceed if the radius meets a minimum size
        if radius > 10: #on dessine le cercle seulement si l'objet est suffisament grand
            # draw the circle and centroid on the frame,
            # then update the list of tracked points
            cv2.circle(frame, (int(x), int(y)), int(radius),
                (0, 255, 255), 2)
            cv2.circle(frame, center, 5, (0, 0, 255), -1)


    pts.appendleft(center) #ajoute le centre a la queue. Les images les plus vieilles sortent automatiquement de la queue
    print_frame(frame, pts, args["buffer"], maxdist*1000)

    #fonction utilise uniquement si la tracking activate est True. Sinon on sort aussi tôt de la fonction.
    auto_tracking(center, mintime, maxdist)

    checking_bord(center, frame)

    key = cv2.waitKey(1) & 0xFF

    #les lignes en dessous decrivent les interactions clavier.
#CALIBRATION
    if key == ord("1"): #commande pour entrer un nom de balise qui servira à convertir les coordonnees pixels en coordonnees GPS
        save_point_1(center)
        
    if key == ord("2"):
        save_point_2(center)

    if key == ord("3"):
        save_point_3(center)
        
    #la condition suivant vaut true si on a rentre 2 points de calibrations differents (un avec "1", l'autre avec "2")
    if key == ord("c") and nb_pts >= [1,1] :
        calibration_2pts()
    if key == ord("k") and nb_pts >= [1,1,1] :
        calibration_3pts()
        config["a"] = coeff[0]
        config["aprim"] = coeff[1]
        config["b"] = coeff[2]
        config["bprim"] = coeff[3]
        config["c"] = coeff[4]
        config["cprim"] = coeff[5]




#COULEURS
    if key == ord("a"): #changer la couleur des trackbar pour tracker le rouge
        set_trackbar_color(redMin, redMax) #les valeurs sont dans le fichier fonctions.py

    if key == ord("z"): #changer la couleur des trackbar pour tracker le jaune
        set_trackbar_color(yellowMin, yellowMax)
        
    if key == ord("e"): #changer la couleur des trackbar pour tracker le vert, utile dans l'utilisation generale
        set_trackbar_color(greenMin, greenMax)

#TRACKING
    if key == ord("t"): # annonce le nom de l'objet plus proche
        annonce_balise(center)

    if key == ord("s"): #"s" comme "suivi", annonce le nom dans le rayon distance max automatiquement
        #à chaque fois qu'on presse "s", on change la valeur du bouleen tracking_activate du fichier fonctions.py
        change_auto_tracking()

    if key == ord("y"): # annonce le nom, la distance et l'orientation de l'objet plus proche
        annonce_balise_adv(center)
    
    if key == ord("v"): # annonce la vitesse et direction du vent
        annonce_vent(center)

    if key == ord("d"): # annonce la distance entre 2 points (si deux points sont detectes par le masque)
        distance_2_points(cnts)
        
#AFFICHAGE
    if key == ord("f"): # retourne l'image. 
        change_flip_img()
    
    if key == ord("o"): # Dessine les cercles autour des balises
        change_draw_circles_onoff()

    if key == ord("p"): # Ecrit le nom des balises
        change_print_names()

    if key == ord("b"): # annonce les bord de carte
        #à chaque fois qu'on presse "b", on change la valeur du bouleen tracking_bord du fichier fonctions.py
        change_tracking_bord()

#GESTION DE LA CONFIG
    if key == ord("x"): #sauvegarde des parametres
        save_param(config,fic_param)
    
    if key == ord("l"): #chargement des parametres
        teinte_min, teinte_max, saturation_min, saturation_max, lumiere_min, lumiere_max, HSVLower, HSVUpper, maxdist, mintime, a, aprim, b, bprin, c, cprim = load_param(fic_param)
        cv2.setTrackbarPos('Teinte Min', 'mask', teinte_min)
        cv2.setTrackbarPos('Teinte Max', 'mask', teinte_max)

        cv2.setTrackbarPos('Saturation Min', 'mask', saturation_min)
        cv2.setTrackbarPos('Saturation Max', 'mask', saturation_max)

        cv2.setTrackbarPos('Lumiere Min', 'mask', lumiere_min)
        cv2.setTrackbarPos('Lumiere Max', 'mask', lumiere_max)
#AIDE
    if key == ord("h"): # affiche l'aide
        it.affiche_interactions()
# THE END
    if key == ord("q"): # quitter la boucle
        break

# if we are not using a video file, stop the camera video stream
if not args.get("video", False): #si pas de video en parametre
    vs.stop() #desactiver la camera

# otherwise, release the camera
else:
    vs.release() #liberer la video

#video_writer.release()
# close all windows
cv2.destroyAllWindows()
