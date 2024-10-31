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

import requests

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
        self.bg_image = Image(source='images/background.png', allow_stretch=True, keep_ratio=False)
        self.layout.add_widget(self.bg_image)

        # "송금" 텍스트
        self.sender_account_text = Label(text="송금", font_name=fontName1, font_size=20,
                                         pos_hint={'x': 0.05, 'y': 0.9}, size_hint=(0.3, 0.05),
                                         color=(0.1, 0.4, 0.8, 1))
        self.layout.add_widget(self.sender_account_text)

        # Back 버튼 추가
        self.back_button = ImageButton(
            source='images/back_button.png',
            size_hint=(None, None), size=(30, 30),
            pos_hint={'x': 0.04, 'y': 0.902}
        )
        self.back_button.bind(on_press=self.go_back_to_home)
        self.layout.add_widget(self.back_button)

        # 출금 계좌 배경 이미지 추가
        self.account_bg_image = Image(source='images/transaction_background.png', size_hint=(0.9, 0.3),
                                      pos_hint={'x': 0.05, 'y': 0.63})
        self.layout.add_widget(self.account_bg_image)

        # 아이콘
        self.icon_image = Image(source='images/icon.png', size_hint=(0.13, 0.13), pos_hint={'x': 0.078, 'y': 0.765})
        self.layout.add_widget(self.icon_image)

        # 계좌번호 표시 레이블
        self.sender_account_label = Label(
            text="", font_name=fontName1, font_size=18, pos_hint={'x': 0.22, 'y': 0.83},
            size_hint=(0.6, 0.05), color=(1, 1, 1, 1), halign='left')
        self.sender_account_label.bind(size=self.sender_account_label.setter('text_size'))
        self.layout.add_widget(self.sender_account_label)

        # 통장 이름 표시 레이블
        self.account_details_label = Label(
            text="", font_name=fontName2, font_size=14, pos_hint={'x': 0.225, 'y': 0.8},
            size_hint=(0.3, 0.05), color=(1, 1, 1, 1), halign='left')
        self.account_details_label.bind(size=self.account_details_label.setter('text_size'))
        self.layout.add_widget(self.account_details_label)

        # 출금 가능 금액 표시 레이블
        self.available_balance_label_text = Label(
            text="출금 가능 금액", font_name=fontName2, font_size=14, pos_hint={'x': 0.09, 'y': 0.736},
            size_hint=(0.3, 0.05), color=(1, 1, 1, 1), halign='left')
        self.available_balance_label_text.bind(size=self.available_balance_label_text.setter('text_size'))
        self.layout.add_widget(self.available_balance_label_text)

        # 출금 가능 금액 숫자 표시
        self.available_balance_label = Label(
            text="", font_name=fontName1, font_size=20, pos_hint={'x': 0.515, 'y': 0.732},
            size_hint=(0.4, 0.05), color=(1, 1, 1, 1), halign='right')
        self.available_balance_label.bind(size=self.available_balance_label.setter('text_size'))
        self.layout.add_widget(self.available_balance_label)

        # 1일 송금 잔여한도 텍스트 레이블
        self.daily_limit_label_text = Label(
            text="1일 송금 잔여한도", font_name=fontName2, font_size=12, pos_hint={'x': 0.09, 'y': 0.704},
            size_hint=(0.4, 0.05), color=(1, 1, 1, 1), halign='left')
        self.daily_limit_label_text.bind(size=self.daily_limit_label_text.setter('text_size'))
        self.layout.add_widget(self.daily_limit_label_text)

        # 1일 송금 잔여한도 금액 레이블
        self.daily_limit_label = Label(
            text="5,000,000원", font_name=fontName1, font_size=14, pos_hint={'x': 0.51, 'y': 0.702},
            size_hint=(0.4, 0.05), color=(1, 1, 1, 1), halign='right')
        self.daily_limit_label.bind(size=self.daily_limit_label.setter('text_size'))
        self.layout.add_widget(self.daily_limit_label)

        # 배경 이미지 추가
        self.receiver_account_bg = Image(source='images/input_background.png', size_hint=(0.83, 0.1),
                                         pos_hint={'x': 0.08, 'y': 0.53})
        self.layout.add_widget(self.receiver_account_bg)

        # 계좌번호 버튼 생성
        self.receiver_account_input = LeftAlignedButton(
            text='계좌번호', font_name=fontName2, halign='left', valign='middle',
            size_hint=(0.8, 0.1), pos_hint={'x': 0.1, 'y': 0.53},
            color=(1, 1, 1, 1), padding=(8, 0)
        )

        self.receiver_account_input.bind(size=lambda instance, value: setattr(instance, 'text_size', (instance.width, None)))
        self.receiver_account_input.bind(on_press=self.show_account_selection_popup)
        self.layout.add_widget(self.receiver_account_input)

        # 송금 금액 입력 창
        self.amount_bg = Image(source='images/input_background.png', size_hint=(0.83, 0.1),
                               pos_hint={'x': 0.08, 'y': 0.41})
        self.layout.add_widget(self.amount_bg)

        self.amount_input = TextInput(hint_text='금액', font_name=fontName2, multiline=False, size_hint=(0.9, 0.1),
            pos_hint={'x': 0.11, 'y': 0.385}, background_color=(0, 0, 0, 0), hint_text_color=(1, 1, 1, 1))
        self.layout.add_widget(self.amount_input)

        # 송금 버튼
        self.transfer_button = ImageButton(source='images/transfer_button.png', size_hint=(0.9, 0.2),
                                           pos_hint={'x': 0.05, 'y': 0.25})
        self.transfer_button.bind(on_press=self.transfer_money_button_pressed)
        self.layout.add_widget(self.transfer_button)

        # 상태 메시지 표시 레이블
        self.status_label = Label(text='송금 정보를 입력하세요', font_name=fontName1, font_size=15, size_hint=(0.83, 0.1),
                                  color=(0.1, 0.4, 0.8, 1), pos_hint={'x': 0.1, 'y': 0.15})
        self.layout.add_widget(self.status_label)

        self.add_widget(self.layout)

    # 홈 화면으로 돌아가는 함수
    def go_back_to_home(self, instance):
        self.manager.current = 'home'

    def on_enter(self):
        if self.sender_account and self.user_seq_no:
            account_data = get_account_data(self.user_seq_no)

            if account_data is None:
                self.status_label.text = "송금 계좌 정보를 불러올 수 없습니다."
                return

            # 계좌 정보가 있을 때만 텍스트를 업데이트
            self.sender_account_label.text = f"{account_data['account_num_masked']}"
            self.account_details_label.text = f"SRV{account_data['fintech_use_num'][-4:]} 통장"
            self.available_balance_label.text = f"{int(account_data['balance_amt']):,}원"
        else:
            self.status_label.text = "송금할 계좌를 선택하세요."

    def show_account_selection_popup(self, instance):
        ref = db.reference('users')
        users_data = ref.get()

        if not users_data:
            self.status_label.text = "계좌 정보를 불러올 수 없습니다."
            return

        all_accounts = {}
        for user_seq_no, user_data in users_data.items():
            account_data = user_data.get('account')
            user_info = user_data.get('user_info')
            if account_data and isinstance(account_data, dict) and user_info:
                all_accounts[user_seq_no] = {
                    'account_num_masked': account_data.get('account_num_masked', 'N/A'),
                    'name': user_info.get('name', 'Unknown')
                }

        if not all_accounts:
            self.status_label.text = "사용 가능한 계좌 정보가 없습니다."
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
            background='images/transfer_background.png',
            background_color=(1, 1, 1, 1)
        )

        # 팝업 열기
        self.account_popup.open()

    def select_account(self, user_seq_no):
        """계좌 선택 후 데이터를 처리하는 함수"""
        account_data = get_account_data(user_seq_no)
        if account_data:
            self.receiver_account_input.text = account_data['account_num_masked']
            self.selected_receiver_account = user_seq_no
            self.account_popup.dismiss()
        else:
            self.status_label.text = "계좌 정보를 불러올 수 없습니다."

    def transfer_money_button_pressed(self, instance):
        receiver_account = self.selected_receiver_account
        amount = self.amount_input.text

        if not self.sender_account or not receiver_account or not amount:
            self.status_label.text = '모든 필드를 입력하세요.'
            return

        result_message = transfer_money(self.user_seq_no, self.sender_account, receiver_account, amount)
        self.status_label.text = result_message

        self.update_home_balance_and_transactions()

        self.manager.current = 'home'

    def update_home_balance_and_transactions(self):
        """홈 화면에 있는 계좌 잔액 및 거래 내역 정보를 업데이트하는 함수"""
        home_screen = self.manager.get_screen('home')
        if home_screen:
            home_screen.refresh_balance()
            home_screen.load_and_display_transactions()

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
