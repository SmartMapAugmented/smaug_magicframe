from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.graphics import Color, Ellipse, Rectangle
from kivy.core.window import Window
from kivy.properties import NumericProperty
from kivy.event import EventDispatcher
from kivy.lang import Builder


class CoordinateEventDispatcher(EventDispatcher):
    x = NumericProperty(0)
    y = NumericProperty(0)


class TouchInput(Widget):
    alpha = NumericProperty(0)  # Opacité complète (1 pour blanc)
    coordinates = CoordinateEventDispatcher()

    def __init__(self, **kwargs):
        super(TouchInput, self).__init__(**kwargs)
        self.bind(alpha=self.set_alpha)

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
        self.draw_touch_indicator(touch)

    def on_touch_move(self, touch):
        print("Touch move to ({}, {})".format(touch.x, touch.y))
        self.coordinates.x = touch.x
        self.coordinates.y = touch.y

    def on_touch_up(self, touch):
        print("Touch up at ({}, {})".format(touch.x, touch.y))
        self.coordinates.x = touch.x
        self.coordinates.y = touch.y

    def draw_touch_indicator(self, touch):
        with self.canvas:
            Color(1, 0, 0)  # Rouge
            Ellipse(pos=(touch.x - 10, touch.y - 10), size=(20, 20))


class TouchApp(App):
    def build(self):
        Window.fullscreen = 'auto'  # Fullscreen
        Window.clearcolor = (1, 1, 1, 1)  # White background (R, G, B, A)

        root = Builder.load_string("""
BoxLayout:
    Image:
        source: 'essai_jpg.jpg'
        allow_stretch: True
        keep_ratio: False
    TouchInput:
""")

        touch_input = root.children[0]
        print("Coordinates in TouchApp:", touch_input.get_coordinates())  # Appel de la méthode get_coordinates()

        return root


if __name__ == '__main__':
    TouchApp().run()
