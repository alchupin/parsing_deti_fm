import requests
import urllib.request
import re

from pathlib import Path
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import ElementNotInteractableException

URL = "https://www.deti.fm/program_child/uid/114343"
PATH = 'CIST'


def get_https_list(url: str) -> list:
    """Формирует список адресов каждого выпуска аудио передачи"""
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get(url)
    btn_city = driver.find_element_by_class_name("nextPage")
    if btn_city:
        btn_city.click()
    driver.implicitly_wait(2)
    btn_interview = driver.find_elements_by_name("userdataform")
    if btn_interview:
        btn_interview[1].click()
    while True:
        try:
            btn_elem = driver.find_element_by_class_name("podcast__list_Btntext")
            btn_elem.click()
        except ElementNotInteractableException:
            break
    text_elem_list = driver.find_elements_by_xpath("//*[contains(@class,'podcasts__item podcasts_line-player_')]")
    https_list = []
    for elem in text_elem_list:
        issue_number = elem.get_attribute("class").split('_')[-1]
        https_list.append("https://www.deti.fm/podcast__player/album/114343/uid/" + issue_number)
    return https_list


def download_mp3(source_list: list) -> None:
    """Сохраняет каждый аудио выпуск в виде mp3-файла"""
    for url in source_list:
        html = requests.get(url)
        soup = BeautifulSoup(html.content, 'html.parser')
        title = soup.find('h1').text
        path = Path(PATH)
        path.mkdir(parents=True, exist_ok=True)
        file = Path(f"{path}/{title}.mp3")
        if not file.is_file():
            for a in soup.find_all('audio', src=re.compile('http.*\.mp3')):
                mp3_url = a['src']
                urllib.request.urlretrieve(mp3_url, f"{path}/{title}.mp3")
        else:
            print(f"Файл {title}.mp3 уже скачан")


def main():
    https_list = get_https_list(URL)
    download_mp3(https_list)


if __name__ == '__main__':
    main()
