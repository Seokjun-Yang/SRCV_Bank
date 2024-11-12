import json
import requests
from firebase_admin import db
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.uix.screenmanager import Screen
from screens.image_button import ImageButton
from kivy.uix.button import Button


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
        self.name_bg = Image(source='images/name_input.png', size_hint=(0.9, 0.12),
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

        # 회원가입 버튼
        self.signup_button = ImageButton(source='images/signup_button2.png', size_hint=(0.533, 0.093), pos_hint={'center_x': 0.5, 'top': 0.248})
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

        self.add_widget(self.layout)

    def on_pre_enter(self):
        # 입력 필드 초기화
        self.name_input.text = ''
        self.email_input.text = ''
        self.password_input.text = ''

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
                        'password' : password
                    }
                })
                print(f'회원가입 완료: {email}')
                self.manager.current = 'login'
            else:
                error_message = data.get("error", {}).get("message", "Unknown error")
                print(f'Signup error: {error_message}')

        except Exception as e:
            print(f'Error signing up: {str(e)}')

    def login(self, instance):
        self.manager.current = 'login'
