import json
import os
import threading
import time

import requests
from firebase_admin import db
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.uix.screenmanager import Screen
from plyer import storagepath
from screens.image_button import ImageButton
from kivy.uix.button import Button
from PIL import Image as PILImage

from SRCV_Bank.utils.metadata_manager import MetadataManager

img = PILImage.open("images/name_input.png")
img = img.resize((555, 150), PILImage.LANCZOS)  # 크기 줄이기 및 고화질 리샘플링
img.save("images/name_input_re.png")  # 리샘플링 후 저장


fontName1 = 'LINESeedKR-Bd.ttf'
fontName2 = 'LINESeedKR-Rg.ttf'

class SignupScreen(Screen):
    def __init__(self, **kwargs):
        super(SignupScreen, self).__init__(**kwargs)
        self.api_key = "AIzaSyDU67MIYsLtwbbpF_rnf0NcmPD_HDeGN8I"
        self.layout = FloatLayout()
        self.user_seq_no = ""
        self.user_data = {}

        # 배경 이미지 추가
        self.bg_image = Image(source='images/signup_background.png', allow_stretch=True, keep_ratio=False)
        self.layout.add_widget(self.bg_image)

        # 이름 입력 창과 배경 이미지
        self.name_bg = Image(source='images/name_input_re.png', size_hint=(0.9, 0.12),
                             pos_hint={'center_x': 0.5, 'top': 0.643})
        self.layout.add_widget(self.name_bg)
        self.name_input = TextInput(hint_text='I', font_name=fontName1, font_size=18, multiline=False,
                                    size_hint=(0.9, 0.05), pos_hint={'x': 0.173, 'top': 0.6},
                                    background_color=(0, 0, 0, 0))  # 배경을 투명하게 설정
        self.layout.add_widget(self.name_input)

        # 이메일 입력 창과 배경 이미지
        self.email_bg = Image(source='images/email_input.png', size_hint=(0.9, 0.12),
                              pos_hint={'center_x': 0.5, 'top': 0.533})
        self.layout.add_widget(self.email_bg)
        self.email_input = TextInput(hint_text='I', font_name=fontName1, font_size=18, multiline=False,
                                     size_hint=(0.9, 0.05), pos_hint={'x': 0.173, 'top': 0.477},
                                     background_color=(0, 0, 0, 0))
        self.layout.add_widget(self.email_input)

        # 비밀번호 입력 창과 배경 이미지
        self.password_bg = Image(source='images/password_input.png', size_hint=(0.9, 0.12),
                                 pos_hint={'center_x': 0.5, 'top': 0.423})
        self.layout.add_widget(self.password_bg)
        self.password_input = TextInput(hint_text='I', font_name=fontName1, font_size=18, password=True,
                                        multiline=False, size_hint=(0.9, 0.05),
                                        pos_hint={'x': 0.173, 'top': 0.367}, background_color=(0, 0, 0, 0))
        self.layout.add_widget(self.password_input)

        self.login_save_label = Label(text='약관에 동의합니다.', font_name=fontName2, font_size=13, size_hint=(0.27, 0.012),
                                      pos_hint={'x': 0.173, 'top': 0.298}, color=(0.3922, 0.3922, 0.3922, 1))
        self.layout.add_widget(self.login_save_label)

        # 회원가입 버튼
        self.signup_button = ImageButton(source='images/signup_button2.png', size_hint=(0.533, 0.093),
                                         pos_hint={'center_x': 0.5, 'top': 0.248})
        self.signup_button.bind(on_press=self.signup)
        self.layout.add_widget(self.signup_button)

        self.signup_label = Label(text='이미 계정이 있으신가요?', font_name=fontName1, font_size=15, size_hint=(0.2, 0.022),
                                  pos_hint={'x': 0.33, 'top': 0.122}, color=(0.4039, 0.4039, 0.4039, 1), halign='left',
                                  valign='middle')
        self.layout.add_widget(self.signup_label)
        self.login_button = Button(text='로그인', font_name=fontName1, font_size=15, size_hint=(0.4, 0.022),
                                   pos_hint={'x': 0.49, 'top': 0.122}, color=(0.4471, 0.749, 0.4706, 1),
                                   background_color=(0, 0, 0, 0))
        self.login_button.bind(on_press=self.login)
        self.layout.add_widget(self.login_button)

        #self.add_widget(self.layout)

        #  얼굴인증 촬영 테스트 버튼
        """self.signup_verification_button = ImageButton(source='images/profile_picture.png', size_hint=(0.9, 0.1), pos_hint={'x': 0.07, 'y': 0.1})
        self.signup_verification_button.bind(on_press=self.verification)
        self.layout.add_widget(self.signup_verification_button)"""

        self.add_widget(self.layout)

    def on_pre_enter(self):
        if not self.user_seq_no:
            print("user_seq_no가 없습니다. 인증을 완료하고 오세요.")
        else:
            print(f"전달받은 user_seq_no: {self.user_seq_no}")


    def signup(self, instance):
        if not self.user_seq_no:
            print('인증을 먼저 완료해주세요.')
            return

        name = self.name_input.text
        email = self.email_input.text
        password = self.password_input.text

        if not all([name, email, password]):
            print('모든 입력 필드를 채워주세요.')
            return

        try:
            # Firebase Authentication 회원가입
            response = requests.post(
                f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={self.api_key}",
                data=json.dumps({
                    'email': email,
                    'password': password,
                    'returnSecureToken': True
                }),
                headers={'Content-Type': 'application/json'}
            )
            data = response.json()

            if 'idToken' in data:
                # 회원가입 정보 Firebase에 저장
                ref = db.reference(f'users/{self.user_seq_no}')
                ref.update({
                    'user_info': {
                        'name': name,
                        'email': email,
                        'password': password
                    }
                })
                print(f'회원가입 완료: {email}')
                #tts와 파일명 변경
                # self.rename_image() #저장된 이미지 이름을 user_seq_no로 변경
                # self.tts() #동작설명
                self.manager.current = 'login'
            else:
                error_message = data.get("error", {}).get("message", "Unknown error")
                print(f'Signup error: {error_message}')

        except Exception as e:
            print(f'Error signing up: {str(e)}')

    def login(self, instance):
        self.manager.current = 'login'

    def tts(self):
        app = App.get_running_app()
        threading.Thread(target=app.speak, args=("회원가입이 완료되었습니다.",)).start()
        time.sleep(1)
    def rename_image(self):
        # 이미지 이름
        self.image_name = 'signup_temp.jpg'
        # 경로
        self.home_dir = storagepath.get_home_dir()
        self.storage_path = os.path.join(self.home_dir, "bank")
        self.image_path = os.path.join(self.storage_path, self.image_name)

        self.new_image_path = os.path.join(self.storage_path, f'{self.user_seq_no}.jpg')
        os.rename(src=self.image_path, dst=self.new_image_path)# user_seq_no.jpg로 이름 변경

        manager = MetadataManager(self.storage_path)
        manager.finalize_metadata(self.user_seq_no)  #메타데이터 추가

    def change_screen(self, screen):
        self.manager.current = screen

