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

fontName = 'LINESeedKR-Bd.ttf'

class SignupScreen(Screen):
    def __init__(self, **kwargs):
        super(SignupScreen, self).__init__(**kwargs)
        self.api_key = "AIzaSyDU67MIYsLtwbbpF_rnf0NcmPD_HDeGN8I"  # Firebase 프로젝트 설정에서 API 키를 확인할 수 있습니다

        self.layout = FloatLayout()
        self.user_seq_no = ""
        self.user_data = {}

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
        self.name_input = TextInput(hint_text='Name', font_name=fontName, font_size=14, multiline=False, size_hint=(0.9, 0.1), pos_hint={'x': 0.1, 'y': 0.62},
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

        # 회원가입 버튼
        self.signup_button = ImageButton(source='images/signup_button.png', size_hint=(0.9, 0.1), pos_hint={'x': 0.05, 'y': 0.2})
        self.signup_button.bind(on_press=self.signup)
        self.layout.add_widget(self.signup_button)

        #  얼굴인증 촬영 테스트 버튼
        self.signup_verification_button = ImageButton(source='images/profile_picture.png', size_hint=(0.9, 0.1), pos_hint={'x': 0.07, 'y': 0.1})
        self.signup_verification_button.bind(on_press=self.verification)
        self.layout.add_widget(self.signup_verification_button)

        # 인증 상태를 출력할 레이블 추가
        self.status_label = Label(text='', font_name=fontName, font_size=14, size_hint=(0.8, 0.1), pos_hint={'x': 0.1, 'y': 0.1}, color=(1, 0, 0, 1))
        self.layout.add_widget(self.status_label)

        self.add_widget(self.layout)
    def verification(self, instance):
        self.manager.current = 'signupVerification'
    def on_enter(self):
        # 회원가입 화면에 진입할 때만 리스너 시작
        self.start_listener()
    def start_listener(self):
        try:
            db.reference('users').listen(self.user_seq_no_listener)
            print("Firebase 리스너가 시작되었습니다.")
        except Exception as e:
            print(f"리스너 시작 중 오류 발생: {str(e)}")
            self.status_label.text = f"리스너 오류: {str(e)}"

    def user_seq_no_listener(self, event):
        try:
            print("Firebase 리스너가 호출되었습니다.")
            print(f"리스너 데이터: {event.data}")

            # 가장 최근에 변경된 user_seq_no 탐색
            if event.data and isinstance(event.data, dict):
                # event.data의 키를 리스트로 변환하고 정렬하여 가장 마지막 키를 가져옴
                changed_user_seq_no = sorted(event.data.keys(), key=lambda x: int(x))[-1]

                if changed_user_seq_no and changed_user_seq_no != self.user_seq_no:
                    print(f"변경된 user_seq_no: {changed_user_seq_no}")
                    self.user_seq_no = changed_user_seq_no  # 변경된 user_seq_no 업데이트
                    self.user_data = db.reference(f'users/{self.user_seq_no}').get()
                    print(f"변경된 user_seq_no에 해당하는 데이터: {self.user_data}")
                    self.status_label.text = "인증 성공! 변경된 user_seq_no를 확인했습니다."
                else:
                    print("변경된 user_seq_no를 찾을 수 없습니다.")
                    self.status_label.text = "유효한 사용자 정보가 없습니다."

            else:
                print("리스너에서 유효한 데이터가 없습니다.")
                self.status_label.text = "리스너에서 유효한 데이터가 없습니다."

        except Exception as e:
            self.status_label.text = f"listener 오류 발생: {str(e)}"
            print(f"listener 오류 발생: {str(e)}")

    def signup(self, instance):
        if not self.user_seq_no:
            self.status_label.text = '인증을 먼저 완료해주세요.'
            return

        name = self.name_input.text
        phone = self.phone_input.text
        email = self.email_input.text
        password = self.password_input.text

        if not all([name, phone, email, password]):
            self.status_label.text = '모든 입력 필드를 채워주세요.'
            return

        try:
            # Firebase Authentication 회원가입
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
                # 회원가입 정보 Firebase에 저장
                ref = db.reference(f'users/{self.user_seq_no}')
                ref.update({
                    'user_info': {
                        'name': name,
                        'email': email,
                        'password' : password,
                        'phone': phone
                    }
                })
                self.status_label.text = f'회원가입 완료: {email}'
                self.manager.current = 'login'
            else:
                error_message = data.get("error", {}).get("message", "Unknown error")
                self.status_label.text = f'Signup error: {error_message}'

        except Exception as e:
            self.status_label.text = f'Error signing up: {str(e)}'
