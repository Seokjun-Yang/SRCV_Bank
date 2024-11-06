from abc import ABC, abstractmethod
import boto3
import os

from dotenv import load_dotenv
from plyer import storagepath

# credential 추가
load_dotenv()
# AWS Rekognition 클라이언트 설정
rekognition = boto3.client('rekognition', region_name='us-east-1',
                           aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                           aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'))

# 인증 전략 패턴
class face_verification(ABC):
    def __init__(self, image_byte):
        self.authenticator = authenticator(image_byte)
    @abstractmethod
    def authenticate(self):
        pass
    @abstractmethod
    def get_seq_no(self):
        pass

class login_auth_result(face_verification):
    def authenticate(self):
        result = self.authenticator.authenticate()
        seq_no = self.authenticator.get_seq_no()
        print(f'login_auth_result:{result}, seq_no:{seq_no}') #None, None
        return result#self.authenticator.authenticate()
    def get_seq_no(self):
        return self.authenticator.get_seq_no()

class transfer_auth_result(face_verification):
    def authenticate(self):
        return self.authenticator.authenticate()
    def get_seq_no(self):
        return self.authenticator.get_seq_no()

class auth_strategy:
    @staticmethod
    def get_strategy(strategy_type, image_byte):
        if strategy_type == 'login':
            return login_auth_result(image_byte)
        elif strategy_type == 'transfer':
            return transfer_auth_result(image_byte)
        else:
            raise ValueError("잘못된 인증 전략 패턴 사용")

# 인증 성공 시 클래스
class success_action(ABC):
    @abstractmethod
    def execute(self, seq_no):
        pass
class login_action(success_action):
    def execute(self, seq_no):#, matched_name = None
        #print(f'matched_name:{matched_name}')
        return seq_no#'home' #matched_name #이미지 이름 반환 'home'#True
class transfer_action(success_action):
    def execute(self, seq_no = None):#, matched_name = None
        return 'transfer'

# 인증 성공 팩토리 패턴
class after_action:
    @staticmethod
    def get_action(action_type):
        if action_type == 'login':
            return login_action()
        elif action_type == 'transfer':
            return transfer_action()
        else:
            raise ValueError("잘못된 결과 반환 팩토리 클래스 사용 ")

#통합 관리
class face_varification_manager:
    def __init__(self, image_byte):
        #super(face_varification_manager, self).__init__(**kwargs)
        self.image_byte = image_byte

    def perform_auth(self, action_type, strategy_type):
        strategy = auth_strategy.get_strategy(strategy_type, self.image_byte)
        print(f'strategy:{strategy}')
        action = after_action.get_action(action_type)
        image_name = strategy.authenticate()  # 인증 결과를 저장
        print(f'image_name:{image_name}') #None

        #seq_no = strategy.get_seq_no()
        if image_name:  # image_name이 있을 경우 인증 성공으로 간주
            print(f'인증 성공:{image_name}')
            return action.execute(image_name)#matched_name=image_name
        else:
            print(f"인증 실패:{image_name}")
            return False


#인증 모듈
class authenticator:
    def __init__(self, image_byte):
        self.similarity_threshold = 97  # 유사도 임계값
        self.auth_successful = False  # 인증 성공 여부
        # 경로
        self.home_dir = storagepath.get_home_dir()
        self.storage_path = os.path.join(self.home_dir, "bank")
        # 촬영 이미지 바이트
        self.image_byte = image_byte

        self._seq_no = None
    def get_seq_no(self):
        return self._seq_no

    def authenticate(self):
        #저장 이미지 전부 비교
        bank_image_path = os.listdir(self.storage_path)
        image_path = [os.path.join(self.storage_path, image_name) for image_name in bank_image_path]

        for name in image_path:
            """AWS Rekognition을 사용해 얼굴 인증"""
            if self.compare_images(name):
                print(f'name:{name}')
                #user_seq_no = os.path.splitext(os.path.basename(name))[0]
                #print(f"user_seq_no:{name}")#user_seq_no
                self._seq_no = os.path.splitext(os.path.basename(name))[0]
                print(f'seq_no:{self._seq_no}') # 정상 출력
                return self._seq_no #True name
        print("No matches found")
        return False

    # registered_image_path -> 이미지 이름 포함
    def compare_images(self, registered_image_path):
        try:
            with open(registered_image_path, 'rb') as reg_img:
                response = rekognition.compare_faces(
                    SourceImage={'Bytes': reg_img.read()},
                    TargetImage={'Bytes': self.image_byte},
                    SimilarityThreshold=self.similarity_threshold
                )

                face_matches = response.get('FaceMatches', [])
                if face_matches:
                    for match in face_matches:
                        similarity = match['Similarity']
                        print(f"Similarity: {similarity}%")
                        if similarity >= self.similarity_threshold:
                            print("인증 되었습니다!")  # tts -> 동작으로 변경
                            return True

            print("인증에 실패하였습니다 ")  # tts -> 동작으로 변경
            return False

        except Exception as e:
            print(f"Error during Rekognition call: {str(e)}")
            #저장 사진이 없는데 로그이 시도 시 ??
            return False