from kivymd.uix.boxlayout import BoxLayout
from kivymd.uix.textfield import (
    MDTextField,
    MDTextFieldLeadingIcon,
)
from kivymd.uix.button import MDIconButton
from kivymd.uix.boxlayout import MDBoxLayout

from kivy.properties import (
    NumericProperty, 
    ObjectProperty)

from includes.ccs import CartesianCoordinateSystem as c
from kivy.metrics import dp
import random

class TextBoxes(BoxLayout):

    box_count = NumericProperty()
    ccs_obj = ObjectProperty()
    textbox_dict = dict()
    GRAPH_COLORS = {
                (0.90, 0.16, 0.22, 1.0) : 0,  # Red
                (0.12, 0.53, 0.90, 1.0) : 0,  # Blue
                (0.13, 0.55, 0.13, 1.0) : 0,  # Forest Green
                (1.00, 0.55, 0.00, 1.0) : 0,  # Orange
                (0.50, 0.00, 0.50, 1.0) : 0,  # Purple
                (0.00, 0.75, 0.75, 1.0) : 0,  # Cyan
                (0.85, 0.10, 0.55, 1.0) : 0,  # Magenta
                (0.60, 0.40, 0.20, 1.0) : 0,  # Brown
                (0.00, 0.00, 0.00, 1.0) : 0,  # Black
                (0.50, 0.50, 0.50, 1.0) : 0   # Gray
        }
  

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.box_count = 1
        self.draw_text_boxes()


    def draw_text_boxes(self):

        min_use = min(self.GRAPH_COLORS.values())
        usable_colors = [color for color, use in self.GRAPH_COLORS.items() if use == min_use]
        color = random.choice(usable_colors)
        self.GRAPH_COLORS[color] += 1

        graph_color_button = MDIconButton(
                icon='graph',
                pos_hint={"center_y" : 0.7, "center_x" : 0.1},
                theme_bg_color='Custom',
                md_bg_color=color,
                theme_icon_color='Custom', 
                icon_color='white'
        )

        row_box = MDBoxLayout(
                orientation='horizontal', 
                size_hint_y=None, 
                height="60dp", 
                padding=[dp(12), dp(5), dp(12), dp(9)],
                spacing = dp(10)
        )

        textbox = MDTextField(
                MDTextFieldLeadingIcon(icon='function'), 
                multiline=False, 
                size_hint_y=None, 
                on_text_validate=self.on_enter, 
                mode='outlined', 
        )

        delete_button = MDIconButton(
                icon="close", 
                pos_hint={"center_y" : 0.7},
                on_release=lambda x: self.delete_box(row_box, textbox)
        )

        row_box.add_widget(graph_color_button)
        row_box.add_widget(textbox)
        row_box.add_widget(delete_button)

        self.textbox_dict[textbox] = {"function" : textbox.text, "color" : color}
        self.add_widget(row_box)

            
    
    def on_enter(self, textbox):
        old_function = self.textbox_dict[textbox]["function"]
        new_function = textbox.text

        if new_function == old_function:
            return

        functions = self.ccs_obj.current_functions.copy()

        if old_function in functions:
            color = functions[old_function]
            self.GRAPH_COLORS[color] -= 1
            del functions[old_function]  


        if new_function:
            functions[new_function] = self.textbox_dict[textbox]["color"]

        self.ccs_obj.current_functions = functions
        self.textbox_dict[textbox]["function"] = new_function


    def delete_box(self, rb, tb):
        tb.text = ''
        self.on_enter(tb)
        self.remove_widget(rb)

    def on_size(self, *args):
        print(self.ccs_obj)
