from kivy.app import App
from firebase_admin import db
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import ButtonBehavior, Button
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.boxlayout import BoxLayout

fontName1 = 'Hancom Gothic Bold.ttf'
fontName2 = 'Hancom Gothic Regular.ttf'

class ImageButton(ButtonBehavior, Image):
    pass

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super(HomeScreen, self).__init__(**kwargs)
        self.layout = FloatLayout()
        self.sender_account = None  # sender_account 초기화 추가
        self.balance_label = None  # balance_label 초기화
        self.setup_ui()
        self.add_widget(self.layout)
        self.notifications_enabled = False
        self.accounts_data = []
        self.sender_account = None

    def setup_ui(self):
        # 배경 이미지
        self.bg_image = Image(source='images/background.png', allow_stretch=True, keep_ratio=False)
        self.layout.add_widget(self.bg_image)
        # 프로필 사진
        self.profile_image = Image(source='images/profile_picture.png', size_hint=(0.1, 0.1),
                                   pos_hint={'x': 0.06, 'y': 0.88})
        self.layout.add_widget(self.profile_image)
        # 설정 버튼
        self.settings_button = ImageButton(source='images/settings_icon.png', size_hint=(0.1, 0.1),
                                           pos_hint={'x': 0.6, 'y': 0.88})
        self.settings_button.bind(on_press=self.open_settings)
        self.layout.add_widget(self.settings_button)
        # 알림 버튼
        self.notifications_button = ImageButton(source='images/notifications_off.png', size_hint=(0.1, 0.1),
                                                pos_hint={'x': 0.73, 'y': 0.88})
        self.notifications_button.bind(on_press=self.toggle_notifications)
        self.layout.add_widget(self.notifications_button)
        # 메뉴 버튼
        self.menu_button = ImageButton(source='images/menu_icon.png', size_hint=(0.1, 0.1),
                                       pos_hint={'x': 0.86, 'y': 0.88})
        self.menu_button.bind(on_press=self.open_menu)
        self.layout.add_widget(self.menu_button)
        # 계좌 목록 이미지
        self.account_bg_image = Image(source='images/account_background.png', size_hint=(0.9, 0.4),
                                      pos_hint={'x': 0.05, 'y': 0.57})
        self.layout.add_widget(self.account_bg_image)

        self.icon_image = Image(source='images/icon.png', size_hint=(0.1, 0.1), pos_hint={'x': 0.1, 'y': 0.78})
        self.layout.add_widget(self.icon_image)

        self.transaction_button = Button(text='거래내역', font_name=fontName1, font_size=16, size_hint=(0.1, 0.1),
                                         pos_hint={'x': 0.23, 'y': 0.65}, background_color=(0, 0, 0, 0),
                                         color=(1, 1, 1, 1))
        self.transaction_button.bind(on_press=self.show_transactions)
        self.layout.add_widget(self.transaction_button)

        # 계좌 잔액 표시 라벨 추가
        self.balance_label = Label(text='', font_name=fontName1, font_size=22, size_hint=(0.45, 0.1),
                                   pos_hint={'x': 0.28, 'y': 0.72}, color=(1, 1, 1, 1))
        self.layout.add_widget(self.balance_label)


        # 송금 버튼 추가 (초기에는 버튼이 비활성화되어 있음)
        self.transfer_button = Button(text='송금', font_name=fontName1, font_size=16, size_hint=(0.1, 0.1),
                                      pos_hint={'x': 0.7, 'y': 0.65}, background_color=(0, 0, 0, 0),
                                      color=(1, 1, 1, 1))
        self.transfer_button.bind(on_press=self.on_transfer_button_pressed)
        self.layout.add_widget(self.transfer_button)

        # 거래 내역
        self.last_transaction_label = Label(text='최근 내역', font_name=fontName1, font_size=18, size_hint=(0.1, 0.1),
                                            pos_hint={'x': 0.11, 'y': 0.57}, color=(0.16, 0.66, 0.54, 1))
        self.layout.add_widget(self.last_transaction_label)

        # 거래 내역 레이아웃 추가 (최근 내역 라벨 바로 아래에 위치시킴)
        self.transaction_layout = BoxLayout(orientation='vertical', size_hint=(1, None), height=0, padding=[0, 0],
                                            spacing=5, pos_hint={'x': 0, 'top': 0.5})  # pos_hint top 값을 0.53으로 조정
        self.layout.add_widget(self.transaction_layout)

        # 거래 내역을 불러와 표시
        self.load_and_display_transactions()

    def load_user_data(self, user_seq_no, user_name):
        self.user_seq_no = user_seq_no
        self.user_name = user_name

        # Firebase에서 users/{name}/account 항목에서 계좌 정보 불러오기
        user_account_ref = db.reference(f'users/{self.user_name}/account')
        account_info = user_account_ref.get()

        if not account_info:
            return

        # 환영 메시지에 이름 표시
        self.welcome_label = Label(text=f'{self.user_name}님,\n반갑습니다!', font_name=fontName1,
                                   font_size=18, size_hint=(0.45, 0.1), pos_hint={'x': 0.1, 'y': 0.88},
                                   color=(0.1, 0.4, 0.8, 1))
        self.layout.add_widget(self.welcome_label)

        # 계좌 번호 표시 (account_num_masked)
        account_number = account_info.get('account_num_masked', 'N/A')
        account_number_label = Label(text=str(account_number), font_name=fontName1, font_size=17,
                                     size_hint=(0.45, 0.1), pos_hint={'x': 0.17, 'y': 0.793},
                                     color=(1, 1, 1, 1))
        self.layout.add_widget(account_number_label)

        # 통장 이름 표시 (fintech_use_num의 뒷자리 4개)
        fintech_use_num = account_info.get('fintech_use_num', '')
        account_name = f'SRV{fintech_use_num[-4:]} 통장'
        alias_label = Label(text=str(account_name), font_name=fontName2, font_size=13,
                            size_hint=(0.45, 0.1), pos_hint={'x': 0.115, 'y': 0.768},
                            color=(1, 1, 1, 1))
        self.layout.add_widget(alias_label)

        # 잔액 표시 (balance_amt)
        balance_amt = account_info.get('balance_amt', 0)
        self.balance_label.text = f'{balance_amt}원'

        self.sender_account = fintech_use_num  # 송금할 계좌 정보 저장
        self.load_and_display_transactions()  # 거래 내역을 올바른 sender_account로 표시

    def refresh_balance(self):
        """송금 후 잔액을 업데이트하는 함수"""
        if self.sender_account:
            account_data = db.reference(f'users/{self.user_name}/account').get()
            if account_data:
                self.balance_label.text = f'{account_data["balance_amt"]}원'

    def on_transfer_button_pressed(self, instance):
        # 송금 버튼을 누르면 송금 화면으로 넘어가며, 선택된 계좌를 전달
        if self.sender_account:
            transfer_screen = self.manager.get_screen('transfer')
            transfer_screen.sender_account = self.sender_account
            transfer_screen.user_name = self.user_name  # user_name 전달
            transfer_screen.sender_account_label.text = f"송금할 계좌: {self.sender_account}"
            self.manager.current = 'transfer'
        else:
            print("송금할 계좌가 없습니다.")  # 오류 메시지 출력

    def load_and_display_transactions(self):
        if not self.sender_account:
            print("No selected account to display transactions")
            return

        # Firebase에서 현재 표시된 계좌의 거래 데이터를 가져옵니다.
        transactions_ref = db.reference(f'users/{self.user_name}/account/transactions')
        transactions_data = transactions_ref.get()

        # 거래 내역을 처리할 때, 리스트와 딕셔너리 구분
        if isinstance(transactions_data, list):
            transactions = list(enumerate(transactions_data))  # 리스트인 경우
        elif isinstance(transactions_data, dict):
            transactions = list(transactions_data.items())  # 딕셔너리인 경우
        else:
            print("Unexpected transactions data format")
            return

        # 거래 내역 레이아웃을 초기화합니다.
        self.transaction_layout.clear_widgets()

        # 거래 내역 간의 간격을 줄이기 위해 spacing 값을 줄임
        self.transaction_layout.spacing = 5  # 간격을 줄이기 위해 spacing을 최소화

        # 각 거래 데이터를 화면에 표시합니다.
        for key, transaction in sorted(transactions, reverse=True):  # 역순으로 정렬
            if not transaction:  # 거래가 None이 아닌지 확인
                continue

            amount = transaction.get('amount', 0)
            date = transaction.get('date', '날짜 없음')
            description = transaction.get('description', '설명 없음')
            transaction_type = transaction.get('type', '거래 유형 없음')
            remaining_balance = transaction.get('balance', '잔액 없음')

            # 거래 내역을 포함할 레이아웃 생성
            transaction_layout = FloatLayout(size_hint_y=None, height=70)

            # 날짜 및 시간 레이블 추가
            datetime_label = Label(text=str(date), font_name=fontName2, font_size=15, color=(0.5, 0.5, 0.5, 1),
                                   size_hint=(None, None), pos_hint={'x': 0.14, 'y': 0.85})
            transaction_layout.add_widget(datetime_label)

            # 설명 레이블 추가
            description_label = Label(text=str(description), font_name=fontName1, font_size=22,
                                      color=(0, 0.7, 0.7, 1), size_hint=(None, None), size=(400,30),
                                      pos_hint={'x': 0.065, 'top': 1.45}, text_size=(400, None), halign='left')
            transaction_layout.add_widget(description_label)

            # 거래 금액 레이블 추가
            amount_label = Label(text=f"{'-' if transaction_type == '출금' else ''}{int(amount):,}원",
                                 font_name=fontName1,
                                 font_size=19, color=(1, 0, 0, 1) if transaction_type == '출금' else (0, 0.5, 0, 1),
                                 size_hint=(None, None), size=(150, 30),  # 레이블 크기 지정
                                 pos_hint={'right': 0.95, 'top': 1.5},
                                 text_size=(150, None), halign='right')  # 텍스트 크기 및 우측 정렬
            transaction_layout.add_widget(amount_label)

            # 남은 잔액 레이블 추가
            balance_label = Label(text=f"잔액: {int(remaining_balance)}원", font_name=fontName2, font_size=12,
                                  color=(0.5, 0.5, 0.5, 1), size_hint=(None, None), size=(150, 30),  # 레이블 크기 지정
                                  pos_hint={'right': 0.945, 'y': 0.8},
                                  text_size=(150, None), halign='right')  # 텍스트 크기 및 우측 정렬
            transaction_layout.add_widget(balance_label)

            # 구분선 이미지 추가
            separator_image = Image(source='images/separator.png', size_hint=(1, None), height=2,  # 이미지의 높이를 조절
                                    pos_hint={'center_x': 0.5, 'y': 0.7})  # y 위치 조정으로 구분선 위치 설정
            transaction_layout.add_widget(separator_image)

            # 거래 내역 레이아웃을 맨 위에 추가
            self.transaction_layout.add_widget(transaction_layout, index=0)  # 가장 위에 추가

        # 거래 내역 레이아웃의 높이를 동적으로 설정
        self.transaction_layout.height = len(transactions) * 70  # 레이블 수에 따라 동적 높이 설정

    def open_settings(self, instance):
        print("Settings button pressed")

    def toggle_notifications(self, instance):
        self.notifications_enabled = not self.notifications_enabled
        if self.notifications_enabled:
            self.notifications_button.source = 'images/notifications_on.png'
            print("Notifications enabled")
        else:
            self.notifications_button.source = 'images/notifications_off.png'
            print("Notifications disabled")

    def open_menu(self, instance):
        print("Menu button pressed")

    def show_transactions(self, instance):
        print("Transaction button pressed")

    def transfer_money(self, instance):
        print("Transfer button pressed")

class MyApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name='home'))
        return sm

if __name__ == '__main__':
    MyApp().run()
