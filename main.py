import os
import pyttsx3 as pyttsx3
from kivy.app import App
from kivy.storage.jsonstore import JsonStore
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window  # 모바일 화면 크기 설정 (테스트용) 실제 앱 빌드에서는 주석처리해야 한다.
import firebase_admin
from firebase_admin import credentials, initialize_app, db  # db 객체 가져오기
from screens.login_screen import LoginScreen
from screens.home_screen import HomeScreen
from screens.auth_screen import AuthScreen
from screens.auth_complete_screen import AuthCompleteScreen
from screens.signup_screen import SignupScreen
from screens.transfer_screen import TransferScreen
from screens.signup_verification_screen import SignupVerification
from screens.second_verification_screen import SecondVerification
from kivy.uix.camera import Camera

Window.size = (300, 600)

class FirebaseApp(App):
    def build(self):
        # Firebase 초기화
        cred_path = os.path.join(os.path.dirname(__file__), 'firebase', 'serviceAccountKey.json')
        cred = credentials.Certificate(cred_path)
        initialize_app(cred, {
            'databaseURL': 'https://bank-a752e-default-rtdb.firebaseio.com'
        })

        # Camera 초기화
        self.camera = Camera(play=False, size_hint=(None, None))
        self.camera.size = Window.size
        # tts 초기화
        self.tts_engine = pyttsx3.init()

        def speak(message):
            self.tts_engine.say(message)
            # self.tts_engine.runAndWait()
            self.tts_engine.wait_for_completion()

        self.speak = speak

        # JsonStore 테스트
        self.store = JsonStore('setting.json')
        # 테스트용 put
        self.store.put('user', userid='test_id', test='test_info')  # put_test, userid/test_id 변경

        # ScreenManager 설정
        self.screen_manager = ScreenManager()
        self.screen_manager.add_widget(LoginScreen(name='login'))
        self.screen_manager.add_widget(AuthScreen(name='auth'))
        self.screen_manager.add_widget(AuthCompleteScreen(name='auth_complete'))
        self.screen_manager.add_widget(SignupScreen(name='signup'))
        self.screen_manager.add_widget(HomeScreen(name='home'))
        self.screen_manager.add_widget(TransferScreen(name='transfer'))
        self.screen_manager.add_widget(SignupVerification(name='signupVerification'))
        self.screen_manager.add_widget(SecondVerification(name='secondVerification'))

        return self.screen_manager

    def on_stop(self):
        if self.camera:
            self.camera.play = False
            self.camera = None

if __name__ == '__main__':
    FirebaseApp().run()
