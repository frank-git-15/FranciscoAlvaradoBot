from robocorp.tasks import task

from selenium import webdriver

import time


search_criteria = "Biden"

class Article:
    def __init__(self,header,description,imgeUrl) -> None:
        self.header = header
        self.description = description
        self.imgeUrl = imgeUrl



@task
def minimal_task():
    with webdriver.Chrome() as driver:
        articles_list = []
        driver.implicitly_wait(10)
        # driver.set_window_size(1024, 768)

        driver.get(f"https://www.aljazeera.com/search/{search_criteria}?sort=date")

        time.sleep(5)

