import json
import requests
import firebase_admin
from firebase_admin import db
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.uix.screenmanager import Screen
from screens.image_button import ImageButton

fontName = 'Hancom Gothic Bold.ttf'

class SignupScreen(Screen):
    def __init__(self, **kwargs):
        super(SignupScreen, self).__init__(**kwargs)
        self.api_key = "AIzaSyDU67MIYsLtwbbpF_rnf0NcmPD_HDeGN8I"  # Firebase 프로젝트 설정에서 API 키를 확인할 수 있습니다

        self.layout = FloatLayout()

        # 배경 이미지 추가
        self.bg_image = Image(source='images/background.png', allow_stretch=True, keep_ratio=False)
        self.layout.add_widget(self.bg_image)
        self.logo_bg = Image(source='images/logo_image.png', size_hint=(0.83, 0.1), pos_hint={'x': 0.1, 'y': 0.85})
        self.layout.add_widget(self.logo_bg)
        self.login_bg = Image(source='images/signup_image.png', size_hint=(0.6, 0.1), pos_hint={'x': 0.2, 'y': 0.75})
        self.layout.add_widget(self.login_bg)

        # 이름 입력 창과 배경 이미지
        self.name_bg = Image(source='images/input_background.png', size_hint=(0.83, 0.1), pos_hint={'x': 0.08, 'y': 0.65})
        self.layout.add_widget(self.name_bg)
        self.name_input = TextInput(hint_text='Name', multiline=False, size_hint=(0.9, 0.1), pos_hint={'x': 0.1, 'y': 0.62},
                                     background_color=(0, 0, 0, 0))  # 배경을 투명하게 설정
        self.layout.add_widget(self.name_input)

        # 휴대폰번호 입력 창과 배경 이미지
        self.phone_bg = Image(source='images/input_background.png', size_hint=(0.83, 0.1), pos_hint={'x': 0.08, 'y': 0.55})
        self.layout.add_widget(self.phone_bg)
        self.phone_input = TextInput(hint_text='Phone Number', multiline=False, size_hint=(0.9, 0.1), pos_hint={'x': 0.1, 'y': 0.52},
                                     background_color=(0, 0, 0, 0))  # 배경을 투명하게 설정
        self.layout.add_widget(self.phone_input)

        # 이메일 입력 창과 배경 이미지
        self.email_bg = Image(source='images/input_background.png', size_hint=(0.83, 0.1), pos_hint={'x': 0.08, 'y': 0.45})
        self.layout.add_widget(self.email_bg)
        self.email_input = TextInput(hint_text='Email', multiline=False, size_hint=(0.9, 0.1), pos_hint={'x': 0.1, 'y': 0.42},
                                     background_color=(0, 0, 0, 0))  # 배경을 투명하게 설정
        self.layout.add_widget(self.email_input)

        # 비밀번호 입력 창과 배경 이미지
        self.password_bg = Image(source='images/input_background.png', size_hint=(0.83, 0.1), pos_hint={'x': 0.08, 'y': 0.35})
        self.layout.add_widget(self.password_bg)
        self.password_input = TextInput(hint_text='Password', password=True, multiline=False, size_hint=(0.9, 0.1), pos_hint={'x': 0.1, 'y': 0.32},
                                        background_color=(0, 0, 0, 0))  # 배경을 투명하게 설정
        self.layout.add_widget(self.password_input)

        # 회원가입 버튼
        self.signup_button = ImageButton(source='images/signup_button.png', size_hint=(0.9, 0.1), pos_hint={'x': 0.05, 'y': 0.2})
        self.signup_button.bind(on_press=self.signup)
        self.layout.add_widget(self.signup_button)

        # 상태 메시지 표시 레이블
        self.status_label = Label(text='회원가입 정보를 입력하세요', font_name=fontName, font_size=15, size_hint=(0.83, 0.1),
                                  color=(0.1, 0.4, 0.8, 1), pos_hint={'x': 0.05, 'y': 0.1})
        self.layout.add_widget(self.status_label)

        self.add_widget(self.layout)

    def signup(self, instance):
        name = self.name_input.text
        phone = self.phone_input.text
        email = self.email_input.text
        password = self.password_input.text
        try:
            # Firebase Authentication REST API를 사용하여 회원가입
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
                self.status_label.text = f'Successfully signed up as: {email}'
                # 사용자 데이터 저장
                self.save_user_to_database(name, phone, email, password)
                self.manager.current = 'login'
            else:
                self.status_label.text = f'Signup error: {data["error"]["message"]}'
        except Exception as e:
            self.status_label.text = f'Error signing up: {str(e)}'

    def save_user_to_database(self, name, phone, email, password):
        # 데이터베이스 레퍼런스 가져오기
        ref = db.reference('users')

        # 사용자 정보를 딕셔너리로 만들기
        user_data = {
            'name': name,
            'phone': phone,
            'email': email,
            'password': password
        }

        ref.push(user_data)
