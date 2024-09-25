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
from kivy.uix.anchorlayout import AnchorLayout

import requests

fontName1 = 'Hancom Gothic Bold.ttf'
fontName2 = 'Hancom Gothic Regular.ttf'

class LeftAlignedButton(ButtonBehavior, Label):
    pass

class TransferScreen(Screen):
    def __init__(self, **kwargs):
        super(TransferScreen, self).__init__(**kwargs)
        self.user_seq_no = None
        self.sender_account = None
        self.layout = FloatLayout()

        # 배경 이미지
        self.bg_image = Image(source='images/background.png', allow_stretch=True, keep_ratio=False)
        self.layout.add_widget(self.bg_image)

        # 송금할 계좌를 보여줄 레이블
        self.sender_account_label = Label(text="송금할 계좌: ", font_name=fontName1, font_size=16,
                                          pos_hint={'x': 0.1, 'y': 0.8}, size_hint=(0.8, 0.1))
        self.layout.add_widget(self.sender_account_label)

        # 배경 이미지 추가
        self.receiver_account_bg = Image(source='images/input_background.png', size_hint=(0.83, 0.1),
                                         pos_hint={'x': 0.08, 'y': 0.53})
        self.layout.add_widget(self.receiver_account_bg)

        # 계좌번호 버튼 생성
        self.receiver_account_input = LeftAlignedButton(
            text='계좌번호', font_name=fontName2, halign='left', valign='middle',
            size_hint=(0.8, 0.1), pos_hint={'x': 0.1, 'y': 0.53},
            color=(1, 1, 1, 1), padding=(8, 0)  # 왼쪽에 여백을 주기 위해 padding 설정
        )

        # 버튼의 text_size를 자신의 크기와 일치하도록 설정
        self.receiver_account_input.bind(
            size=lambda instance, value: setattr(instance, 'text_size', (instance.width, None)))

        # 버튼을 레이아웃에 추가
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
        self.transfer_button = Button(text='송금하기', font_name=fontName1, font_size=15, size_hint=(0.8, 0.1),
                                      pos_hint={'x': 0.1, 'y': 0.25},
                                      background_color=(0, 0, 0, 0), color=(0, 0.7, 0.7, 1))
        self.transfer_button.bind(on_press=self.transfer_money_button_pressed)
        self.layout.add_widget(self.transfer_button)

        # 상태 메시지 표시 레이블
        self.status_label = Label(text='송금 정보를 입력하세요', font_name=fontName1, font_size=15, size_hint=(0.83, 0.1),
                                  color=(0.1, 0.4, 0.8, 1), pos_hint={'x': 0.1, 'y': 0.15})
        self.layout.add_widget(self.status_label)

        self.add_widget(self.layout)


    def on_enter(self):
        if self.sender_account:
            self.sender_account_label.text = f"송금할 계좌: {self.sender_account}"
        else:
            self.status_label.text = "송금할 계좌를 선택하세요."

    def show_account_selection_popup(self, instance):
        if not self.user_seq_no:
            self.status_label.text = "사용자 정보가 설정되지 않았습니다."
            return

        ref = db.reference(f'users/{self.user_seq_no}/accounts')
        accounts_data = ref.get()

        if not accounts_data:
            self.status_label.text = "계좌 정보를 불러올 수 없습니다."
            return

        account_layout = GridLayout(cols=1, size_hint_y=None)
        account_layout.bind(minimum_height=account_layout.setter('height'))

        for fintech_use_num, account in accounts_data.items():
            account_button = Button(
                text=f"{account['account_holder_name']} - {account['account_num_masked']}",
                size_hint_y=None, height=40
            )
            account_button.bind(on_release=lambda btn, f=fintech_use_num: self.select_account(f))
            account_layout.add_widget(account_button)

        scroll_view = ScrollView(size_hint=(1, None), size=(300, 400))
        scroll_view.add_widget(account_layout)

        self.account_popup = Popup(title="Select an Account", content=scroll_view, size_hint=(None, None),
                                   size=(350, 450))
        self.account_popup.open()

    def select_account(self, fintech_use_num):
        self.receiver_account_input.text = fintech_use_num
        self.account_popup.dismiss()

    def transfer_money_button_pressed(self, instance):
        receiver_account = self.receiver_account_input.text
        amount = self.amount_input.text

        if not self.sender_account or not receiver_account or not amount:
            self.status_label.text = '모든 필드를 입력하세요.'
            return

        # 송금 함수 호출
        result_message = transfer_money(self.user_seq_no, self.sender_account, receiver_account, amount)
        self.status_label.text = result_message  # 상태 메시지 업데이트

        # 송금 후 홈 화면으로 전환
        self.manager.current = 'home'

        # 송금 후 홈 화면의 잔액 및 거래 내역 업데이트
        self.update_home_balance_and_transactions()

    def update_home_balance_and_transactions(self):
        """홈 화면에 있는 계좌 잔액 및 거래 내역 정보를 업데이트하는 함수"""
        home_screen = self.manager.get_screen('home')
        if home_screen:
            home_screen.refresh_balance()  # 잔액 업데이트
            home_screen.load_and_display_transactions()  # 거래 내역 업데이트
def get_account_data(user_seq_no, fintech_use_num):
    ref = db.reference(f'users/{user_seq_no}/accounts/{fintech_use_num}')
    return ref.get()

def update_account_balance(user_seq_no, fintech_use_num, new_balance):
    """Firebase에서 계좌 잔액을 업데이트하는 함수"""
    ref = db.reference(f'users/{user_seq_no}/accounts/{fintech_use_num}')
    ref.update({'balance_amt': new_balance})

def record_transaction(user_seq_no, fintech_use_num, amount, transaction_type, description, new_balance):
    account_data = get_account_data(user_seq_no, fintech_use_num)
    holder_name = account_data.get('account_holder_name', 'Unknown')

    transaction_ref = db.reference(f'users/{user_seq_no}/accounts/{fintech_use_num}/transactions')
    transactions = transaction_ref.get()
    if transactions and "initial" in transactions:
        transaction_ref.child("initial").delete()

    transaction_ref.push({
        'amount': amount,
        'type': transaction_type,
        'description': description,
        'balance': new_balance,
        'holder_name': holder_name,
        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 현재 날짜 및 시간 저장
    })

def transfer_money(user_seq_no, sender_account, receiver_account, amount):
    """송금 기능 구현 함수"""
    sender_data = get_account_data(user_seq_no, sender_account)
    receiver_data = get_account_data(user_seq_no, receiver_account)

    if int(sender_data['balance_amt']) < int(amount):
        return "잔액이 부족합니다."

    # Updating balances
    sender_new_balance = int(sender_data['balance_amt']) - int(amount)
    receiver_new_balance = int(receiver_data['balance_amt']) + int(amount)

    # Update Firebase balances
    update_account_balance(user_seq_no, sender_account, sender_new_balance)
    update_account_balance(user_seq_no, receiver_account, receiver_new_balance)

    # Record the transactions (user_seq_no를 추가하여 변경된 부분)
    record_transaction(user_seq_no, sender_account, amount, '출금', f'{receiver_data["account_holder_name"]}으로 송금', sender_new_balance)
    record_transaction(user_seq_no, receiver_account, amount, '입금', f'{sender_data["account_holder_name"]}로부터 입금', receiver_new_balance)

    return f'{amount}원이 {receiver_data["account_holder_name"]}에게 송금되었습니다.'