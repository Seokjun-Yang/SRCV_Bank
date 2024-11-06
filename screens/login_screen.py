from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.uix.screenmanager import Screen
from screens.image_button import ImageButton
from kivy.uix.button import Button
from firebase_admin import db

fontName1 = 'LINESeedKR-Bd.ttf'
fontName2 = 'LINESeedKR-Rg.ttf'

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)

        self.api_key = "AIzaSyDU67MIYsLtwbbpF_rnf0NcmPD_HDeGN8I"  # Firebase 프로젝트 설정에서 API 키를 확인할 수 있습니다

        self.layout = FloatLayout()

        # 배경 이미지 추가
        self.bg_image = Image(source='images/login_background.png', allow_stretch=True, keep_ratio=False)
        self.layout.add_widget(self.bg_image)

        # 이메일 입력 창과 배경 이미지
        self.email_bg = Image(source='images/email_input.png', size_hint=(0.9, 0.12), pos_hint={'center_x': 0.5, 'top': 0.588}, allow_stretch=True, keep_ratio=False)
        self.layout.add_widget(self.email_bg)
        self.email_input = TextInput(hint_text='I', font_name=fontName1, font_size=18, multiline=False, size_hint=(0.9, 0.05), pos_hint={'x': 0.173, 'top': 0.54},
                                     background_color=(0, 0, 0, 0))
        self.layout.add_widget(self.email_input)

        # 비밀번호 입력 창과 배경 이미지
        self.password_bg = Image(source='images/password_input.png', size_hint=(0.9, 0.12), pos_hint={'center_x': 0.5, 'top': 0.478})
        self.layout.add_widget(self.password_bg)
        self.password_input = TextInput(hint_text='I', font_name=fontName1, font_size=18, password=True, multiline=False, size_hint=(0.9, 0.05),
                                        pos_hint={'x': 0.173, 'top': 0.422}, background_color=(0, 0, 0, 0))
        self.layout.add_widget(self.password_input)


        self.login_save_label = Label(text='로그인 정보 저장', font_name=fontName2, font_size=13, size_hint=(0.237, 0.012),
                                  pos_hint={'x': 0.173, 'top': 0.353}, color=(0.3922, 0.3922, 0.3922, 1))
        self.layout.add_widget(self.login_save_label)

        self.forget_password_label = Label(text='비밀번호를 잊으셨나요?', font_name=fontName2, font_size=13, size_hint=(0.336, 0.012),
                                  pos_hint={'x': 0.58, 'top': 0.353}, color=(0.3922, 0.3922, 0.3922, 1))
        self.layout.add_widget(self.forget_password_label)

        # 로그인 버튼
        self.login_button = ImageButton(source='images/login_button2.png', size_hint=(0.533, 0.093), pos_hint={'center_x': 0.5, 'top': 0.298})
        self.login_button.bind(on_press=self.login)
        self.layout.add_widget(self.login_button)

        self.signup_label = Label(text='계정이 없으신가요?', font_name=fontName1, font_size=15, size_hint=(0.2, 0.022),
                                  pos_hint={'x': 0.32, 'top': 0.18}, color=(0.4039, 0.4039, 0.4039, 1), halign='left', valign='middle')
        self.layout.add_widget(self.signup_label)
        self.signup_button = Button(text='회원가입', font_name=fontName1, font_size=15, size_hint=(0.2, 0.022),
                                    pos_hint={'x': 0.56, 'top': 0.18}, color=(0.4471, 0.749, 0.4706, 1), background_color=(0, 0, 0, 0))
        self.signup_button.bind(on_press=self.signup)
        self.layout.add_widget(self.signup_button)
        self.or_label = Label(text='또는', font_name=fontName1, font_size=15, size_hint=(0.063, 0.022),
                                  pos_hint={'center_x': 0.5, 'top': 0.13}, color=(0.3922, 0.3922, 0.3922, 1), halign='left', valign='middle')
        self.layout.add_widget(self.or_label)
        self.camera_auth_label = Label(text='얼굴인증 로그인', font_name=fontName1, font_size=17, size_hint=(0.327, 0.025),
                                  pos_hint={'center_x': 0.5, 'top': 0.075}, color=(0.9608, 0.7608, 0.4196, 1), halign='left', valign='middle')
        self.layout.add_widget(self.camera_auth_label)

        # 얼굴인증 촬영 버튼
        self.second_verification_button = ImageButton(source='images/camera_button.png', size_hint=(0.117, 0.058),
                                                      pos_hint={'x': 0.817, 'top': 0.075})
        self.second_verification_button.bind(on_press=self.test_verification)
        self.layout.add_widget(self.second_verification_button)

        self.add_widget(self.layout)

    def login(self, instance):
        email = self.email_input.text
        password = self.password_input.text

        try:
            # Firebase 데이터베이스에서 이메일로 사용자 정보 검색
            users_ref = db.reference('users')
            users = users_ref.get()

            if not users:
                return

            # Firebase에서 사용자 데이터 검색
            for user_seq_no, user_data in users.items():
                user_info = user_data.get('user_info')
                if not user_info:
                    continue

                if user_info.get('email') == email and user_info.get('password') == password:
                    # 홈 화면으로 사용자 정보 전달
                    home_screen = self.manager.get_screen('home')
                    home_screen.load_user_data(user_seq_no)
                    self.manager.current = 'home'
                    return
        except Exception as e:
            pass
    def signup(self, instance):
        self.manager.current = 'phone_auth'
    def test_verification(self, instance):
        self.manager.current = 'secondVerification'
