import requests
from kivy.config import Config
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.app import MDApp
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.screen import MDScreen

from mambu import MambuAPI
from models import *

Config.set("graphics", "width", "375")
Config.set("graphics", "height", "812")
Config.write()

simple_db = Database()
mambu_api = MambuAPI()
# Builder.load_file('main.kv')


class PopUpWindow(MDFloatLayout):
    show_text = ObjectProperty(None)

    def __init__(self, display_text):
        super(PopUpWindow, self).__init__()
        self.ids.show_text.text = display_text


class SignUpWindow(MDScreen):
    first_name = ObjectProperty(None)
    last_name = ObjectProperty(None)
    nric = ObjectProperty(None)
    address = ObjectProperty(None)
    country_of_birth = ObjectProperty(None)
    razerID = ObjectProperty(None)

    def signupBtn(self):
        res = mambu_api.create_client(
            self.first_name.text,
            self.last_name.text,
            self.nric.text,
            self.address.text,
            self.country_of_birth.text,
            self.razerID.text,
        )

        if res.status_code == requests.codes.ok or res.status_code == requests.codes.created:
            self.reset()
            content = PopUpWindow(
                f"Welcome to Razer Bank, {self.first_name.text}!"
            )
            popup_win = Popup(
                title="Success", content=content, size_hint=(0.95, 0.2)
            )
            popup_win.open()
            sm.current = "login"
        else:
            self.set_error_message("Sign up fail =(")

    def gobackBtn(self):
        sm.current = 'login'

    def set_error_message(self, instance_textfield):
        content = PopUpWindow(
                "Sign Up fail =(, Please try again."
            )
        popup_win = Popup(
            title="Fail", content=content, size_hint=(0.95, 0.2)
        )
        popup_win.open()

        self.ids.first_name.error = True
        self.ids.first_name.helper_text = instance_textfield

    def reset(self):
        self.first_name.text = ''
        self.last_name.text = ''
        self.nric.text = ''
        self.address.text = ''
        self.country_of_birth.text = ''
        self.razerID.text = ''
        self.ids.first_name.error = False
        self.ids.first_name.helper_text = ''    


class LoginWindow(MDScreen):
    username = ObjectProperty(None)
    password = ObjectProperty(None)

    def loginBtn(self):
        if simple_db.validate(self.username.text):
            sm.current = "main"
            MainWindow.username = self.username.text
            self.reset()
        else:
            self.set_error_message("Invalid Login =(")

    def createBtn(self):
        self.reset()
        sm.current = "signup"

    def set_error_message(self, instance_textfield):
        content = PopUpWindow(
                "Login fail =(, Please try again."
            )
        popup_win = Popup(
            title="Fail", content=content, size_hint=(0.95, 0.2)
        )
        popup_win.open()
        self.ids.username.error = True
        self.ids.username.helper_text = instance_textfield

    def reset(self):
        self.username.text = ""
        self.password.text = ""
        self.ids.username.error = False
        self.ids.username.helper_text = ''


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
    # created_field = ObjectProperty(None)
    # username_field = ObjectProperty(None)
    balance = ObjectProperty(None)

    def logOut(self):
        sm.current = "login"
    
    def comeHome(self):
        sm.current = 'main'
    
    def comeMore(self):
        sm.current = 'more'
    def do_smth(self):
        print('Hi')
    def on_enter(self, *args):
        # password, name, created = db.get_user(self.current)
        accounts = simple_db.get_accounts(self.username)
        if len(accounts) == 0:
            content = PopUpWindow(
                f"Welcome {self.username}. Let's Begin by Creating a Saving Account"
            )
            popup_win = Popup(
                title="Create a Saving Account", content=content, size_hint=(0.95, 0.2)
            )
            popup_win.open()
        
            mambu_api.create_current_acc(simple_db.get_client_id(self.username))

            self.on_enter()
        elif len(accounts) == 1:
            res = mambu_api.get_account(accounts[0].mambu_acc_id).json()
            print(self.username)
            print('-'*88)
            self.ids.top_toolbar.title = self.username
            self.ids.balance.text = '$ ' + res['availableBalance']
        else:
            pass



class WindowManager(ScreenManager):
    pass


sm = WindowManager()

class MainApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Green"
        self.theme_cls.theme_style = "Dark"
        screens = [
            LoginWindow(name="login"),
            SignUpWindow(name="signup"),
            MainWindow(name="main"),
            MoreWindow(name="more"),
        ]
        for screen in screens:
            sm.add_widget(screen)

        sm.current = "login"

        return sm


if __name__ == "__main__":
    MainApp().run()
