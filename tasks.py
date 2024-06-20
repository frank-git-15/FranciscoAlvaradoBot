from robocorp.tasks import task

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

import time


search_criteria = "Biden"

class Article:
    def __init__(self,header,description,imgeUrl) -> None:
        self.header = header
        self.description = description
        self.imgeUrl = imgeUrl


class webScrapper:

    def __init__(self,is_background,search_phrase):
        self.is_background = is_background
        self.search_phrase = search_phrase

    def extractListOfArticles(self):
        # Configure Chrome options
        options = Options()

        # Configuraciones adicionales
        options.add_argument("--disable-extensions")#Disable extensions of chrome
        options.add_argument("--profile-directory=Default")#use the default profile
        options.add_argument("--incognito")#Ensure that execution is not affected by cookies, browser cache or hystory
        options.add_argument("--start-maximized")#Maximize chrome window
        if self.is_background:
            # Execute the bot in background
            options.add_argument("--headless")  # Execute the script without graphic interface
            options.add_argument("--disable-gpu")  # Disable the use of GPU
            options.add_argument("--window-size=1920,1080")  # Set a window size
        with webdriver.Chrome(options=options) as driver:
            driver.implicitly_wait(10)
            driver.get(f"https://www.aljazeera.com/search/{self.search_phrase}?sort=date")

            try:
                while True:
                    try:
                        show_more_button = driver.find_element(By.XPATH,'//*[@id="main-content-area"]/div[2]/div[2]/button/span[2]')
                        driver.execute_script("arguments[0].scrollIntoView();", show_more_button)
                        show_more_button.click()
                        time.sleep(5)
                    except Exception as e:
                        print("Unable to find the show more button")
                        break
                
                articles =  driver.find_elements(By.XPATH, '//div[@class="search-result__list"]/article')

                if len(articles) > 0:
                    for article in articles:
                        header = article.find_element(By.CLASS_NAME,"gc__header-wrap").text
                        description = article.find_element(By.CLASS_NAME,"gc__excerpt").text

                        try:
                            img_element = article.find_element(By.CLASS_NAME, 'article-card__image')
                            img_url = img_element.get_attribute('src')
                        except Exception as e:
                            print(f"Error getting url of image")
                            img_url = None
                    

                        yield {"header":header,"description":description,"imageURL":img_url}
                else:
                    return None

            except Exception as e:
                return None
        




                


        


    






@task
def minimal_task():
    articlesList = []
    myWebScrapper = webScrapper(is_background=True,search_phrase=search_criteria)

    try:
        for article in myWebScrapper.extractListOfArticles():
            article_obj = Article(article["header"],article["description"],article["imageURL"])
            articlesList.append(article_obj)

    except Exception as e:
        print (e)





        

