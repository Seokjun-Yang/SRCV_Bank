import json
import requests
from firebase_admin import db
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.uix.screenmanager import Screen
from screens.image_button import ImageButton
from kivy.uix.button import Button
import webbrowser
import threading
from kivy.clock import Clock

fontName = 'Hancom Gothic Bold.ttf'

class SignupScreen(Screen):
    def __init__(self, **kwargs):
        super(SignupScreen, self).__init__(**kwargs)
        self.api_key = "AIzaSyDU67MIYsLtwbbpF_rnf0NcmPD_HDeGN8I"  # Firebase 프로젝트 설정에서 API 키를 확인할 수 있습니다

        self.layout = FloatLayout()

        self.access_token = ""
        self.refresh_token = ""
        self.user_seq_no = ""
        self.user_id = ""

        # 배경 이미지 추가
        self.bg_image = Image(source='images/background.png', allow_stretch=True, keep_ratio=False)
        self.layout.add_widget(self.bg_image)
        self.logo_bg = Image(source='images/logo_image.png', size_hint=(0.83, 0.1), pos_hint={'x': 0.1, 'y': 0.85})
        self.layout.add_widget(self.logo_bg)
        self.login_bg = Image(source='images/signup_image.png', size_hint=(0.6, 0.1), pos_hint={'x': 0.2, 'y': 0.75})
        self.layout.add_widget(self.login_bg)

        # 이름 입력 창과 배경 이미지
        self.name_bg = Image(source='images/input_background.png', size_hint=(0.83, 0.1), pos_hint={'x': 0.08, 'y': 0.65})
        self.layout.add_widget(self.name_bg)
        self.name_input = TextInput(hint_text='Name', multiline=False, size_hint=(0.9, 0.1), pos_hint={'x': 0.1, 'y': 0.62},
                                     background_color=(0, 0, 0, 0))  # 배경을 투명하게 설정
        self.layout.add_widget(self.name_input)

        # 휴대폰번호 입력 창과 배경 이미지
        self.phone_bg = Image(source='images/input_background.png', size_hint=(0.83, 0.1), pos_hint={'x': 0.08, 'y': 0.56})
        self.layout.add_widget(self.phone_bg)
        self.phone_input = TextInput(hint_text='Phone Number', multiline=False, size_hint=(0.9, 0.1), pos_hint={'x': 0.1, 'y': 0.533},
                                     background_color=(0, 0, 0, 0))  # 배경을 투명하게 설정
        self.layout.add_widget(self.phone_input)

        # 이메일 입력 창과 배경 이미지
        self.email_bg = Image(source='images/input_background.png', size_hint=(0.83, 0.1), pos_hint={'x': 0.08, 'y': 0.47})
        self.layout.add_widget(self.email_bg)
        self.email_input = TextInput(hint_text='Email', multiline=False, size_hint=(0.9, 0.1), pos_hint={'x': 0.1, 'y': 0.443},
                                     background_color=(0, 0, 0, 0))  # 배경을 투명하게 설정
        self.layout.add_widget(self.email_input)

        # 비밀번호 입력 창과 배경 이미지
        self.password_bg = Image(source='images/input_background.png', size_hint=(0.83, 0.1), pos_hint={'x': 0.08, 'y': 0.38})
        self.layout.add_widget(self.password_bg)
        self.password_input = TextInput(hint_text='Password', password=True, multiline=False, size_hint=(0.9, 0.1), pos_hint={'x': 0.1, 'y': 0.353},
                                        background_color=(0, 0, 0, 0))  # 배경을 투명하게 설정
        self.layout.add_widget(self.password_input)

        # 인증받기 버튼
        self.auth_button = Button(text='인증받기', font_name=fontName, font_size=15, size_hint=(0.8, 0.1),
                                  pos_hint={'x': 0.1, 'y': 0.3}, background_color=(0, 0, 0, 0),
                                  color=(0, 0.7, 0.7, 1))
        self.auth_button.bind(on_press=self.request_auth)
        self.layout.add_widget(self.auth_button)

        # 회원가입 버튼
        self.signup_button = ImageButton(source='images/signup_button.png', size_hint=(0.9, 0.1), pos_hint={'x': 0.05, 'y': 0.2})
        self.signup_button.bind(on_press=self.signup)
        self.layout.add_widget(self.signup_button)

        # 상태 메시지 표시 레이블
        self.status_label = Label(text='회원가입 정보를 입력하세요', font_name=fontName, font_size=15, size_hint=(0.83, 0.1),
                                  color=(0.1, 0.4, 0.8, 1), pos_hint={'x': 0.05, 'y': 0.1})
        self.layout.add_widget(self.status_label)

        self.add_widget(self.layout)

    def request_auth(self, instance):
        name = self.name_input.text
        email = self.email_input.text
        password = self.password_input.text
        phone = self.phone_input.text

        if not name or not email or not password:
            self.status_label.text = '이름, 이메일, 비밀번호를 입력해주세요.'
            return

        try:
            # Step 1: 입력된 사용자 정보를 Firebase에 먼저 저장
            ref = db.reference(f'users/{name}')
            ref.update({
                'name': name,
                'email': email,
                'password': password,
                'phone': phone
            })

            # Step 2: 금융결제원 API 호출하여 번호 인증 시작
            client_id = 'd79bfcd3-1b00-4f8b-8ffc-aa06a317801c'
            redirect_uri = 'https://us-central1-bank-a752e.cloudfunctions.net/authCallback'
            state = '12345678912345678912345678912345'

            auth_url = (
                f"https://testapi.openbanking.or.kr/oauth/2.0/authorize?"
                f"response_type=code&"
                f"client_id={client_id}&"
                f"redirect_uri={redirect_uri}&"
                f"scope=login inquiry transfer&"
                f"state={state}&"
                f"auth_type=0"
            )
            # 웹브라우저에서 인증 URL 열기
            threading.Thread(target=self.open_browser_and_wait_for_auth, args=(auth_url,)).start()

        except Exception as e:
            self.status_label.text = f'Firebase 저장 오류: {str(e)}'

    def open_browser_and_wait_for_auth(self, auth_url):
        webbrowser.open(auth_url)
        Clock.schedule_interval(self.check_firebase_for_tokens, 5)  # 5초마다 Firebase에서 token 확인

    def check_firebase_for_tokens(self, dt):
        threading.Thread(target=self.fetch_user_tokens).start()  # 별도 스레드에서 token 확인

    def fetch_user_tokens(self):
        ref = db.reference('users')
        tokens = ref.order_by_key().get()

        if tokens:
            for key, value in tokens.items():
                if 'user_seq_no' in value:
                    self.user_seq_no = value['user_seq_no']
                    self.access_token = value['access_token']
                    self.refresh_token = value['refresh_token']
                    self.user_id = self.user_seq_no

                    name = self.name_input.text

                    # 인증 완료 후 계좌 정보를 가져옴
                    if self.access_token:
                        self.fetch_account_info(self.access_token, name)  # 여기서 key는 사용자 이름입니다.
                    # Kivy의 UI 업데이트는 Clock.schedule_once를 사용하여 메인 스레드에서 수행
                    Clock.schedule_once(lambda dt: self.update_status_label())
                    break

    def update_status_label(self):
        self.status_label.text = f'인증이 완료되었습니다. user_seq_no: {self.user_seq_no}'

    def signup(self, instance):
        if not self.user_seq_no:
            self.status_label.text = '인증을 먼저 완료해주세요.'
            return

        name = self.name_input.text
        phone = self.phone_input.text
        email = self.email_input.text
        password = self.password_input.text

        try:
            # Firebase Authentication REST API를 사용하여 회원가입
            response = requests.post(
                f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={self.api_key}",
                data=json.dumps({
                    'email': email,
                    'password': password,
                    'returnSecureToken': True
                }),
                headers={'Content-Type': 'application/json'}
            )
            data = response.json()
            if 'idToken' in data:
                self.status_label.text = f'Successfully signed up as: {email}'
                self.manager.current = 'login'
            else:
                self.status_label.text = f'Signup error: {data["error"]["message"]}'
        except Exception as e:
            self.status_label.text = f'Error signing up: {str(e)}'

    def fetch_account_info(self, access_token, name):
        try:
            # 계좌 목록 조회 API 호출
            account_list_response = requests.get(
                f'https://testapi.openbanking.or.kr/v2.0/user/me?user_seq_no={self.user_seq_no}',
                headers={
                    'Authorization': f'Bearer {access_token}',
                }
            )

            # API 요청 성공 여부 확인
            if account_list_response.status_code != 200:
                self.status_label.text = f'API 요청 실패: {account_list_response.status_code}'
                return

            # 계좌 목록을 추출하여 저장
            account_list = account_list_response.json().get('res_list', [])

            # 가장 최근 계좌 정보 가져오기
            if account_list:
                recent_account = account_list[0]
                account_info = {
                    'fintech_use_num': recent_account['fintech_use_num'],
                    'bank_name': recent_account['bank_name'],
                    'account_num_masked': recent_account['account_num_masked'],
                    'balance_amt': 100000,  # 기본 잔액
                    'available_amt': 90000,  # 출금 가능 금액 (잔액의 90%)
                    'transactions': [{
                        'amount': 0,
                        'date': 'No Date',
                        'description': 'no transactions',
                        'type': '정보 없음',
                        'balance': 0
                    }]  # 기본 거래 내역으로 no data 설정
                }

                # Firebase의 name 항목 아래 계좌 정보를 저장
                ref = db.reference(f'users/{name}/account')
                ref.set(account_info)
                self.status_label.text = '계좌 정보 및 거래 내역이 저장되었습니다.'
            else:
                self.status_label.text = '계좌 정보를 가져올 수 없습니다.'

        except Exception as e:
            self.status_label.text = f'계좌 정보를 가져오는 중 오류 발생: {str(e)}'
