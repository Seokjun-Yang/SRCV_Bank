import webbrowser

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.screenmanager import Screen
from kivy.animation import Animation
from kivy.uix.button import Button
from firebase_admin import db
from screens.image_button import ImageButton

fontName1 = 'LINESeedKR-Bd.ttf'
fontName2 = 'LINESeedKR-Rg.ttf'

class PhoneAuthScreen(Screen):
    def __init__(self, **kwargs):
        super(PhoneAuthScreen, self).__init__(**kwargs)
        self.user_seq_no = ""
        self.listener = None

        # 화면 레이아웃 설정
        self.layout = FloatLayout()

        # 배경 이미지
        self.bg_image = Image(source='images/background.png', allow_stretch=True, keep_ratio=False)
        self.layout.add_widget(self.bg_image)

        # 뒤로가기 버튼
        self.back_button = ImageButton(source='images/back_button.png', allow_stretch=True, keep_ratio=False,
                                       size_hint=(None, None), size=(25, 25), pos_hint={'x': 0.07, 'top': 0.94})
        self.back_button.bind(on_press=self.go_back_to_start)
        self.layout.add_widget(self.back_button)

        # 진행바
        self.progress_bar_image = Image(source='images/progress_bar1.png', size_hint=(0.373, 0.013), pos_hint={'center_x': 0.5, 'top': 0.93})
        self.layout.add_widget(self.progress_bar_image)

        # 단계 표시
        self.progress_label = Label(text="1/2", font_name=fontName1, font_size=19,
                                    size_hint=(0.083, 0.03), pos_hint={'x': 0.85, 'top': 0.938}, color=(0.4471, 0.749, 0.4706, 1))
        self.layout.add_widget(self.progress_label)

        self.step_label = Label(text="단계 1", font_name=fontName2, font_size=19,
                                    size_hint=(0.2, 0.05), pos_hint={'center_x': 0.5, 'top': 0.85},
                                    color=(0.4471, 0.749, 0.4706, 1))
        self.layout.add_widget(self.step_label)
        self.phone_text = Image(source='images/phone_text.png', size_hint=(0.4, 0.06),
                                        pos_hint={'center_x': 0.5, 'top': 0.795})
        self.layout.add_widget(self.phone_text)

        # 안내 아이콘
        self.phone_icon = Image(source='images/authentication.png', size_hint=(0.5, 0.25), pos_hint={'center_x': 0.5, 'top': 0.683})
        self.layout.add_widget(self.phone_icon)

        # 안내 문구
        self.twinkle_icon = Image(source='images/twinkle_icon.png', size_hint=(0.07, 0.033),
                                pos_hint={'x': 0.143, 'top': 0.362})
        self.layout.add_widget(self.twinkle_icon)
        self.key_icon = Image(source='images/key_icon.png', size_hint=(0.07, 0.033),
                                pos_hint={'x': 0.143, 'top': 0.3})
        self.layout.add_widget(self.key_icon)

        self.info1_label = Label(text="아래 버튼을 눌러\n휴대폰 인증을 진행해 주세요.", font_name=fontName1, font_size=16, halign="left",
                                 size_hint=(0.5, 0.042), pos_hint={'x': 0.26, 'top': 0.37}, color=(0.4039, 0.4039, 0.4039, 1))
        self.layout.add_widget(self.info1_label)
        self.info2_label = Label(text="인증절차에서 통장도 만들어주세요.", font_name=fontName1, font_size=16, halign="left",
                                 size_hint=(0.6, 0.015), pos_hint={'x': 0.26, 'top': 0.29}, color=(0.4039, 0.4039, 0.4039, 1))
        self.layout.add_widget(self.info2_label)

        # 인증 버튼
        self.auth_button = ImageButton(source='images/phoneauth_button.png', size_hint=(0.84, 0.083), pos_hint={'center_x': 0.5, 'top': 0.153})
        self.auth_button.bind(on_press=self.request_auth)
        self.layout.add_widget(self.auth_button)

        # 인증 완료 이미지 (처음에는 보이지 않도록 투명하게 설정)
        self.complete_image = Image(source='images/complete_image1.png', size_hint=(0.95, 0.475),
                                    pos_hint={'center_x': 0.5, 'top': 0.478}, opacity=0)
        self.layout.add_widget(self.complete_image)

        # 완료 버튼 (이미지 위에 추가하고, 처음에는 보이지 않도록 설정)
        self.complete_button = Button(text="다음 단계로 이동", font_name=fontName1, font_size=19,
                                      size_hint=(0.4, 0.02), pos_hint={'center_x': 0.5, 'y': 0.05}, opacity=0,
                                      background_color=(0, 0, 0, 0), color=(0.9608, 0.8902, 0.4196, 1))
        self.complete_button.bind(on_press=self.go_to_next_screen)
        self.layout.add_widget(self.complete_button)

        # 레이아웃을 화면에 추가
        self.add_widget(self.layout)

    def on_enter(self):
        self.start_listener()
        App.get_running_app().speak_text('번호인증 단계입니다. 아래의 버튼을 눌러주세요.')
        Clock.schedule_once(lambda dt:App.get_running_app().delay, 2)

    def on_leave(self):
        self.stop_listener()

    def start_listener(self):
        try:
            self.ref = db.reference('users')
            self.listener = self.ref.listen(self.user_seq_no_listener)
        except Exception as e:
            print(f"리스너 시작 중 오류 발생: {str(e)}")

    def stop_listener(self):
        try:
            if self.listener:
                self.listener.close()
                self.listener = None
                print("Firebase 리스너가 중지되었습니다.")
            else:
                print("Listener is already None or not initialized.")
        except Exception as e:
            print(f"리스너 중지 중 오류 발생: {str(e)}")

    def user_seq_no_listener(self, event):
        try:
            # event.path에서 user_seq_no 부분 추출
            path_parts = event.path.split('/')

            # 업데이트 경로에 user_seq_no가 포함된 경우만 추출
            if len(path_parts) > 1:
                updated_user_seq_no = path_parts[1]
                self.user_seq_no = updated_user_seq_no
                print(f"업데이트된 user_seq_no: {self.user_seq_no}")

                # 업데이트된 user_seq_no에 대한 데이터 출력 (필요에 따라 주석 처리 가능)
                updated_data = db.reference(f'users/{self.user_seq_no}').get()

                if self.user_seq_no:
                    self.show_complete_image()
            else:
                print("유효한 user_seq_no를 포함하지 않는 업데이트 경로입니다.")

        except Exception as e:
            print(f"listener 오류 발생: {str(e)}")

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

        except Exception as e:
            print(f"번호 인증 요청 중 오류 발생: {str(e)}")

    def show_complete_image(self):

        # 인증 완료 이미지와 완료 버튼을 서서히 표시하는 애니메이션 추가
        anim = Animation(opacity=1, duration=0.5)
        anim.start(self.complete_image)
        anim.start(self.complete_button)
        self.auth_button.disabled = True
        App.get_running_app().speak_text('번호 인증이 완료되었습니다. 다음 화면으로 이동합니다.')
        Clock.schedule_once(lambda dt:App.get_running_app().delay, 3)

    def go_to_next_screen(self, instance):
        # 인증 완료 버튼을 누르면 다음 화면으로 이동
        signup_screen = self.manager.get_screen('signup')
        signup_screen.user_seq_no = self.user_seq_no  # user_seq_no 전달
        print(f"SignupScreen으로 user_seq_no 전달: {self.user_seq_no}")
        self.complete_image.opacity = 0
        self.complete_button.opacity = 0
        self.auth_button.disabled = False

        Clock.schedule_once(lambda dt:self.change_screen('face_auth'), 1)

    def go_back_to_start(self, instance):
        App.get_running_app().speak_text('이전 화면으로 돌아갑니다.')
        Clock.schedule_once(lambda dt:App.get_running_app().delay, 1)
        Clock.schedule_once(lambda dt:self.change_screen('start'), 1)
    def change_screen(self, screen):
        self.manager.current = screen