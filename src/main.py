from kivy.core.window import Window
from kivy.lang import Builder
from kivymd.app import MDApp

from includes import ccs


class GrapheneApp(MDApp):
    def build(self):
        self.theme_cls.material_style = "M3"
        Window.clearcolor = self.theme_cls.backgroundColor
        self.theme_cls.theme_style = "Light"
        kv = Builder.load_file("../design/style.kv")
        return kv


if __name__ == "__main__":
    app = GrapheneApp()
    app.run()
