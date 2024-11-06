import webbrowser
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget
from kivy.graphics import Color, Line, Ellipse, RoundedRectangle
from kivy.animation import Animation
from screens.image_button import ImageButton

fontName = 'LINESeedKR-Bd.ttf'

class AuthScreen(Screen):
    def __init__(self, **kwargs):
        super(AuthScreen, self).__init__(**kwargs)

        # 화면 레이아웃 설정
        self.layout = FloatLayout()

        # 배경 이미지
        self.bg_image = Image(source='images/background.png', allow_stretch=True, keep_ratio=False)
        self.layout.add_widget(self.bg_image)

        # 백버튼
        self.back_button = ImageButton(
            source='images/back_button.png',
            size_hint=(None, None), size=(30, 30),
            pos_hint={'x': 0.04, 'y': 0.902}
        )
        self.back_button.bind(on_press=self.go_back_to_home)
        self.layout.add_widget(self.back_button)

        # 단계 표시
        self.step_label = Label(
            text="1단계: 번호 인증",
            font_name=fontName, font_size=24,  # 글자 크기를 크게
            size_hint=(1, 0.1), pos_hint={'x': 0, 'y': 0.87},
            color=(0.25, 0.41, 0.88, 1)
        )
        self.layout.add_widget(self.step_label)

        # 단계 표시 밑에 막대 이미지 추가
        self.progress_bar_image = Image(
            source='images/[1]progress_bar.png',  # 여기에 막대 이미지 파일 경로를 입력
            size_hint=(0.7, 0.16),  # 이미지 크기 조정
            pos_hint={'center_x': 0.5, 'y': 0.76}  # step_label 바로 아래에 위치
        )
        self.layout.add_widget(self.progress_bar_image)

        # 안내 아이콘
        self.icon = Image(
            source='images/phone_icon.png',
            size_hint=(0.2, 0.2),
            pos_hint={'center_x': 0.5, 'center_y': 0.6}
        )
        self.layout.add_widget(self.icon)

        # 아이콘에 애니메이션 추가 (살짝 커졌다 작아지는 효과)
        anim = Animation(size_hint=(0.22, 0.22), duration=0.5) + Animation(size_hint=(0.2, 0.2), duration=0.5)
        anim.repeat = True
        anim.start(self.icon)

        # 안내 문구
        self.info_label = Label(
            text="번호 인증을 위해\n아래 버튼을 눌러주세요.",
            font_name=fontName, font_size=25,
            halign="center",
            size_hint=(0.9, 0.2), pos_hint={'x': 0.05, 'y': 0.35},
            color=(0.16, 0.66, 0.54, 1)
        )
        self.layout.add_widget(self.info_label)

        # 인증 버튼
        self.auth_button = ImageButton(
            source='images/auth_button.png',
            size_hint=(0.8, 0.15), pos_hint={'x': 0.1, 'y': 0.1}
        )
        self.auth_button.bind(on_press=self.request_auth)
        self.layout.add_widget(self.auth_button)

        # 레이아웃을 화면에 추가
        self.add_widget(self.layout)
    def request_auth(self, instance):
        try:
            print("번호 인증 요청 시작")
            print("번호 인증 중... 잠시만 기다려주세요.")

            client_id = 'd79bfcd3-1b00-4f8b-8ffc-aa06a317801c'
            redirect_uri = 'https://us-central1-bank-a752e.cloudfunctions.net/authCallback'
            state = '12345678912345678912345678912345'

            auth_url = (
                f"https://testapi.openbanking.or.kr/oauth/2.0/authorize?response_type=code&"
                f"client_id={client_id}&redirect_uri={redirect_uri}&scope=login inquiry transfer&"
                f"state={state}&auth_type=0"
            )
            webbrowser.open(auth_url)

            # 인증 완료 후 AuthCompleteScreen으로 이동
            self.manager.current = 'auth_complete'

        except Exception as e:
            print(f"번호 인증 요청 중 오류 발생: {str(e)}")

    def go_back_to_home(self, instance):
        self.manager.current = 'home'
