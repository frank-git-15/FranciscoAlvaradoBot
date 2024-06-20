from robocorp.tasks import task

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import time


search_criteria = "Biden"

class Article:
    def __init__(self,header,description,imgeUrl) -> None:
        self.header = header
        self.description = description
        self.imgeUrl = imgeUrl


def webScrapper(is_background=True):
    # Configute Chrome options
    options = Options()

    # Configuraciones adicionales
    options.add_argument("--disable-extensions")#Disable extensions of chrome
    options.add_argument("--profile-directory=Default")#use the default profile
    options.add_argument("--incognito")#Ensure that execution is not affected by cookies, browser cache or hystory
    options.add_argument("--start-maximized")#Maximize chrome window
    if is_background:
        # Execute the bot in background
        options.add_argument("--headless")  # Execute the script without graphic interface
        options.add_argument("--disable-gpu")  # Disable the use of GPU
        options.add_argument("--window-size=1920,1080")  # Set a window size
    with webdriver.Chrome() as driver:
        driver.implicitly_wait(10)
        driver.get(f"https://www.aljazeera.com/search/{search_criteria}?sort=date")

        


    






@task
def minimal_task():
    webScrapper(False)



        

