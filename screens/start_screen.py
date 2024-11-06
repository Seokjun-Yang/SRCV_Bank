from kivy.uix.screenmanager import Screen
from kivy.uix.button import ButtonBehavior
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout

fontName2 = 'LINESeedKR-Rg.ttf'

class ImageButton(ButtonBehavior, Image):
    pass

class StartScreen(Screen):
    def __init__(self, **kwargs):
        super(StartScreen, self).__init__(**kwargs)

        self.layout = FloatLayout()

        # 배경 이미지
        self.bg_image = Image(source='images/start_background.png', allow_stretch=True, keep_ratio=False)
        self.layout.add_widget(self.bg_image)

        self.text1 = Label(text="쉽고 편안한 금융 생활", font_name=fontName2, font_size=18, color=(0.1647, 0.6157, 0.5608, 1),
                                   halign='center', valign='middle',
                                   size_hint=(0.5, None), height=30, pos_hint={'center_x': 0.5, 'top': 0.86})
        self.text1.bind(size=self.text1.setter('text_size'))
        self.layout.add_widget(self.text1)
        self.logo_image = Image(source='images/main_logo.png',
                                size_hint=(0.8, 0.07), pos_hint={'center_x': 0.5, 'top': 0.82})
        self.layout.add_widget(self.logo_image)
        self.text2 = Label(text="언제 어디서나 쉽고 빠르게, 믿을 수 있는\n금융 서비스를 제공합니다.", font_name=fontName2, font_size=14, color=(0.2902, 0.2902, 0.2902, 1),
                                   halign='center', valign='middle',
                                   size_hint=(1, None), height=60, pos_hint={'center_x': 0.5, 'top': 0.75})
        self.text2.bind(size=self.text2.setter('text_size'))
        self.layout.add_widget(self.text2)

        self.main_image = Image(source='images/main_image.png',
                                size_hint=(0.83, 0.5), pos_hint={'center_x': 0.5, 'top': 0.72})
        self.layout.add_widget(self.main_image)

        # 로그인 버튼
        self.login_button = ImageButton(source='images/login_button.png', size_hint=(0.7, 0.07),
                                        pos_hint={'center_x': 0.5, 'top': 0.2})
        self.login_button.bind(on_press=self.go_to_login)

        # 회원가입 버튼
        self.signup_button = ImageButton(source='images/signup_button.png', size_hint=(0.7, 0.07),
                                         pos_hint={'center_x': 0.5, 'top': 0.125})
        self.signup_button.bind(on_press=self.go_to_signup)

        # 레이아웃에 버튼 추가
        self.layout.add_widget(self.login_button)
        self.layout.add_widget(self.signup_button)

        self.add_widget(self.layout)

    def go_to_login(self, instance):
        self.manager.current = 'login'

    def go_to_signup(self, instance):
        self.manager.current = 'phone_auth'
