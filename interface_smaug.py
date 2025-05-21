import tkinter
from tkinter import ttk, Tk, Button, Canvas
from tkinter import *
import cv2
import PIL.Image, PIL.ImageTk
import time
# import imutils
import os
import sqlite3
from multithread_detect import detection
from pts_calage import *
from balises import *
from fonctions import *
from quizz import Quizz,cr_liste_quizz,cr_liste_questions
from ToNavisu import ToNavisu

os.environ['PATH'] = os.environ['PATH'] + ';.\\dll'

from ToDb import ToDb
import traceback
import json
from datetime import datetime, timezone


class InterfaceSmaug:
    """
    Classe pour l'interface. La définir dans le __init__
    """
    def __init__(self, window, window_title, thread, video_source=-1):
        
        self.x = 0  # position x du curseur en pixel vers la droite
        self.y = 0  # position y du curseur en pixel vers le bas
        #points x,y des 3 points de calage
        self.point_calage1 = (0,0)
        self.point_calage2 = (0,0)
        self.point_calage3 = (0,0)
        self.nb_pts_cales = 0
        
        self.thread_detect = thread
        
        self.mode_jeu = False
        
        # fenetre principale  + titre provenant du lancement dans le main
        self.window = window
        self.window.title(window_title)
        # source video (picam -1)
        self.video_source = video_source

        #classe MyVideoCapture
        self.vid = MyVideoCapture(self.thread_detect, self.video_source) #video_source sert à rien

                #variable i sert à positionner les éléments en vertical
        i = 0
        
        # a nettoyer tous ces fichiers de config
        self.rep_config = 'config/'
        self.file_logo = 'logo.png'
        self.file_config = 'config.txt'
        
        # initialisation variables pour envoi de données vers navisu
        # peut etre a mettre dans la config dans ToNavisu ou le quizz à voir
        self.configJson = 'config.json'
        
        with open(self.configJson) as json_data:
            params = json.load(json_data)
        for p in params:
            if ( "CONFNAVISU" in p):
                self.host = p["HOST"]
                self.port = p["PORT"]
                self.cmd = p["CMD_TRACK"]
                self.origin = p["ORIGIN"]
                self.target = p["TARGET_SHIP"]
                
        #---------------------------------------------------------------  Paramétrage de la fenetre ------------------------------------------------------------------
        #Taille
        self.root = window
        
        self.root.title ("SMAUG")
        self.root.geometry("1000x700")
        self.root.configure(background='#ECF0F1')

        # --------------- lien avec une touche ------
        
        self.root.event_add = ('<<touche>>', '<f>','<g>')
        self.root.bind('f', self.gest_keypress)
        self.root.bind('d', self.gest_keypress)
        self.root.bind('g', self.gest_keypress)
        self.root.bind('i', self.gest_keypress)
        self.root.bind('j', self.gest_keypress)
        self.root.bind('k', self.gest_keypress)
        self.root.bind('t', self.gest_keypress)
        self.root.bind('a', self.gest_keypress)
        self.root.bind('n', self.gest_keypress)
        self.root.bind('y', self.gest_keypress)
        self.root.bind('s', self.gest_keypress)
        self.root.bind('p', self.gest_keypress)

        #---------------------------------------------------------------  Bandeau SMAUG avec Nom + logo --------------------------------------------------------------
        #Nom
        eti_logo = Label(self.root, text='Smart Map AUGmented',font=("Cooper Black", 20))
        eti_logo.grid (row=i,column=0,columnspan=4)


        #Logo
        logo = PhotoImage(file=self.rep_config + self.file_logo)
        logo = logo.subsample(2, 2) 
        Label(self.root, image=logo).grid(row=i,column=4,columnspan=2)

        i = i + 1

        a=Label(self.root, text='')
        a.grid (row=i,column=0)
        i = i + 1

        #--------------------------------------------------------------- Les onglets ------------------------------------------------------------------------------
        # Création du système d'onglets
        Barre_onglet = ttk.Notebook(self.root)   
        Barre_onglet.grid (row=i,column=0,columnspan=6)
        i = i + 1

        # Ajout de l'onglet 1 [gère la détection]
        o1 = ttk.Frame(Barre_onglet)       
        o1.grid (row=i,column=0,columnspan=5)
        Barre_onglet.add(o1, text='Détection')

        # Ajout de l'onglet 2 [gère le géoréferencement]
        o2 = ttk.Frame(Barre_onglet)       
        o2.grid (row=i,column=2,columnspan=5)
        Barre_onglet.add(o2, text='Calage')
        i = i +1
        
        # Ajout de l'onglet 3 [gère le quizz]
        self.o3 = ttk.Frame(Barre_onglet)
        self.o3.grid (row=i,column=4,columnspan=5)
        Barre_onglet.add(self.o3, text='Quizz')
        o3 = self.o3
        i = i +1
        
        #------------------------------------------------------------------------------------------------------------------------------------------------------
        #---------------------------------------------------------------  ONGLET DETECTION ------------------------------------------------------------------------------
        #------------------------------------------------------------------------------------------------------------------------------------------------------

        #--------------------------------------------------------------- Gestion de la config------------------------------------------------------------------------------

        Eti_config_detect = Label(o1, text = "Choisir la configuration de détection :")
        Eti_config_detect.grid (row=i,column=0,columnspan=3)

        #Liste à charger dans la liste déroulante FONCTION A CREER
        lst_config_detect=self.search_config("config_detection")
        print(" configuration de la detection : " + str(lst_config_detect))

        # 3) - Création de la Combobox via la méthode ttk.Combobox()
        Cmb_config_detect = ttk.Combobox(o1, values=lst_config_detect)
        Cmb_config_detect.grid (row=i,column=3,columnspan=2)
         
        # 4) - Choisir l'élément qui s'affiche par défaut
        #Cmb_config.current(1)

        #bouton pour sauvagarder les tracksbar en cours
        Btn_config_detect = Button(o1, text="sauvegarder les valeurs", command=self.save_config('config_detect'))
        Btn_config_detect.grid (row=i,column=5,columnspan=2)
        i = i + 1

        # saut de ligne
        Label(o1, text='').grid (row=i,column=2,columnspan=3)
        i = i + 1
        #--------------------------------------------------------------- Les scales bar ------------------------------------------------------------------------------

        #load_trackbar_config ('defaut')
        self.val= self.load_config ('defaut')
        print(self.val)

        #teinte_min
        self.var_teinte_min = IntVar()
        

        eti_teinte_min = Label(o1, text='Teinte Min')
        eti_teinte_min.grid (row=i,column=0,columnspan=2)

        self.scale_teinte_min = Scale( o1, variable = self.var_teinte_min,command=self.maj_val_teinte_min,
                       orient=HORIZONTAL,resolution = 1,length=360,width= 15,sliderlength= 10, from_ = 0, to=360,
                       troughcolor='#85C1E9',bg='#ECF0F1',bd = 3,relief=FLAT,
                       showvalue=0)
        self.scale_teinte_min.set (self.val[1])
        self.scale_teinte_min.grid (row=i,column=2,columnspan=2)

        self.eti_val_teinte_min = Label(o1, text='Teinte Min')
        self.eti_val_teinte_min.grid (row=i,column=4,columnspan=2)

        i = i + 1

        #teinte max
        self.var_teinte_max = IntVar()

        eti_teinte_max = Label(o1, text='Teinte max')
        eti_teinte_max.grid (row=i,column=0,columnspan=2)

        self.scale_teinte_max = Scale( o1, variable = self.var_teinte_max,command=self.maj_val_teinte_max,
                       orient=HORIZONTAL,resolution = 1,length=360,width= 15,sliderlength= 10, from_ = 0, to=360,
                       troughcolor='#85C1E9',bg='#ECF0F1',bd = 3,relief=FLAT,
                       showvalue=0)
        self.scale_teinte_max.set (self.val[2])
        self.scale_teinte_max.grid (row=i,column=2,columnspan=2)

        self.eti_val_teinte_max = Label(o1, text='teinte max')
        self.eti_val_teinte_max.grid (row=i,column=4,columnspan=2)

        i = i + 1

        #Saut de ligne
        Label(o1, text='').grid (row=i,column=2,columnspan=3)
        i = i + 1

        #saturation min
        self.var_saturation_min = IntVar()

        eti_saturation_min = Label(o1, text='Saturation min')
        eti_saturation_min.grid (row=i,column=0,columnspan=2)

        self.scale_saturation_min = Scale( o1, variable = self.var_saturation_min,command=self.maj_val_saturation_min,
                       orient=HORIZONTAL,resolution = 1,length=360,width= 15,sliderlength= 10, from_ = 0, to=360,
                       troughcolor='#85C1E9',bg='#ECF0F1',bd = 3,relief=FLAT,
                       showvalue=0)
        self.scale_saturation_min.set (self.val[3])
        self.scale_saturation_min.grid (row=i,column=2,columnspan=2)

        self.eti_val_saturation_min = Label(o1, text='saturation min')
        self.eti_val_saturation_min.grid (row=i,column=4,columnspan=2)

        i = i + 1

        #saturation max
        self.var_saturation_max = IntVar()

        eti_saturation_max = Label(o1, text='Saturation max')
        eti_saturation_max.grid (row=i,column=0,columnspan=2)

        self.scale_saturation_max = Scale( o1, variable = self.var_saturation_max,command=self.maj_val_saturation_max,
                       orient=HORIZONTAL,resolution = 1,length=360,width= 15,sliderlength= 10, from_ = 0, to=360,
                       troughcolor='#85C1E9',bg='#ECF0F1',bd = 3,relief=FLAT,
                       showvalue=0)
        self.scale_saturation_max.set (self.val[4])
        self.scale_saturation_max.grid (row=i,column=2,columnspan=2)

        self.eti_val_saturation_max = Label(o1, text='Saturation max')
        self.eti_val_saturation_max.grid (row=i,column=4,columnspan=2)

        i = i + 1

        #Saut de ligne
        Label(o1, text='').grid (row=i,column=2,columnspan=3)
        i = i + 1

        #lumiere min
        self.var_lumiere_min = IntVar()

        eti_lumiere_min = Label(o1, text='Lumiere min')
        eti_lumiere_min.grid (row=i,column=0,columnspan=2)

        self.scale_lumiere_min = Scale( o1, variable = self.var_lumiere_min,command=self.maj_val_lumiere_min,
                       orient=HORIZONTAL,resolution = 1,length=360,width= 15,sliderlength= 10, from_ = 0, to=360,
                       troughcolor='#85C1E9',bg='#ECF0F1',bd = 3,relief=FLAT,
                       showvalue=0)
        self.scale_lumiere_min.set (self.val[5])
        self.scale_lumiere_min.grid (row=i,column=2,columnspan=2)

        self.eti_val_lumiere_min = Label(o1, text='lumiere min')
        self.eti_val_lumiere_min.grid (row=i,column=4,columnspan=2)

        i = i + 1

        #lumiere max
        self.var_lumiere_max = IntVar()

        eti_lumiere_max = Label(o1, text='Lumiere max')
        eti_lumiere_max.grid (row=i,column=0,columnspan=2)

        self.scale_lumiere_max = Scale( o1, variable = self.var_lumiere_max,command=self.maj_val_lumiere_max,
                       orient=HORIZONTAL,resolution = 1,length=360,width= 15,sliderlength= 10, from_ = 0, to=360,
                       troughcolor='#85C1E9',bg='#ECF0F1',bd = 3,relief=FLAT,
                       showvalue=0)
        self.scale_lumiere_max.set (self.val[6])
        self.scale_lumiere_max.grid (row=i,column=2,columnspan=2)

        self.eti_val_lumiere_max = Label(o1, text='lumiere max')
        self.eti_val_lumiere_max.grid (row=i,column=4,columnspan=2)

        i = i + 1
        
                #--------------------------------------------------------------- La fenêtre caméra -----------------------------------------------------------------------------
        """
        # Créer le canvas
        self.cv = Canvas(o1)
        
        # Gère la taille selon la vidéo et l'emplacement du canvas
        self.cv = tkinter.Canvas(o1, width = self.vid.width, height = self.vid.height)
        self.cv.grid (row=i,column=0,columnspan=6)
        

        self.cv.bind("<Motion>",
                lambda event, a=self.cv:
                self.recup_pointer(a))
        self.cv.bind("<Button-1>", self.rec_point)

        #---------------------------------------------------------------  mise à jour frame------------------------------------------------------------------------------
         
        # After it is called once, the update method will be automatically called every delay milliseconds
        self.delay = 15
        self.update_mask()

    """
        #------------------------------------------------------------------------------------------------------------------------------------------------------
        #---------------------------------------------------------------  ONGLET CALAGE------------------------------------------------------------------------------
        #------------------------------------------------------------------------------------------------------------------------------------------------------
        
        #--------------------------------------------------------------- Gestion de la config------------------------------------------------------------------------------
        i = 0
        Eti_config_calage = Label(o2, text = "Choisir la configuration du calage :")
        Eti_config_calage.grid (row=i,column=0,columnspan=3)

        
        #Liste à charger dans la liste déroulante
        
        lst_config_calage=self.search_config("config_calage")
        print(" liste config de calage : "  + str(lst_config_calage))

        # 3) - Création de la Combobox via la méthode ttk.Combobox()
        Cmb_config_calage = ttk.Combobox(o2, values=lst_config_calage)
        Cmb_config_calage.grid (row=i,column=3,columnspan=2)
         
        # 4) - Choisir l'élément qui s'affiche par défaut
        Cmb_config_calage.current(0)

        #bouton pour sauvegarder les tracksbar en cours
        Btn_config_calage = Button(o2, text="sauvegarder les valeurs", command=self.save_config('toto'))
        Btn_config_calage.grid (row=i,column=5,columnspan=2)
        i = i + 1

        # saut de ligne
        Label(o2, text='').grid (row=i,column=2,columnspan=3)
        i = i + 1
        
        #bouton pour lancer la fenetre de géoréférencement (calage)
        
        Btn_calage = Button(o2, text="Lancer le calage géographique", command=self.LanceCalage)
        Btn_calage.grid (row=i,column=0,columnspan=3)
        Btn_config_position = Button(o2, text="récupérer position", command=self.affiche_coords)
        Btn_config_position.grid (row=i,column=1,columnspan=3)
        Btn_cal_man = Button(o2, text="Calage manuel (3 clics)", command=self.rec_point_manu)
        Btn_cal_man.grid (row=i,column=2,columnspan=3)
        i = i + 1
        print("fin creation bouton calage")
                # saut de ligne
        Label(o2, text='').grid (row=i,column=2,columnspan=3)
        i = i + 1
        
        #--------------------------------------------------------------- La fenêtre caméra -----------------------------------------------------------------------------
        
        
        # Créer le canvas
        self.cv = Canvas(o2)
        
        # Gère la taille selon la vidéo et l'emplacement du canvas
        self.cv = tkinter.Canvas(o2, width = self.vid.width, height = self.vid.height)
        self.cv.grid (row=i,column=0,columnspan=6)
        #------------------------------------------------------------------------------------------------------------------------------------------------------
        #---------------------------------------------------------------  ONGLET QUIZZ------------------------------------------------------------------------------
        #------------------------------------------------------------------------------------------------------------------------------------------------------
        
        #--------------------------------------------------------------- Gestion de l interface ------------------------------------------------------------------------------

        i = 0
        Eti_config_quizz = Label(o3, text = "Choix du quizz :")
        Eti_config_quizz.grid (row=i,column=0,columnspan=2)
        
        #Liste à charger dans la liste déroulante FONCTION A CREER
        lst_config_quizz=cr_liste_quizz("config.json")
        #print(" configuration de la detection : " + str(lst_config_detect))
        
        # Création de la Combobox via la méthode ttk.Combobox()
        self.Cmb_config_quizz = ttk.Combobox(o3, values=lst_config_quizz)
        self.Cmb_config_quizz.grid (row=i,column=3,columnspan=2)
        self.Cmb_config_quizz['state'] = 'readonly'
        
        #mise à jour des question en fonction du quizz
        self.Cmb_config_quizz.bind('<<ComboboxSelected>>',self.majquestions)
        
        # Choisir l'élément qui s'affiche par défaut
        self.Cmb_config_quizz.current(0)
        #print(self.Cmb_config_quizz.get())
        
        Btn_lancer_quizz = Button(o3,
                                  text="lancer quizz",
                                  command=lambda: self.lanceQuizz(self.Cmb_config_quizz.get()))
        Btn_lancer_quizz.grid(row=i,column=5,columnspan=2)
        i = i + 1
        
        # bouton question précédente
        Btn_question_prec = Button(o3, text="<<", command=self.questionprec)
        Btn_question_prec.grid (row=i,column=0,columnspan=2)
        
        # label no de question

        self.var_no_question = StringVar()
        try:
            mon_no = str(self.mon_quizz.question_courante + 1 )
            #print('essai')
        except:
            mon_no = "pas actif"
            #print('raté')
            
        self.var_no_question.set(mon_no)
        self.Eti_no_question = Label(o3, textvariable = self.var_no_question)
        self.Eti_no_question.grid (row=i,column=2,columnspan=1)
        
        i = i + 1
        
        # combobox questions
        self.lst_questions_quizz = []
        self.lst_questions_quizz = cr_liste_questions(self.Cmb_config_quizz.get(), self.configJson)
        
        self.Cmb_questions = ttk.Combobox(o3, values=self.lst_questions_quizz)
        self.Cmb_questions.grid (row=i,column=4,columnspan=2)
        self.Cmb_questions.current(0)
        self.Cmb_questions['state'] = 'readonly'
        
        #mise à jour des question en fonction du quizz
        
        # bouton question suivante
        Btn_question_suiv = Button(o3, text=">>", command=self.questionsuiv)
        Btn_question_suiv.grid(row=i,column=6,columnspan=2)
        i = i + 1
        
        # bouton lit question
        Btn_lit_question = Button(o3,
                                  text = "Dire la question",
                                  command=lambda: self.dispatch_touches("j",self.thread_detect.pos_latlong))
        Btn_lit_question.grid(row=i,column=1,columnspan=2)
        
        # bouton lit réponse
        Btn_lit_reponse = Button(o3,
                                 text = "Lire la réponse",
                                 command=lambda: self.dispatch_touches("k",self.thread_detect.pos_latlong))
        Btn_lit_reponse.grid(row=i,column=4,columnspan=2)
        
        # bouton envoi vers navisu
        Btn_navisu = Button(o3,
                            text = "Corrigé",
                            command =lambda : self.mon_quizz.gestion_navisu("response"))
        Btn_navisu.grid(row=i, column=6, columnspan=2)                    
        
        #bouton lance tracking on/off
        i = i + 1
        Btn_track = Button(o3,
                            text = "start/stop",
                            command=lambda: self.dispatch_touches("s",self.thread_detect.pos_latlong))
        Btn_track.grid(row=i,column=1,columnspan=2)
        
        # label etat du tracking
        boolTrack = self.testTracking()
        self.var_labelQuizz = StringVar()
        self.var_labelQuizz.set("Tracking : " + str(boolTrack))
        self.labelQuizz = Label(o3, textvariable = self.var_labelQuizz)
        self.labelQuizz.grid(row=i,column=3,columnspan=2)
        
        self.table_position = i + 1
        
        
        
        #---------------------------------------------------------------  mise à jour frame------------------------------------------------------------------------------
         
        # After it is called once, the update method will be automatically called every delay milliseconds
        self.delay = 15
        self.update_frame()
        

        
        # --------------------------------------------- Boucle ---------------------------------------
        self.window.mainloop()

        #------------------------------------------------------------------------------------------------------------------------------------------------------
        #---------------------------------------------------------------  FONCTIONS------------------------------------------------------------------------------
        #------------------------------------------------------------------------------------------------------------------------------------------------------

    #----------------------------------------------------------------Fonctions TracksBars-----------------------------------------------------------------------
        
    def majquestions(self,event):
        """
        mettre à jour la combobox des questions
        """
        #print("maj questions")
        self.lst_questions_quizz = cr_liste_questions(self.Cmb_config_quizz.get(), self.configJson)
        self.Cmb_questions['values'] = self.lst_questions_quizz
        self.Cmb_questions.current(0)

    def questionsuiv(self):
        if self.Cmb_questions.current() < len(self.lst_questions_quizz)-1:
            self.Cmb_questions.current(self.Cmb_questions.current() + 1 )
            
    def questionprec(self):
        if self.Cmb_questions.current() > 0:
            self.Cmb_questions.current(self.Cmb_questions.current() - 1 )
            
    def gest_keypress(self,event):
        print("test bind touche" + event.char)
        #ici envoyer vers dispatch fonctions avec les argurments tels que la postiion du bateau
        self.dispatch_touches(event.char,self.thread_detect.pos_latlong)

    def createTableQuestions(self):
        """
        créer la table des questions s'affiche au lancement du quizz quand on clique sur le bouton lancer quizz
        """
        recap_questions = self.mon_quizz.recap_questions
        rows = len(self.mon_quizz.recap_questions) + 1 
        cols = len(self.mon_quizz.recap_questions[0])
        self.table_questions = ttk.Treeview(self.o3)
        self.table_questions['columns'] = ('Question','Texte','résultat')
        
        self.table_questions.column("#0", width=0,  stretch=NO)
        self.table_questions.column('Question',anchor=CENTER, width=80)
        self.table_questions.column('Texte',anchor=CENTER,width=80)
        self.table_questions.column('résultat',anchor=CENTER,width=80)
        
        self.table_questions.heading('Question',text="No Question",anchor=CENTER)
        self.table_questions.heading('Texte',text="Intitulé",anchor=CENTER)
        self.table_questions.heading('résultat',text="Réponse donnée",anchor=CENTER)

        j = 0
        for i in self.mon_quizz.recap_questions:
            self.table_questions.insert(parent='',index='end',iid=j,text='',
                values=(i[0]+1,i[1],i[2]))
            j = j + 1
            
        self.table_questions.grid(row=self.table_position,column=2,columnspan=2)
        
    def lanceQuizz(self,quizz):
        # Si on est pas dans le mode jeu, alors on lance le quizz et on passe dans le mode jeu
        if self.mode_jeu == False:
            print("mode de jeu off, lancement du quizz")
            self.mon_quizz = Quizz(quizz,self.configJson)
            self.mon_quizz.gestion_navisu("read")
            self.mode_jeu = True
            self.var_no_question.set("question " + str(self.mon_quizz.question_courante +1 ))
            self.createTableQuestions()    
        # Si on est dans le mode jeu, alors vérifier que le nom du quizz courant
        # est le même que celui dans la combo : self.Cmb_config_quizz.get()
        #si non on redémarre un nouveau quizz sans oublier de tuer l'autre
        #si oui on continue
        elif self.mode_jeu == True:
            print("mode de jeu on, verification qu'on ne change pas de quizz")
            if not self.Cmb_config_quizz.get() == self.mon_quizz.quizz_name:
                print("changement de quizz")
                del self.mon_quizz
                self.mon_quizz = Quizz(quizz,self.configJson)
                self.mon_quizz.gestion_navisu("read")
                self.var_no_question.set("question " + str(self.mon_quizz.question_courante +1 ))
                self.createTableQuestions()

    def testTracking(self):
        try:
            if self.thread_navisu.execution:
                print("thread vers navisu existe")
                if self.thread_navisu.execution == True:
                    print("envoi en cours")
                    envoi = True
                else:
                    print("pas d envoi en cours")
                    envoi = False
            else:
                print("thread vers navisu existe pas, pas d'envoi en cours")
                envoi = False
                
        except:
            print("pas de thread")
            envoi = False
        return envoi
    
    def maj_table_question(self,question_courante):
        """
        mise a jour de la table du recapitulatif des question en fonction de la réponse
        self.table_questions à mettre à jour (Treeview)
        """
        recap = self.mon_quizz.recap_questions[question_courante]
        print(str(question_courante) + ' ' + str(recap))
        selected = question_courante
        self.table_questions.item(selected, values=(recap[0],recap[1],recap[2]))
        
    def dispatch_touches(self,touche,position):        
        if touche == 'i':
            reponse = interro_bdd('bionomie','bionomie','legende_co',position[0],position[1])
            print(str(reponse))
            it.lit_wav('./Interrogation/son/' + str(reponse) +".wav")
        elif touche == 'j' and self.mode_jeu == False:
            print('activation mode jeu, creation du quizz')
            nomQuizzALancer = self.Cmb_config_quizz.get()
            print(nomQuizzALancer)
            self.lanceQuizz(nomQuizzALancer)
        elif touche == 'j' and self.mode_jeu == True:
            print(touche, str(position),"posage question")
            self.mon_quizz.dit_question()
        elif touche == 'k' and self.mode_jeu == True:
            print(touche, str(position),"lit reponse question")
            self.mon_quizz.lit_reponse(position)
            self.questionsuiv()
            self.maj_table_question(self.mon_quizz.question_courante-1)
            self.var_no_question.set("question : " + str(self.mon_quizz.question_courante + 1))
        elif touche == 't':
            balise_proche = nearest_point(position)
            print(str(balise_proche))
            distance_min = distance(coordonnees[balise_proche[0]], position)
            distance_min = round(distance_min, 3) * 1000
            print(coordonnees[balise_proche[0]])
            print("Point tracké aux coordonnées :", position)
            print("balise la plus proche : ", balise_proche, "à ", str(distance_min), "m")
            it.say_it("\"" + balise_proche[0] + "\"")
        elif touche == 'a':
            print("affichages coordonnées")
            self.affiche_coords()
        elif touche == 'p':
            self.snapshot()
        elif touche == 'n':
            print("envoi position vers navisu")
            envoi_navisu(position)
        elif touche == 's':
            print("gestion tracking pour navisu")
            # si pas de variable thread_navisu alors on le lance sinon on le stoppe
            try:
                if self.thread_navisu.execution:
                    print("thread existe")
                    if self.thread_navisu.execution == True:
                        print("arret thread navisu etat : ", self.thread_navisu.execution)
                        self.thread_navisu.execution = False
                        self.thread_navisu.join(10)
                        print('fin thread termine')
                        self.var_labelQuizz.set("Tracking : False")
                    else:
                        print("lancement thread navisu etat : ", self.thread_navisu.execution)
                        self.thread_navisu = ToNavisu(self.thread_detect, self.host, self.port, self.cmd,self.origin, self.target)
                        self.thread_navisu.start()
                        self.var_labelQuizz.set("Tracking : True")
                else:
                    print("lancement thread navisu etat : ", self.thread_navisu.execution)
                    self.thread_navisu = ToNavisu(self.thread_detect, self.host, self.port, self.cmd,self.origin, self.target)
                    self.thread_navisu.start()
                    self.var_labelQuizz.set("Tracking : True")
            except:
                print("demarrage envoi data vers navisu")
                self.thread_navisu = ToNavisu(self.thread_detect, self.host, self.port, self.cmd,self.origin, self.target)
                self.thread_navisu.start()
                self.var_labelQuizz.set("Tracking : True")
            print("apres except navisu")
        elif touche == 'd':
            print("gestion majdb")
            # si pas de variable thread_navisu alors on le lance sinon on le stoppe
            try:
                if self.thread_todb.execution:
                    print("thread trouvé etat execution en debut de boucle: ", self.thread_todb.execution)
                    if self.thread_todb.execution == True:
                        print("arret thread todb etat : ", self.thread_todb.execution)
                        self.thread_todb.execution = False
                        self.thread_todb.join(10)
                        print('fin thread termine')
                    elif self.thread_todb.execution == False:
                        print("lancmeent thread todb etat : ", self.thread_todb.execution)
                        self.thread_todb = ToDb(self.thread_detect,'db_boat.sqlite','boat')
                        self.thread_todb.start()
                else:
                    print("lancement thread todb etat : ", self.thread_db.execution)
                    self.thread_todb = ToDb(self.thread_detect,'db_boat.sqlite','boat')
                    self.thread_todb.start()
            except:
                #traceback.print_exc() # pour afficher l'except quand ça marche pas
                print("demarrage envoi data vers todb")
                print("------------------------------")
                self.thread_todb = ToDb(self.thread_detect,'db_boat.sqlite','boat')
                self.thread_todb.start()
            print("apres except database")
            
        elif touche == 'y':
            balise_proche = nearest_point(position)
            print(str(balise_proche))
            distance_min = distance(coordonnees[balise_proche[0]], position)
            distance_min = round(distance_min, 3) * 1000
            print("Point tracké aux coordonnées :", position)
            direction = azimut(position, coordonnees[balise_proche[0]])
            #it.say_it("la balise la plus proche est" + balise_proche[0])
            print("\"" + "la balise la plus proche est " + balise_proche[0] + " elle se situe a " + str(distance_min) + " metres au " + str(direction) + "\"")           
            it.say_it("\"" + "la balise la plus proche est " + balise_proche[0] + " elle se situe a " + str(distance_min) + " metres au " + str(direction) + "\"")

            #it.say_it("la balise la plus proche est " + balise_proche[0] + "elle se situe a " + str(distance_min) +"metres au " + str(direction))
            #it.say_it("la balise la plus proche est " + balise_proche[0])

        else:
            print("touche non autorisée")

    def maj_val_teinte_min(self,valeur):
       if self.var_teinte_min.get() > self.var_teinte_max.get() :
          self.scale_teinte_max.set(self.var_teinte_min.get() + 10)
       self.maj_val('')

    def maj_val_teinte_max(self,valeur):
       if self.var_teinte_min.get() > self.var_teinte_max.get() :
          self.scale_teinte_min.set(self.var_teinte_max.get() - 10)
       self.maj_val('')

    def maj_val_saturation_min(self,valeur):
       if self.var_saturation_min.get() > self.var_saturation_max.get() :
          self.scale_saturation_max.set(self.var_saturation_min.get() + 10)
       self.maj_val('')

    def maj_val_saturation_max(self,valeur):
       if self.var_saturation_min.get() > self.var_saturation_max.get() :
          self.scale_saturation_min.set(self.var_saturation_max.get() - 10)
       self.maj_val('')

    def maj_val_lumiere_min(self,valeur):
       if self.var_lumiere_min.get() > self.var_lumiere_max.get() :
          self.scale_lumiere_max.set(self.var_lumiere_min.get() + 10)
       self.maj_val('')

    def maj_val_lumiere_max(self,valeur):
       if self.var_lumiere_min.get() > self.var_lumiere_max.get() :
          self.scale_lumiere_min.set(self.var_lumiere_max.get() - 10)
       self.maj_val('')

    def maj_val(self,valeur):
       self.eti_val_teinte_min.config(text = self.var_teinte_min.get())#Mise à jour de la valeur Teinte Min
       self.eti_val_teinte_max.config(text = self.var_teinte_max.get())#Mise à jour de la valeur Teinte max
       self.eti_val_saturation_min.config(text = self.var_saturation_min.get())#Mise à jour de la valeur Saturation min
       self.eti_val_saturation_max.config(text = self.var_saturation_max.get())#Mise à jour de la valeur Saturation max
       self.eti_val_lumiere_min.config(text = self.var_lumiere_min.get())#Mise à jour de la valeur Lumiere min
       self.eti_val_lumiere_max.config(text = self.var_lumiere_max.get())#Mise à jour de la valeur Lumiere max
       
       lst_val = [self.var_teinte_min.get(),self.var_teinte_max.get(),
                  self.var_saturation_min.get(),self.var_saturation_max.get(),
                  self.var_lumiere_min.get(),self.var_lumiere_max.get()]
       self.thread_detect.get_trackbar_param(lst_val)
       #print(lst_val)

    #----------------------------------------------------------------Fonctions Config----------------------------------------------------------------------

    #
    def search_config(self,type_config):
        # gère la connection à la BDD SQLITE + l'extension spatiale  
        marequete = 'SELECT nom_config FROM ' + str(type_config)
        
        conn = sqlite3.connect('config/config.sqlite')
        cur = conn.cursor()
        cur.execute(marequete)
        lignes = cur.fetchall()
        configurations = []
        if len(lignes) > 0 :
            for i in lignes:
                    configurations.append(i[0])
            return configurations
        #else:
        #    return 0

    def load_config (self,type_config):
        fichierconfig = open(self.rep_config+self.file_config, "r")
        for ligne in fichierconfig:
            if type_config in ligne:
                lst_config=ligne.split(';')
                self.var_teinte_min2 = lst_config[1]
        fichierconfig.close()
        return lst_config
       
    def save_config (self,type_config):
        print("type_config")
        
    def affiche_coords (self):
        print("position bateau x,y : ", self.thread_detect.pos)
        print("position bateau : ",self.thread_detect.pos_latlong)
        
    def LanceCalage(self):
        """
        crée une fenêtre pour le calage
        fonction recup_pointer quand le curseur bouge
        fonction rec_point au clic
        """
        print("lancement du calage")
        frame = self.thread_detect.frame_export
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        size = (self.vid.width, self.vid.height)
        print(size[0],size[1])
        
        fenetre_calage = Toplevel(self.root)
        fenetre_calage.title("Fenetre de Calage")
        
                
        
        mon_canvas = Canvas(fenetre_calage)
        
        mon_canvas.bind("<Motion>",
                lambda event, a=mon_canvas:
                self.recup_pointer(a))
        
        mon_canvas.bind("<Button-1>", self.rec_point)
        mon_canvas.pack(side='top', fill='both', expand='yes')
        
        mon_canvas.configure(width=size[0], height=size[1]) # 
        self.photo1 = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
        mon_canvas.create_image(0, 0, image = self.photo1, anchor = tkinter.NW)

    #----------------------------------------------------------------Fonctions Video -----------------------------------------------------------------------
            
    def snapshot(self):
        # Get a frame from the video source
        print("clic")
        frame = self.vid.get_frame()
        nom_snap = "frame-" + time.strftime("%d-%m-%Y-%H-%M-%S") + ".jpg"
        cv2.imwrite( nom_snap, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
        return(nom_snap)

    def update_frame(self):
        # Get a frame from the video source
        frame = self.vid.get_frame()

        self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
        self.cv.create_image(0, 0, image = self.photo, anchor = tkinter.NW)

        self.window.after(self.delay,self.update_frame)
    
    def update_mask(self):
        # Get a frame from the video source
        mask = self.vid.get_mask()

        self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(mask))
        self.cv.create_image(0, 0, image = self.photo, anchor = tkinter.NW)

        self.window.after(self.delay,self.update_mask)

    def rec_point_manu(self):
        """
        fonction pour enregistrer les 3 points de calage
        on positionne le bateau, et on clique sur le bouton pour enregistrer le point de calage.
        """
        print("calage manuel")
        #print("point clic", self.x,self.y)
        if self.nb_pts_cales == 0 :
            self.point_calage1 = self.thread_detect.pos
            self.nb_pts_cales = self.nb_pts_cales + 1
            print("1 points enregistré : ",self.point_calage1, self.point_calage2, self.point_calage3)
        elif self.nb_pts_cales == 1 :
            self.point_calage2 = self.thread_detect.pos
            self.nb_pts_cales = self.nb_pts_cales + 1
            print("2 points enregistrés : ",self.point_calage1, self.point_calage2, self.point_calage3)
        elif self.nb_pts_cales == 2 :
            self.point_calage3 = self.thread_detect.pos
            self.nb_pts_cales = self.nb_pts_cales + 1
            print("3 points enregistrés : ",self.point_calage1, self.point_calage2, self.point_calage3)
            print("lancemenent du calage")
            self.coeffs = det_coeffs((coordonnees_cal["1"],self.point_calage1),(coordonnees_cal["2"],self.point_calage2),(coordonnees_cal["3"],self.point_calage3))
            self.thread_detect.coeffs = self.coeffs
            print("coeffs : ", self.coeffs)
        else :
            self.point_calage1 = self.thread_detect.pos
            self.point_calage2 = 0,0
            self.point_calage3 = 0,0
            self.nb_pts_cales = 1
            print("1 points enregistré : ",self.point_calage1, self.point_calage2, self.point_calage3)

    def rec_point(self,event):
        """
        fonction pour enregistrer les 3 points de calage
        à chaque clic de la souris on enregistre la position de la souris.
        """
        print("calage souris")
        #print("point clic", self.x,self.y)
        if self.nb_pts_cales == 0 :
            self.point_calage1 = self.x,self.y
            self.nb_pts_cales = self.nb_pts_cales + 1
            print("1 points enregistré : ",self.point_calage1, self.point_calage2, self.point_calage3)
        elif self.nb_pts_cales == 1 :
            self.point_calage2 = self.x,self.y
            self.nb_pts_cales = self.nb_pts_cales + 1
            print("2 points enregistrés : ",self.point_calage1, self.point_calage2, self.point_calage3)
        elif self.nb_pts_cales == 2 :
            self.point_calage3 = self.x,self.y
            self.nb_pts_cales = self.nb_pts_cales + 1
            print("3 points enregistrés : ",self.point_calage1, self.point_calage2, self.point_calage3)
            print("lancemenent du calage")
            self.coeffs = det_coeffs((coordonnees_cal["1"],self.point_calage1),(coordonnees_cal["2"],self.point_calage2),(coordonnees_cal["3"],self.point_calage3))
            self.thread_detect.coeffs = self.coeffs
            print("coeffs : ", self.coeffs)
        else :
            self.point_calage1 = self.x,self.y
            self.point_calage2 = 0,0
            self.point_calage3 = 0,0
            self.nb_pts_cales = 1
            print("1 points enregistré : ",self.point_calage1, self.point_calage2, self.point_calage3)
    
    def recup_pointer(self,cv):
        """
        récupération de la coordonnée du curseur dans la fenetre en ppixel x,y
        """
        self.x, self.y = self.root.winfo_pointerxy() #position dans la fenêtre du pc
        
        #print("position fnetre pc : ", self.x, self.y)
        #self.x,self.y = cv.canvasx(self.x),cv.canvasy(self.y) # positions dans le canvas

        self.x = self.x - cv.winfo_rootx() #position dans la fenêtre root
        self.y = self.y - cv.winfo_rooty()
        #self.x = self.x - cv.winfo_pointerx()
        #self.y = self.y - cv.winfo_pointery()
        #print("position avec canvasx : ",self.x, self.y)
        return(self.x, self.y)



class MyVideoCapture:
    """
    Classe pour la capture video. Inserer le code opencv ici. En fait il est dans le thread
    """
    
    def __init__(self, thread, video_source=-1):
        # Open the video source
        self.thread = thread
        
        # Get video source width and height
        self.width = thread.video_width
        self.height = thread.video_height

    def get_frame(self):
        frame = self.thread.frame_export
        return (cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    
    def get_mask(self):
        mask = self.thread.mask_export
        return (cv2.cvtColor(mask, cv2.COLOR_BGR2RGB))

    # Release the video source when the object is destroyed
    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()

# Création des threads

thread_1 = detection("1") # le 1 sert à rien
thread_1.start()
while not thread_1.detection_on: #attente que la caméra soit lancée
    pass
print('camera lancee')
#lancement de l'interface, le thread de detection doit tourner pour pouvoir lui passer les paramètres HSV
print('creation objet classe interface')
interface = InterfaceSmaug(tkinter.Tk(), "Smaug", thread_1)
print('lancement de l interface')

thread_1.join()

print('fin')

