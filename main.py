from requests_html import HTMLSession
from bs4 import BeautifulSoup as bs
import re
import json as json
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
#from selenium.webdriver.common.by import By
import time
import sqlite3

video_url = input("Enter URL of the YouTube Video: ")
print("Please wait for 60 sec till fatching your data from ",video_url)
vi_id=video_url.split("v=")[1].split("&")[0]
session = HTMLSession()

def extract_video_informations(url):
    resp = session.get(url)
    resp.html.render(timeout=60)
    soup = bs(resp.html.html, "html.parser")
    result = {}

    result["id"]=vi_id
    result["title"] = soup.find("meta", itemprop="name")['content']
    result["views"] = soup.find("meta", itemprop="interactionCount")['content']
    result["description"] = soup.find("meta", itemprop="description")['content']
    result["date_published"] = soup.find("meta", itemprop="datePublished")['content']

    data = re.search(r"var ytInitialData = ({.*?});", soup.prettify()).group(1)
    data_json = json.loads(data)
    videoPrimaryInfoRenderer = data_json['contents']['twoColumnWatchNextResults']['results']['results']['contents'][0]['videoPrimaryInfoRenderer']
    videoSecondaryInfoRenderer = data_json['contents']['twoColumnWatchNextResults']['results']['results']['contents'][1]['videoSecondaryInfoRenderer']
    likes_label = videoPrimaryInfoRenderer['videoActions']['menuRenderer']['topLevelButtons'][0]['toggleButtonRenderer']['defaultText']['accessibility']['accessibilityData']['label']
    likes_str = likes_label.split(' ')[0].replace(',', '')
    result["likes"] = '0' if likes_str == 'No' else likes_str

    for k, v in result.items():
        print('{} : {}'.format(k, v))
        print("-----------------------------------------------------------------------------")
    addtodb(result)

def scrapcomment(url):
    option=webdriver.ChromeOptions()
    option.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=option)
    driver.get(url)
    time.sleep(10)
    prev_h=0 
    while True:
        height=driver.execute_script("""
            function getActualHeight() {
                            return Math.max(
                                Math.max(document.body.scrollHeight, document.documentElement.scrollHeight),
                                Math.max(document.body.offsetHeight, document.documentElement.offsetHeight),
                                Math.max(document.body.clientHeight, document.documentElement.clientHeight)
                            );
                        }
                        return getActualHeight();
            """)
        driver.execute_script(f"window.scrollTo({prev_h},{prev_h+300})")
        time.sleep(4)
        prev_h+=300    
        if prev_h >=height:
            break
    soup=bs(driver.page_source,'html.parser')
    driver.quit()
    comment_div=soup.select('#content #content-text') 
    comment_list= [x.text for x in comment_div]
    print("Comments-",comment_list)
   
    


if __name__=="__main__":
    urls=[
        video_url
    ]
    scrapcomment(urls[0])
 
def rec():
    driver=webdriver.Chrome(executable_path=r"C:\Users\DELL\.wdm\drivers\chromedriver\win32\102.0.5005.61\chromedriver.exe")
    # driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=option)
    driver.get(video_url)
    hrefs = [video.get_attribute('href') for video in driver.find_elements_by_id("thumbnail")]
    # hrefs = [video.get_attribute('href') for video in driver.find_elements(by=By.ID,value="thumbnail")]
    res_str = [ele for ele in hrefs if isinstance(ele, str)]
    id=[i.split("v=")[1].split("&")[0] for i in res_str]
    print("-----------------------------------------------------------------------------")
    print("All Recomanded Video's Id:",id)




def addtodb(result):
    sqliteConnection = sqlite3.connect('yt.db')
    cursor = sqliteConnection.cursor()
    
    
        
    query = 'INSERT INTO data values("'+result["id"]+'","'+result["title"]+'",'+result["views"]+',"'+result["description"]+'","'+result["date_published"]+'",'+result["likes"]+');'
    cursor.execute(query)
    sqliteConnection.commit()
    print("RECORD INSERTED SUCESSFULLY")
    print("-----------------------------------------------------------------------------")
    cursor.close()

print(extract_video_informations(video_url))
rec()