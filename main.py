import os
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window  # 모바일 화면 크기 설정 (테스트용) 실제 앱 빌드에서는 주석처리해야 한다.
from firebase_admin import credentials, initialize_app

from screens.login_screen import LoginScreen
from screens.home_screen import HomeScreen
from screens.signup_screen import SignupScreen

Window.size = (300, 600)

class FirebaseApp(App):
    def build(self):
        # Firebase 초기화
        cred_path = os.path.join(os.path.dirname(__file__), 'firebase', 'serviceAccountKey.json')
        cred = credentials.Certificate(cred_path)
        initialize_app(cred, {
            'databaseURL': 'https://bank-a752e-default-rtdb.firebaseio.com'
        })

        self.screen_manager = ScreenManager()
        self.screen_manager.add_widget(LoginScreen(name='login'))
        self.screen_manager.add_widget(SignupScreen(name='signup'))
        self.screen_manager.add_widget(HomeScreen(name='home'))

        return self.screen_manager

if __name__ == '__main__':
    FirebaseApp().run()
