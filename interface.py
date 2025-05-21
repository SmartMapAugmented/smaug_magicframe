from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from kivy.event import EventDispatcher
from kivy.properties import NumericProperty
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Rectangle
from kivy.clock import Clock

import os
from quizz import Quizz
from fonctions import calc_pos, charge_quizz



os.environ['PATH'] = os.environ['PATH'] + ';.\\dll'
configJson = "config.json"
mon_quizz = ''


def lanceQuizz(quizz):
    mon_quizz = ''
    mon_quizz = Quizz(quizz, configJson)

    return mon_quizz

class CoordinateEventDispatcher(EventDispatcher):
    x = NumericProperty(0)
    y = NumericProperty(0)

class TouchInput(Widget):
    alpha = NumericProperty(0)  # Opacité complète (1 pour blanc)
    coordinates = CoordinateEventDispatcher()

    def __init__(self, **kwargs):
        super(TouchInput, self).__init__(**kwargs)
        self.bind(alpha=self.set_alpha)
        self.type = 'down'

    def set_alpha(self, instance, value):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(1, 1, 1, self.alpha)  # Blanc
            Rectangle(pos=self.pos, size=self.size)

    def on_coordinates(self, instance, value):
        print("Coordinates:", self.coordinates.x, self.coordinates.y)

    def get_coordinates(self):
        return self.coordinates.x, self.coordinates.y

    def on_touch_down(self, touch):
        print("Touch down at ({}, {})".format(touch.x, touch.y))
        self.coordinates.x = touch.x
        self.coordinates.y = touch.y
        self.type = "down"
        self.draw_touch_indicator(touch)

    def on_touch_move(self, touch):
        print("Touch move to ({}, {})".format(touch.x, touch.y))
        self.type = "move"
        self.coordinates.x = touch.x
        self.coordinates.y = touch.y

    def on_touch_up(self, touch):
        print("Touch up at ({}, {})".format(touch.x, touch.y))
        self.type = "up"
        self.coordinates.x = touch.x
        self.coordinates.y = touch.y

    def draw_touch_indicator(self, touch):
        with self.canvas:
            Color(1, 0, 0)  # Rouge
            Ellipse(pos=(touch.x - 10, touch.y - 10), size=(20, 20))

class TouchApp(App):

    def build(self):

        self.actif = False

        def update_image_size(instance, value):
            image.size = Window.size  # Set image size to window size
            image.pos = root.pos      # Set image position to root position
            touch_input.size = Window.size  # Set touch input size to window size
            touch_input.pos = root.pos      # Set touch input position to root position
            self.max_x = Window.size[0] - Window.size[0]/4
            print("dans update image size",self.max_x)

        def update_coordinates(instance, value):
            self.max_x = Window.size[0] - Window.size[0] / 4
            if touch_input.coordinates.x < self.max_x:
                self.x = touch_input.coordinates.x
                self.y = touch_input.coordinates.y
                self.type = touch_input.type
                print("Coordonnées du curseur :", self.x, self.y, self.type, self.max_x)
            else:
                print('clic dans colonne bouton')

        def disable_button():
            # désactiver le bouton
            print("désactivation des boutons")
            button_lire.disabled = True
            button_dire.disabled = True
            button_mode.disabled = True

        def enable_button(dt):
            # Réactiver le bouton
            print("activation des boutons")
            button_lire.disabled = False
            button_dire.disabled = False
            button_mode.disabled = False

        def on_button_dire_click(instance):
            disable_button()
            Clock.schedule_once(enable_button, 5)
            print("valeur mon quizz : ", self.mon_quizz)
            # test si le quizz est lancé ou non. Si pas lancé alors on le lance pour eviter bug
            if self.mon_quizz == '':
                self.mon_quizz = lanceQuizz(self.nom_quizz)
            self.mon_quizz.dit_question()

        def on_button_lire_click(instance):
            disable_button()
            Clock.schedule_once(enable_button, 5)
            # test si le quizz est lancé ou non. Si pas lancé alors on le lance pour eviter bug
            if self.mon_quizz == '':
                self.mon_quizz = lanceQuizz(self.nom_quizz)

            self.label.text = "Lire la réponse"
            print("lecture aux coordonnées : ", self.x, self.y)
            position_pix = (self.x,self.y)
            # ici insérer la conversion pixel vers coord.
            # avant il faut caler : ok fait dans le quizz au démarrage a partir du config.json
            print(position_pix)
            print(self.mon_quizz.coeffs)
            position = calc_pos(position_pix,self.mon_quizz.coeffs)
            print("la position calculée est : ",position)

            print("etat bouton normalement True:",button_lire.disabled)
            self.label.text = "dire la question"
            # on lit la réponse
            self.mon_quizz.lit_reponse(position)
            #on attend qques seconde pour lancer test_timer qui et self.actif a True

        def on_button_mode_click(instance):
            self.label.text = "Lancement du quizz" + self.nom_quizz
            self.mon_quizz = lanceQuizz(self.nom_quizz)

        self.mon_quizz = ''
        self.nom_quizz = "europe_intermediaire" #la donnee est en 3857 car dans fonction
        self.nom_quizz = charge_quizz(configJson)
        self.configJson = configJson
        self.mode_jeu = False
        self.x = 0
        self.y = 0
        self.type = ''
        self.max_x = Window.size[0] - Window.size[0]/4 # remplacer par largeur de fenetre - 1/4 de celle-ci
        Window.fullscreen = 'auto'  # Mode plein écran automatique
        Window.clearcolor = (1, 1, 1, 1)  # Fond blanc (R, G, B, A)
        self.carte = "carte_europe_2024.jpg"

        # Créer un layout pour contenir les éléments de l'interface utilisateur
        layout = FloatLayout()

        # Ajouter une image à l'interface utilisateur
        image = Image(source=self.carte, allow_stretch=False, keep_ratio=True)
        image.pos_hint = {'x': 0, 'y': 0}
        layout.add_widget(image)

        touch_input = TouchInput()
        layout.add_widget(touch_input)

        # Créer un libellé pour afficher le message "Cliquez sur le bouton pour afficher Bonjour"
        self.label = Label(text="Cliquez sur le bouton pour afficher Bonjour", size_hint=(0.75, 1), pos_hint={'x': 0, 'y': 0})
        layout.add_widget(self.label)

        # Créer des boutons
        button_mode = Button(text="Lancer Quizz", size_hint=(0.23, 0.33), pos_hint={'right': 1, 'top': 1})
        button_lire = Button(text="Lire réponse", size_hint=(0.23, 0.33), pos_hint={'right': 1, 'top': 0.666667})
        button_dire = Button(text="Dire question", size_hint=(0.23, 0.33), pos_hint={'right': 1, 'top': 0.333333})

        button_dire.bind(on_press=on_button_dire_click)
        button_lire.bind(on_press=on_button_lire_click)
        button_mode.bind(on_press=on_button_mode_click)


        # Ajouter les boutons à l'interface utilisateur
        layout.add_widget(button_dire)
        layout.add_widget(button_lire)
        layout.add_widget(button_mode)

        touch_input.coordinates.bind(x=update_coordinates, y=update_coordinates)

        print("size : ", Window.size)
        return layout

if __name__ == '__main__':
    TouchApp().run()
