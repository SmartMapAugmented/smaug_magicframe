from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.graphics import Color, Ellipse, Rectangle
from kivy.core.window import Window
from kivy.properties import NumericProperty
from kivy.event import EventDispatcher
import os

from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window

os.environ['PATH'] = os.environ['PATH'] + ';.\\dll'

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
        # print("Touch down at ({}, {})".format(touch.x, touch.y))
        self.coordinates.x = touch.x
        self.coordinates.y = touch.y
        self.type = "down"
        self.draw_touch_indicator(touch)

    def on_touch_move(self, touch):
        # print("Touch move to ({}, {})".format(touch.x, touch.y))
        self.type = "move"
        self.coordinates.x = touch.x
        self.coordinates.y = touch.y

    def on_touch_up(self, touch):
        # print("Touch up at ({}, {})".format(touch.x, touch.y))
        self.type = "up"
        self.coordinates.x = touch.x
        self.coordinates.y = touch.y

    def draw_touch_indicator(self, touch):
        with self.canvas:
            Color(1, 0, 0)  # Rouge
            Ellipse(pos=(touch.x - 10, touch.y - 10), size=(20, 20))

class TouchApp(App):

    def build(self):
        self.x = 0
        self.y = 0
        self.type = ''
        Window.fullscreen = 'auto'  # Fullscreen
        Window.clearcolor = (1, 1, 1, 1)  # White background (R, G, B, A)
        layout = FloatLayout()

        root = Widget()
        image = Image(source='essai_jpg.jpg', allow_stretch=True, keep_ratio=False)
        layout.add_widget(image)
        touch_input = TouchInput()

        self.label = Label(text="Cliquez sur le bouton pour afficher Bonjour", size_hint=(0.75, 1),
                           pos_hint={'x': 0, 'y': 0})


        def on_button_click(self, instance):
            # Modifier le texte du libellé pour afficher "Bonjour"
            self.label.text = "Bonjour"

        button1 = Button(text="Bouton 1", size_hint=(0.25, 0.25), pos_hint={'right': 1, 'top': 0.75})
        button2 = Button(text="Bouton 2", size_hint=(0.25, 0.25), pos_hint={'right': 1, 'top': 0.5})
        button3 = Button(text="Bouton 3", size_hint=(0.25, 0.25), pos_hint={'right': 1, 'top': 0.25})



        # Ajouter le libellé et le bouton à la disposition en boîte
        layout.add_widget(self.label)
        layout.add_widget(button1)
        layout.add_widget(button2)
        layout.add_widget(button3)



        print("coordonnées 1: ",touch_input.x,touch_input.y)

        # Function to update image size when window size changes

        def update_image_size(instance, value):
            image.size = Window.size  # Set image size to window size
            image.pos = root.pos      # Set image position to root position
            touch_input.size = Window.size  # Set touch input size to window size
            touch_input.pos = root.pos      # Set touch input position to root position

        def update_coordinates(instance, value):
            self.x = touch_input.coordinates.x
            self.y = touch_input.coordinates.y
            self.type = touch_input.type
            print("Coordonnées du curseur :", self.x, self.y, self.type)



        # Bind update function to window size changes
        Window.bind(size=update_image_size)
        root.add_widget(image)
        root.add_widget(touch_input)
        touch_input = root.children[0]
        touch_input.coordinates.bind(x=update_coordinates, y=update_coordinates)


        return root


if __name__ == '__main__':
    TouchApp().run()
    print("fin")

