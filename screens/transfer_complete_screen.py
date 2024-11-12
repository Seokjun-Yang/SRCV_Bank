from kivy.app import App
from kivy.clock import Clock
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.button import Button
from firebase_admin import db
from datetime import datetime
from kivy.uix.image import Image

class ImageButton(ButtonBehavior, Image):
    pass

class ClickableLabel(ButtonBehavior, Label):
    pass

fontName1 = 'LINESeedKR-Bd.ttf'
fontName2 = 'LINESeedKR-Rg.ttf'





class TransferCompleteScreen(Screen):
    def __init__(self, **kwargs):
        super(TransferCompleteScreen, self).__init__(**kwargs)
        self.layout = FloatLayout()

        # 배경 이미지
        self.bg_image = Image(source='images/transfer_complete_background.png', allow_stretch=True, keep_ratio=False)
        self.layout.add_widget(self.bg_image)

        # 완료 아이콘 이미지
        self.success_icon = Image(source='images/success_icon.png', size_hint=(0.23, 0.12),
                                  pos_hint={'center_x': 0.5, 'top': 0.91})
        self.layout.add_widget(self.success_icon)

        # 송금 완료 텍스트
        self.completion_text = Label(text="송금이 완료되었습니다!\n안전하게 잘 보내드렸어요.", font_name=fontName1, font_size=20,
                                     size_hint=(None, None), halign='center', pos_hint={'center_x': 0.5, 'top': 0.79},
                                     color=(0, 0, 0, 1))
        self.layout.add_widget(self.completion_text)

        # 체크 아이콘 이미지
        self.done_icon = Image(source='images/done.png', size_hint=(None, None), size=(40, 40),
                               pos_hint={'x': 0.71, 'top': 0.415})
        self.layout.add_widget(self.done_icon)

        # 송금 정보 텍스트 레이블들
        self.date_title = Label(
            text="날짜", font_name=fontName2, font_size=15, size_hint=(None, None),
            pos_hint={'x': 0.2, 'top': 0.65}, color=(0.466, 0.466, 0.466, 1),
            halign='left', valign='middle', text_size=(100, None)  # 너비를 설정하여 좌측 정렬
        )
        self.time_title = Label(
            text="시간", font_name=fontName2, font_size=15, size_hint=(None, None),
            pos_hint={'x': 0.55, 'top': 0.65}, color=(0.466, 0.466, 0.466, 1),
            halign='right', valign='middle', text_size=(100, None)  # 너비를 설정하여 우측 정렬
        )
        self.receiver_title = Label(
            text="받는 사람", font_name=fontName2, font_size=15, size_hint=(None, None),
            pos_hint={'x': 0.2, 'top': 0.56}, color=(0.466, 0.466, 0.466, 1),
            halign='left', valign='middle', text_size=(100, None)  # 너비를 설정하여 좌측 정렬
        )
        self.amount_title = Label(
            text="보낸 금액", font_name=fontName2, font_size=15, size_hint=(None, None),
            pos_hint={'x': 0.2, 'top': 0.47}, color=(0.466, 0.466, 0.466, 1),
            halign='left', valign='middle', text_size=(100, None)  # 너비를 설정하여 좌측 정렬
        )

        self.layout.add_widget(self.date_title)
        self.layout.add_widget(self.time_title)
        self.layout.add_widget(self.receiver_title)
        self.layout.add_widget(self.amount_title)

        # 송금 정보 레이블들
        self.date_label = Label(text="", font_name=fontName1, font_size=17, size_hint=(None, None),
                                pos_hint={'x': 0.2, 'top': 0.615}, color=(0, 0, 0, 1),
                                halign='left', valign='middle', text_size=(100, None))
        self.time_label = Label(text="", font_name=fontName1, font_size=17, size_hint=(None, None),
                                pos_hint={'x': 0.55, 'top': 0.615}, color=(0, 0, 0, 1),
                                halign='right', valign='middle', text_size=(100, None))
        self.receiver_label = Label(text="", font_name=fontName1, font_size=17, size_hint=(None, None),
                                    pos_hint={'x': 0.2, 'top': 0.525}, color=(0, 0, 0, 1),
                                    halign='left', valign='middle', text_size=(100, None))
        self.amount_label = Label(text="", font_name=fontName1, font_size=17, size_hint=(None, None),
                                  pos_hint={'x': 0.2, 'top': 0.435}, color=(0, 0, 0, 1),
                                  halign='left', valign='middle', text_size=(100, None))
        self.layout.add_widget(self.date_label)
        self.layout.add_widget(self.time_label)
        self.layout.add_widget(self.receiver_label)
        self.layout.add_widget(self.amount_label)

        # 도움 안내 투명 버튼 (텍스트 레이블과 투명 버튼을 겹치도록 설정)
        self.help_button = ClickableLabel(
            text="[color=6C6C6C]도움이 필요하신가요?[/color]\n[color=5A945E]여기를 눌러 메시지를 보내주세요![/color]",
            markup=True, font_name=fontName1, font_size=14,
            size_hint=(0.45, 0.1), pos_hint={'center_x': 0.5, 'top': 0.29}, halign='center'
        )
        self.help_button.bind(on_press=self.open_message_input)
        self.layout.add_widget(self.help_button)

        # 확인 완료 버튼
        self.complete_button = ImageButton(source='images/confirm_button.png', size_hint=(0.84, 0.083),
                                           pos_hint={'center_x': 0.5, 'top': 0.118})
        self.complete_button.bind(on_press=self.go_back_to_home)
        self.layout.add_widget(self.complete_button)

        # 흐림 처리된 배경 이미지 추가
        self.bg_blurred_image = Image(source='images/transfer_background_blurred.png', allow_stretch=True, keep_ratio=False, opacity=0)
        self.layout.add_widget(self.bg_blurred_image)

        # 메시지 입력 TextInput
        self.message_input = TextInput(
            hint_text='메시지를 입력하세요...', font_name=fontName1, font_size=15, size_hint=(0.8, 0.3), pos_hint={'center_x': 0.5, 'y': 0.4},
            multiline=False, opacity=0, padding=(20, 50)
        )
        self.layout.add_widget(self.message_input)

        # 닫기 버튼 추가
        self.close_button = Button(
            text='X', font_name=fontName1, font_size=15, size_hint=(None, None), size=(30, 30),
            pos_hint={'x': 0.8, 'top': 0.69}, opacity=0, background_color=(0.447, 0.749, 0.471, 1)
        )
        self.close_button.bind(on_press=self.close_message_input)
        self.layout.add_widget(self.close_button)

        # 보내기 버튼
        self.send_button = Button(
            text='보내기', font_name=fontName1, font_size=15, size_hint=(0.2, 0.05),
            pos_hint={'center_x': 0.5, 'center_y': 0.45}, opacity=0, background_color=(0.447, 0.749, 0.471, 1)
        )
        self.send_button.bind(on_press=self.send_message)
        self.layout.add_widget(self.send_button)

        self.add_widget(self.layout)

    def set_transfer_info(self, date, time, receiver, amount):
        """송금 완료 정보 설정"""
        self.date_label.text = f"{date}"
        self.time_label.text = f"{time}"
        self.receiver_label.text = f"{receiver}"
        self.amount_label.text = f"{amount:,}원"

    def set_user_seq_no(self, user_seq_no):
        """사용자의 user_seq_no 설정"""
        self.user_seq_no = user_seq_no

    def open_message_input(self, instance):
        self.bg_blurred_image.opacity = 1  # 흐림 처리된 이미지 표시
        self.message_input.opacity = 1
        self.send_button.opacity = 1
        self.close_button.opacity = 1
        self.message_input.focus = True

    def close_message_input(self, instance):
        self.bg_blurred_image.opacity = 0  # 흐림 처리된 이미지 숨김
        self.message_input.opacity = 0
        self.send_button.opacity = 0
        self.close_button.opacity = 0

    def send_message(self, instance):
        message = self.message_input.text.strip()
        if message:
            db.reference(f'users/{self.user_seq_no}/user_messages').push({
                'message': message,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            self.message_input.text = ""
            self.close_message_input(None)
            print("메시지가 전송되었습니다!")

    def go_back_to_home(self, instance):
        """홈 화면으로 돌아가는 함수"""
        App.get_running_app().speak_text(f'송금 완료되었습니다!')#잔액이 {balance_amt}원으로 업데이트 되었습니다.
        Clock.schedule_once(lambda dt:self.change_screen('home'), 2)

    def change_screen(self, screen):
        self.manager.current = screen