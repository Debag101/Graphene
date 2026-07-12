from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.properties import (
    NumericProperty, 
    ObjectProperty)

from includes.ccs import CartesianCoordinateSystem as c

class TextBoxes(BoxLayout):

    box_count = NumericProperty()
    ccs_obj = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.box_count = 1
        print(f'inside {self.ccs_obj}')
        self.draw_text_boxes()


    def draw_text_boxes(self):
        for _ in range(self.box_count):
            tb = TextInput(text='Enter Function',
                           multiline=False, 
                           on_text_validate=self.on_enter)
            
            tb.bind(text=self.on_text)
            self.add_widget(tb)
            
    
    def on_enter(self, textbox):
        print('Function Entered')
        print(self.ccs_obj)


    def on_text(self, *args):
        # print('On Text : ', args)
        pass

    def on_size(self, *args):
        print(self.ccs_obj)

    