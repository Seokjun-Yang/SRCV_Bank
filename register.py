from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.camera import Camera
from kivy.clock import Clock
from PIL import Image
import cv2
import numpy as np
import os
from plyer import storagepath

class RegistrationApp(App):
    def build(self):
        # 레이아웃 설정
        self.layout = BoxLayout(orientation='vertical')

        # 카메라 위젯
        self.camera = Camera(resolution=(640, 480), play=True)
        self.layout.add_widget(self.camera)

        # 상태 라벨
        self.status_label = Label(text="사진 촬영을 준비 중입니다...")
        self.layout.add_widget(self.status_label)

        # 사진 촬영 버튼
        self.capture_button = Button(text="사진 촬영")
        self.capture_button.bind(on_press=self.capture_image)
        self.layout.add_widget(self.capture_button)
        
        # 3초 후 자동 촬영
        Clock.schedule_once(self.capture_image, 10) # 10초 뒤 자동 촬영 

        return self.layout

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
                registered_image_path = os.path.join(self.storage_path, 'registered_image.jpg')

                # 텍스처를 이미지로 변환
                frame = self.texture_to_image(texture)


                #registered_image_path = 'registered_image.jpg'
                frame.save(registered_image_path)
                self.status_label.text = f"사진이 저장되었습니다. captured"

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

    def delete_registered_image(self, instance=None):
        """저장된 이미지를 삭제하는 함수"""
        
        registered_image_path = os.path.join(storagepath.get_home_dir(), 'registered_image.jpg') #os.path.join(self.storage_path, 'registered_image.jpg')
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

if __name__ == '__main__':
    RegistrationApp().run()

    '''
    app = ReifistrationApp()
    # Manually call any function
    # 특정 메소드만 사용 시시
    #app.delete_registered_image()  # This will delete the image directly
    #app.retake_image(None)  
    app.run()
    '''
