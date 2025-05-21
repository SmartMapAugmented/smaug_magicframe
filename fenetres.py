from balises import *
import tkinter as tk # Python 3 import
from fonctions import *

root = tk.Tk()

def my_function():
    #global name_point_1
    entry_name = my_entry.get()
    if entry_name not in coordonnees:
        print("nom entre inconnu : ", entry_name) 
    else:
        name_point_1 = entry_name
        print(entry_name)
        root.destroy()
        #do stuff with url_member

def cancel_funct():
    print("annulation ok")
    root.destroy()


def create_window():
    my_label = tk.Label(root, text = "Nom de la balise")
    my_label.grid(row = 0, column = 0)
    my_entry = tk.Entry(root)
    my_entry.grid(row = 0, column = 1)

    my_button = tk.Button(root, text = "Valider", command = my_function)
    my_button.grid(row = 1, column = 1)
    my_cancel = tk.Button(root, text = "Annuler", command = cancel_funct)
    my_cancel.grid(row = 1, column = 0)


    root.mainloop()