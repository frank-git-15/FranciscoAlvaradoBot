from robocorp import workitems
from robocorp.tasks import task

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

import time
import re
import os
import requests
import zipfile
import logging
from random import randint
import pandas as pd

from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta


folder_outputs = "output/"

#configure logging
"""
Format
asctime = time when log was created
name = Name of the logger used to log the call.
levelname = Text logging level for the message ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
message = The logged message
"""
# logging.basicConfig(
#     filename=os.path.join(folder_outputs,'execution_logs.log'),
#     #Minimum log level
#     level=logging.DEBUG,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# )
# logger = logging.getLogger(__name__)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

#create handler for all the logs
all_logs_handler = logging.FileHandler(os.path.join(folder_outputs, 'execution_logs.log'))
all_logs_handler.setLevel(logging.DEBUG)
all_logs_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
all_logs_handler.setFormatter(all_logs_formatter)

#create handler for info and higher log levels
error_logs_handler = logging.FileHandler(os.path.join(folder_outputs, 'info_logs.log'))
error_logs_handler.setLevel(logging.INFO)
error_logs_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
error_logs_handler.setFormatter(error_logs_formatter)


#Add handlers to looger
logger.addHandler(all_logs_handler)
logger.addHandler(error_logs_handler)



def addLog(message:str="",log_level:str="debug"):
    """
    Create a log message using a logger a print message

    Args:
        log_level (str): log level should be one of the following: 'debug', 'info', 'warning', 'error', 'critical'.
        message (str): message that will contain the log

    Raises:
        Invalid log level: If the log level is not correct a log message will be thrown
        None message:  If message is None a log message will be thrown
    """
    log_level = log_level.lower()

    log_levels = ["debug", "info", "warning", "error", "critical"]


    if message is not None:
        
        if log_level in log_levels:
            if log_level == "debug":
                logger.debug(message)
            elif log_level == "info":
                logger.info(message)
            elif log_level == "warning":
                logger.warning(message)
            elif log_level == "error":
                logger.error(message)
            elif log_level == "critical":
                logger.critical(message)
        else:
            if "error" in message.lower():
                logger.warn(f"You are trying to create a log message with a wrong log level({log_level}) | creating log using error log level")
                logger.error(message)
            else:  
                logger.warn(f"You are trying to create a log message with a wrong log level({log_level}) | creating log using debug log level")
                logger.debug(message)
        print(message)
    else:
        logger.warn(f"You are trying to create a log message with message with None value")




def getTimeStamp():
    """
    Generate a time stamp and also add a random num between 0 and 999 in order to avoid duplicity

    output:
        timeStamp (str)   
    """
    random_integer = str(randint(0,999))
    timeStamp = str(datetime.now().strftime("%m%d%Y%H%M%S"))
    timeStamp = timeStamp+random_integer
    return timeStamp


