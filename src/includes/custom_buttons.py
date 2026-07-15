from kivymd.uix.label import MDIcon
from kivy.uix.behaviors import ButtonBehavior
from kivymd.uix.behaviors import RectangularRippleBehavior

class CustomButton(ButtonBehavior, RectangularRippleBehavior, MDIcon):

    def __init__(self, **kwargs):
        super(CustomButton, self).__init__(**kwargs)
        

    