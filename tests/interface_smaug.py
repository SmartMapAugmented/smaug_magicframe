from tkinter import *
from tkinter import ttk, Button, Canvas
from PIL import Image, ImageTk
import os
from multithread_detect import detection


#---------variables generales
rep_config = 'config/'
file_logo = 'logo.png'
file_config = 'config.txt'



#---------Paramétrage des trackbars
def maj_val_teinte_min(valeur):
   if var_teinte_min.get() > var_teinte_max.get() :
      scale_teinte_max.set(var_teinte_min.get() + 10)
   maj_val('')

def maj_val_teinte_max(valeur):
   if var_teinte_min.get() > var_teinte_max.get() :
      scale_teinte_min.set(var_teinte_max.get() - 10)
   maj_val('')

def maj_val_saturation_min(valeur):
   if var_saturation_min.get() > var_saturation_max.get() :
      scale_saturation_max.set(var_saturation_min.get() + 10)
   maj_val('')

def maj_val_saturation_max(valeur):
   if var_saturation_min.get() > var_saturation_max.get() :
      scale_saturation_min.set(var_saturation_max.get() - 10)
   maj_val('')

def maj_val_lumiere_min(valeur):
   if var_lumiere_min.get() > var_lumiere_max.get() :
      scale_lumiere_max.set(var_lumiere_min.get() + 10)
   maj_val('')

def maj_val_lumiere_max(valeur):
   if var_lumiere_min.get() > var_lumiere_max.get() :
      scale_lumiere_min.set(var_lumiere_max.get() - 10)
   maj_val('')

def maj_val(valeur):
   eti_val_teinte_min.config(text = var_teinte_min.get())#Mise à jour de la valeur Teinte Min
   eti_val_teinte_max.config(text = var_teinte_max.get())#Mise à jour de la valeur Teinte max
   eti_val_saturation_min.config(text = var_saturation_min.get())#Mise à jour de la valeur Saturation min
   eti_val_saturation_max.config(text = var_saturation_max.get())#Mise à jour de la valeur Saturation max
   eti_val_lumiere_min.config(text = var_lumiere_min.get())#Mise à jour de la valeur Lumiere min
   eti_val_lumiere_max.config(text = var_lumiere_max.get())#Mise à jour de la valeur Lumiere max
   
   lst_val = [var_teinte_min.get(),
                  var_teinte_max.get(),var_saturation_min.get(),
                  var_saturation_max.get(),var_lumiere_min.get(),var_lumiere_max.get()]
   thread_1.get_trackbar_param(lst_val)
   print(lst_val)


#--------- Save config
#
def load_config (type_config):
    fichierconfig = open(rep_config+file_config, "r")
    for ligne in fichierconfig:
        if type_config in ligne:
            lst_config=ligne.split(';')
            var_teinte_min2 = lst_config[1]
    fichierconfig.close()
    return lst_config
   
def save_config (type_config):
    print(type_config)
    
    
    
root = Tk()

#variable i sert à positionner les éléments en vertical
i = 0

#---------------------------------------------------------------  Paramétrage de la fenetre ------------------------------------------------------------------
#Taille
root.title ("SMAUG")
root.geometry("1000x700")
root.configure(background='#ECF0F1')

#---------------------------------------------------------------  Bandeau SMAUG avec Nom + logo --------------------------------------------------------------
#Nom
eti_logo = Label(root, text='Smart Map AUGmented',font=("Cooper Black", 20))
eti_logo.grid (row=i,column=0,columnspan=4)


#Logo
logo = PhotoImage(file=rep_config + file_logo)
logo = logo.subsample(2, 2) 
Label(root, image=logo).grid(row=i,column=4,columnspan=2)

i = i + 1

a=Label(root, text='')
a.grid (row=i,column=0)
i = i + 1

#--------------------------------------------------------------- Les onglets ------------------------------------------------------------------------------
# Création du système d'onglets
Barre_onglet = ttk.Notebook(root)   
Barre_onglet.grid (row=i,column=0,columnspan=6)
i = i + 1

# Ajout de l'onglet 1 [gère la détection]
o1 = ttk.Frame(Barre_onglet)       
o1.grid (row=i,column=0,columnspan=5)
Barre_onglet.add(o1, text='Détection')

# Ajout de l'onglet 1 [gère le géoréferencement]
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
Btn_config = Button(o1, text="sauvegarder les valeurs", command=save_config('config_detect'))
Btn_config.grid (row=i,column=5,columnspan=2)
i = i + 1

# saut de ligne
Label(o1, text='').grid (row=i,column=2,columnspan=3)
i = i + 1
#--------------------------------------------------------------- Les scales bar ------------------------------------------------------------------------------

#load_trackbar_config ('defaut')
val= load_config ('defaut')
print(val)

#teinte_min
var_teinte_min = IntVar()

eti_teinte_min = Label(o1, text='Teinte Min')
eti_teinte_min.grid (row=i,column=0,columnspan=2)

scale_teinte_min = Scale( o1, variable = var_teinte_min,command=maj_val_teinte_min,
               orient=HORIZONTAL,resolution = 1,length=360,width= 15,sliderlength= 10, from_ = 0, to=360,
               troughcolor='#85C1E9',bg='#ECF0F1',bd = 3,relief=FLAT,
               showvalue=0)
scale_teinte_min.set (val[1])
scale_teinte_min.grid (row=i,column=2,columnspan=2)

eti_val_teinte_min = Label(o1, text='Teinte Min')
eti_val_teinte_min.grid (row=i,column=4,columnspan=2)

