import threading

from kivy.app import App
from kivy.graphics.texture import Texture
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
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
from kivy.uix.image import Image as KivyImage
from SRVBank.screens.image_button import ImageButton
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
fontName1 = 'Hancom Gothic Bold.ttf'
fontName2 = 'Hancom Gothic Regular.ttf'

# 본인 인증 시 사용
# AWS Rekognition 클라이언트 설정
rekognition = boto3.client('rekognition', region_name='us-east-1')


class SignupVerification(Screen):
    def __init__(self, **kwargs):
        super(SignupVerification, self).__init__(**kwargs)
        self.layout = FloatLayout()

        #
        self.second = 5
        # 라벨로 상태 표시
        self.str = f"{self.second}초 후 자동으로 사진이 촬영됩니다..."
        #print(f"self.str:{self.str}")
        self.status_label = Label(text=self.str, font_name=fontName2, size_hint=(None, None), size=(200, 50),pos_hint={'center_x': 0.5, 'top': 0.8}, color=(0.255, 0.412, 0.882, 1))
        #print(self.status_label)


        self.layout.add_widget(self.status_label)

        Window.clearcolor = (1, 1, 1, 1)
        self.camera = None

        self.add_widget(self.layout)
    def mt_tts(self, message):
        threading.Thread(target=self.speak, args=(message,) ).start()
        #Clock.schedule_once(self.capture_image, 10)
    def speak(self, message):
        app = App.get_running_app()
        app.speak(message)

    def update_camera_texture(self, dt):
        if self.camera.play:
            # 텍스처가 None이 아닌지 확인
            if self.camera.texture is not None:
                self.camera.texture = self.camera._camera.texture  # 텍스처 수동 갱신
                print("Camera texture updated")
            else:
                print("Camera texture is None")
    def go_back(self, instance):
        self.manager.current = 'signup'
    def update_frame(self, dt):
        # OpenCV로 프레임 읽기
        ret, frame = self.capture.read()
        if ret:
            # OpenCV의 BGR 이미지를 Kivy가 인식할 수 있는 RGB로 변환
            frame = cv2.flip(frame, 0)  # 상하 반전
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            buf = frame.tobytes()
            image_texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='rgb')
            image_texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')
            self.image_view.texture = image_texture  # Image 위젯에 텍스처 적용
    def initCamera(self):#, seconds
        # 카메라가 이미 초기화되어 있는지 확인
        #Window.size = (300, 600)
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



    def on_camera_ready(self, instance):
        # 카메라 텍스처가 준비되었을 때 play 시작
        print("Camera texture is ready")
        #self.camera.play = True
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
        # 3초 후에 자동으로 촬영 함수 호출
        Clock.schedule_once(self.capture_image, self.second)  # 3초 후에 자동으로 촬영

        pass
    def on_pre_enter(self, *args):
        #self.initCamera()
        #self.camera.play = True
        pass

    def check_camera_ready(self, dt):
        if self.camera.texture:
            print("Camera texture is ready")
            self.camera.play = True
            return False  # 텍스처가 준비되면 더 이상 체크하지 않음
        else:
            print("Camera texture is still None")
            print(f"check_camera_ready: {self.camera.play}" )


    def on_leave(self, *args):
        if self.camera:
            print("Camera stopped")
            self.camera.play = False  # 화면을 벗어날 때 카메라 끄기
            self.layout.remove_widget(self.camera)  # 위젯에서 카메라 삭제
            self.camera = None  # 카메라 객체 해제

    def go_back(self, instance):
        self.manager.current = 'login'  # 메인 화면으로 이동

    def capture_image(self, instance):
        """사진을 촬영하고 로컬에 저장"""
        self.status_label.text = "사진을 촬영 중입니다... capture..."

        # 카메라에서 현재 프레임 가져오기
        texture = self.camera.texture
        if texture is None:
            self.status_label.text = "카메라로부터 이미지를 가져오지 못했습니다."
            return

        if texture:
            try:
                # 앱 전용 저장소 경로 가져오기 (안드로이드의 내부 저장소)
                self.storage_path = storagepath.get_home_dir()  # 외부 사진 디렉토리 사용
                if not self.storage_path:
                    self.status_label.text = "저장 경로를 찾을 수 없습니다."
                    return
                # 저장될 경로 설정
                app = App.get_running_app()
                id = app.store.get('user')
                #print(f"???:{id['userid']}") -> test_id
                registered_image_path = os.path.join(self.storage_path, f"{id['test']}.jpg") # 파일명 변경 예정 f'test.jpg'/
                #test -> userid 변경하여 사용

                # 텍스처를 이미지로 변환
                frame = self.texture_to_image(texture)

                #registered_image_path = 'registered_image.jpg'
                frame.save(registered_image_path)
                self.status_label.text = f"사진이 저장되었습니다."

                Clock.schedule_once(self.on_success, 1)
                #다음 회원가입 마무리

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

    def delete_registered_image(self, instance=None):
        """저장된 이미지를 삭제하는 함수"""

        registered_image_path = os.path.join(storagepath.get_home_dir(),
                                             'test.jpg')  # os.path.join(self.storage_path, 'registered_image.jpg')
        if os.path.exists(registered_image_path):
            os.remove(registered_image_path)
            self.status_label.text = "등록된 이미지가 삭제되었습니다."
            print("등록된 이미지가 삭제되었습니다.")
        else:
            self.status_label.text = "삭제할 이미지가 없습니다."
            print("삭제할 이미지가 없습니다.")

    def retake_image(self, instance):
        """사진 재촬영 및 저장"""
        self.delete_registered_image()  # 기존 이미지 삭제
        self.capture_image(instance)  # 새 이미지 촬영 및 저장

    def on_success(self, second):
        """인증 성공 시 호출되는 함수"""
        # 인증 성공 시 정상적으로 기능 수행 가능(입출금 등)
        #print("성공적으로 인증되었습니다!")  # 출력 완료
        self.manager.current = 'login'

    def init_opencv_camera(self):
        self.capture = cv2.VideoCapture(0)  # 0번 카메라 장치 사용
        if self.capture.isOpened():
            ret, frame = self.capture.read()
            if ret:
                print("OpenCV camera initialized")
            else:
                print("Failed to capture frame")
        else:
            print("Failed to open OpenCV camera")