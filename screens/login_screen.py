import requests
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.uix.screenmanager import Screen
from screens.image_button import ImageButton
from kivy.uix.button import Button

fontName = 'Hancom Gothic Bold.ttf'

class LoginScreen(Screen):
    def __init__(self, **kwargs):

        super(LoginScreen, self).__init__(**kwargs)

        self.api_key = "AIzaSyDU67MIYsLtwbbpF_rnf0NcmPD_HDeGN8I"  # Firebase 프로젝트 설정에서 API 키를 확인할 수 있습니다

        self.layout = FloatLayout()

        # 배경 이미지 추가
        self.bg_image = Image(source='images/background.png', allow_stretch=True, keep_ratio=False)
        self.layout.add_widget(self.bg_image)
        self.logo_bg = Image(source='images/logo_image.png', size_hint=(0.83, 0.1), pos_hint={'x': 0.1, 'y': 0.8})
        self.layout.add_widget(self.logo_bg)
        self.login_bg = Image(source='images/login_image.png', size_hint=(0.6, 0.1), pos_hint={'x': 0.2, 'y': 0.65})
        self.layout.add_widget(self.login_bg)

        # 이메일 입력 창과 배경 이미지
        self.email_bg = Image(source='images/input_background.png', size_hint=(0.83, 0.1), pos_hint={'x': 0.08, 'y': 0.48})
        self.layout.add_widget(self.email_bg)
        self.email_input = TextInput(hint_text='Email', multiline=False, size_hint=(0.9, 0.1), pos_hint={'x': 0.1, 'y': 0.45},
                                     background_color=(0, 0, 0, 0))  # 배경을 투명하게 설정
        self.layout.add_widget(self.email_input)

        # 비밀번호 입력 창과 배경 이미지
        self.password_bg = Image(source='images/input_background.png', size_hint=(0.83, 0.1), pos_hint={'x': 0.08, 'y': 0.4})
        self.layout.add_widget(self.password_bg)
        self.password_input = TextInput(hint_text='Password', password=True, multiline=False, size_hint=(0.9, 0.1), pos_hint={'x': 0.1, 'y': 0.37},
                                        background_color=(0, 0, 0, 0))  # 배경을 투명하게 설정
        self.layout.add_widget(self.password_input)

        self.status_label = Label(text='Please log in', size_hint=(0.8, 0.1), pos_hint={'x': 0.1, 'y': 0.35})

        # 로그인 버튼에 배경 이미지 추가
        self.login_button = ImageButton(source='images/login_button.png', size_hint=(0.8, 0.1), pos_hint={'x': 0.1, 'y': 0.25})
        self.login_button.bind(on_press=self.login)

        # 회원가입 버튼 (텍스트만 표시하고 배경을 투명하게 설정)
        self.signup_button = Button(text='회원가입하기', font_name=fontName, font_size=15, size_hint=(1.1, 0.05), pos_hint={'x': 0.09, 'y': 0.2}, background_color=(0, 0, 0, 0), color=(0, 0.7, 0.7, 1))
        self.signup_button.bind(on_press=self.signup)
        self.signup_label = Label(text='계정이 없나요?', font_name=fontName, font_size=15, size_hint=(0.6, 0.05), size=(150, 30), pos_hint={'x': 0.05, 'y': 0.2}, color=(0.1, 0.4, 0.8, 1))

        # 상태 메시지 표시 레이블
        self.status_label = Label(text='계속 사용하려면 로그인 하십시요', font_name=fontName, font_size=15, size_hint=(0.83, 0.1),
                                  size=(self.bg_image.width * 0.8, self.bg_image.height * 0.1),
                                  color=(0.1, 0.4, 0.8, 1),
                                  pos_hint={'x': 0.08, 'y': 0.6})

        self.layout.add_widget(self.status_label)
        self.layout.add_widget(self.login_button)
        self.layout.add_widget(self.signup_button)
        self.layout.add_widget(self.signup_label)

        self.add_widget(self.layout)

    def login(self, instance):
        email = self.email_input.text
        password = self.password_input.text
        try:
            # Firebase Authentication REST API를 사용하여 로그인
            response = requests.post(
                f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={self.api_key}",
                data={
                    'email': email,
                    'password': password,
                    'returnSecureToken': True
                })
            data = response.json()
            if 'idToken' in data:
                self.status_label.text = f'Successfully logged in as: {email}'
                self.manager.current = 'home'
            else:
                self.status_label.text = f'Login error: {data["error"]["message"]}'
        except Exception as e:
            self.status_label.text = f'Error logging in: {str(e)}'

    def signup(self, instance):
        self.manager.current = 'signup'