i = i + 1

#teinte max
var_teinte_max = IntVar()

eti_teinte_max = Label(o1, text='Teinte max')
eti_teinte_max.grid (row=i,column=0,columnspan=2)

scale_teinte_max = Scale( o1, variable = var_teinte_max,command=maj_val_teinte_max,
               orient=HORIZONTAL,resolution = 1,length=360,width= 15,sliderlength= 10, from_ = 0, to=360,
               troughcolor='#85C1E9',bg='#ECF0F1',bd = 3,relief=FLAT,
               showvalue=0)
scale_teinte_max.set (val[2])
scale_teinte_max.grid (row=i,column=2,columnspan=2)

eti_val_teinte_max = Label(o1, text='teinte max')
eti_val_teinte_max.grid (row=i,column=4,columnspan=2)

i = i + 1

#Saut de ligne
Label(o1, text='').grid (row=i,column=2,columnspan=3)
i = i + 1

#saturation min
var_saturation_min = IntVar()

eti_saturation_min = Label(o1, text='Saturation min')
eti_saturation_min.grid (row=i,column=0,columnspan=2)

scale_saturation_min = Scale( o1, variable = var_saturation_min,command=maj_val_saturation_min,
               orient=HORIZONTAL,resolution = 1,length=360,width= 15,sliderlength= 10, from_ = 0, to=360,
               troughcolor='#85C1E9',bg='#ECF0F1',bd = 3,relief=FLAT,
               showvalue=0)
scale_saturation_min.set (val[3])
scale_saturation_min.grid (row=i,column=2,columnspan=2)

eti_val_saturation_min = Label(o1, text='saturation min')
eti_val_saturation_min.grid (row=i,column=4,columnspan=2)

i = i + 1

#saturation max
var_saturation_max = IntVar()

eti_saturation_max = Label(o1, text='Saturation max')
eti_saturation_max.grid (row=i,column=0,columnspan=2)

scale_saturation_max = Scale( o1, variable = var_saturation_max,command=maj_val_saturation_max,
               orient=HORIZONTAL,resolution = 1,length=360,width= 15,sliderlength= 10, from_ = 0, to=360,
               troughcolor='#85C1E9',bg='#ECF0F1',bd = 3,relief=FLAT,
               showvalue=0)
scale_saturation_max.set (val[4])
scale_saturation_max.grid (row=i,column=2,columnspan=2)

eti_val_saturation_max = Label(o1, text='Saturation max')
eti_val_saturation_max.grid (row=i,column=4,columnspan=2)

i = i + 1

#Saut de ligne
Label(o1, text='').grid (row=i,column=2,columnspan=3)
i = i + 1

#lumiere min
var_lumiere_min = IntVar()

eti_lumiere_min = Label(o1, text='Lumiere min')
eti_lumiere_min.grid (row=i,column=0,columnspan=2)

scale_lumiere_min = Scale( o1, variable = var_lumiere_min,command=maj_val_lumiere_min,
               orient=HORIZONTAL,resolution = 1,length=360,width= 15,sliderlength= 10, from_ = 0, to=360,
               troughcolor='#85C1E9',bg='#ECF0F1',bd = 3,relief=FLAT,
               showvalue=0)
scale_lumiere_min.set (val[5])
scale_lumiere_min.grid (row=i,column=2,columnspan=2)

eti_val_lumiere_min = Label(o1, text='lumiere min')
eti_val_lumiere_min.grid (row=i,column=4,columnspan=2)

i = i + 1

#lumiere max
var_lumiere_max = IntVar()

eti_lumiere_max = Label(o1, text='Lumiere max')
eti_lumiere_max.grid (row=i,column=0,columnspan=2)

scale_lumiere_max = Scale( o1, variable = var_lumiere_max,command=maj_val_lumiere_max,
               orient=HORIZONTAL,resolution = 1,length=360,width= 15,sliderlength= 10, from_ = 0, to=360,
               troughcolor='#85C1E9',bg='#ECF0F1',bd = 3,relief=FLAT,
               showvalue=0)
scale_lumiere_max.set (val[6])
scale_lumiere_max.grid (row=i,column=2,columnspan=2)

eti_val_lumiere_max = Label(o1, text='lumiere max')
eti_val_lumiere_max.grid (row=i,column=4,columnspan=2)

i = i + 1


#------------------------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------  ONGLET CALAGE------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------------------------
nom_image = "cartesmaug.jpg"
im=Image.open(nom_image).convert("1") #pour conversion bmp
size = (im.width //8, im.height //8)
#print(size)

Photo=ImageTk.PhotoImage(im)
        
# adapters for tkinter
im1 = ImageTk.BitmapImage(im.resize(size))
im2 = ImageTk.PhotoImage(Image.open(nom_image).resize(size))


cv = Canvas(o2)
cv.grid (row=i,column=4,columnspan=6)

""" A GERER + les fonctions
cv.bind("<Motion>", self.fonc4)
cv.bind("<Button-1>", self.rec_point)
cv.pack(side='top', fill='both', expand='yes')
"""
cv.create_image(1, 1, image=im2, anchor='nw')
cv.configure(width=size[0], height=size[1]) # 


# Création des threads

thread_1 = detection("1") # le 1 sert à rien 
thread_1.start()
while not thread_1.detection_on: #attente que la caméra soit lancée
    pass

#lancement de l'interface, le thread de detection doit tourner pour pouvoir lui passer les paramètres HSV
print('lancement de l interface')
root.mainloop()
print('après main loop')
thread_1.join()