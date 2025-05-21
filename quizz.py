import interactions as it
from fonctions import question_bdd
from time import sleep
import json
from fonctions import det_coeffs
from datetime import datetime, timezone

#import descarte_VR

import os


os.environ['PATH'] = os.environ['PATH'] + ';.\\dll'

class Quizz:
    """
    classe pour gérer le quizz
        arborescence d'un quizz <nomDuQuizz> :
            - fichier config.json configuration des quizz
              (on peut y mettre plusieurs quizz, la clé quizzname doit être unique) :
                - liste des noms des questions
                - nom du quizz
                - nom des fichiers de bonne et mauvaise réponse
                - nom de la table des réponse : contient les objets géographiques réponses                    
            - dossier <nom_quizz>:
                - fichier <nom_quizz>.sqlite : contient les zones de réponse
                    un attribut reponse contient le nom de la zone et sert à la requête de questionnement 
                - dossier son_<nomDuQuizz>
                    - fichiers sons :
                        - fichier score Xsur5.wav ou Xsur15.wav (à modifier), 1 par score possible
                        - fichier <question>.wav, 1 par question, corresponds aux questions du fichier json
                        - fichier BonneReponse.wav
                        - fichier MauvaiseReponse.wav
                        
    
    """

    def __init__(self, nomQuizz, fichier_config):

        self.question_courante = 0
        self.score = 0
        self.quizz_name = nomQuizz
        self.trueId = 0
        # a remplacer par un chargement d un fichier json config_quizz.json
        print("chargement fichier de config :",fichier_config)
        with open(fichier_config) as json_data:
            params = json.load(json_data)
        print("lancement du quizz : " + self.quizz_name)
        
        self.recap_questions = []  # tableau des question contenant un tuple de 3 : (no_question,texte,reponse donnee)
        
        for i in params:
            if ( "quizzName" in i):
                if i["quizzName"] == nomQuizz: 
                    print("chargement du quizz : " + nomQuizz)
                    self.son_bonneReponse = i["sonBonneReponse"]
                    self.son_mauvaiseReponse = i["sonMauvaiseReponse"]
                    self.bdd_name = i["quizzName"]
                    self.table = i["quizzTable"]
                    self.questions = i["questions"]
                    print("liste des questions : " + str(self.questions))
                    self.rep_quizz = "./" + self.quizz_name + "/"
                    self.rep_sons_quizz = self.rep_quizz + "son_" + nomQuizz + "/"
                    self.fichierBase = self.rep_quizz + i["quizzFichier"]
                    self.calage = i["calage"] # points dans le scr de la carte
                    self.calage_pix = i["calage_pix"] # points correspondants en x,y pixels sur carte

            if ( "CONFNAVISU" in i):
                self.host = i["HOST"]
                self.port = i["PORT"]
                self.control = i["CONTROL"]
                self.read = i["READ_FILE"]
                self.origin = i["ORIGIN"]
        idx = 0
        for i in self.questions:
            question = (idx,i,'')
            self.recap_questions.append(question)
            idx = idx + 1
            
        print(str(self.recap_questions))
        #ajouter det_coeffs à partir de calage et calage_pix
        #det_coeffs(ptA, ptB, ptC)
        # format pt : ((lat,lon),(x,y))
        # dans le fichier de calage, mettre y_terrain,x_terrain et non pas x,y
        print("affichage pts calage y x terrain a la creation de la classe : ",self.calage)
        print("affichage pts calage x y frame a la creation de la classe : ",self.calage_pix)
        coord_A = self.calage[0]
        coord_B = self.calage[1]
        coord_C = self.calage[2]
        coord_pix_A = self.calage_pix[0]
        coord_pix_B = self.calage_pix[1]
        coord_pix_C = self.calage_pix[2]

        coord_A = self.json_to_calage(coord_A)
        coord_B = self.json_to_calage(coord_B)
        coord_C = self.json_to_calage(coord_C)

        coord_pix_A = self.json_to_calage(coord_pix_A)
        coord_pix_B = self.json_to_calage(coord_pix_B)
        coord_pix_C = self.json_to_calage(coord_pix_C)

        print("coordonnées de A: ",coord_A[0],coord_A[1])
        print("coordonnées de A pixel: ",coord_pix_A[0],coord_pix_A[1])
        print("coordonnées de B: ",coord_B[0],coord_pix_B[1])
        print("coordonnées de B pixel: ", coord_pix_B[0], coord_pix_B[1])
        print("coordonnées de C: ",coord_C[0],coord_C[1])
        print("coordonnées de C pixel: ", coord_pix_C[0], coord_pix_C[1])

        ptA = ((coord_A[0],coord_A[1]),(coord_pix_A[0],coord_pix_A[1]))
        ptB = ((coord_B[0],coord_B[1]),(coord_pix_B[0],coord_pix_B[1]))
        ptC = ((coord_C[0],coord_C[1]),(coord_pix_C[0],coord_pix_C[1]))

        self.coeffs = det_coeffs(ptA,ptB,ptC)
        print("coefficients ok : ",self.coeffs)
    
    def __del__(self):
        #€self.dit_score()
        print("fin du quizz : " + self.quizz_name)

    def json_to_calage(self,machaine):
        liste_coord = machaine.split(",")
        x = float(liste_coord[0])
        y = float(liste_coord[1])
        print("dans json to calage coord :",x,y)
        return x,y

    def dit_score(self):
        print("Fini !")
        print("liste des questions avec les réponses : ")
        print(str(self.recap_questions))
        print("Votre score est de " + str(self.score) + " / 15 ")
        it.lit_wav(self.rep_sons_quizz + str(self.score) + 'sur15.wav')

    def dit_question(self):
        #annonce de la question
        print("question no : ", self.question_courante)
        question = self.questions[self.question_courante]
        print("placer le bateau dans :", question)
        it.lit_wav(self.rep_sons_quizz + str(question) +".wav")
        self.gestion_navisu("question")

    def lit_reponse(self,position):
        #lire la reponse par rapport a la position du bateau et lance la solution
        print("table : " + str(self.table))
        print("position dans lit_reponse : ",position)
        reponse = question_bdd(self.fichierBase,\
                               self.table,\
                               position[1],\
                               position[0],\
                               self.questions[self.question_courante])
        self.trueId = reponse
        self.dit_reponse(reponse)
        #descarte_VR.ecrit_position_fichier(position)
        self.gestion_navisu('validate')
        
    def gestion_navisu(self,question):
        #creation des requetes pour navisu
        heure = str(datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))
        
        
        trueId = str(self.trueId)
        
        self.quizz_navisu = "scenarioSmaug"
        self.req_read = "http://" +self.host + ":" +self.port + \
                        "/read?cmd=scenario&origin=" + self.origin + \
                        "&path=scenarios/" + self.quizz_navisu + \
                        "/&target=" + self.quizz_navisu + ".json" + \
                        "&timestamp=" + heure
                        
        
        self.req_question = "http://" + self.host + ":" +self.port + \
                            "/control?cmd=question&origin=" + self.origin + \
                            "&target=q" + str(self.question_courante + 1) + "&timestamp=" + heure
        
        self.req_start = "http://" + self.host + ":" + self.port + \
                         "/control?cmd=start&target=" + str(self.question_courante +1) + \
                         "&origin=" + self.origin + "&timestamp=" + heure
        
        self.req_stop = "http://"+ self.host + ":" + self.port + \
                        "control?cmd=stop&target=" + str(self.question_courante + 1) + \
                        "&origin=" + self.origin + "&timestamp=" + heure
        
        self.req_validate = "http://" + self.host + ":" + self.port + \
                            "/control?cmd=validate&target=" + trueId + \
                            "&origin=" + self.origin +"&timestamp=" + heure
        
        self.req_response = "http://" +self.host + ":" + self.port + \
                            "/control?cmd=response&target=" + str(self.question_courante) + \
                            "&origin=" + self.origin + "&timestamp=" + heure
        
        if (question == "read"):
            marequete = self.req_read
        elif (question == "question"):
            marequete = self.req_question
        elif (question == "start"):
            marequete = self.req_start
        elif (question == "stop"):
            marequete = self.req_stop
        elif (question == "validate"):
            marequete = self.req_validate
        elif (question == "response"):
            marequete = self.req_response
        
        print("envoi requête " + question + " : " + marequete)
        print(" ATTENTION !! requete non envoyée, décommentez la ligne suivante pour corriger")
        #envoi_requete_navisu(marequete)

    def dit_reponse(self,reponse):
        # gestion de la réponse
        print("reponse donnee : " + str(reponse) + " pour la question " + str(self.question_courante))
        if int(reponse) == 1:
            self.score = self.score + 1
            print("bonne réponse dans dit_reponse")
            self.recap_questions[self.question_courante] = (self.recap_questions[self.question_courante][0], \
                                                            self.recap_questions[self.question_courante][1],
                                                            'Bonne')
            it.lit_wav(self.rep_sons_quizz + self.son_bonneReponse)
            sleep(2)
        else:
            print("mauvaise réponse dans dit_reponse")
            self.recap_questions[self.question_courante] = (self.recap_questions[self.question_courante][0], \
                                                            self.recap_questions[self.question_courante][1],
                                                            'Fausse')
            it.lit_wav(self.rep_sons_quizz + self.son_mauvaiseReponse )
            
            sleep(2)
            print(str(self.recap_questions[self.question_courante]))
        
        if self.question_courante < len(self.questions) - 1:
            self.question_courante = self.question_courante + 1
        else:
            sleep(3)
            self.dit_score()
            self.question_courante = 0

def cr_liste_quizz(fichier_config):
    """
    fontction pour lister les quizz définis dans le fichier de config
    pour entre autres affichage dans interface
    """
    listeQuizz=[]
    with open(fichier_config) as json_data:
        params = json.load(json_data)
    for i in params:
        if ( "quizzName" in i):
            listeQuizz.append(i["quizzName"])
        
    return listeQuizz

def cr_liste_questions(nomquizz, fichier_config):
    """
    créer la liste des questions d'un quizz d'un fichier de config
    pour affichage interface
    """
    questions = []
    with open(fichier_config) as json_data:
        params = json.load(json_data)
        
        for i in params:
            if ( "quizzName" in i):
                if i["quizzName"] == nomquizz:
                    questions = i["questions"]
                
    return questions      

def test():
    monquizz = Quizz("Quizz_Pim","config.json")

    # for i in range(2):
    #     monquizz.dit_question()
    #     monquizz.lit_reponse([48.3843424, -4.4962450])
    #print("affichage pts calage dans main : ",monquizz.calage_pix)
    # monquizz = '' # pour reset le quizz
    # monquizz.dit_score()



# décommenter pour tester 
#test()