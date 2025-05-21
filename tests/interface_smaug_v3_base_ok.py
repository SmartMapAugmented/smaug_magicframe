import tkinter
from tkinter import ttk, Tk, Button, Canvas
from tkinter import *
import cv2
import PIL.Image, PIL.ImageTk
import time
import imutils
import os
from multithread_detect import detection

class App:
    """
    Classe pour l'interface. La définir dans le __init__
    """
    def __init__(self, window, window_title, video_source=-1):
        
        self.x = 0  # position x du curseur en pixel vers la droite
        self.y = 0  # position y du curseur en pixel vers le bas
        #points x,y des 3 points de calage
        self.point_calage1 = (0,0)
        self.point_calage2 = (0,0)
        self.point_calage3 = (0,0)
        self.nb_pts_cales = 0
        
        # fenetre principale  + titre provenant du lancement dans le main
        self.window = window
        self.window.title(window_title)
        # source video (picam -1)
        self.video_source = video_source

        # open video source (by default this will try to open the computer webcam)
        #classe MyVideoCapture
        self.vid = MyVideoCapture(self.video_source)
        """ original
        # Create a canvas that can fit the above video source size
        self.canvas = tkinter.Canvas(window, width = self.vid.width, height = self.vid.height)
        self.canvas.pack()
        ""
        # Button that lets the user take a snapshot
        self.btn_snapshot=tkinter.Button(window, text="Snapshot", width=50, command=self.snapshot)
        self.btn_snapshot.pack(anchor=tkinter.CENTER, expand=True)
        """
                #variable i sert à positionner les éléments en vertical
        i = 0
        self.rep_config = 'config/'
        self.file_logo = 'logo.png'
        self.file_config = 'config.txt'

        #---------------------------------------------------------------  Paramétrage de la fenetre ------------------------------------------------------------------
        #Taille
        self.root = window
        
        self.root.title ("SMAUG")
        self.root.geometry("1000x700")
        self.root.configure(background='#ECF0F1')

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
        #------------------------------------------------------------------------------------------------------------------------------------------------------
        #---------------------------------------------------------------  ONGLET DETECTION ------------------------------------------------------------------------------
        #------------------------------------------------------------------------------------------------------------------------------------------------------

        #--------------------------------------------------------------- Gestion de la config------------------------------------------------------------------------------

        Eti_config = Label(o1, text = "Choisir la configuration de détection :")
        Eti_config.grid (row=i,column=0,columnspan=3)

        #Liste à charger dans la liste déroulante FONCTION A CREER
        lst_config=["Défaut", "Bleu","Rouge","IR"]

        # 3) - Création de la Combobox via la méthode ttk.Combobox()
        Cmb_config = ttk.Combobox(o1, values=lst_config)
        Cmb_config.grid (row=i,column=3,columnspan=2)
         
        # 4) - Choisir l'élément qui s'affiche par défaut
        Cmb_config.current(0)

        #bouton pour sauvagarder les tracksbar en cours
        Btn_config = Button(o1, text="sauvegarder les valeurs", command=self.save_config('config_detect'))
        Btn_config.grid (row=i,column=5,columnspan=2)
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

        scale_teinte_min = Scale( o1, variable = self.var_teinte_min,command=self.maj_val_teinte_min,
                       orient=HORIZONTAL,resolution = 1,length=360,width= 15,sliderlength= 10, from_ = 0, to=360,
                       troughcolor='#85C1E9',bg='#ECF0F1',bd = 3,relief=FLAT,
                       showvalue=0)
        scale_teinte_min.set (self.val[1])
        scale_teinte_min.grid (row=i,column=2,columnspan=2)

        self.eti_val_teinte_min = Label(o1, text='Teinte Min')
        self.eti_val_teinte_min.grid (row=i,column=4,columnspan=2)

        i = i + 1

        #teinte max
        self.var_teinte_max = IntVar()

        eti_teinte_max = Label(o1, text='Teinte max')
        eti_teinte_max.grid (row=i,column=0,columnspan=2)

        scale_teinte_max = Scale( o1, variable = self.var_teinte_max,command=self.maj_val_teinte_max,
                       orient=HORIZONTAL,resolution = 1,length=360,width= 15,sliderlength= 10, from_ = 0, to=360,
                       troughcolor='#85C1E9',bg='#ECF0F1',bd = 3,relief=FLAT,
                       showvalue=0)
        scale_teinte_max.set (self.val[2])
        scale_teinte_max.grid (row=i,column=2,columnspan=2)

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

        scale_saturation_min = Scale( o1, variable = self.var_saturation_min,command=self.maj_val_saturation_min,
                       orient=HORIZONTAL,resolution = 1,length=360,width= 15,sliderlength= 10, from_ = 0, to=360,
                       troughcolor='#85C1E9',bg='#ECF0F1',bd = 3,relief=FLAT,
                       showvalue=0)
        scale_saturation_min.set (self.val[3])
        scale_saturation_min.grid (row=i,column=2,columnspan=2)

        self.eti_val_saturation_min = Label(o1, text='saturation min')
        self.eti_val_saturation_min.grid (row=i,column=4,columnspan=2)

        i = i + 1

        #saturation max
        self.var_saturation_max = IntVar()

        eti_saturation_max = Label(o1, text='Saturation max')
        eti_saturation_max.grid (row=i,column=0,columnspan=2)

        scale_saturation_max = Scale( o1, variable = self.var_saturation_max,command=self.maj_val_saturation_max,
                       orient=HORIZONTAL,resolution = 1,length=360,width= 15,sliderlength= 10, from_ = 0, to=360,
                       troughcolor='#85C1E9',bg='#ECF0F1',bd = 3,relief=FLAT,
                       showvalue=0)
        scale_saturation_max.set (self.val[4])
        scale_saturation_max.grid (row=i,column=2,columnspan=2)

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

        scale_lumiere_min = Scale( o1, variable = self.var_lumiere_min,command=self.maj_val_lumiere_min,
                       orient=HORIZONTAL,resolution = 1,length=360,width= 15,sliderlength= 10, from_ = 0, to=360,
                       troughcolor='#85C1E9',bg='#ECF0F1',bd = 3,relief=FLAT,
                       showvalue=0)
        scale_lumiere_min.set (self.val[5])
        scale_lumiere_min.grid (row=i,column=2,columnspan=2)

        self.eti_val_lumiere_min = Label(o1, text='lumiere min')
        self.eti_val_lumiere_min.grid (row=i,column=4,columnspan=2)

        i = i + 1

        #lumiere max
        self.var_lumiere_max = IntVar()

        eti_lumiere_max = Label(o1, text='Lumiere max')
        eti_lumiere_max.grid (row=i,column=0,columnspan=2)

        scale_lumiere_max = Scale( o1, variable = self.var_lumiere_max,command=self.maj_val_lumiere_max,
                       orient=HORIZONTAL,resolution = 1,length=360,width= 15,sliderlength= 10, from_ = 0, to=360,
                       troughcolor='#85C1E9',bg='#ECF0F1',bd = 3,relief=FLAT,
                       showvalue=0)
        scale_lumiere_max.set (self.val[6])
        scale_lumiere_max.grid (row=i,column=2,columnspan=2)

        self.eti_val_lumiere_max = Label(o1, text='lumiere max')
        self.eti_val_lumiere_max.grid (row=i,column=4,columnspan=2)

        i = i + 1


        #------------------------------------------------------------------------------------------------------------------------------------------------------
        #---------------------------------------------------------------  ONGLET CALAGE------------------------------------------------------------------------------
        #------------------------------------------------------------------------------------------------------------------------------------------------------
        nom_image = "cartesmaug.jpg"
        im=PIL.Image.open(nom_image).convert("1") #pour conversion bmp
        size = (im.width //8, im.height //8)
        #print(size)

        Photo=PIL.ImageTk.PhotoImage(im)
                
        # adapters for tkinter
        im1 = PIL.ImageTk.BitmapImage(im.resize(size))
        im2 = PIL.ImageTk.PhotoImage(PIL.Image.open(nom_image).resize(size))
        #im2 = PIL.ImageTk.PhotoImage(PIL.Image.open(self.thread.frame_export).resize(size))
        #im2 = Image.fromarray(self.thread.frame_export)
        #imgtk = ImageTk.PhotoImage(image=im2)
        
        self.cv = Canvas(o2)
        
        # Create a canvas that can fit the above video source size
        self.cv = tkinter.Canvas(o2, width = self.vid.width, height = self.vid.height)
        self.cv.pack()
        
        
        #cv.pack(side='top', fill='both', expand='no')
        #cv.grid (row=i,column=4,columnspan=6)
        #cv.bind("<Motion>", self.recup_pointer)
        """
        print("widget parents:",cv.winfo_parent())
        print("coord fenetre root : ", self.root.winfo_pointerxy())
        
        print("coord du canvas dans sa fenêtre : ", cv.winfo_rootx(), cv.winfo_rooty())
        print("coord du canvas  : ", cv.winfo_x(), cv.winfo_y())
        print("coord de l'onglet2  : ", o2.winfo_x(), o2.winfo_y())
        print("geometry de cv : ",cv.winfo_geometry())
        #print("coord de l'onglet2  : ", o2.winfo_x(), o2.winfo_y())
        """
        self.cv.bind("<Motion>",
                lambda event, a=self.cv:
                self.recup_pointer(a))
        #cv.create_image(1, 1, image=im2, anchor='nw')
        #cv.configure(width=size[0], height=size[1])
        self.cv.bind("<Button-1>", self.rec_point)
        
        # After it is called once, the update method will be automatically called every delay milliseconds
        self.delay = 15
        self.update()
        

        
        self.window.mainloop()

    def maj_val_teinte_min(self,valeur):
       if self.var_teinte_min.get() > self.var_teinte_max.get() :
          scale_teinte_max.set(self.var_teinte_min.get() + 10)
       self.maj_val('')

    def maj_val_teinte_max(self,valeur):
       if self.var_teinte_min.get() > self.var_teinte_max.get() :
          scale_teinte_min.set(self.var_teinte_max.get() - 10)
       self.maj_val('')

    def maj_val_saturation_min(self,valeur):
       if self.var_saturation_min.get() > self.var_saturation_max.get() :
          scale_saturation_max.set(self.var_saturation_min.get() + 10)
       self.maj_val('')

    def maj_val_saturation_max(self,valeur):
       if self.var_saturation_min.get() > self.var_saturation_max.get() :
          scale_saturation_min.set(self.var_saturation_max.get() - 10)
       self.maj_val('')

    def maj_val_lumiere_min(self,valeur):
       if self.var_lumiere_min.get() > self.var_lumiere_max.get() :
          scale_lumiere_max.set(self.var_lumiere_min.get() + 10)
       self.maj_val('')

    def maj_val_lumiere_max(self,valeur):
       if self.var_lumiere_min.get() > self.var_lumiere_max.get() :
          scale_lumiere_min.set(self.var_lumiere_max.get() - 10)
       self.maj_val('')

    def maj_val(self,valeur):
       self.eti_val_teinte_min.config(text = self.var_teinte_min.get())#Mise à jour de la valeur Teinte Min
       self.eti_val_teinte_max.config(text = self.var_teinte_max.get())#Mise à jour de la valeur Teinte max
       self.eti_val_saturation_min.config(text = self.var_saturation_min.get())#Mise à jour de la valeur Saturation min
       self.eti_val_saturation_max.config(text = self.var_saturation_max.get())#Mise à jour de la valeur Saturation max
       self.eti_val_lumiere_min.config(text = self.var_lumiere_min.get())#Mise à jour de la valeur Lumiere min
       self.eti_val_lumiere_max.config(text = self.var_lumiere_max.get())#Mise à jour de la valeur Lumiere max
       
       lst_val = [self.var_teinte_min.get(),
                      self.var_teinte_max.get(),self.var_saturation_min.get(),
                      self.var_saturation_max.get(),self.var_lumiere_min.get(),self.var_lumiere_max.get()]
       #thread_1.get_trackbar_param(lst_val)
       print(lst_val)


    #--------- Save config
    #
    def load_config (self,type_config):
        fichierconfig = open(self.rep_config+self.file_config, "r")
        for ligne in fichierconfig:
            if type_config in ligne:
                lst_config=ligne.split(';')
                self.var_teinte_min2 = lst_config[1]
        fichierconfig.close()
        return lst_config
       
    def save_config (self,type_config):
        print(type_config)
            
    def snapshot(self):
        # Get a frame from the video source
        ret, frame = self.vid.get_frame()

        if ret:
            cv2.imwrite("frame-" + time.strftime("%d-%m-%Y-%H-%M-%S") + ".jpg", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))

    def update(self):
        # Get a frame from the video source
        ret, frame = self.vid.get_frame()

        if ret:
            self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
            self.cv.create_image(0, 0, image = self.photo, anchor = tkinter.NW)

        self.window.after(self.delay, self.update)

    def rec_point(self,event):
        """
        fonction pour enregistrer les 3 points de calage  sur le clic de la souris
        """
        print("point clic", self.x,self.y)
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
        print("position fnetre pc : ", self.x, self.y)
        #self.x,self.y = cv.canvasx(self.x),cv.canvasy(self.y) # positions dans le canvas
        self.x = cv.canvasx(self.x)
        self.y = cv.canvasy(self.y)
        #self.x = cv.winfo_pointerx()
        #self.y = cv.winfo_pointery()
        print("position avec canvasx : ",self.x, self.y)
        return(self.x, self.y)
    
class MyVideoCapture:
    """
    Classe pour la capture video. Inserer le code opencv ici.
    """
    
    def __init__(self, video_source=-1):
        # Open the video source
        self.vid = cv2.VideoCapture(video_source)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)

        # Get video source width and height
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

    def get_frame(self):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret:
                # Return a boolean success flag and the current frame converted to BGR
                return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            else:
                return (ret, None)
        else:
            return (ret, None)

    # Release the video source when the object is destroyed
    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()

# Create a window ( tkinter.Tk() ) and pass it to the Application object
App(tkinter.Tk(), "Smaug")
print('coucou')