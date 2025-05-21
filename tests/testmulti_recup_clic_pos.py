from tkinter import *
from threading import Thread
from time import sleep


x = 0
y = 0

#creation classe thread fenetre
class fenetre(Thread):
    """ Un thread qui lit la position de la souris et l'affiche dans la fenêtre
        et qui remplit les variables x et y de la classe
    """

    # a la creation, lit l'argument donné (nomThread)
    def __init__(self, nomThread):
        Thread.__init__(self)
        self.nomThread = nomThread
        # definition des variables de la classe. nom_delobjet.x pour y accéder en dehors
        self.x = 0
        self.y = 0


    def fonc4(self,event):
        self.chaine.configure(text = str(self.fen.winfo_pointerxy()))
        self.x, self.y = self.fen.winfo_pointerxy() #position dans la fenêtre du pc
        self.x = self.x - self.fen.winfo_rootx() #position dans la fenêtre
        self.y = self.y - self.fen.winfo_rooty()

    def run(self):
        
        self.fen = Tk()
        self.cadre = Frame(self.fen, width =500, height =150, bg="yellow")

        self.cadre.bind("<Motion>", self.fonc4)
         
        self.cadre.pack()
        self.chaine = Label(self.fen, text = "VIDE")
        self.chaine.pack()
         
        self.fen.mainloop()
        print("fin ",self.nomThread)


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
