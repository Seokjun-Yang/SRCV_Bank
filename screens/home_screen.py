import requests
from kivy.app import App
from firebase_admin import db
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import ButtonBehavior, Button
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from datetime import datetime
import sounddevice as sd
import numpy as np
import base64

from kivy.config import Config

Config.set('graphics', 'dpi', '320')  # DPI를 높게 설정하여 텍스트와 화면을 선명하게

fontName1 = 'LINESeedKR-Bd.ttf'
fontName2 = 'LINESeedKR-Rg.ttf'

class ImageButton(ButtonBehavior, Image):
    pass

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super(HomeScreen, self).__init__(**kwargs)
        self.layout = FloatLayout()
        self.sender_account = None
        self.balance_label = None
        self.notifications_enabled = False
        self.accounts_data = []

        self.setup_ui()
        self.add_widget(self.layout)

    def setup_ui(self):
        # 배경 이미지
        self.bg_image = Image(source='images/home_background.png', allow_stretch=True, keep_ratio=False)
        self.layout.add_widget(self.bg_image)

        # 상단 사용자 정보 영역
        self.profile_image = Image(source='images/profile_picture.png', allow_stretch=True, keep_ratio=False,
            size_hint=(0.116, 0.058), pos_hint={'x': 0.076, 'top': 0.956}
        )
        self.layout.add_widget(self.profile_image)

        self.welcome_label = Label(text="환영", font_name=fontName1, font_size=19, color=(1, 1, 1, 1), halign='left', valign='middle',
                                   size_hint=(0.5, None), height=30, pos_hint={'x': 0.22, 'top': 0.95})
        self.welcome_label.bind(size=self.welcome_label.setter('text_size'))
        self.layout.add_widget(self.welcome_label)

        self.menu_button = ImageButton(source='images/menu_icon.png', allow_stretch=True, keep_ratio=False,
                                           size_hint=(0.083, 0.042), pos_hint={'x': 0.843, 'top': 0.948})
        self.layout.add_widget(self.menu_button)

        # 카드형 계좌 정보 영역
        self.account_card = Image(source='images/account.png', allow_stretch=True, keep_ratio=False,
                                  size_hint=(0.85, 0.25), pos_hint={'center_x': 0.5, 'top': 0.86})
        self.layout.add_widget(self.account_card)

        self.account_number_label = Label(text="계좌번호", font_name=fontName1, font_size=19, color=(1, 1, 1, 1), halign='left', valign='middle',
                                          size_hint=(0.7, None), height=30, pos_hint={'x': 0.12, 'top': 0.85})
        self.account_number_label.bind(size=self.account_number_label.setter('text_size'))
        self.layout.add_widget(self.account_number_label)

        self.alias_label = Label(text="통장이름", font_name=fontName2, font_size=15, color=(1, 1, 1, 1),
                                 size_hint=(0.403, 0.018), pos_hint={'x': 0.055, 'top': 0.811})
        self.layout.add_widget(self.alias_label)

        self.icon = Image(source='images/icon.png', allow_stretch=True, keep_ratio=False,
                          size_hint=(0.1, 0.05), pos_hint={'x': 0.783, 'top': 0.845})
        self.layout.add_widget(self.icon)

        self.balance_shadow_label = Label(text="잔액", font_name=fontName1, font_size=35, color=(0.553, 0.725, 0.573, 1),
                                          size_hint=(0.503, 0.035), pos_hint={'center_x': 0.505, 'top': 0.726})
        self.layout.add_widget(self.balance_shadow_label)
        self.balance_label = Label(text="잔액", font_name=fontName1, font_size=35, color=(1, 1, 1, 1),
                                   size_hint=(0.503, 0.035), pos_hint={'center_x': 0.5, 'top': 0.731})
        self.layout.add_widget(self.balance_label)

        # 송금 버튼
        self.transfer_button = ImageButton(source='images/transfer_button.png', allow_stretch=True, keep_ratio=False,
                                           size_hint=(0.39, 0.12), pos_hint={'x': 0.54, 'top': 0.586})
        self.transfer_button.bind(on_press=self.on_transfer_button_pressed)
        self.layout.add_widget(self.transfer_button)

        # 거래 내역 영역
        self.last_transaction_label = Label(text="거래 내역", font_name=fontName1, font_size=20, color=(0, 0, 0, 1),
                                            size_hint=(0.203, 0.018), pos_hint={'x': 0.07, 'top': 0.485})
        self.layout.add_widget(self.last_transaction_label)

        # ScrollView를 사용하여 거래 내역 스크롤 가능하게 설정
        self.scroll_view = ScrollView(size_hint=(0.9, 0.3), pos_hint={'center_x': 0.5, 'top': 0.43})
        self.transaction_layout = BoxLayout(orientation='vertical', size_hint_y=None, padding=[10, 5], spacing=5)
        self.transaction_layout.bind(minimum_height=self.transaction_layout.setter('height'))
        self.scroll_view.add_widget(self.transaction_layout)
        self.layout.add_widget(self.scroll_view)

        # 거래 내역 불러오기
        self.load_and_display_transactions()

        #하단 메뉴 영역
        self.home_button = ImageButton(source='images/home_icon.png', allow_stretch=True, keep_ratio=False,
                                           size_hint=(0.073, 0.036), pos_hint={'x': 0.176, 'top': 0.081})
        self.layout.add_widget(self.home_button)

        self.voice_button = ImageButton(source='images/voice_icon.png', allow_stretch=True,
                                           size_hint=(0.18, 0.09), pos_hint={'center_x': 0.5, 'top': 0.105})
        self.voice_button.bind(on_press=self.on_voice_button_pressed)
        self.layout.add_widget(self.voice_button)

        self.info_button = ImageButton(source='images/info_icon.png', allow_stretch=True, keep_ratio=False,
                                           size_hint=(0.073, 0.036), pos_hint={'x': 0.753, 'top': 0.081})
        self.info_button.bind(on_press=self.go_to_my_page)
        self.layout.add_widget(self.info_button)

    def load_user_data(self, user_seq_no):
        self.user_seq_no = user_seq_no
        # Firebase에서 정보 불러오기
        user_info_ref = db.reference(f'users/{self.user_seq_no}/user_info')
        user_info = user_info_ref.get()

        if user_info:
            self.user_name = user_info.get('name', 'Unknown')
            self.welcome_label.text = f"안녕하세요, {self.user_name}님!"

        # Firebase에서 계좌 정보 불러오기
        user_account_ref = db.reference(f'users/{self.user_seq_no}/account')
        account_info = user_account_ref.get()
        if account_info:
            account_number = account_info.get('account_num_masked', 'N/A')
            self.account_number_label.text = str(account_number)

            fintech_use_num = account_info.get('fintech_use_num', '')
            self.alias_label.text = f'SRV{fintech_use_num[-4:]} 통장'

            balance_amt = account_info.get('balance_amt', 0)
            self.balance_label.text = f'{balance_amt:,}원'
            balance_amt = account_info.get('balance_amt', 0)
            self.balance_shadow_label.text = f'{balance_amt:,}원'

            self.sender_account = fintech_use_num
            self.load_and_display_transactions()

    def refresh_balance(self):
        """송금 후 홈 화면의 잔액을 업데이트하는 함수"""
        if self.user_seq_no:
            account_data = db.reference(f'users/{self.user_seq_no}/account').get()
            if account_data:
                balance_amt = account_data.get('balance_amt', 0)
                self.balance_label.text = f'{balance_amt:,}원'
                self.balance_shadow_label.text = f'{balance_amt:,}원'
            else:
                print("계좌 데이터를 불러올 수 없습니다.")
        else:
            print("유효한 사용자 번호가 없습니다.")

    def on_transfer_button_pressed(self, instance):
        # 송금 버튼을 누르면 송금 화면으로 넘어가며, 선택된 계좌를 전달
        if self.sender_account:
            transfer_screen = self.manager.get_screen('transfer')
            transfer_screen.sender_account = self.sender_account
            transfer_screen.user_seq_no = self.user_seq_no
            self.manager.current = 'transfer'
        else:
            print("송금할 계좌가 없습니다.")  # 오류 메시지 출력

    def load_and_display_transactions(self):
        if not self.sender_account:
            return

        # Firebase에서 현재 표시된 계좌의 거래 데이터를 가져옵니다.
        transactions_ref = db.reference(f'users/{self.user_seq_no}/account/transactions')
        transactions_data = transactions_ref.get()

        # 거래 내역이 없거나 초기 값만 있는 경우 확인
        if not transactions_data or (
                isinstance(transactions_data, list) and len(transactions_data) == 1 and
                transactions_data[0].get('amount') == 0 and
                transactions_data[0].get('balance') == 0 and
                transactions_data[0].get('date') == "No Date" and
                transactions_data[0].get('description') == "no transactions" and
                transactions_data[0].get('type') == "정보 없음"
        ):
            if self.scroll_view in self.layout.children:
                self.layout.remove_widget(self.scroll_view)

            empty_layout = FloatLayout(size_hint=(1, 1))

            # 빈 거래 내역 이미지 추가
            empty_image = Image(source='images/empty_basket.jpg',
                                size_hint=(None, None), size=(180, 180), pos_hint={'center_x': 0.5, 'center_y': 0.33})
            empty_layout.add_widget(empty_image)

            # 거래 내역 없음 텍스트 추가
            no_transactions_label = Label(text="거래 내역이 없습니다", font_name=fontName1, font_size=20,
                                          color=(0.267, 0.388, 0.278, 1), size_hint=(None, None), size=(200, 50),
                                          pos_hint={'center_x': 0.5, 'center_y': 0.19},
                                          text_size=(200, None), halign="center", valign="middle")
            no_transactions_label.bind(size=no_transactions_label.setter('text_size'))
            empty_layout.add_widget(no_transactions_label)

            # 레이아웃에 빈 상태 레이아웃 추가
            self.layout.add_widget(empty_layout)

            return

        if self.scroll_view not in self.layout.children:
            self.layout.add_widget(self.scroll_view)

        self.transaction_layout.clear_widgets()  # 기존 거래 내역을 초기화

        if isinstance(transactions_data, list):
            transactions = list(enumerate(transactions_data))  # 리스트인 경우
        elif isinstance(transactions_data, dict):
            transactions = list(transactions_data.items())  # 딕셔너리인 경우
        else:
            print("Unexpected transactions data format")
            return

        # 거래 내역 간의 간격을 줄이기 위해 spacing 값을 줄임
        self.transaction_layout.spacing = 0  # 간격을 줄이기 위해 spacing을 최소화

        # 각 거래 데이터를 화면에 표시합니다.
        for i, (key, transaction) in enumerate(sorted(transactions, key=lambda x: x[0], reverse=True)):
            if not transaction:
                continue

            amount = transaction.get('amount', 0)
            date = transaction.get('date', '날짜 없음')
            description = transaction.get('description', '설명 없음')
            transaction_type = transaction.get('type', '거래 유형 없음')

            # 거래 내역을 포함할 레이아웃 생성
            transaction_layout = FloatLayout(size_hint_y=None, height=80)

            # 설명 레이블 추가
            description_label = Label(
                text=str(description), font_name=fontName1, font_size=19, color=(0, 0, 0, 1),
                size_hint=(None, None), size=(400, 30), pos_hint={'x': 0.06, 'y': 0.62},
                halign='left', valign='middle', text_size=(400, None), mipmap=True
            )
            transaction_layout.add_widget(description_label)

            # 날짜 및 시간 레이블 추가
            datetime_label = Label(
                text=str(date), font_name=fontName1, font_size=13, color=(0.5, 0.5, 0.5, 1),
                size_hint=(None, None), size=(100, 70), pos_hint={'x': 0.06, 'y': 0.02},
                halign='left', valign='middle', text_size=(100, 70), mipmap=True
            )
            transaction_layout.add_widget(datetime_label)

            # 거래 금액 레이블 추가
            amount_label = Label(
                text=f"{'+ ' if transaction_type == '입금' else '- ' if transaction_type == '출금' else ''}{int(amount):,}",
                font_name=fontName1, font_size=19,
                color=(0.68, 0.29, 0.29, 1) if transaction_type == '출금' else (0.29, 0.36, 0.29, 1),
                size_hint=(None, None), size=(100, 70), pos_hint={'x': 0.62, 'y': 0.22},
                halign='right', valign='middle', text_size=(100, 70), mipmap=True
            )
            transaction_layout.add_widget(amount_label)

            # 거래 내역 레이아웃을 맨 위에 추가
            self.transaction_layout.add_widget(transaction_layout, index=0)

        # 거래 내역 레이아웃의 높이를 동적으로 설정
        self.transaction_layout.height = len(transactions) * 70  # 레이블 수에 따라 동적 높이 설정

    def on_voice_button_pressed(self, instance):
        # 음성 데이터를 녹음하여 base64로 변환
        simulated_transcription = "원혁주에게 만원 보내줘"

        response = requests.post(
            "https://us-central1-bank-a752e.cloudfunctions.net/recognizeSpeech",
            json={"text": simulated_transcription}  # 음성 데이터 대신 임의의 텍스트 전송
        )
        if response.status_code == 200:
            result = response.json()
            recipient = result.get("recipient")
            amount = result.get("amount")

            if recipient and amount:
                # 송금 화면을 가져와 수신자와 금액을 표시
                transfer_screen = self.manager.get_screen('transfer')
                transfer_screen.selected_receiver_account = self.find_user_by_name(recipient)
                transfer_screen.account_info_label.text = f"{recipient}"
                transfer_screen.amount_input.text = str(amount)

                # 송금 화면으로 전환
                self.manager.current = 'transfer'
            else:
                print("수신자 또는 금액 정보가 서버에서 올바르게 전달되지 않았습니다.")
        else:
            print("음성 인식 오류:", response.text)
    def get_audio_data(self):
        """사용자 음성을 녹음하고 음성 데이터를 Base64로 변환하여 반환"""
        duration = 5  # 녹음 시간 (초)
        sample_rate = 16000  # 샘플링 속도

        print("녹음을 시작합니다...")
        audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
        sd.wait()  # 녹음이 끝날 때까지 대기
        print("녹음이 완료되었습니다.")

        # 음성 데이터를 Base64로 인코딩하여 반환
        audio_data = np.squeeze(audio)
        audio_base64 = base64.b64encode(audio_data.tobytes()).decode('utf-8')

        return audio_base64

    def find_user_by_name(self, name):
        """이름으로 사용자 정보 찾기 (Firebase에서 이름을 통한 조회를 시뮬레이션)"""
        users_ref = db.reference('users')
        users_data = users_ref.get()
        for user_seq_no, user_info in users_data.items():
            if user_info.get('user_info', {}).get('name') == name:
                return user_seq_no
        return None

    def go_to_my_page(self, instance):
        my_page_screen = self.manager.get_screen('info')
        my_page_screen.load_user_info(self.user_seq_no)
        self.manager.current = 'info'

class MyApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name='home'))
        return sm

if __name__ == '__main__':
    MyApp().run()
