from kivy.app import App
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

# AWS Rekognition 클라이언트 설정
rekognition = boto3.client('rekognition', region_name='us-east-1')

class FaceAuthApp(App):
    def build(self):
        self.failed_attempts = 0  # 실패 횟수
        self.max_attempts = 3  # 최대 시도 횟수 (3번으로 수정)
        self.similarity_threshold = 97  # 유사도 임계값
        self.auth_successful = False  # 인증 성공 여부
        # 내부 디렉토리 경로
        self.storage_path = storagepath.get_home_dir()
        # 레이아웃 설정
        self.layout = BoxLayout(orientation='vertical')

        # 카메라 위젯
        self.camera = Camera(resolution=(640, 480), play=True)
        self.layout.add_widget(self.camera)

        # 상태 라벨
        self.status_label = Label(text="3초 후 자동으로 사진이 촬영됩니다...")
        self.layout.add_widget(self.status_label)

        # 테스트 버튼 추가 (수동으로 인증 테스트 가능)
        #self.test_button = Button(text="인증 시도")
        #self.test_button.bind(on_press=self.on_test_button_press)
        #self.layout.add_widget(self.test_button)

        # 3초 후 자동 촬영
        Clock.schedule_once(self.capture_and_authenticate, 3)



        return self.layout

    #테스트 버튼
    def on_test_button_press(self, instance):
        """테스트 버튼을 눌러 인증을 시도합니다."""
        self.capture_and_authenticate(instance)

    def load_registered_image(self):
        # 저장된 이미지를 가져오는 함수
        registered_image_path = os.path.join(self.storage_path, 'registered_image.jpg')
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
                registered_image_path = os.path.join(storagepath.get_home_dir(), 'registered_image.jpg')  #r'E:\final\SRCV_Bank\assets\id_0059_25_30_F.png' #로컬에 저장된 이미지 가져와서 비교   registered_image.jpg

                # 바이트 형태로 변환
                frame_bytes = self.image_to_bytes(frame)

                # 회원가입 시 촬영한 사진과 비교 (registered_image.jpg 대체 경로 사용)
                registered_image_path = os.path.join(self.storage_path, 'registered_image.jpg') #self.load_registered_image() #r'E:\final\SRCV_Bank\assets\id_0059_25_30_F.png'
                
                if not os.path.exists(registered_image_path):
                    self.status_label.text = "등록된 이미지가 없습니다."
                    return

                # 2차 본인 인증 시도
                is_authenticated = self.authenticate_user(registered_image_path, frame_bytes)

                if is_authenticated:
                    self.status_label.text = "success on verification."
                    self.on_success()
                else:
                    self.failed_attempts += 1
                    if self.failed_attempts >= self.max_attempts:
                        self.status_label.text = "can not verifify more."
                        #이전 화면 복귀 혹은 더 이상 재시도를 하지 않도록 종료 처리 가능
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
        self.status_label.text = "인증 성공: 특별한 행동을 수행할 수 있습니다."
        # 다음 화면 추가



            
# 콜백 사용 시
def run_login(callback):
    app = FaceAuthApp()  # LoginApp()
    app.on_auth_complete = callback  # 인증 후 호출될 콜백 함수 설정
    app.run()

if __name__ == '__main__':
    app = FaceAuthApp()
    app.run()
