import os
import threading
import time
from queue import PriorityQueue, Empty

import boto3
import pyaudio
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window  # 모바일 화면 크기 설정 (테스트용) 실제 앱 빌드에서는 주석처리해야 한다.
from firebase_admin import credentials, initialize_app, db  # db 객체 가져오기

from SRCV_Bank.screens.face_auth_screen import FaceAuthScreen
from SRCV_Bank.screens.info_screen import InfoScreen
from SRCV_Bank.screens.phone_auth_screen import PhoneAuthScreen
from SRCV_Bank.screens.start_screen import StartScreen
from SRCV_Bank.screens.transfer_complete_screen import TransferCompleteScreen
from screens.transfer_fv_screen import transfer_FV_screen
from screens.login_screen import LoginScreen
from screens.home_screen import HomeScreen
from screens.auth_screen import AuthScreen
from screens.auth_complete_screen import AuthCompleteScreen
from screens.signup_screen import SignupScreen
from screens.transfer_screen import TransferScreen
from screens.signup_verification_screen import SignupVerification
from screens.login_fv_screen import login_FV_screen
from kivy.uix.camera import Camera
from screens.test import test_screen
Window.size = (300, 600)
from dotenv import load_dotenv

load_dotenv()
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

        # polly 초기화
        self.polly = boto3.client('polly', region_name='us-east-1',#AWS_REGION
                                  aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),#AWS_ACCESS_KEY_ID
                                  aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'))#AWS_SECRET_ACCESS_KEY
        # 오디오 초기화
        self.audio = pyaudio.PyAudio()
        # 현재 상태
        self.current_stream = None
        self.current_thread = None
        self.stop_flag = threading.Event()
        self.lock = threading.Lock()

        # ScreenManager 설정
        self.screen_manager = ScreenManager()
        self.screen_manager.add_widget(StartScreen(name='start'))
        self.screen_manager.add_widget(LoginScreen(name='login'))
        self.screen_manager.add_widget(PhoneAuthScreen(name='phone_auth'))
        self.screen_manager.add_widget(FaceAuthScreen(name='face_auth'))
        self.screen_manager.add_widget(SignupScreen(name='signup'))
        self.screen_manager.add_widget(HomeScreen(name='home'))
        self.screen_manager.add_widget(TransferScreen(name='transfer'))
        self.screen_manager.add_widget(TransferCompleteScreen(name='transfer_complete'))
        self.screen_manager.add_widget(SignupVerification(name='signupVerification'))
        self.screen_manager.add_widget(AuthScreen(name='auth'))
        #self.screen_manager.add_widget(AuthCompleteScreen(name='auth_complete'))
        self.screen_manager.add_widget(login_FV_screen(name='loginVerification'))
        self.screen_manager.add_widget(transfer_FV_screen(name='transferVerification'))

        self.screen_manager.add_widget(InfoScreen(name='info'))



        return self.screen_manager

    def speak_text(self, message, on_complete=None):
        try:
            if self.current_thread and self.current_thread.is_alive():
                self.stop_flag.set()
                self.current_thread.join()
                self.stop_flag.clear()

            response = self.polly.synthesize_speech(
                Text=message,
                OutputFormat="pcm",
                VoiceId="Seoyeon"
            )
            audio_stream = response['AudioStream']

            self.current_thread = threading.Thread(target=self.play_audio, args=(audio_stream,))
            self.current_thread.start()
            if on_complete:
                threading.Thread(target=lambda: (self.current_thread.join(), on_complete())).start()
        except Exception as e:
            print(f'speak_text:{e}')

    def play_audio(self, audio_stream):
        with self.lock:
            if self.current_stream:
                self.current_stream.stop_stream()
                self.current_stream.close()
                self.current_stream = None

            stream = self.audio.open(
                format=self.audio.get_format_from_width(2),
                channels=1,
                rate=16000,
                output=True
            )
            self.current_stream = stream

            while not self.stop_flag.is_set():
                data = audio_stream.read(1024)
                if not data:
                    break
                stream.write(data)

            stream.stop_stream()
            stream.close()
            self.current_stream = None

    def on_stop(self):
        if self.camera:
            self.camera.play = False
            self.camera = None

        if self.audio:
            self.audio.terminate()
    def delay(self, dt):
        pass

if __name__ == '__main__':
    FirebaseApp().run()
