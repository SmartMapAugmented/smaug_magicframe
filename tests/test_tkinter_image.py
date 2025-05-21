from tkinter import Tk, Button, Canvas
from PIL import Image, ImageTk
import imutils
import os



root = Tk()  
root.title("display image")  
nom_image = "cartesmaug.jpg"
im=Image.open(nom_image).convert("1") #pour conversion bmp
size = (im.width //8, im.height //8)
print(size)

photo=ImageTk.PhotoImage(im)

# penser à installer la lib python3-pil.imagetk
"""
cv = Canvas()  
cv.pack(side='top', fill='both', expand='yes')  
cv.create_image(1, 1, image=photo, anchor='nw')  
"""
# adapters for tkinter
im1 = ImageTk.BitmapImage(im.resize(size))
im2 = ImageTk.PhotoImage(Image.open(nom_image).resize(size))

cv = Canvas()  
cv.pack(side='top', fill='both', expand='yes')
cv.create_image(1, 1, image=im2, anchor='nw')
cv.configure(width=size[0], height=size[1]) # 

# These can be used everywhere Tkinter expects an image object marche pas
#Tk.label(root, image=im1, bd=10).grid(row=0, column=0)
#Tk.label(root, image=im2, bd=10).grid(row=0, column=1)


root.mainloop()

print('fin')


