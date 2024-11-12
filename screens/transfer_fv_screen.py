import gc
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
from PIL import Image, ImageFile
import cv2
import numpy as np
import os
from plyer import storagepath
from kivy.uix.screenmanager import Screen

from SRCV_Bank.utils.face_verification import face_varification_manager

fontName1 = 'LINESeedKR-Bd.ttf'
fontName2 = 'LINESeedKR-Rg.ttf'
ImageFile.DEBUG = True
class transfer_FV_screen(Screen):
    def __init__(self, **kwargs):
        super(transfer_FV_screen, self).__init__(**kwargs)
        self.layout = FloatLayout()
        # 상태 라벨
        self.second = 5
        self.str = f"{self.second}초 후 자동으로 사진이 촬영됩니다..."
        self.status_label = Label(text=self.str, font_name=fontName2, size_hint=(None, None), size=(200, 50),pos_hint={'center_x': 0.5, 'top': 0.8}, color=(0.255, 0.412, 0.882, 1))
        print(self.status_label)
        self.layout.add_widget(self.status_label)

        self.camera = None


        self.add_widget(self.layout)

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
        self.camera.play = True
        self.layout.add_widget(self.camera)

        App.get_running_app().speak_text(f"화면에 얼굴을 잘 맞춰주세요. {self.second}초 후 자동으로 촬영됩니다.")
        Clock.schedule_once(self.capture_and_authenticate, self.second+1)#self.second

    def on_pre_enter(self, *args):
        self.camera = App.get_running_app().camera
        self.camera.size = Window.size
        self.camera.play = True
        self.camera.size_hint = (None, None)
        #self.camera.pos = (0, 0)
        print("Camera started")

    def on_leave(self, *args):
        if self.camera:
            print("Camera stopped")
            self.camera.play = False  # 카메라 끄기
            self.layout.remove_widget(self.camera)  # 위젯에서 카메라 삭제
            self.camera = None  # 카메라 객체 해제
            gc.collect()  # 메모리 정리
        #self.executor.shutdown(wait=False)

    def go_back(self, instance):
        self.manager.current = 'home'  # home 화면으로 이동


    def capture_and_authenticate(self, instance):
        """카메라에서 사진을 촬영하고 인증을 진행합니다."""
        self.status_label.text = "사진을 분석 중입니다..."

        # 카메라에서 현재 프레임 가져오기
        texture = self.camera.texture
        if texture is None:
            self.status_label.text = "촬영이 불가합니다 ."
            return None

        if texture:
            try:
                # 텍스처를 이미지로 변환
                frame = self.texture_to_image(texture)
                print(f'frame:{frame}')
                # 바이트 형태로 변환
                frame_bytes = self.image_to_bytes(frame)
                print(f'frame bytes:{frame_bytes}')

                # 인증 시도 -> 매니저 사용
                face_verification = face_varification_manager(frame_bytes)
                is_authenticated = face_verification.perform_auth('transfer')

                if is_authenticated:
                    self.status_label.text = "인증 성공했습니다."
                    #Clock.schedule_once(lambda dt: App.get_running_app().speak_text("인증에 성공했습니다."), 1)
                    Clock.schedule_once(lambda dt: self.on_success(), 2)
                else:
                    self.failed_attempts += 1
                    if self.failed_attempts >= self.max_attempts:
                        self.status_label.text = "더 이상 인증할 수 없습니다."
                        Clock.schedule_once(App.get_running_app().speak_text('이전 화면으로 돌아갑니다.'))
                        Clock.schedule_once(self.change_screen('login'), 4)
                        # 이전 화면 복귀 혹은 더 이상 재시도를 하지 않도록 종료 처리 가능
                    else:
                        self.status_label.text = f"인증에 실패했습니다. {self.failed_attempts}/{self.max_attempts} 번."
                        Clock.schedule_once(App.get_running_app().speak_text('인증에 실패했습니다. 얼굴을 잘 보여주세요.'))
                        Clock.schedule_once(self.capture_and_authenticate, 5)

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
        #img_byte_arr = io.BytesIO()  # 초기화None

        try:
            print(f'img mode:{img.mode}')
            if img.mode != 'RGB':
                img = img.convert("RGB")

            with io.BytesIO() as byte_buffer:
                print(f'byte_buffer 초기화: {byte_buffer}')
                img.save(byte_buffer, format='JPEG')  # JPEG 대신 PNG로 테스트 가능
                print('after img.save')
                img_byte_arr = byte_buffer.getvalue()  # 바이트 값 저장
                print(f'변환된 이미지 바이트 배열 크기: {len(img_byte_arr)} 바이트')
                return img_byte_arr
        except Exception as e:
            print(f'이미지 처리 중 오류 발생: {e}')
            raise e



    def on_success(self):
        print("인증되었습니다!")
        App.get_running_app().speak_text('인증되었습니다.')
        Clock.schedule_once(lambda dt:self.change_screen('transfer'), 3)
        #self.manager.current = 'transfer'

    def change_screen(self, screen):
        self.manager.current = screen