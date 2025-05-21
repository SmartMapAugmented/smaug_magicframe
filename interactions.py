import pyttsx3
import time
import os
#import simpleaudio as sa
from kivy.core.audio import SoundLoader


# voix français linux : voice.id ==26
# voix français windows : voice.id ==0

if os.sys.platform == 'linux':
    num_voix = 26
if os.sys.platform == 'win32' or os.sys.platform == 'win64':
    num_voix = 0

def say_it(phrase):
    #Fonction text-to-speech
    os.system("espeak-ng -v fr-fr -s 120 " + phrase)

def lit_wav(fichier):
    print("lecture du fichier dans fonction lit_wav : " + fichier)

    #os.system("cvlc " + str(fichier) + " --stop-time 25 vlc://quit 2>/dev/null &")
    mon_son = SoundLoader.load(fichier)
    mon_son.play()
    """fichier_audio.play().wait_done()"""
    print("pas de son parce que simple audio ne passe pas")

"""
# fonction avec de la vraie synthère vocale
def say_it(phrase):
    # Fonction text-to-speech
    global num_voix
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('rate', 150)  # Speed percent (can go over 100)
    engine.setProperty('volume', 1)  # Volume 0-1
    engine.setProperty('voice', voices[num_voix].id)  # changes the voice
    engine.say(phrase)
    engine.runAndWait()
"""

interactions = {"1": "entrer les coordonnees du point de calibration 1",
                "2": "entrer les coordonnees du point de calibration 1",
                "3": "entrer les coordonnees du point de calibration 1",
                "c": "calibration 2 pts",
                "k": "calibration 3 pts",
                "a": "tracker le rouge",
                "z": "tracker le jaune",
                "e": "tracker le vert",
                "t": "annonce le nom de l'objet plus proche",
                "s": "s comme suivi, annonce le nom dans le rayon distance max automatiquement",
                "y": "annonce le nom, la distance et l orientation de l objet plus proche",
                "v": "annonce la vitesse et direction du vent",
                "d": " annonce la distance entre 2 points (si deux points sont detectes par le masque)",
                "f": "retourne l'image",
                "o": "Dessine les cercles autour des balises",
                "p": "Ecrit le nom des balises",
                "b": "annonce les bord de carte",
                "x": "sauvegarder la configuration",
                "l": "charger la configuration",
                "h": "afficher cette aide",
                "q": "quitter"
                }


def affiche_interactions():
    for i in interactions:
        print("- ", str(i)," : ",interactions[i])

def test():
    fichier = "./Quizz_Pim/son_Quizz_Pim/Q12.wav"
    lit_wav(fichier)

#test()

