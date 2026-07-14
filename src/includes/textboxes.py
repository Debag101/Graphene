from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.properties import (
    NumericProperty, 
    ObjectProperty)

from includes.ccs import CartesianCoordinateSystem as c

class TextBoxes(BoxLayout):

    box_count = NumericProperty()
    ccs_obj = ObjectProperty()
    textbox_dict = dict()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.box_count = 1
        self.draw_text_boxes()


    def draw_text_boxes(self):
        for _ in range(self.box_count):
            tb = TextInput(text='Enter Function',
                           multiline=False, 
                           on_text_validate=self.on_enter, 
                           size_hint_y = None)
            
            self.textbox_dict.update({tb: tb.text})
            self.add_widget(tb)
            
    
    def on_enter(self, textbox):
        old_function = self.textbox_dict[textbox]

        if not old_function:
            return 
        
        new_function = textbox.text

        if new_function == old_function:
            return
        
        if old_function != 'Enter Function':
            self.ccs_obj.current_functions.remove(old_function)
            
        self.ccs_obj.current_functions.append(new_function)
        self.textbox_dict.update({textbox: new_function})

        print('here', self.ccs_obj.current_functions)


    # def on_text(self, *args):
    #     # print('On Text : ', args)
    #     pass

    def on_size(self, *args):
        print(self.ccs_obj)

    