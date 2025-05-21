from tkinter import Tk, Button, Canvas
from PIL import Image, ImageTk
import imutils
import os
from threading import Thread
from time import sleep





class fenetre(Thread):
    """ Un thread qui lit la position de la souris et l'affiche dans la fenêtre
        et qui remplit les variables x et y de la classe
    """

    # a la creation, lit l'argument donné (nomThread)
    def __init__(self, nomThread):
        Thread.__init__(self)
        self.nomThread = nomThread
        # definition des variables de la classe. nom_delobjet.x pour y accéder en dehors
        self.x = 0  # position x du curseur en pixel vers la droite
        self.y = 0  # position y du curseur en pixel vers le bas
        #points x,y des 3 points de calage
        self.point_calage1 = (0,0)
        self.point_calage2 = (0,0)
        self.point_calage3 = (0,0)
        self.nb_pts_cales = 0


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
        self.x = self.x - self.root.winfo_rootx() #position dans la fenêtre root
        self.y = self.y - self.root.winfo_rooty()
        
        #print("coordo dans canvas : ",cv.canvasx(self.root.winfo_rootx()),cv.canvasy(self.root.winfo_rooty()))
        #self.x,self.y = cv.canvasx(self.root.winfo_rootx()),cv.canvasy(self.root.winfo_rooty())
        #self.x,self.y = cv.canvasx(self.x),cv.canvasy(self.y) # positions dans le canvas
        print("coordonnees : ",self.x,self.y)
        return(self.x, self.y)

    def run(self):
        
        self.root = Tk()  
        self.root.title("display image")  
        nom_image = "cartesmaug.jpg"
        im=Image.open(nom_image).convert("1") #pour conversion bmp
        size = (im.width //8, im.height //8)
        print(size)

        photo=ImageTk.PhotoImage(im)
        
        # adapters for tkinter
        im1 = ImageTk.BitmapImage(im.resize(size))
        im2 = ImageTk.PhotoImage(Image.open(nom_image).resize(size))

        cv = Canvas()
        toto='coucou'
        cv.bind("<Motion>",
                lambda event, a=cv:
                self.recup_pointer(a))
        
        cv.bind("<Button-1>", self.rec_point)
        cv.pack(side='top', fill='both', expand='yes')
        #self.chaine = Label(self.root, text = "VIDE")
        #self.chaine.pack()
        cv.create_image(1, 1, image=im2, anchor='nw')
        cv.configure(width=size[0], height=size[1]) # 
        
        print("test coord canvas : ",cv.canvasx(self.root.winfo_rootx()),cv.canvasy(self.root.winfo_rooty()))
        # These can be used everywhere Tkinter expects an image object marche pas
        #Tk.label(root, image=im1, bd=10).grid(row=0, column=0)
        #Tk.label(root, image=im2, bd=10).grid(row=0, column=1)


        self.root.mainloop()
        
        
print("creation du thread")
fenetre1 = fenetre("thread 1") #fenetre1 est le thread
print("lancement du thread")
fenetre1.start()
print("le programme continue")
print("lancement d'une boucle pour printer la position du curseur toutes les secondes")
for i in range(20):
    print(fenetre1.x,fenetre1.y)
    sleep(1)

print("attente de l'arret du thread")
fenetre1.join()

print('fin')