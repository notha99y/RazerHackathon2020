from kivy.config import Config
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.app import MDApp
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.screen import MDScreen

from models import *

Config.set("graphics", "width", "375")
Config.set("graphics", "height", "812")
Config.write()

simple_db = Database()
# Builder.load_file('main.kv')
class LoginWindow(MDScreen):
    username = ObjectProperty(None)
    password = ObjectProperty(None)

    def loginBtn(self):
        if simple_db.validate(self.username.text):
            sm.current = "main"
            MainWindow.username = self.username.text
            self.reset()
            self.ids.username.error = False
        else:
            self.set_error_message("Invalid Login")

        

    def createBtn(self):
        self.reset()
        sm.current = "create"

    def set_error_message(self, instance_textfield):
        self.ids.username.error = True
        self.ids.username.helper_text = instance_textfield

    def reset(self):
        self.username.text = ""
        self.password.text = ""


class SignUpWindow(MDScreen):
    pass


class HomeWindow(MDScreen):
    pass


class SocialWindow(MDScreen):
    pass


class PaymentWindow(MDScreen):
    pass


class AcitivtyWindow(MDScreen):
    pass


class MoreWindow(MDScreen):
    pass


class MainWindow(MDScreen):
    created_field = ObjectProperty(None)
    username_field = ObjectProperty(None)
    # current = ""

    def logOut(self):
        sm.current = "login"

    def on_enter(self, *args):
        # password, name, created = db.get_user(self.current)
        created = "15 May 2020"

        self.username_field.text = "Username: " + self.username
        self.created_field.text = "Created On: " + created


class WindowManager(ScreenManager):
    pass


sm = WindowManager()


class MainApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Green"
        self.theme_cls.theme_style = "Dark"
        screens = [LoginWindow(name="login"), MainWindow(name="main")]
        for screen in screens:
            sm.add_widget(screen)

        sm.current = "login"

        return sm


if __name__ == "__main__":
    MainApp().run()
