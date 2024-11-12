import requests
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from firebase_admin import db
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from datetime import datetime
class ImageButton(ButtonBehavior, Image):
    pass

fontName1 = 'LINESeedKR-Bd.ttf'
fontName2 = 'LINESeedKR-Rg.ttf'

class LeftAlignedButton(ButtonBehavior, Label):
    pass

class TransferScreen(Screen):
    def __init__(self, **kwargs):
        super(TransferScreen, self).__init__(**kwargs)
        self.user_seq_no = None
        self.sender_account = None
        self.selected_receiver_account = None
        self.layout = FloatLayout()

        # 배경 이미지
        self.bg_image = Image(source='images/transfer_background.png', allow_stretch=True, keep_ratio=False)
        self.layout.add_widget(self.bg_image)

        # Back 버튼
        self.back_button = ImageButton(source='images/back_button.png', allow_stretch=True, keep_ratio=False,
                                       size_hint=(None, None), size=(25, 25), pos_hint={'x': 0.06, 'top': 0.94})
        self.back_button.bind(on_press=self.go_back_to_home)
        self.layout.add_widget(self.back_button)
        # "홈" 텍스트
        self.home_text = Label(text="홈", font_name=fontName1, font_size=20, pos_hint={'x': 0.153, 'top': 0.932},
                               size_hint=(0.046, 0.018), color=(0.447, 0.749, 0.471, 1))
        self.layout.add_widget(self.home_text)
        # 송금안내 텍스트
        self.information_text = Label(text="돈을 보내려면\n아래 항목을 입력해주세요.", font_name=fontName1, font_size=17,
                                      pos_hint={'x': 0.093, 'top': 0.876}, size_hint=(0.446, 0.042),
                                      color=(0.227, 0.231, 0.224, 1))
        self.layout.add_widget(self.information_text)

        # 계좌 선택 버튼
        self.select_account_button = ImageButton(source='images/plus_icon.png', size_hint=(None, None), size=(50, 50),
                                                 pos_hint={'x': 0.163, 'top': 0.721})
        self.select_account_button.bind(on_press=self.show_account_selection_popup)
        self.layout.add_widget(self.select_account_button)
        # 계좌 정보 표시 레이블
        self.account_info_label = Label(text="누구에게 송금할까요?", font_name=fontName1, font_size=18,
                                        pos_hint={'x': 0.27, 'top': 0.721}, size_hint=(None, None), line_height=1.3,
                                        size=(200, 50), color=(0, 0, 0, 1), halign='left', valign='middle')
        self.account_info_label.bind(size=self.account_info_label.setter('text_size'))
        self.layout.add_widget(self.account_info_label)

        # 송금 금액 입력 창
        self.amount_input = TextInput(hint_text='0.0', font_name=fontName1, font_size=55, multiline=False,
                                      size_hint=(0.583, None), height=120,
                                      pos_hint={'center_x': 0.5, 'center_y': 0.5}, background_color=(0, 0, 0, 0),
                                      hint_text_color=(0.8, 0.8, 0.8, 1), foreground_color=(0.431, 0.431, 0.431, 1),
                                      halign='center')
        self.amount_input.padding_y = [self.amount_input.height / 2 - self.amount_input.line_height / 2, 0]
        self.layout.add_widget(self.amount_input)

        # 출금 가능 금액 표시 레이블
        self.balance_layout_image = Image(source='images/balance_layout.png', size_hint=(0.676, 0.075),
                                          pos_hint={'center_x': 0.5, 'top': 0.296})
        self.layout.add_widget(self.balance_layout_image)
        self.balance_icon_image = Image(source='images/balance_icon.png', size_hint=(None, None), size=(25, 25),
                                        pos_hint={'x': 0.213, 'top': 0.275})
        self.layout.add_widget(self.balance_icon_image)
        self.balance_label = Label(text="", font_name=fontName1, font_size=18,
                                   color=(0.354, 0.58, 0.369, 1), size_hint=(0.46, 0.05), halign='left',
                                   pos_hint={'x': 0.316, 'top': 0.285})
        self.layout.add_widget(self.balance_label)

        # 송금 버튼
        self.transfer_button = ImageButton(source='images/transfer_button_2.png', size_hint=(0.84, 0.083),
                                           pos_hint={'center_x': 0.5, 'top': 0.14})
        self.transfer_button.bind(on_press=self.transfer_money_button_pressed)
        self.layout.add_widget(self.transfer_button)

        self.add_widget(self.layout)

    # 홈 화면으로 돌아가는 함수
    def go_back_to_home(self, instance):
        App.get_running_app().speak_text('홈 화면으로 돌아갑니다.')
        Clock.schedule_once(lambda dt: App.get_running_app().delay, 2)
        Clock.schedule_once(lambda dt:self.change_screen('home'), 1)

    def on_enter(self):
        # 송금 화면에 들어올 때 입력값 초기화
        self.amount_input.text = ""
        self.account_info_label.text = "누구에게 송금할까요?"
        self.selected_receiver_account = None
        self.load_balance_info()  # 잔액 정보 로드
        App.get_running_app().speak_text(self.account_info_label.text)


    def load_balance_info(self):
        if hasattr(self, 'user_seq_no'):
            account_ref = db.reference(f'users/{self.user_seq_no}/account')
            account_info = account_ref.get()
            if account_info:
                balance_amt = account_info.get('balance_amt', 0)
                self.balance_label.text = f'송금 가능 금액: {balance_amt:,}'
            else:
                self.balance_label.text = "잔액 정보를 불러올 수 없습니다."
        else:
            self.balance_label.text = "유효한 계좌 정보가 없습니다."

    def show_account_selection_popup(self, instance):
        ref = db.reference('users')
        users_data = ref.get()

        if not users_data:
            return

        App.get_running_app().speak_text('송금할 계좌를 선택해주세요.')
        Clock.schedule_once(lambda dt: App.get_running_app().delay, 2)

        all_accounts = {}
        for user_seq_no, user_data in users_data.items():
            # user_data가 dict인지 확인하여 `bool` 타입이 아닌 경우에만 진행
            if isinstance(user_data, dict):
                account_data = user_data.get('account')
                user_info = user_data.get('user_info')
                if account_data and isinstance(account_data, dict) and user_info:
                    all_accounts[user_seq_no] = {
                        'account_num_masked': account_data.get('account_num_masked', 'N/A'),
                        'name': user_info.get('name', 'Unknown')
                    }

        if not all_accounts:
            return

        # 팝업의 전체 레이아웃을 FloatLayout으로 설정
        popup_layout = FloatLayout(size_hint=(1, 1))

        # "최근 이체" 텍스트 추가 (상단에 위치)
        recent_transfer_label = Label(
            text="[color=#29A98B]최근 이체[/color]",
            font_name=fontName2,
            markup=True,
            size_hint=(None, None),
            size=(100, 50),
            pos_hint={'x': 0.01, 'y': 1},
            halign='left'
        )
        recent_transfer_label.bind(size=recent_transfer_label.setter('text_size'))
        popup_layout.add_widget(recent_transfer_label)

        # "최근 이체" 아래에 이미지 추가
        recent_transfer_image = Image(
            source='images/recent_transfer_icon.png',
            size_hint=(None, None),
            size=(100, 50),
            pos_hint={'x': 0.1, 'y': 0.82}
        )
        popup_layout.add_widget(recent_transfer_image)

        # 계좌 목록을 담을 레이아웃 생성
        account_layout = GridLayout(cols=1, size_hint_y=None)
        account_layout.bind(minimum_height=account_layout.setter('height'))

        # 모든 사용자들의 계좌 목록 추가
        for account_key, account in all_accounts.items():
            button_text = f"[color=#000000]{account['name']}[/color]\n[color=#29A98B]{account['account_num_masked']}[/color]"

            account_button = Button(
                text=button_text,
                size_hint_y=None, height=50, font_name=fontName2,
                text_size=(300, None),
                markup=True,
                background_normal='',
                background_down='',
                halign='center', valign='middle'
            )
            account_button.bind(on_release=lambda btn, f=account_key: self.select_account(f))
            account_layout.add_widget(account_button)

            # 계좌 목록 사이에 구분 이미지 추가
            separator_image = Image(source='images/separator.png', size_hint_y=None, height=20)
            account_layout.add_widget(separator_image)

        # ScrollView에 GridLayout 추가 (계좌 목록을 스크롤할 수 있도록 설정)
        scroll_view = ScrollView(size_hint=(1, 0.6), pos_hint={'x': 0, 'y': 0.35})
        scroll_view.add_widget(account_layout)

        # FloatLayout에 ScrollView 추가
        popup_layout.add_widget(scroll_view)

        # 팝업 생성 및 배경 설정
        self.account_popup = Popup(
            title="계좌 선택",
            content=popup_layout,
            size_hint=(None, None),
            size=(350, 450),
            background='images/account_select_background.png',
            background_color=(1, 1, 1, 1)
        )

        # 팝업 열기
        self.account_popup.open()

    def select_account(self, user_seq_no):
        """계좌 선택 시 계좌 정보를 표시하고 송금 대상 설정"""
        account_data = get_account_data(user_seq_no)
        if account_data:
            self.selected_receiver_account = user_seq_no
            account_num_masked = account_data.get('account_num_masked', 'N/A')
            receiver_name = db.reference(f'users/{user_seq_no}/user_info/name').get()
            self.account_info_label.text = f"{account_num_masked}\n{receiver_name}"

            App.get_running_app().speak_text(f'{receiver_name}의 계좌를 선택했습니다.')
            Clock.schedule_once(lambda dt:App.get_running_app().delay, 2)
            self.account_popup.dismiss()
        else:
            self.status_label.text = "계좌 정보를 불러올 수 없습니다." #???
            App.get_running_app().speak_text(self.status_label.text)
            Clock.schedule_once(lambda dt:App.get_running_app().delay, 2)

    def transfer_money_button_pressed(self, instance):
        receiver_account = self.selected_receiver_account
        amount = self.amount_input.text

        if not self.sender_account or not receiver_account or not amount:
            return

        # 송금 기능 호출 및 거래 내역 기록
        result_message = transfer_money(self.user_seq_no, self.sender_account, receiver_account, amount)
        print(result_message)

        # 거래 내역 정보를 가져와서 완료 화면으로 전달
        date = datetime.now().strftime('%Y-%m-%d')
        am_pm = datetime.now().strftime('%p')
        am_pm_korean = '오전' if am_pm == 'AM' else '오후'
        time = f"{am_pm_korean} {datetime.now().strftime('%I:%M')}"
        receiver_name = db.reference(f'users/{receiver_account}/user_info/name').get()

        # 송금 완료 화면으로 전환
        complete_screen = self.manager.get_screen('transfer_complete')
        complete_screen.set_transfer_info(
            date=date,
            time=time,
            receiver=receiver_name,
            amount=int(amount)
        )
        complete_screen.set_user_seq_no(self.user_seq_no)  # user_seq_no 설정

        App.get_running_app().speak_text(f'{receiver_name}에게 {amount}원을송금합니다.')
        Clock.schedule_once(lambda dt:App.get_running_app().delay, 2)
        Clock.schedule_once(lambda dt:self.change_screen('transfer_complete'), 0.5)
        #self.manager.current = 'transfer_complete'

        self.update_home_balance_and_transactions()

    def update_home_balance_and_transactions(self):
        """홈 화면에 있는 계좌 잔액 및 거래 내역 정보를 업데이트하는 함수"""
        home_screen = self.manager.get_screen('home')
        if home_screen:
            home_screen.refresh_balance()
            home_screen.load_and_display_transactions()
    def change_screen(self, screen):
        self.manager.current = screen

