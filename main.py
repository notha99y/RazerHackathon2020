import requests
from kivy.config import Config
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.app import MDApp
from kivymd.icon_definitions import md_icons
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.list import IconLeftWidget, TwoLineIconListItem
from kivymd.uix.screen import MDScreen

from mambu import MambuAPI
from models import *

Config.set("graphics", "width", "375")
Config.set("graphics", "height", "812")
Config.write()

simple_db = Database()
mambu_api = MambuAPI()
# Builder.load_file('main.kv')
icons = list(md_icons.keys())


class PopUpWindow(MDFloatLayout):
    show_text = ObjectProperty(None)

    def __init__(self, display_text):
        super(PopUpWindow, self).__init__()
        self.ids.show_text.text = display_text


class PopTopUpWindow(MDFloatLayout):
    topup_amount = ObjectProperty(None)

    def __init__(self, account_id):
        super(PopTopUpWindow, self).__init__()
        self.account_id = account_id

    def on_enter(self):
        mambu_api.deposit(self.account_id, self.topup_amount.text)


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

        if (
            res.status_code == requests.codes.ok
            or res.status_code == requests.codes.created
        ):
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
        sm.current = "login"

    def set_error_message(self, instance_textfield):
        content = PopUpWindow("Sign Up fail =(, Please try again.")
        popup_win = Popup(title="Fail", content=content, size_hint=(0.95, 0.2))
        popup_win.open()

        self.ids.first_name.error = True
        self.ids.first_name.helper_text = instance_textfield

    def reset(self):
        self.first_name.text = ""
        self.last_name.text = ""
        self.nric.text = ""
        self.address.text = ""
        self.country_of_birth.text = ""
        self.razerID.text = ""
        self.ids.first_name.error = False
        self.ids.first_name.helper_text = ""


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
        content = PopUpWindow("Login fail =(, Please try again.")
        popup_win = Popup(title="Fail", content=content, size_hint=(0.95, 0.2))
        popup_win.open()
        self.ids.username.error = True
        self.ids.username.helper_text = instance_textfield

    def reset(self):
        self.username.text = ""
        self.password.text = ""
        self.ids.username.error = False
        self.ids.username.helper_text = ""


class HomeWindow(MDScreen):
    pass


class SocialWindow(MDScreen):
    pass


class PaymentWindow(MDScreen):
    pass


class AcitivtyWindow(MDScreen):
    pass


class MoreWindow(MDScreen):
    def on_enter(self):
        self.ids.top_toolbar.title = self.username

    def logOut(self):
        sm.current = "login"

    def comeHome(self):
        sm.current = "main"

    def comeMore(self):
        sm.current = "more"


class ItemDrawer(TwoLineIconListItem):
    icon = StringProperty()


class MainWindow(MDScreen):
    # created_field = ObjectProperty(None)
    # username_field = ObjectProperty(None)
    balance = ObjectProperty(None)

    def logOut(self):
        sm.current = "login"

    def comeHome(self):
        sm.current = "main"
        self.on_enter()

    def comeMore(self):
        sm.current = "more"
        MoreWindow.username = self.username

    def topUp(self):
        content = PopTopUpWindow(self.account_id)
        popup_win = Popup(
            title="Top up", content=content, size_hint=(0.95, 0.8)
        )
        popup_win.open()

    def on_enter(self):
        # password, name, created = db.get_user(self.current)
        self.ids.balance.text = "$ 0"
        self.ids.list_container.clear_widgets()

        accounts = simple_db.get_accounts(self.username)
        if len(accounts) == 0:
            content = PopUpWindow(
                f"Welcome {self.username}. Let's Begin by Creating a Saving Account"
            )
            popup_win = Popup(
                title="Create a Saving Account",
                content=content,
                size_hint=(0.95, 0.2),
            )
            popup_win.open()

            mambu_api.create_current_acc(
                simple_db.get_client_id(self.username)
            )

        elif len(accounts) == 1:
            # Assign account id
            self.account_id = accounts[0].mambu_acc_id
            # Get account details from mambu
            res = mambu_api.get_account(self.account_id).json()
            # Assign username to frontend
            self.ids.top_toolbar.title = self.username
            # Assign available balance to the frontend
            self.ids.balance.text = "$ " + res["availableBalance"]

            # Get transactions
            res = mambu_api.get_all_transactions(self.account_id).json()
            if len(res) > 0:
                for transaction in res:
                    entry_date = transaction["entryDate"]
                    amount = transaction["amount"]
                    trans_type = transaction["type"]

                    if trans_type == "DEPOSIT":
                        icon = "cash"

                    else:
                        icon = "credit-card"

                    self.ids.list_container.add_widget(
                        ItemDrawer(
                            text=f"Amount: ${amount}",
                            secondary_text=f"Trans Date: {entry_date}",
                            icon="cash",
                        )
                    )

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
