from firebase_admin import db
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.screenmanager import Screen
from kivy.uix.button import ButtonBehavior, Button

fontName1 = 'Hancom Gothic Bold.ttf'
fontName2 = 'Hancom Gothic Regular.ttf'

class ImageButton(ButtonBehavior, Image):
    pass

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super(HomeScreen, self).__init__(**kwargs)
        self.layout = FloatLayout()

        # 배경 이미지
        self.bg_image = Image(source='images/background.png', allow_stretch=True, keep_ratio=False)
        self.layout.add_widget(self.bg_image)
        # 프로필 사진
        self.profile_image = Image(source='images/profile_picture.png', size_hint=(0.1, 0.1), pos_hint={'x': 0.06, 'y': 0.88})
        self.layout.add_widget(self.profile_image)
        # 설정 버튼
        self.settings_button = ImageButton(source='images/settings_icon.png', size_hint=(0.1, 0.1), pos_hint={'x': 0.6, 'y': 0.88})
        self.settings_button.bind(on_press=self.open_settings)
        self.layout.add_widget(self.settings_button)
        # 알림 버튼
        self.notifications_button = ImageButton(source='images/notifications_off.png', size_hint=(0.1, 0.1), pos_hint={'x': 0.73, 'y': 0.88})
        self.notifications_button.bind(on_press=self.toggle_notifications)
        self.layout.add_widget(self.notifications_button)
        # 메뉴 버튼
        self.menu_button = ImageButton(source='images/menu_icon.png', size_hint=(0.1, 0.1), pos_hint={'x': 0.86, 'y': 0.88})
        self.menu_button.bind(on_press=self.open_menu)
        self.layout.add_widget(self.menu_button)
        # 계좌 목록 이미지
        self.account_bg_image = Image(source='images/account_background.png', size_hint=(0.9, 0.4), pos_hint={'x': 0.05, 'y': 0.58})
        self.layout.add_widget(self.account_bg_image)
        #아이콘
        self.icon_image = Image(source='images/icon.png', size_hint=(0.1, 0.1), pos_hint={'x': 0.1, 'y': 0.78})
        self.layout.add_widget(self.icon_image)
        #통장정보
        self.account_text_label = Label(text='SRV 통장', font_name=fontName2, font_size=14, size_hint=(0.45, 0.1), pos_hint={'x': 0.09, 'y': 0.795}, color=(1, 1, 1, 1))
        self.layout.add_widget(self.account_text_label)

        self.initial_balance_text_label = Label(text='출금가능금액', font_name=fontName2, font_size=18, size_hint=(0.45, 0.1), pos_hint={'x': 0.02, 'y': 0.7}, color=(1, 1, 1, 1))
        self.layout.add_widget(self.initial_balance_text_label)

        self.remaining_text_label = Label(text='1일 송금 잔여한도', font_name=fontName2, font_size=18, size_hint=(0.45, 0.1), pos_hint={'x': 0.07, 'y': 0.66}, color=(1, 1, 1, 1))
        self.layout.add_widget(self.remaining_text_label)
        #기능 목록
        self.function_bg_image = Image(source='images/function_background.png', size_hint=(0.9, 0.4), pos_hint={'x': 0.05, 'y': 0.43})
        self.layout.add_widget(self.function_bg_image)

        self.transaction_button = Button(text='거래내역', font_name=fontName1, font_size=16, size_hint=(0.1, 0.1),
                                         pos_hint={'x': 0.12, 'y': 0.58}, background_color=(0, 0, 0, 0),
                                         color=(1, 1, 1, 1))
        self.transaction_button.bind(on_press=self.show_transactions)
        self.layout.add_widget(self.transaction_button)

        self.transfer_button = Button(text='송금', font_name=fontName1, font_size=16, size_hint=(0.1, 0.1), pos_hint={'x': 0.78, 'y': 0.58}, background_color=(0, 0, 0, 0), color=(1, 1, 1, 1))
        self.transfer_button.bind(on_press=self.transfer_money)
        self.layout.add_widget(self.transfer_button)

        # 수신자
        self.receiver_label = Label(text='수신자', font_name=fontName1, font_size=20, size_hint=(0.1, 0.1), pos_hint={'x': 0.07, 'y': 0.48}, color=(0.3, 0.8, 0.6, 1))
        self.layout.add_widget(self.receiver_label)
        self.receiver_profile_image = Image(source='images/receiver_profile.png', size_hint=(0.9, 0.4), pos_hint={'x': 0.05, 'y': 0.27})
        self.layout.add_widget(self.receiver_profile_image)

        # 거래 내역
        self.last_transaction_label = Label(text='거래 내역', font_name=fontName1, font_size=20, size_hint=(0.1, 0.1), pos_hint={'x': 0.1, 'y': 0.35}, color=(0.3, 0.8, 0.6, 1))
        self.layout.add_widget(self.last_transaction_label)
        self.transaction_history_image1 = Image(source='images/transaction_history1.png', size_hint=(1, 0.2), pos_hint={'x': 0, 'y': 0.24})
        self.layout.add_widget(self.transaction_history_image1)
        self.transaction_history_image2 = Image(source='images/transaction_history2.png', size_hint=(1, 0.2), pos_hint={'x': 0, 'y': 0.17})
        self.layout.add_widget(self.transaction_history_image2)
        self.transaction_history_image3 = Image(source='images/transaction_history5.png', size_hint=(1, 0.2), pos_hint={'x': 0, 'y': 0.1})
        self.layout.add_widget(self.transaction_history_image3)
        self.transaction_history_image4 = Image(source='images/transaction_history4.png', size_hint=(1, 0.2), pos_hint={'x': 0, 'y': 0.03})
        self.layout.add_widget(self.transaction_history_image4)
        self.transaction_history_image5 = Image(source='images/transaction_history3.png', size_hint=(1, 0.1), pos_hint={'x': 0, 'y': 0})
        self.layout.add_widget(self.transaction_history_image5)

        user_data = db.reference('users').get()
        if user_data:
            account_data = list(user_data.values())[0]
            self.account_number = account_data['account_number']
            self.initial_balance = account_data['balance']
            self.remaining_limit = account_data['remaining_limit']
            self.welcome_text = account_data['name']

            # 환영 메시지
            self.welcome_label = Label(text=f'{self.welcome_text}님,\n반갑습니다!', font_name=fontName1, font_size=18,
                                               size_hint=(0.45, 0.1), pos_hint={'x': 0.1, 'y': 0.88},
                                               color=(0.1, 0.4, 0.8, 1))
            self.layout.add_widget(self.welcome_label)

            # 계좌 번호 레이블
            self.account_number_label = Label(text=f'{self.account_number}', font_name=fontName1, font_size=17,
                                              size_hint=(0.45, 0.1), pos_hint={'x': 0.2, 'y': 0.768},
                                              color=(1, 1, 1, 1))
            self.layout.add_widget(self.account_number_label)

            # 초기 금액 레이블
            self.balance_label = Label(text=f'{self.initial_balance}원', font_name=fontName1, font_size=22,
                                       size_hint=(0.45, 0.1), pos_hint={'x': 0.55, 'y': 0.7}, color=(1, 1, 1, 1))
            self.layout.add_widget(self.balance_label)

            # 1일 송금 잔여한도 레이블
            self.remaining_limit_label = Label(text=f'{self.remaining_limit}원', font_name=fontName2, font_size=18,
                                               size_hint=(0.45, 0.1), pos_hint={'x': 0.55, 'y': 0.66}, color=(1, 1, 1, 1))
            self.layout.add_widget(self.remaining_limit_label)

            self.balance2_label = Label(text=f'{self.initial_balance}원', font_name=fontName1, font_size=22,
                                       size_hint=(0.45, 0.1), pos_hint={'x': 0.27, 'y': 0.58}, color=(1, 1, 1, 1))
            self.layout.add_widget(self.balance2_label)

        self.add_widget(self.layout)

        self.notifications_enabled = False

    def open_settings(self, instance):
        # 설정 버튼 클릭 시 동작 정의
        print("Settings button pressed")

    def toggle_notifications(self, instance):
        # 알림 허용 버튼 클릭 시 동작 정의
        self.notifications_enabled = not self.notifications_enabled
        if self.notifications_enabled:
            self.notifications_button.source = 'images/notifications_on.png'
            print("Notifications enabled")
        else:
            self.notifications_button.source = 'images/notifications_off.png'
            print("Notifications disabled")

    def open_menu(self, instance):
        # 메뉴 버튼 클릭 시 동작 정의
        print("Menu button pressed")

    def show_transactions(self, instance):
        # 거래내역 버튼 클릭 시 동작 정의
        print("Transaction button pressed")

    def transfer_money(self, instance):
        # 송금 버튼 클릭 시 동작 정의
        print("Transfer button pressed")