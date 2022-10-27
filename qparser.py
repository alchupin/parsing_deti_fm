import os
import requests
import urllib.request

from pathlib import Path
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException

import eyed3
from eyed3.id3.frames import ImageFrame

URL = "https://www.deti.fm/program_child/uid/114343"
PATH = 'HRUM_with_images'


def get_https_list(url: str) -> list:
    """Формирует список адресов каждого выпуска аудио передачи"""
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get(url)

    driver.implicitly_wait(1)
    # btn_interview = driver.find_elements_by_name("banner-popup__close")
    # if btn_interview:
    #     btn_interview[1].click()
    while True:
        try:
            btn_elem = driver.find_element_by_link_text('Показать ещё')
            btn_elem.click()
        except NoSuchElementException:
            break

    text_elem_list = driver.find_elements_by_xpath("//*[contains(@class,'podcast__playlist')]")
    https_list = []
    for elem in text_elem_list:
        https_list.append({
            'title': elem.get_attribute('data-track-title'),
            'audio_url': elem.get_attribute('data-track'),
            'image_url': elem.get_attribute('data-track-cover')
            })
    return https_list


def download_mp3(source_list: list) -> None:
    """Сохраняет каждый аудио выпуск в виде mp3-файла"""
    for item in source_list:
        title = item.get('title').strip()
        audio_url = item.get('audio_url')
        cover_url = item.get('image_url')

        path = Path(PATH)
        if not os.path.exists(PATH):
            os.makedirs(PATH)
        image_dir_path = Path(path / 'images')
        if not os.path.exists(image_dir_path):
            os.makedirs(image_dir_path)
        image_file_name = Path(f"{image_dir_path}/{title}.jpg")
        image_file_full_path = image_file_name.resolve()
        img_data = requests.get(cover_url).content
        with open(image_file_full_path, 'wb') as handler:
            handler.write(img_data)

        path = Path(PATH)
        path.mkdir(parents=True, exist_ok=True)
        audio_file_path = Path(f"{path}/{title}.mp3")
        if not audio_file_path.is_file():
            urllib.request.urlretrieve(audio_url, audio_file_path)
            audiofile = eyed3.load(audio_file_path)
            if (audiofile.tag == None):
                audiofile.initTag()

            audiofile.tag.images.set(ImageFrame.FRONT_COVER, open(image_file_name,'rb').read(), 'image/jpeg')

            audiofile.tag.save()

        else:
            print(f"Файл {title}.mp3 уже скачан")


def main():
    https_list = get_https_list(URL)
    download_mp3(https_list)
    



if __name__ == '__main__':
    main()
