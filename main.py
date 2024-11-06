import os
import threading
from queue import PriorityQueue, Empty

import pyttsx3
from kivy.app import App
from kivy.storage.jsonstore import JsonStore
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window  # 모바일 화면 크기 설정 (테스트용) 실제 앱 빌드에서는 주석처리해야 한다.
import firebase_admin
from firebase_admin import credentials, initialize_app, db  # db 객체 가져오기

from SRCV_Bank.screens.face_auth_screen import FaceAuthScreen
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
        self.tts_queue = PriorityQueue()
        self.is_speaking = False

        # Queue에서 메시지를 비동기로 처리할 스레드 시작
        threading.Thread(target=self._process_tts_queue, daemon=True).start()
        def speak(message, priority=1):
            if self.is_speaking:
                self.stop_speaking()
            self.tts_queue.put((priority, message))
        self.speak = speak

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
        self.screen_manager.add_widget(AuthCompleteScreen(name='auth_complete'))
        self.screen_manager.add_widget(login_FV_screen(name='loginVerification'))
        self.screen_manager.add_widget(transfer_FV_screen(name='transferVerification'))
        self.screen_manager.add_widget(test_screen(name='test_screen')) #테스트용
        return self.screen_manager

    def on_stop(self):
        if self.camera:
            self.camera.play = False
            self.camera = None
        if self.tts_engine:
            self.tts_engine.stop()
            self.tts_engine = None

    def _process_tts_queue(self):
        while True:
            try:
                #message = self.tts_queue.get(timeout=1)  # Queue에서 메시지 가져오기
                priority, message = self.tts_queue.get(timeout=1)
                self.is_speaking = True  # TTS 재생 중 표시
                self.tts_engine.say(message)
                self.tts_engine.runAndWait()
                self.is_speaking = False  # TTS 재생 완료 표시
                self.tts_queue.task_done()
            except Empty:
                continue  # 대기 중인 메시지가 없으면 루프 유지

    def _speak_async(self, message):
        if self.is_speaking:
            self.tts_engine.stop()  # 현재 TTS 중단
            self.is_speaking = False

    def stop_speaking(self):
        # pyttsx3는 직접적으로 멈추는 기능이 없지만, 비동기 스레드를 통해 정지 기능을 추가할 수 있음
        if self.is_speaking:
            self.tts_engine.stop()  # 현재 TTS 중단
            self.is_speaking = False

        # 큐 비우기
        while not self.tts_queue.empty():
            try:
                self.tts_queue.get_nowait()
                self.tts_queue.task_done()
            except Empty:
                break

if __name__ == '__main__':
    FirebaseApp().run()