def get_account_data(user_seq_no):
    """Firebase에서 user_seq_no을 통해 계좌 데이터를 가져오는 함수"""
    ref = db.reference(f'users/{user_seq_no}/account')
    return ref.get()

def update_account_balance(user_seq_no, new_balance):
    """Firebase에서 계좌 잔액을 업데이트하는 함수"""
    ref = db.reference(f'users/{user_seq_no}/account')
    ref.update({'balance_amt': new_balance})

def record_transaction(user_seq_no, amount, transaction_type, description, new_balance):
    """거래 내역 기록 함수 """
    transaction_ref = db.reference(f'users/{user_seq_no}/account/transactions')
    transactions = transaction_ref.get()

    # 초기 거래 데이터를 'initial'로 지정했다면 삭제
    if transactions and isinstance(transactions, list):
        # 거래 내역 중에서 'initial' 데이터를 찾아 삭제
        for i, transaction in enumerate(transactions):
            if transaction and transaction.get('description') == 'no transactions':
                transaction_ref.child(str(i)).delete()  # 해당 인덱스의 데이터를 삭제
                break
    elif transactions and isinstance(transactions, dict):
        # 'initial' 거래 내역을 딕셔너리에서 찾아 삭제
        for key, transaction in transactions.items():
            if transaction and transaction.get('description') == 'no transactions':
                transaction_ref.child(key).delete()  # 해당 키의 데이터를 삭제
                break

    transaction_ref.push({
        'amount': amount,
        'type': transaction_type,
        'description': description,
        'balance': new_balance,
        'date': datetime.now().strftime('%Y.%m.%d')
    })

