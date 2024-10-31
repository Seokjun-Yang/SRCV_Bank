from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen

fontName = 'LINESeedKR-Bd.ttf'

class AuthCompleteScreen(Screen):
    def __init__(self, **kwargs):
        super(AuthCompleteScreen, self).__init__(**kwargs)

        # 레이아웃 설정
        self.layout = FloatLayout()

        # 배경 이미지 (필요시 추가)
        self.bg_image = Label(text='', size_hint=(1, 1), pos_hint={'center_x': 0.5, 'center_y': 0.5})
        self.layout.add_widget(self.bg_image)

        # 완료 안내 문구
        self.message_label = Label(
            text="번호 인증이 완료됐어요!\n회원가입하실 정보를 입력해주세요.",
            font_name=fontName, font_size=18,
            size_hint=(0.8, 0.3), pos_hint={'center_x': 0.5, 'center_y': 0.6},
            halign="center", color=(0, 0, 0, 1)
        )
        self.layout.add_widget(self.message_label)

        # 다음 버튼
        self.next_button = Button(
            text="다음", font_name=fontName, font_size=16,
            size_hint=(0.4, 0.1), pos_hint={'center_x': 0.5, 'center_y': 0.4},
            background_color=(0, 0.6, 0.8, 1), color=(1, 1, 1, 1)
        )
        self.next_button.bind(on_press=self.go_to_signup)
        self.layout.add_widget(self.next_button)

        # 레이아웃을 화면에 추가
        self.add_widget(self.layout)

    def go_to_signup(self, instance):
        # 다음 버튼을 클릭하면 회원가입 화면으로 이동
        self.manager.current = 'signup'
