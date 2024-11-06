from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from firebase_admin import db
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.button import ButtonBehavior
from kivy.uix.screenmanager import Screen
from kivy.animation import Animation


fontName1 = 'LINESeedKR-Bd.ttf'
fontName2 = 'LINESeedKR-Rg.ttf'

class ImageButton(ButtonBehavior, Image):
    pass

class FaceAuthScreen(Screen):
    def __init__(self, **kwargs):
        super(FaceAuthScreen, self).__init__(**kwargs)
        self.user_seq_no = ""
        self.is_verified = False

        # 레이아웃 설정
        self.layout = FloatLayout()

        # 배경 이미지
        self.bg_image = Image(source='images/background.png', allow_stretch=True, keep_ratio=False)
        self.layout.add_widget(self.bg_image)

        # 뒤로가기 버튼
        self.back_button = ImageButton(source='images/back_button.png', allow_stretch=True, keep_ratio=False,
                                       size_hint=(None, None), size=(25, 25), pos_hint={'x': 0.07, 'top': 0.94})
        self.back_button.bind(on_press=self.go_back_to_auth)
        self.layout.add_widget(self.back_button)

        # 진행바
        self.progress_bar_image = Image(source='images/progress_bar2.png', size_hint=(0.373, 0.013),
                                        pos_hint={'center_x': 0.5, 'top': 0.93})
        self.layout.add_widget(self.progress_bar_image)

        # 단계 표시
        self.progress_label = Label(text="2/2", font_name=fontName1, font_size=19,
                                    size_hint=(0.083, 0.03), pos_hint={'x': 0.85, 'top': 0.938},
                                    color=(0.4471, 0.749, 0.4706, 1))
        self.layout.add_widget(self.progress_label)

        self.step_label = Label(text="단계 2", font_name=fontName2, font_size=19,
                                size_hint=(0.2, 0.05), pos_hint={'center_x': 0.5, 'top': 0.85},
                                color=(0.4471, 0.749, 0.4706, 1))
        self.layout.add_widget(self.step_label)
        self.face_text = Image(source='images/face_text.png', size_hint=(0.4, 0.06),
                                pos_hint={'center_x': 0.5, 'top': 0.795})
        self.layout.add_widget(self.face_text)

        # 안내 아이콘
        self.face_icon = Image(source='images/facerecognition.png', size_hint=(0.5, 0.25),
                                pos_hint={'center_x': 0.5, 'top': 0.677})
        self.layout.add_widget(self.face_icon)

        # 안내 문구
        self.twinkle_icon = Image(source='images/twinkle_icon.png', size_hint=(0.07, 0.033),
                                  pos_hint={'x': 0.107, 'top': 0.367})
        self.layout.add_widget(self.twinkle_icon)
        self.camera_icon = Image(source='images/camera_icon.png', size_hint=(0.07, 0.033),
                              pos_hint={'x': 0.107, 'top': 0.297})
        self.layout.add_widget(self.camera_icon)

        self.info1_label = Label(text="버튼을 눌러 얼굴 인증을 시작해 주세요.", font_name=fontName1, font_size=16, halign="left",
                                 size_hint=(0.67, 0.014), pos_hint={'x': 0.223, 'top': 0.358},
                                 color=(0.4039, 0.4039, 0.4039, 1))
        self.layout.add_widget(self.info1_label)
        self.info2_label = Label(text="화면 안내에 따라\n얼굴을 카메라에 맞춰주세요.", font_name=fontName1, font_size=16, halign="left",
                                 size_hint=(0.5, 0.042), pos_hint={'x': 0.223, 'top': 0.302},
                                 color=(0.4039, 0.4039, 0.4039, 1))
        self.layout.add_widget(self.info2_label)

        # 인증 버튼
        self.auth_button = ImageButton(source='images/faceauth_button.png', size_hint=(0.84, 0.083),
                                       pos_hint={'center_x': 0.5, 'top': 0.153})
        self.auth_button.bind(on_press=self.verification)
        self.layout.add_widget(self.auth_button)

        # 인증 완료 이미지 (처음에는 보이지 않도록 투명하게 설정)
        self.complete_image = Image(source='images/complete_image2.png', size_hint=(0.95, 0.475),
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
        if self.is_verified:
            self.show_complete_image()
    def verification(self, instance):
        self.manager.current = 'signupVerification'
    def show_complete_image(self):
        anim = Animation(opacity=1, duration=0.5)
        anim.start(self.complete_image)
        anim.start(self.complete_button)
        self.auth_button.disabled = True
    def go_to_next_screen(self, instance):
        self.auth_button.disabled = False
        self.manager.current = 'signup'
    def go_back_to_auth(self, instance):
        self.manager.current = 'phone_auth'