def transfer_money(sender_seq_no, sender_account, receiver_seq_no, amount):
    """송금 기능 구현 함수 (users/{user_seq_no}/account 기반)"""
    sender_data = get_account_data(sender_seq_no)
    receiver_data = get_account_data(receiver_seq_no)

    # 송신자와 수신자의 이름 가져오기
    sender_name = db.reference(f'users/{sender_seq_no}/user_info/name').get()
    receiver_name = db.reference(f'users/{receiver_seq_no}/user_info/name').get()

    if sender_data is None:
        return "송금 계좌 정보를 불러올 수 없습니다."
    if receiver_data is None:
        return "수신 계좌 정보를 불러올 수 없습니다."

    if int(sender_data['balance_amt']) < int(amount):
        return "잔액이 부족합니다."

    sender_new_balance = int(sender_data['balance_amt']) - int(amount)
    receiver_new_balance = int(receiver_data['balance_amt']) + int(amount)

    update_account_balance(sender_seq_no, sender_new_balance)
    update_account_balance(receiver_seq_no, receiver_new_balance)

    record_transaction(sender_seq_no, amount, '출금', f'{receiver_name}에게 송금', sender_new_balance)
    record_transaction(receiver_seq_no, amount, '입금', f'{sender_name}로부터 입금', receiver_new_balance)

    return f'{amount}원이 {receiver_name}에게 송금되었습니다.'