class Article:
    """"
    This class represents an article from the web page https://www.aljazeera.com/ with a header, description and an image URL
    When an article is create the publication date is extracted from the description also detects if there amounts of money are mentioned.

    Attribute:
        header (str): header of the article
        description (str): description of the article
        imgeUrl(str): url of the article image , this URL is use to download the image

    """
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
        """"
            This funcion extract from a text the next type of date month/day/year
            
            Args:
                text: text that will be analized
            outputs:
                if a date was found:
                    date(str): return the found date in this forma month/day/year, example jan/01/2024
                if a date was not found:
                    None
            example outputs:
                jan/01/2021
                Feb/02/2024
                Aug/15/1998
        """
        pattern_months = r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s(\d{1,2}),\s(\d{4})"
        matches = re.findall(pattern_months, text.lower())

        if matches:
            date = "/".join(list(matches[0]))
            return date
        else: 
            return None
    def __extractTimeAgo(self,text):
        """"
            This function extractd the part of the article description that mentions how many minutes, hours or days ago the post was created
            text : str

            Args:
                text: text that will be analized
            outputs:
                if some time ago information was found:
                    timeAgo (str): return the found time ago
                if some time ago information was  not found:
                    None
            
            Example outputs:
                3 days
                2 minutes
                10 hours
        """
        pattern = r'(.*)\s+ago\s+\.{1,3}'
        matches = re.findall(pattern, text.lower())

        if matches:
            time_ago = matches[0] 
            return time_ago
        else:
            return None
    def __getPublicationDateFromTimeAgo(self,timeAgo):
        
        """"
            This funcion calculate the publication date base on the time ago, for example '10 days'
            
            Args:
                timeAgo: time ago information (example: 10 days, 1 hour, 5 minutes, 8 hours)
            outputs:
                 newDate (str): time ago converted to date
            
            
            Raises:
                Time ago to long: The time ago must be exactly  2 words
                None message:  If message is None a log message will be thrown
        """
        parts = timeAgo.split()
        try:
            amount = int(parts[0])
        except Exception as e:
            addLog(f"Time ago {timeAgo} date is not correct, it must be exactly 2 words, for example 2 days, 10 hours, 17 minutes etc | error {e}","error")
            return None
        unit = str(parts[1]).lower()
        
        currentDate = datetime.now()

        units = ["minutes","hours","hour","minute","day","days"]

        if unit in units:
        
            if unit == "minutes" or unit == "minute":
                newDate = currentDate - timedelta(minutes = amount)
            elif unit == "hours" or unit == "hour":
                newDate = currentDate - timedelta(hours = amount)
            elif unit == "days" or unit == "day":
                newDate = currentDate - timedelta(days = amount)
        else:
            addLog(f"Time unit {unit} is not correct it must be one of these units: {units}","error")
            newDate = None
        try:
            newDate = newDate.strftime("%b/%d/%Y")
        except Exception as e:
            addLog("Error converting newDate to string | e","error")
            newDate = None
        return newDate
    def __extractDatePublication(self,description):
        
        """"
        This function extractes the publication date of an article from its description
        Args:
            description(str): article description 
        outputs:
            datePublicationOfArticle(str): date of publication of the article

        """
        addLog("Extracting publication date from article .....","debug")
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

        """"
        This function make sure that the date of each post has the same format Month(str)/Day/Year

        arg:
            date(str): date to standarize
        
        out:
            date_dateTime(datetime): date as a datetime type
        
        Raises:
            Error converting date in string to date datetime type: return None

        """

        try:
            date_dateTime = datetime.strptime(date,"%b/%d/%Y")
        except Exception as e:
            addLog(f"Error standarizing {date} | {e}","error")
            date_dateTime = None
        return date_dateTime

    def get_date_publish_str(self):
        """"
            This function converts the attribute of the article date_publish(datetime) in a date(str)

            output:
                dateStr(str): publication date of the article now in string type
        """
        try:
            dateStr = datetime.strftime(self.date_publish,"%b/%d/%Y")
        except Exception as e:
            addLog(f"Error converting date {datetime} to string | {e}","error")
            dateStr = None
        return dateStr

    def get_description_cleaned(self):
        """
            This function cleans the article description, removing dates at the beginning 
            or information about how long ago the post was created.

            output:
                description_cleaned: description with no text related to date or time ago info at the beginning
        """
        regex_date = re.compile(r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s(\d{1,2}),\s(\d{4})\s(\.\.\.\s)+",re.IGNORECASE)
        regex_time_ago = re.compile(r"^\d+\s(?:hours?|minutes?|days?)\sago\s(\.\.\.\s)+", re.IGNORECASE)

        addLog("Cleaning description .....","debug")
        description_cleaned = regex_date.sub("", self.description)
        #Delete the date or time ago from the description
        description_cleaned = regex_time_ago.sub("", description_cleaned)
        addLog("Cleaning description finished","debug")
        return description_cleaned

    def get_ocuurences_search_phrase(self,search_phrase):
        """
            This function counts how many time a phrase appears in the description or in the header of the article

            args:
                search_phrase (str): phrase to search for in the description and header
            
            output:
                total_ocurrences (int): amount of time that the phrase appears in the description or in the header.

        """
        ocurrences_in_description = self.description.lower().count(search_phrase.lower())
        ocurrences_in_header = self.header.lower().count(search_phrase.lower())

        total_ocurrences = ocurrences_in_description+ocurrences_in_header

        return total_ocurrences

    def __contains_money_amount(self):
        """
            This function detects if the description or header contains any amount of money
            
            output:
                true or false

        """
        money_pattern = r'\$[\d,]+(?:\.\d+)?|\b\d+\s*(?:dollars?|USD)\b'

        return bool(re.search(money_pattern, self.description)) or bool(re.search(money_pattern, self.header)) 
    
    def download_image(self,img_title,folder_path = "output/images"):
        """
            This function do0wnload an image using an URL and stores it in this folder output/images

            args:
                img_title(str): title of the image
                folder_path(str): path where the images will be downloaded, by default is used output/images
            
            output if not error:
                fullPathImg (str): path where the image was donwloaded
            output if error:
                None
        """
        addLog(f"Trying to download image from {self.imgeUrl}","debug")
        img_title = str(img_title)
        
        if not os.path.exists(folder_path):
            try:
                os.mkdir(folder_path)
                addLog(f"Folder {folder_path} created :)","info")
            except:
                addLog(f"Unable to create folder {folder_path} | Error: {e}","error")
                return None
            
        addLog("Verifying if image name has a correct image extension","debug")
        img_title_splitted = img_title.lower().split(".")
        if img_title_splitted[-1] != "png" and img_title_splitted[-1] != "jpg":
            addLog(f"The image extension was not correct, adding .png extension to the image title {img_title}","debug")
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
                    addLog(f"It was NOT possible to save the downloade image in this path {fullPathImg}, trying again using just the timestamp","error")
                    timeStamp = datetime.now().strftime("%m%d%Y%H%M%S")
                    fullPathImg = os.path.join(folder_path,timeStamp+".png")

                    try:
                        with open(fullPathImg,'wb') as img:
                            img.write(response.content)
                            return fullPathImg
                    except Exception as e:
                        addLog(f"It was not possible to save the downloade image in this path {fullPathImg}","error")
                        return None
            else:
                addLog(f"Image could be downloaded using this URL {self.imgeUrl}","error")
                return None
        except Exception as e:
            addLog(f"Error downloading image from article {e}","error")
            return None


class webScrapper:
    """"
    This class represents a web scrapper that extract information from the web page https://www.aljazeera.com/ extracting the header, description and image URL
    from each article

    Attribute:
        is_background (bool): header of the article
        search_phrase (str): phrase to be searched on the website https://www.aljazeera.com/
    """
    def __init__(self,
                 is_background:bool,
                 search_phrase:str):
        self.is_background = is_background
        self.search_phrase = search_phrase

    def extractListOfArticles(self):

        """"
            Function that navigare to https://www.aljazeera.com/search search the inputted phrase and sort it by date.
            This seach is performed in an incongito chrome window in order to do not be detected as a bot.

            output (yield):
                {
                    "header":str,
                    "description":str,
                    "imageURL":str
                }
        """
        # Configure Chrome options
        options = Options()

        # Configuraciones adicionales
        options.add_argument("--disable-extensions")#Disable extensions of chrome
        options.add_argument("--profile-directory=Default")#use the default profile
        options.add_argument("--incognito")#Ensure that execution is not affected by cookies, browser cache or hystory
        options.add_argument("--start-maximized")#Maximize chrome window
        if self.is_background:
            # Execute the bot in background
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--headless")  # Execute the script without graphic interface
            options.add_argument("--disable-gpu")  # Disable the use of GPU
            options.add_argument("--window-size=1920,1080")  # Set a window size
        options.add_argument("--remote-debugging-port=9222")
        with webdriver.Chrome(options=options) as driver:
            driver.implicitly_wait(10)
            addLog(f"Going to web page https://www.aljazeera.com/search/{self.search_phrase}?sort=date .......","info")
            driver.get(f"https://www.aljazeera.com/search/{self.search_phrase}?sort=date")
            try:
                while True:

                    try:
                        show_more_button = driver.find_element(By.XPATH,'//*[@id="main-content-area"]/div[2]/div[2]/button/span[2]')
                        driver.execute_script("arguments[0].scrollIntoView();", show_more_button)
                        show_more_button.click()
                        addLog("Show more button clicked","debug")
                        time.sleep(5)
                    except Exception as e:
                        addLog(f"Unable to find the show more button | {e}","error")
                        break
                
                addLog("Detecting if there is some article to analyze")
                articles =  driver.find_elements(By.XPATH, '//div[@class="search-result__list"]/article')

                if len(articles) > 0:
                    addLog(f"{len(articles)} articles extracted, extracting infomation of each particular article: header, description and image url","info")
                    for article in articles:
                        header = article.find_element(By.CLASS_NAME,"gc__header-wrap").text
                        description = article.find_element(By.CLASS_NAME,"gc__excerpt").text
                        try:
                            img_element = article.find_element(By.CLASS_NAME, 'article-card__image')
                            img_url = img_element.get_attribute('src')
                        except Exception as e:
                            addLog(f"Error getting url of image {e}","error")
                            img_url = None
                    

                        yield {"header":header,
                               "description":description,
                               "imageURL":img_url}
                else:
                    return None

            except Exception as e:
                addLog(f"Error extracting articles from web page https://www.aljazeera.com/search/ | {e}","fatal")
                return None
            
class FilterArticles:
    """"
    This class represents an articles filter


    Attribute:
        articles_list (list[Article]): list of Article objects
        num_months_before (int): How many months ago are the articles needed
    
    Constructor:
        num_articles_didnt_processed = initialized to 0
        num_articles_processed = initialized to 0
    """
    def __init__(self,
                 articles_list:list[Article],
                 num_months_before:int):
        self.articles_list = articles_list
        self.num_months_before = num_months_before
        self.num_articles_didnt_processed = 0
        self.num_articles_processed = 0

    def __get_last_date_to_gather_articles(self,
                                           num_months_before):

        """
       This function get the last date that we want an Article from.
       Get the fist day of the current month then subtract  the amount of months inputted
       args:
            num_months_before (int): How many months ago are the articles needed
        
        output:
            first_day_of_month(datetime): date of the last month that we want a post
        """
    
        try:
            today = datetime.now()

            first_day_of_month = today.replace(day=1)

            if num_months_before < 2:
                return first_day_of_month

            else:
                num_months_before -=1 
                return first_day_of_month - relativedelta(months=num_months_before)
            
        except TypeError as e:
            addLog(f"You need to enter a integer value {num_months_before} | {e}")
            return None
        except Exception as e:
            addLog(f"Error getting the last month date that we want an article from | {e}")
        
    #this function verify if the date of an article is not older thant the date that was generate by get_last_date_to_gather_articles
    def __filter_by_month(self,article:Article):
        """"
            This function verifies if the date of an article is not older thant the date that was generate by get_last_date_to_gather_articles,
            and delete the articles that has an older date

            args:
                article (Article): article object

        """
        filter_date = self.__get_last_date_to_gather_articles(self.num_months_before)
        try:
            if article.date_publish.date() >= filter_date.date():
                self.num_articles_processed += 1
                return True
            else:
                self.num_articles_didnt_processed += 1
                addLog(f"Date {article.date_publish.date()} is olden than {filter_date.date()}","debug")
                return False
        except Exception as e:
            addLog(f"Error filtering article by date, article not deleted | {e}")
            return True
        
    #Filter each article in articles_list using the filter_by_month function
    def get_filtered_articles(self):
        """
            This function applies the filter 'filter_by_month' to each article in the 'articles_list'

            ouput:
                articlesList_filtered (list(Articles)): filtered list of articles 
        """
        try:
            articlesList_filtered = list(filter(self.__filter_by_month,self.articles_list))

        except Exception as e:
            addLog(f"Error applying filter to each article, returning the same article list | {e}")
            articlesList_filtered = self.articles_list
        
        return articlesList_filtered


class Report:
    """"
    This class represents Report

    Attribute:
        articles_list (list[Article]): list of Article objects
        search_criteria (int): seach phrase that was used
    """
    def __init__(self,articlesList:list[Article],search_criteria) -> None:
        self.articlesList = articlesList
        self.search_criteria= search_criteria

    def buildExcelFile(self):
        """
        This function create an excel file report using the article list.
            the report has this headers: Header, Descritption,Date, Ocurrences of search phrase, Contains some money amount, Image path
        """
        articles_list = []
        downloaded_images = []
        for article in self.articlesList:
            timeStamp = getTimeStamp()
            imageTitle = f"{self.search_criteria} {timeStamp}.png"
            description = article.get_description_cleaned()
            ocuurences_search_phrase = article.get_ocuurences_search_phrase(self.search_criteria)
            path_downloaded_image = article.download_image(imageTitle)

            downloaded_images.append(path_downloaded_image)


            articles_list.append({"Header":article.header,
                                "Descritption":description,
                                "Date":str(article.date_publish.date()),
                                "Ocurrences of search phrase":ocuurences_search_phrase,
                                'Contains some money amount':article.contains_some_money_amount,
                                "Image path":os.path.basename(path_downloaded_image)
                                })
        if len(articles_list) > 0:
                addLog(f"Writing results of {len(articles_list)} found articles to the report ....","info")
                excelFileName = os.path.join(folder_outputs,f"articles_webScraping {timeStamp}.xlsx")

                timeStamp = getTimeStamp()
                df_articles = pd.DataFrame(articles_list)
                df_articles.to_excel(excelFileName,index=False)

                addLog(f"Report created, locatin: {excelFileName}")

                if len(downloaded_images) > 0:
                    self.zip_images(downloaded_images)

                return excelFileName
        else:
            addLog("No articles founded","warn")
            return None

    def zip_images(self,image_path_list):
        """
            this function zip a list of file

            args:
                image_path_list (list(file paths)): 
        """
        addLog("Zipping list of files ....","info")
        try:
            with zipfile.ZipFile("output/consolidated_images.zip", 'w') as zipf:
                for file in image_path_list:
                    zipf.write(file, os.path.basename(file))
            addLog(f"Created zip file - output/consolidated_images.zip","info")
        except Exception as e:
            addLog("Error zipping images | {e}","eror")

        

@task
def minimal_task():

    addLog("Getting work item from control room","info")

    item = workitems.inputs.current

    search_criteria = item.payload["payload"]["search_criteria"]
    months_before = item.payload["payload"]["months_before"]

    

    if search_criteria is not None or search_criteria =="":

        print(f"search_criteria {search_criteria}")
        print(f"months_before {months_before}")

        addLog("Web scraping started ....","info")
        addLog(f"Search phrase that will be used: {search_criteria}","info")
        addLog(f"Getting articles of the last : {months_before} months","info")


        
        articlesList = []
        addLog("Starting web scrapper....","info")
        myWebScrapper = webScrapper(is_background=True,
                                    search_phrase=search_criteria)

        try:
            addLog("Creating objects Articles  ....","debug")
            for article in myWebScrapper.extractListOfArticles():

                article_obj = Article(article["header"],
                                    article["description"],
                                    article["imageURL"])
                articlesList.append(article_obj)
            
            addLog(f"{len(articlesList)} objects Articles created  ....","debug")
            
            if len(articlesList) > 0:

                addLog(f"instantiating filter for articles ... ","debug")
                articlesFilter = FilterArticles(articles_list=articlesList,
                                                num_months_before=months_before)
                
                if months_before > 2:
                    addLog(f"Filtering {len(articlesList)} articles to have only the articles of the last {months_before} months","debug")
                else:
                    addLog(f"Filtering {len(articlesList)} articles to have only the articles of the current month","debug")  
                articles_filtered_list = articlesFilter.get_filtered_articles()

                addLog(f"Amount of Articles that did NOT meet the filter: {articlesFilter.num_articles_didnt_processed}","info")
                addLog(f"Amount of Articles that did meet the filter: {articlesFilter.num_articles_processed}","info")

                addLog(f"Instantiating Report class ... ","debug")
                report = Report(articlesList=articles_filtered_list,search_criteria=search_criteria)

                addLog(f"Creating report excel file report with all the gathered information ... ","info")
                excelFileName = report.buildExcelFile()
                addLog(f"Report created, excel file name: {excelFileName}","info")

            else:
                addLog(f"No articles found using seach phrase {search_criteria}","warning")
            

        except Exception as e:
            addLog(f"Error processing articles | {e}","critical")
            workitems.ApplicationException(f"Error processing articles | {e}")
        
    else:
        addLog(f"Seach criteria is empty {search_criteria}","error")
        workitems.BusinessException(f"Seach criteria is empty {search_criteria}")
        





        

