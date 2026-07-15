from kivymd.uix.boxlayout import BoxLayout
from kivymd.uix.textfield import (
    MDTextField,
    MDTextFieldLeadingIcon,
    MDTextFieldHintText,
    MDTextFieldHelperText,
    MDTextFieldTrailingIcon,
    MDTextFieldMaxLengthText,
)

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
            tb = MDTextField(
                    MDTextFieldLeadingIcon(icon='function',),
                    multiline = False, 
                    size_hint_y = None, 
                    on_text_validate = self.on_enter, 
                    mode = 'outlined'
            )
            
            self.textbox_dict.update({tb: tb.text})
            self.add_widget(tb)
            
    
    def on_enter(self, textbox):
        old_function = self.textbox_dict[textbox]
        new_function = textbox.text

        print(f'Old : {old_function}\nNew: {new_function}')

        if new_function == old_function:
            return

        if old_function:
            self.ccs_obj.current_functions.remove(old_function)    

        self.ccs_obj.current_functions.append(new_function)
        self.textbox_dict.update({textbox: new_function})


    def on_size(self, *args):
        print(self.ccs_obj)

    