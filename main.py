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
from kivymd.uix.list import (
    IconLeftWidget,
    IRightBodyTouch,
    OneLineAvatarIconListItem,
    TwoLineIconListItem,
)
from kivymd.uix.screen import MDScreen
from kivymd.uix.selectioncontrol import MDCheckbox

from mambu import MambuAPI
from models import *

Config.set("graphics", "width", "375")
Config.set("graphics", "height", "812")
Config.write()

simple_db = Database()
mambu_api = MambuAPI()
# Builder.load_file('main.kv')
icons = list(md_icons.keys())


class ListItemWithCheckbox(OneLineAvatarIconListItem):
    """Custom list item."""

    icon = StringProperty("android")


class RightCheckbox(IRightBodyTouch, MDCheckbox):
    """Custom right container."""

    # count_id = ObjectProperty(None)

    # def __init__(self, count_id):
    #     super(RightCheckbox, self).__init__()


class ItemDrawer(TwoLineIconListItem):
    icon = StringProperty()


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


class PopAccountsWindows(MDFloatLayout):
    selected_account_id = ObjectProperty(None)
    def __init__(self, username):
        super(PopAccountsWindows, self).__init__()
        self.username = username
        self.accounts = simple_db.get_accounts(username)
        for account in self.accounts:
            self.ids.scroll.add_widget(
                ListItemWithCheckbox(
                        text="Account No: " + str(account.id) + " Owner:" + self.username,
                        icon="account",
                    )
            )
    def on_enter(self):
        widgets = list(self.ids.scroll.walk())
        cut_idx = 0
        for i, widget in enumerate(widgets):
            try:
                if widget.state == "down":
                    cut_idx = i
            except:
                continue
        account_no = ''
        for widget in widgets[:cut_idx]:
            try:
                if 'Account No: ' in widget.text:
                    account_no = widget.text[len('Account No: ')]

            except:
                continue
        sm.current = 'login'
        sm.current = 'main'
        screens[2].selected_account_id = account_no

class PopCollaborateWindow(MDFloatLayout):
    secondary_client_name = ObjectProperty(None)

    def __init__(self, account_id, username):
        super(PopCollaborateWindow, self).__init__()
        self.account_id = account_id
        self.account = (
            db.query(Account)
            .filter(Account.mambu_acc_id == self.account_id)
            .all()[0]
        )
        clients = db.query(Client).all()
        self.client_names = [
            client.first_name + " " + client.last_name for client in clients
        ]
        for client in clients:
            if client.first_name != username:
                self.ids.scroll.add_widget(
                    ListItemWithCheckbox(
                        text=client.first_name + " " + client.last_name,
                        icon="account",
                    )
                )

    def on_enter(self):
        widgets = list(self.ids.scroll.walk())
        cut_idx = 0
        for i, widget in enumerate(widgets):
            try:
                if widget.state == "down":
                    cut_idx = i
            except:
                continue
        secondary_client_name = ""
        for widget in widgets[:cut_idx]:
            try:
                if widget.text in self.client_names:
                    secondary_client_name = widget.text
            except:
                continue
        _secondary_client_name_first_name = secondary_client_name.split(" ")[
            :-1
        ]
        secondary_client_name_first_name = ""
        for name in _secondary_client_name_first_name:
            secondary_client_name_first_name += name + " "

        secondary_client_id = (
            db.query(Client)
            .filter(Client.first_name == secondary_client_name_first_name[:-1])
            .all()[0]
            .id
        )
        self.account.update_secondary_client_id(secondary_client_id)


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
                f"Welcome to Razer Bank!"
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


class MainWindow(MDScreen):
    def __init__(self, name, selected_account_id):
        super(MainWindow, self).__init__()
        self.selected_account_id = selected_account_id
        print('in init')
        print(self.selected_account_id)
    
    balance = ObjectProperty(None)

    def logOut(self):
        sm.current = "login"
        self.ids.balance.text = "$ 0"
        self.ids.list_container.clear_widgets()
        self.ids.collaborator.text = ''
        self.selected_account_id = None
    def comeHome(self):
        sm.current = "main"
        self.on_enter()

    def comeMore(self):
        sm.current = "more"
        MoreWindow.username = self.username

    def collaborateBtn(self):
        content = PopCollaborateWindow(self.account_id, self.username)
        popup_win = Popup(
            title="Collaborate with a Friend",
            content=content,
            size_hint=(0.95, 0.95),
        )
        popup_win.open()
        content.account_id = self.account_id

    def topUp(self):
        self.on_enter()
        content = PopTopUpWindow(self.account_id)
        popup_win = Popup(
            title="Top up", content=content, size_hint=(0.95, 0.8)
        )
        popup_win.open()

    def on_enter(self):
        self.ids.balance.text = "$ 0"
        self.ids.list_container.clear_widgets()
        self.ids.collaborator.text = ''
        accounts = simple_db.get_accounts(self.username)
        print(self.selected_account_id)
        print(self.username)
        if self.selected_account_id:
            accounts = db.query(Account).filter(Account.id ==self.selected_account_id).all()
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
            self.populate_enter(accounts)
        else:
            
            content = PopAccountsWindows(
                self.username
            )
            popup_win = Popup(
                title="Select your account",
                content=content,
                size_hint=(0.95, 0.95),
            )
            popup_win.open()

    def populate_enter(self, accounts):
        self.collaborator_id = accounts[0].secondary_client_id
        self.first_user_id = accounts[0].client_id
        # Assign account id
        self.account_id = accounts[0].mambu_acc_id
        # Get account details from mambu
        res = mambu_api.get_account(self.account_id).json()
        # Assign username to frontend
        self.ids.top_toolbar.title = self.username
        # Assign available balance to the frontend
        self.ids.balance.text = "$ " + res["availableBalance"]
        # Assign Collaborator in MDlabel
        if self.collaborator_id:
            collaborator_name = (
                db.query(Client)
                .filter(Client.id == self.collaborator_id)
                .all()[0]
                .first_name
            )
            first_username = db.query(Client).get(self.first_user_id).first_name
            self.ids.collaborator.text = (
                f"{first_username} sharing with {collaborator_name}"
            )

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


class WindowManager(ScreenManager):
    pass


sm = WindowManager()


class MainApp(MDApp):
    def build(self):
        global screens

        self.theme_cls.primary_palette = "Green"
        self.theme_cls.theme_style = "Dark"
        screens = [
            LoginWindow(name="login"),
            SignUpWindow(name="signup"),
            MainWindow(name="main", selected_account_id = None),
            MoreWindow(name="more"),
        ]
        for screen in screens:
            sm.add_widget(screen)

        sm.current = "login"

        return sm


if __name__ == "__main__":
    MainApp().run()
