import time

from kivy.animation import Animation
from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import Color, Line
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget
from screens.image_button import ImageButton
from kivy.uix.button import Button
from firebase_admin import db
import requests

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

        self.logo_icon = Image(source='images/logo_image.png', size_hint=(0.15, 0.075),
                               pos_hint={'x': 0.067, 'top': 0.958})
        self.layout.add_widget(self.logo_icon)
        self.welcome_text_label = Label(text='환영합니다', font_name=fontName2, font_size=20, size_hint=(0.233, 0.033),
                                        pos_hint={'x': 0.072, 'top': 0.85}, color=(0, 0, 0, 1), halign='left',
                                        valign='middle')
        self.layout.add_widget(self.welcome_text_label)
        self.login_text = Image(source='images/login_text.png', size_hint=(0.353, 0.07),
                                pos_hint={'x': 0.063, 'top': 0.81})
        self.layout.add_widget(self.login_text)
        self.login_text_label = Label(text='얼굴인증으로 은행계정에 로그인', font_name=fontName1, font_size=15,
                                      size_hint=(0.453, 0.025),
                                      pos_hint={'x': 0.09, 'top': 0.732}, color=(0.325, 0.325, 0.325, 1), halign='left',
                                      valign='middle')
        self.layout.add_widget(self.login_text_label)

        self.login_text_label = Label(text='또는 이메일을 사용하여 로그인', font_name=fontName1, font_size=17,
                                      size_hint=(0.533, 0.025),
                                      pos_hint={'x': 0.075, 'top': 0.302}, color=(1, 1, 1, 1), halign='left',
                                      valign='middle')
        self.layout.add_widget(self.login_text_label)

        # 이메일 입력 창과 배경 이미지
        self.email_bg = Image(source='images/email_input2.png', size_hint=(0.7, 0.058),
                              pos_hint={'x': 0.067, 'top': 0.25})
        self.layout.add_widget(self.email_bg)
        self.email_icon = Image(source='images/email.png', size_hint=(0.068, 0.033),
                                pos_hint={'x': 0.117, 'top': 0.238})
        self.layout.add_widget(self.email_icon)
        self.email_input = TextInput(hint_text='I', font_name=fontName1, font_size=15,
                                     pos_hint={'x': 0.2, 'top': 0.238},
                                     background_color=(0, 0, 0, 0), multiline=False, size_hint=(0.9, 0.05))
        self.layout.add_widget(self.email_input)

        # 비밀번호 입력 창과 배경 이미지
        self.password_bg = Image(source='images/password_input2.png', size_hint=(0.7, 0.058),
                                 pos_hint={'x': 0.067, 'top': 0.167})
        self.layout.add_widget(self.password_bg)
        self.password_icon = Image(source='images/password.png', size_hint=(0.067, 0.033),
                                   pos_hint={'x': 0.117, 'top': 0.155})
        self.layout.add_widget(self.password_icon)
        self.password_input = TextInput(hint_text='I', font_name=fontName1, font_size=15, password=True,
                                        multiline=False,
                                        size_hint=(0.9, 0.05), background_color=(0, 0, 0, 0),
                                        pos_hint={'x': 0.2, 'top': 0.155})
        self.layout.add_widget(self.password_input)

        # 로그인 버튼
        self.login_button = ImageButton(source='images/login_button2.png', size_hint=(0.133, 0.067),
                                        pos_hint={'x': 0.8, 'top': 0.213})
        self.login_button.bind(on_press=self.login)
        self.layout.add_widget(self.login_button)

        self.warning_icon = Image(source='images/warning.png', size_hint=(0.1, 0.05),
                                  pos_hint={'x': 0.21, 'top': 0.063})
        self.layout.add_widget(self.warning_icon)
        self.signup_label = Label(text='계정이 없으신가요?', font_name=fontName1, font_size=15, size_hint=(0.2, 0.022),
                                  pos_hint={'x': 0.385, 'top': 0.05}, color=(0.4039, 0.4039, 0.4039, 1), halign='left',
                                  valign='middle')
        self.layout.add_widget(self.signup_label)
        self.signup_button = Button(text='회원가입', font_name=fontName1, font_size=15, size_hint=(0.2, 0.022),
                                    pos_hint={'x': 0.633, 'top': 0.05}, color=(0.4471, 0.749, 0.4706, 1),
                                    background_color=(0, 0, 0, 0))
        self.signup_button.bind(on_press=self.signup)
        self.layout.add_widget(self.signup_button)

        # 얼굴인증 촬영 버튼
        self.wave_effect = Widget(size_hint=(0.5, 0.5), pos_hint={'center_x': 0.5, 'center_y': 0.52})
        with self.wave_effect.canvas:
            Color(0.827, 0.933, 0.596, 0.3)
            self.wave_circle = Line(circle=(self.wave_effect.center_x, self.wave_effect.center_y, 70), width=2)
        self.wave_effect.bind(pos=self.update_wave_circle, size=self.update_wave_circle)
        self.layout.add_widget(self.wave_effect)
        self.start_wave_animation()

        self.second_verification_button = ImageButton(source='images/camera_image.png', size_hint=(0.333, 0.167),
                                                      pos_hint={'center_x': 0.5, 'top': 0.605})
        self.second_verification_button.bind(on_press=self.face_login)
        self.layout.add_widget(self.second_verification_button)
        self.animate_second_verification_button()

        self.add_widget(self.layout)

    def update_wave_circle(self, *args):
        # Line 원형의 위치와 크기 업데이트 (정원 형태 유지)
        self.wave_circle.circle = (self.wave_effect.center_x, self.wave_effect.center_y, self.wave_effect.width / 2)

    def start_wave_animation(self):
        # 원형 파동 애니메이션 정의
        anim = Animation(size_hint=(0.5, 0.5), opacity=0, duration=1)
        anim.bind(on_complete=self.reset_wave_animation)
        anim.start(self.wave_effect)

    def reset_wave_animation(self, *args):
        # 애니메이션 초기화 후 반복 실행
        self.wave_effect.size_hint = (0.3, 0.3)
        self.wave_effect.opacity = 1
        self.start_wave_animation()

    def animate_second_verification_button(self):
        anim = Animation(size_hint=(0.35, 0.18), duration=0.5) + Animation(size_hint=(0.333, 0.167), duration=0.5)
        anim.repeat = True
        anim.start(self.second_verification_button)

    def login(self, instance):
        email = self.email_input.text
        password = self.password_input.text
        App.get_running_app().speak_text("로그인 버튼을 눌렀습니다.")
        Clock.schedule_once(lambda dt:self.delay, 1)

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
                    Clock.schedule_once(lambda dt:self.change_screen('home'), 4)
                    return

            App.get_running_app().speak_text("이메일과 비밀번호를 다시 확인해주세요.")
            Clock.schedule_once(lambda dt: self.delay, 1)

        except Exception as e:
            pass

    def signup(self, instance):
        App.get_running_app().speak_text("회원가입 버튼을 눌렀습니다. 번호 인증 화면으로 이동합니다.")
        Clock.schedule_once(lambda dt:self.change_screen('phone_auth'), 10)

    def clear_inputs(self):
        """로그인 필드 초기화"""
        self.email_input.text = ''
        self.password_input.text = ''

    def face_login(self, instance):
        App.get_running_app().speak_text("카메라를 클릭했습니다. 얼굴인증 로그인 화면으로 이동합니다.")
        Clock.schedule_once(lambda dt:self.change_screen('loginVerification'), 5)

    def on_pre_enter(self, *args):#
        self.app = App.get_running_app()

        pass

    def on_leave(self, *args):
        #self.cancel_speak()
        pass

    def on_enter(self, *args):
        tts = '이메일과 비밀번호를 입력해주세요. 혹은 중앙의 카메라를 눌러 얼굴인증을 해주세요.'
        self.app.speak_text(tts)

    def change_screen(self, screen):
        self.manager.current = screen

    def delay(self):
        pass