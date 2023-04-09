import requests
import os
from io import BytesIO
import json
from tqdm import tqdm


class VKYandexPhotoSaver:
    def __init__(self, vk_token, yd_token):
        self.vk_token = vk_token
        self.yd_token = yd_token
        self.vk_api_version = "5.130"
        self.vk_api_url = "https://api.vk.com/method"
        self.yd_api_url = "https://cloud-api.yandex.net/v1/disk/resources"
        self.params = {'access_token': self.vk_token, 'v': self.vk_api_version}
        self.headers = {"Authorization": f"OAuth {yd_token}"}

    def create_folder(self, folder_path):
        """Создание папки на Яндекс.Диске"""
        folder_params = {
            'path': folder_path,
            'overwrite': 'true',
            'permissions': 'rw'
        }
        response = requests.put(self.yd_api_url, params=folder_params, headers=self.headers)
        if response.status_code == 409:
            delete_params = {
                'path': folder_path
            }
            response = requests.delete(self.yd_api_url, params=delete_params, headers=self.headers)
        else:
            response.raise_for_status()

    def get_vk_photos(self, user_id):
        """Получение списка фотографий из VK"""
        params = {
            'user_ids': user_id,
            'owner_id': user_id,
            'album_id': 'profile',
            'extended': 1,
            'photo_sizes': 1
        }
        response = requests.get(f"{self.vk_api_url}/photos.get", params={**self.params, **params})
        response.raise_for_status()
        return response.json()['response']['items']

    def save_photo_to_yandex_disk(self, url, name, folder_path):
        """Сохранение фотографии на Яндекс.Диск"""
        response = requests.get(url)
        response.raise_for_status()
        data = BytesIO(response.content)
        name = self.get_unique_file_name(name,
                                         folder_path)  # добавляем числовой суффикс, если файл с таким именем уже существует
        upload_params = {
            'path': f'{folder_path}/{name}'
        }
        response = requests.get(f"{self.yd_api_url}/upload", params=upload_params, headers=self.headers)
        response.raise_for_status()
        upload_url = response.json()['href']
        response = requests.put(upload_url, headers=self.headers, data=data)
        response.raise_for_status()

    def save_photos(self, user_id, folder_path='/VKPhotos'):
        """Сохранение фотографий на Яндекс.Диск"""
        photos = self.get_vk_photos(user_id)
        sorted_photos = sorted(photos, key=lambda x: -x['likes']['count'])
        self.create_folder(folder_path)
        for i, photo in enumerate(tqdm(sorted_photos)):
            sizes = photo['sizes']
            max_size = max(photo['sizes'], key=lambda x: x['width'] * x['height'])
            url = max_size['url']
            size = photo['sizes'][-2]['type']
            likes_count = photo['likes']['count']
            name = f"{likes_count}.jpg"
            self.save_photo_to_yandex_disk(url, name, folder_path)

            size_params = {
                "file_name": name,
                "size": size
            }

            with open(f"{i + 1}.json", "w") as f:
                json.dump(size_params, f, ensure_ascii=False, indent=4)

    def get_unique_file_name(self, file_name, folder_path):
        """Генерация уникального имени файла с учётом уже существующих файлов в папке"""
        existing_files = set()
        response = requests.get(self.yd_api_url, params={'path': folder_path}, headers=self.headers)
        response.raise_for_status()
        for item in response.json()['_embedded']['items']:
            existing_files.add(item['name'])
        if file_name not in existing_files:
            return file_name
        else:
            base_name, ext = os.path.splitext(file_name)
            i = 1
            while f"{base_name}_{i}{ext}" in existing_files:
                i += 1
            return f"{base_name}_{i}{ext}"



vk_token = str(input('Введите токен VK:' ))
yd_token = str(input('Введите токен Яндекс:' ))
saver = VKYandexPhotoSaver(vk_token, yd_token)
saver.save_photos('2440629')
#saver.save_photos(int(input('Введите ID gпользователя VK:' )))
