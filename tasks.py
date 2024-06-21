from robocorp.tasks import task
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

import time
import re
import os
import requests
from random import randint
import pandas as pd
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta
from robocorp import workitems
import zipfile

folder_outputs = "output/"




def getTimeStamp():
    random_integer = str(randint(0,999))
    timeStamp = str(datetime.now().strftime("%m%d%Y%H%M%S"))
    timeStamp = timeStamp+random_integer
    return timeStamp

class Article:
    def __init__(self,
                 header,
                 description,
                 imgeUrl):
        self.header = header
        self.description = description
        self.imgeUrl = imgeUrl
        self.date_publish = self.__extractDatePublication(self.description)
        self.contains_some_money_amount = self.__contains_money_amount()

    def __extractDate(self,text):
        pattern_months = r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s(\d{1,2}),\s(\d{4})"
        matches = re.findall(pattern_months, text.lower())

        if matches:
            date = "/".join(list(matches[0]))
            return date
        else: 
            return None
    def __extractTimeAgo(self,text):
    
        pattern = r'(.*)\s+ago\s+\.{1,3}'
        matches = re.findall(pattern, text.lower())

        if matches:
            return matches[0]
        else:
            return None
    def __getPublicationDateFromTimeAgo(self,timeAgo):
    
        parts = timeAgo.split()
        try:
            amount = int(parts[0])
        except Exception as e:
            print(e)
            return None
        unit = str(parts[1]).lower()
        
        currentDate = datetime.now()
        
        if unit == "minutes" or unit == "minute":
            newDate = currentDate - timedelta(minutes = amount)
        elif unit == "hours" or unit == "hour":
            newDate = currentDate - timedelta(hours = amount)
        elif unit == "days" or unit == "day":
            newDate = currentDate - timedelta(days = amount)
        else:
            newDate = None
        try:
            newDate = newDate.strftime("%b/%d/%Y")
        except:
            newDate = None
        return newDate
    def __extractDatePublication(self,description):

        datePublication = self.__extractDate(description)

        datePublicationOfArticle = None

        if datePublication is not None:
            datePublicationOfArticle = datePublication
        else:
            timeAgo = self.__extractTimeAgo(description)
            if timeAgo is not None:
                dateFromTimeAgo = self.__getPublicationDateFromTimeAgo(timeAgo)

                datePublicationOfArticle = dateFromTimeAgo
        
        if datePublicationOfArticle is not None:
            datePublicationOfArticle = self.__standarizeDate(datePublicationOfArticle)

        return datePublicationOfArticle

    
    def __standarizeDate(self,date):

        try:
            date_dateTime = datetime.strptime(date,"%b/%d/%Y")

            #dateStr = datetime.strftime(date_dateTime,"%b/%d/%Y")

        except Exception as e:
            print(f"Error standarizing {date} | {e}")
            date_dateTime = None
        return date_dateTime

    def get_date_publish_str(self):
        try:
            dateStr = datetime.strftime(self.date_publish,"%b/%d/%Y")
        except Exception as e:
            print(f"Error converting date {datetime} to string | {e}")

            dateStr = None
        return dateStr

    def get_description_cleaned(self):
        regex_date = re.compile(r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s(\d{1,2}),\s(\d{4})\s(\.\.\.\s)+",re.IGNORECASE)
        regex_time_ago = re.compile(r"^\d+\s(?:hours?|minutes?|days?)\sago\s(\.\.\.\s)+", re.IGNORECASE)
        description_cleaned = regex_date.sub("", self.description)

        
        #Delete the date or time ago from the description
        description_cleaned = regex_time_ago.sub("", description_cleaned)

        return description_cleaned

    def get_ocuurences_search_phrase(self,search_phrase):
        ocurrences_in_description = self.description.lower().count(search_phrase.lower())
        ocurrences_in_header = self.header.lower().count(search_phrase.lower())



        return ocurrences_in_description+ocurrences_in_header

    def __contains_money_amount(self):
        money_pattern = r'\$[\d,]+(?:\.\d+)?|\b\d+\s*(?:dollars?|USD)\b'

        return bool(re.search(money_pattern, self.description)) or bool(re.search(money_pattern, self.header)) 
    
    def download_image(self,img_title,folder_path = "output/images"):

        img_title = str(img_title)
        
        if not os.path.exists(folder_path):
            try:
                os.mkdir(folder_path)
                print(f"Folder {folder_path} created :)")
            except:
                print(f"Unable to create folder {folder_path} | Error: {e}")
                return None
            
        #Verify that the image file name has a correct image extension
        img_title_splitted = img_title.lower().split(".")
        if img_title_splitted[-1] != "png" and img_title_splitted[-1] != "jpg":
            img_title = img_title+".png"


        try:

            response = requests.get(self.imgeUrl)
            if response.status_code==200:
                try:
                    fullPathImg = os.path.join(folder_path,img_title)
                    with open(fullPathImg,'wb') as img:
                        img.write(response.content)
                        return fullPathImg
                except Exception as e:
                    timeStamp = datetime.now().strftime("%m%d%Y%H%M%S")
                    fullPathImg = os.path.join(folder_path,timeStamp+".png")
                    with open(fullPathImg,'wb') as img:
                        img.write(response.content)
                        return fullPathImg
        except Exception as e:
            print(f"Error downloading image from article {e}")
            return None


class webScrapper:

    def __init__(self,
                 is_background,
                 search_phrase):
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
                    

                        yield {"header":header,
                               "description":description,
                               "imageURL":img_url}
                else:
                    return None

            except Exception as e:
                print(f"Error - {e}")
                return None
            
class FilterArticles:
    def __init__(self,
                 articles_list,
                 num_months_before) -> None:
        self.articles_list = articles_list
        self.num_months_before = num_months_before
        self.num_articles_didnt_processed = 0
        self.num_articles_processed = 0

    
    #this function get the last date that we want an Article from 
    #Input num_months_before | integer
    #output datetime variable
    def __get_last_date_to_gather_articles(self,
                                           num_months_before):
    
        try:
            today = datetime.now()

            first_day_of_month = today.replace(day=1)

            if num_months_before < 2:
                return first_day_of_month

            else:
                num_months_before -=1 
                return first_day_of_month - relativedelta(months=num_months_before)
            
        except TypeError as e:
            print("You need to enter a integer value")
            return None
        
    #this function verify if the date of an article is not older thant the date that was generate by get_last_date_to_gather_articles
    def __filter_by_month(self,article):
        filter_date = self.__get_last_date_to_gather_articles(self.num_months_before)
        try:
            #print(f"Date post {article.date_publish.date()} | filter {filter_date.date()} ")
            if article.date_publish.date() >= filter_date.date():
                self.num_articles_processed += 1
                return True
            else:
                self.num_articles_didnt_processed += 1

                #print(f"Date {article.date_publish.date()} is older than {filter_date.date()}")
                return False
        except Exception as e:
            print("error filtering article by date")
            return False
        
    #Filter each article in articles_list using the filter_by_month function
    def get_filtered_articles(self):
        try:
            articlesList_filtered = list(filter(self.__filter_by_month,self.articles_list))
        except Exception as e:
            print(f"Error filtering articles | {e}")
            articlesList_filtered = []
        
        return articlesList_filtered


class Report:
    def __init__(self,articlesList:list[Article],search_criteria) -> None:
        self.articlesList = articlesList
        self.search_criteria= search_criteria

    def buildExcelFile(self):
        articles_list = []
        downloaded_images = []
        for article in self.articlesList:
            timeStamp = getTimeStamp()
            imageTitle = f"{self.search_criteria} {timeStamp}.png"
            description = article.get_description_cleaned()
            ocuurences_search_phrase = article.get_ocuurences_search_phrase(self.search_criteria)
            path_downloaded_image = article.download_image(imageTitle)

            downloaded_images.append(path_downloaded_image)


            articles_list.append({"header":article.header,
                                "descritption":description,
                                "date":str(article.date_publish.date()),
                                "ocurrences search phrase":ocuurences_search_phrase,
                                'contains some_money amount':article.contains_some_money_amount,
                                "image path":os.path.basename(path_downloaded_image)
                                })
        if len(articles_list) > 0:
                excelFileName = os.path.join(folder_outputs,f"articles_webScraping {timeStamp}.xlsx")

                timeStamp = getTimeStamp()
                df_articles = pd.DataFrame(articles_list)
                df_articles.to_excel(excelFileName,index=False)

                if len(downloaded_images) > 0:
                    self.zip_images(downloaded_images)

                return excelFileName
        else:
            print("No articles founded")
            return None

    def zip_images(self,image_path_list):
        with zipfile.ZipFile("output/consolidated_images.zip", 'w') as zipf:
            for file in image_path_list:
                zipf.write(file, os.path.basename(file))
        print(f"Created zip file - output/consolidated_images.zip")
        

@task
def minimal_task():

    item = workitems.inputs.current

    print("Received payload: ",item.payload)

    print(f"payload type {type(item.payload)}")

    search_criteria = item.payload["payload"]["search_criteria"]
    months_before = item.payload["payload"]["months_before"]

    print(f"search_criteria {search_criteria}")
    print(f"months_before {months_before}")

    
    articlesList = []
    myWebScrapper = webScrapper(is_background=True,
                                search_phrase=search_criteria)

    try:
        for article in myWebScrapper.extractListOfArticles():

            article_obj = Article(article["header"],
                                  article["description"],
                                  article["imageURL"])
            articlesList.append(article_obj)
        
        if len(articlesList) > 0:
            articlesFilter = FilterArticles(articles_list=articlesList,
                                            num_months_before=months_before)
            
            articles_filtered_list = articlesFilter.get_filtered_articles()

            print(f"Total of articles {len(articlesList)}")
            print(f"Articles did not processed {articlesFilter.num_articles_didnt_processed}")
            print(f"Articles processed {articlesFilter.num_articles_processed}")

            report = Report(articlesList=articles_filtered_list,search_criteria=search_criteria)

            excelFileName = report.buildExcelFile()

           

            print(f"output excel file {excelFileName}")
        else:
            print("No articles found")
        

    except Exception as e:
        print (f"************* Error {e}")
    
    print("Break")





        

