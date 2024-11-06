import os
from datetime import datetime
from kivy.storage.jsonstore import JsonStore
from plyer import storagepath


class Metadata:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Metadata, cls).__new__(cls)
            cls._instance.store = JsonStore("metadata.json")
        return cls._instance

    def get_store(self):
        return self.store


class MetadataManager:
    def __init__(self, storage_path, max_images=5):
        self.store = Metadata().get_store()
        self.storage_path = storage_path
        self.max_images = max_images

        if not os.path.exists(storage_path):
            os.makedirs(storage_path)

    def save_temp_metadata(self, temp_name):
        """임시 메타데이터로 저장"""
        temp_path = os.path.join(self.storage_path, temp_name)
        self.store.put("temp", path=temp_path, time=datetime.now().isoformat())
        print("Temp metadata saved.")

    def finalize_metadata(self, user_seq_no):
        """임시 메타데이터의 키를 최종 사용자 번호로 변경"""
        if self.store.exists("temp"):
            temp_data = self.store.get("temp")
            self.store.put(user_seq_no, path=temp_data['path'], time=temp_data['time'])
            self.store.delete("temp")
            print(f"Metadata for user {user_seq_no} finalized.")
        else:
            print("No temp metadata found.")

    def delete_image_metadata(self, user_seq_no):
        """특정 유저의 메타데이터 삭제"""
        if self.store.exists(user_seq_no):
            self.store.delete(user_seq_no)
            print(f"Deleted metadata for user_seq_no: {user_seq_no}")
        else:
            print(f"No metadata found for user_seq_no: {user_seq_no}")

    def get_image_path(self, user_seq_no):
        """유저의 이미지 경로를 반환"""
        if self.store.exists(user_seq_no):
            return self.store.get(user_seq_no)['path']
        print(f"No metadata found for user_seq_no: {user_seq_no}")
        return None

    def delete_oldest_image(self):
        """저장된 메타데이터 중 가장 오래된 항목 삭제"""
        oldest_image = None
        oldest_time = datetime.now().isoformat()

        for key in self.store.keys():
            user_data = self.store.get(key)
            if user_data['time'] < oldest_time:
                oldest_time = user_data['time']
                oldest_image = key

        if oldest_image:
            self.store.delete(oldest_image)
            return oldest_image
        return None
