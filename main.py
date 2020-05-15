from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.app import MDApp
from kivymd.uix.button import MDRectangleFlatButton


class LoginWindow(Screen):
    email = ObjectProperty(None)
    password = ObjectProperty(None)

    def loginBtn(self):
        # if db.validate(self.email.text, self.password.text):
        #     MainWindow.current = self.email.text
        #     self.reset()
        #     sm.current = "main"
        # else:
        #     invalidLogin()

        MainWindow.current = self.email.text
        self.reset()
        sm.current = "main"

    def createBtn(self):
        self.reset()
        sm.current = "create"

    def reset(self):
        self.email.text = ""
        self.password.text = ""


class HomeWindow(Screen):
    pass


class SocialWindow(Screen):
    pass


class PaymentWindow(Screen):
    pass


class AcitivtyWindow(Screen):
    pass


class MoreWindow(Screen):
    pass


class MainWindow(Screen):
    n = ObjectProperty(None)
    created = ObjectProperty(None)
    email = ObjectProperty(None)
    current = ""

    def logOut(self):
        sm.current = "login"

    def on_enter(self, *args):
        # password, name, created = db.get_user(self.current)
        name, created = "Ray Ow", "15 May 2020"
        self.n.text = "Account Name: " + name
        self.email.text = "Email: " + self.current
        self.created.text = "Created On: " + created


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
