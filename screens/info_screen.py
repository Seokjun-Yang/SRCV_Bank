from firebase_admin import db
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import ButtonBehavior
from kivy.uix.screenmanager import Screen, ScreenManager
fontName1 = 'LINESeedKR-Bd.ttf'
fontName2 = 'LINESeedKR-Rg.ttf'

class ImageButton(ButtonBehavior, Image):
    pass

class InfoScreen(Screen):
    def __init__(self, **kwargs):
        super(InfoScreen, self).__init__(**kwargs)
        self.layout = FloatLayout()

        # 뒤로 가기 버튼
        self.back_button = ImageButton(source='images/back_button.png', allow_stretch=True, keep_ratio=False,
                                       size_hint=(None, None), size=(25, 25), pos_hint={'x': 0.06, 'top': 0.94})
        self.back_button.bind(on_press=self.go_back_to_home)
        self.layout.add_widget(self.back_button)

        # "홈" 텍스트
        self.home_text = Label(text="홈", font_name=fontName1, font_size=20, pos_hint={'x': 0.153, 'top': 0.932},
                               size_hint=(0.046, 0.018), color=(0.447, 0.749, 0.471, 1))
        self.layout.add_widget(self.home_text)

        # 프로필 사진
        self.profile_image = Image(source='images/profile_picture2.png',
                                   size_hint=(0.33, 0.16), pos_hint={'center_x': 0.5, 'top': 0.76})
        self.layout.add_widget(self.profile_image)

        # 이름 라벨 - 프로필 사진 바로 아래에 위치 조정
        self.name_label = Label(text='', font_name=fontName1, font_size=25, color=(0.4039, 0.4039, 0.4039, 1),
                                pos_hint={'center_x': 0.5, 'top': 1.03})  # 위치 조정
        self.layout.add_widget(self.name_label)

        # 계좌번호 라벨 - 이름 라벨 바로 아래에 위치 조정
        self.account_number_label = Label(text='', font_name=fontName1, font_size=20, color=(0.4039, 0.4039, 0.4039, 1),
                                          pos_hint={'center_x': 0.5, 'top': 0.96})  # 위치 조정
        self.layout.add_widget(self.account_number_label)

        # 로그아웃 버튼 - 계좌번호 라벨 아래에 위치 조정
        self.logout_button = ImageButton(source='images/logout_button.png', size_hint=(0.54, 0.083),
                                         pos_hint={'center_x': 0.5, 'top': 0.29})  # 위치 조정
        self.logout_button.bind(on_press=self.logout)
        self.layout.add_widget(self.logout_button)

        self.add_widget(self.layout)

    def load_user_info(self, user_seq_no):
        # Firebase에서 사용자 정보 로드
        user_info_ref = db.reference(f'users/{user_seq_no}/user_info')
        user_info = user_info_ref.get()
        if user_info:
            self.name_label.text = f"{user_info.get('name', 'Unknown')}님"
            account_ref = db.reference(f'users/{user_seq_no}/account')
            account_info = account_ref.get()
            if account_info:
                self.account_number_label.text = f"{account_info.get('account_num_masked', 'N/A')}"

    def logout(self, instance):
        login_screen = self.manager.get_screen('login')
        login_screen.clear_inputs()
        self.manager.current = 'start'

    def go_back_to_home(self, instance):
        self.manager.current = 'home'
