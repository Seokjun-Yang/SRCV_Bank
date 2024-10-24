import threading

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.camera import Camera
from kivy.clock import Clock
from kivy.core.image import Image as CoreImage
import boto3
import io
from PIL import Image
import cv2
import numpy as np
import os
from plyer import storagepath
from kivy.uix.screenmanager import Screen

fontName1 = 'Hancom Gothic Bold.ttf'
fontName2 = 'Hancom Gothic Regular.ttf'

# AWS Rekognition 클라이언트 설정
rekognition = boto3.client('rekognition', region_name='us-east-1')


class SecondVerification(Screen):
    def __init__(self, **kwargs):
        super(SecondVerification, self).__init__(**kwargs)
        self.on_auth_complete = None  # 인증 완료 후 실행할 콜백 함수

        self.failed_attempts = 0  # 실패 횟수
        self.max_attempts = 3  # 최대 시도 횟수 (3번으로 수정)
        self.similarity_threshold = 97  # 유사도 임계값
        self.auth_successful = False  # 인증 성공 여부
        # 내부 디렉토리 경로
        self.storage_path = storagepath.get_home_dir()
        # 레이아웃 설정
        self.layout = FloatLayout()


        # 상태 라벨
        self.second = 5
        self.str = f"{self.second}초 후 자동으로 사진이 촬영됩니다..."
        self.status_label = Label(text=self.str, font_name=fontName2, size_hint=(None, None), size=(200, 50),pos_hint={'center_x': 0.5, 'top': 0.8}, color=(0.255, 0.412, 0.882, 1))
        print(self.status_label)
        self.layout.add_widget(self.status_label)

        self.camera = None


        self.add_widget(self.layout)
    def mt_tts(self, message):
        threading.Thread(target=self.speak, args=(message,) ).start()

    def speak(self, message):
        app = App.get_running_app()
        app.speak(message)
    def initCamera(self):#, seconds
        win_size = Window.size
        if not self.camera:
            self.camera = Camera(resolution=Window.size, index=0, )#size = Window.size
            self.camera.size_hint = (None, None)
            self.camera.size = win_size
            self.camera.pos = (0,0)

            print("Camera initialized")
            self.layout.add_widget(self.camera)

        else:
            print("Camera already initialized")

        if not self.camera.play:
            self.camera.play = True
            self.camera.size_hint = (None, None)
            #self.camera.resolution = win_size
            self.camera.size = win_size
            self.camera.pos = (0,0)
            #self.layout.add_widget(self.camera)
    def on_enter(self, *args):
        app = App.get_running_app()
        self.camera = app.camera
        self.camera.size = Window.size
        if not self.camera:
            self.camera = app.camera
            self.layout.add_widget(self.camera)
            print(f"not self.camera: {self.camera}")
        else:
            self.layout.add_widget(self.camera)
            print(f"self.camera: {self.camera}")

        if not self.camera.play:
            # self.layout.add_widget(self.camera)
            self.camera.play = True


        self.mt_tts(self.str)
        Clock.schedule_once(self.capture_and_authenticate, self.second)

    def on_pre_enter(self, *args):
        print("Camera started")
        #self.initCamera()

    def on_leave(self, *args):
        if self.camera:
            print("Camera stopped")
            self.camera.play = False  # 화면을 벗어날 때 카메라 끄기
            self.layout.remove_widget(self.camera)  # 위젯에서 카메라 삭제
            self.camera = None  # 카메라 객체 해제

    def go_back(self, instance):
        self.manager.current = 'main'  # 메인 화면으로 이동
    # 테스트 버튼
    def on_test_button_press(self, instance):
        """테스트 버튼을 눌러 인증을 시도합니다."""
        self.capture_and_authenticate(instance)

    def load_registered_image(self):
        # 저장된 이미지를 가져오는 함수
        registered_image_path = os.path.join(self.storage_path, 'test.jpg')
        if os.path.exists(registered_image_path):
            with open(registered_image_path, 'rb') as img_file:
                return img_file.read()
        else:
            print("no registered image")
            return None

    def capture_and_authenticate(self, instance):
        """카메라에서 사진을 촬영하고 인증을 진행합니다."""
        self.status_label.text = "사진을 분석 중입니다..."

        # 카메라에서 현재 프레임 가져오기
        texture = self.camera.texture
        if texture is None:
            self.status_label.text = "can not get an image from camera."
            return None

        if texture:
            try:
                # 텍스처를 이미지로 변환
                frame = self.texture_to_image(texture)

                # 앱의 로컬 저장소 경로 가져오기
                app = App.get_running_app()
                id = app.store.get('user')

                # 바이트 형태로 변환
                frame_bytes = self.image_to_bytes(frame)

                # 회원가입 시 촬영한 사진과 비교 (registered_image.jpg 대체 경로 사용)
                registered_image_path = os.path.join(storagepath.get_home_dir(),
                                                     f"{id['test']}.jpg") #로컬에 저장된 이미지 가져와서 비교 -> f"{id['userid']}.jpg"
                #test -> userid 변경하여 사용

                if not os.path.exists(registered_image_path):
                    self.status_label.text = "등록된 이미지가 없습니다."
                    #다시 찍는 로직 추가
                    return

                # 2차 본인 인증 시도
                is_authenticated = self.authenticate_user(registered_image_path, frame_bytes)

                if is_authenticated:
                    self.status_label.text = "success on verification."
                    self.on_success()
                    #self.verification()

                else:
                    self.failed_attempts += 1
                    if self.failed_attempts >= self.max_attempts:
                        self.status_label.text = "can not verifify more."
                        # 이전 화면 복귀 혹은 더 이상 재시도를 하지 않도록 종료 처리 가능
                    else:
                        self.status_label.text = f"auth failed. {self.failed_attempts}/{self.max_attempts} tried."
                        Clock.schedule_once(self.capture_and_authenticate, 3)

            except Exception as e:
                self.status_label.text = f"오류 발생: {str(e)}"
                print(f"Error during image capture: {str(e)}")

    def texture_to_image(self, texture):
        """Kivy 텍스처를 PIL 이미지로 변환"""
        size = texture.size
        pixels = texture.pixels
        frame = np.frombuffer(pixels, np.uint8).reshape(size[1], size[0], 4)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2RGB)  # RGBA -> RGB로 변환
        return Image.fromarray(frame)

    def image_to_bytes(self, img):
        """PIL 이미지를 바이트 배열로 변환"""
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()
        return img_byte_arr

    def authenticate_user(self, registered_image_path, login_image_bytes):
        """AWS Rekognition을 사용해 얼굴 인증"""
        try:
            with open(registered_image_path, 'rb') as reg_img:
                response = rekognition.compare_faces(
                    SourceImage={'Bytes': reg_img.read()},
                    TargetImage={'Bytes': login_image_bytes},
                    SimilarityThreshold=self.similarity_threshold
                )

                face_matches = response.get('FaceMatches', [])
                if face_matches:
                    for match in face_matches:
                        similarity = match['Similarity']
                        print(f"Similarity: {similarity}%")
                        if similarity >= self.similarity_threshold:
                            print("Authentication successful!")
                            return True

            print("Authentication failed: No matching faces found.")
            return False

        except Exception as e:
            print(f"Error during Rekognition call: {str(e)}")
            return False

    def on_success(self):
        """인증 성공 시 호출되는 함수"""
        print("성공적으로 인증되었습니다!")
        self.manager.current = 'home' #여기를 ....  고민 -> 테스트를 위해 임시 이동
        #분기

    def verification(self):
        previous_screen = self.manager.previous

        if(previous_screen == 'login'):
            #로그인 할때 사용 시
            self.manager.current = 'home'
            pass
        elif(previous_screen == 'transfer'):
            #송금 때 사용 시
            #self.manager.current =
            pass
        #self.manager.current = 'signupVerification'
        #분기

    def test_verification(self, instance):
        self.manager.current = 'home'

