# 0   不爬文 ;  1   爬文
SwitchLTN       1   # 自由時報 
SwitchUDN       1   # 聯合新聞網
SwitchCNA       1   # 中央社
SwitchET        1   # ETtoday
SwitchApple     1   # 壹蘋新聞網
SwitchSET       1   # 三立新聞網
SwitchMIRROR    1   # 鏡週刊 
SwitchTVBS      1   # TVBS
SwitchNOWNEWS   1   # NOWNEWS
SwitchCTWANT    1   # CTWANT
SwitchEBC       1   # 東森新聞
SwitchCTS       1   # 華視新聞

# 有些新聞網頁在滑鼠滾輪往下滾的時候會載入新的新聞，
# 假如下滑這些頁數以後還是沒有爬完 "timeSlot" 個小時內的新聞，
# 可以把下面這個數字加大，但爬文所需時間會慢一些
scrollPages   6     # >  4 ，自由和聯合新聞數量較多   
timeSlot      1.1   # 收集幾個小時內的新聞
scrollDelay   2.0   # 模擬滑鼠滾輪往下滾的間隔時間

places    ["竹市", "消防局", "消防署", "竹塹"]
persons   ["高虹安", "高市長", "消防員", "消防人員", "消防替代役", "消防役", "EMT",
           "義消", "義警消", "搜救人員", "救護技術員", "消促會", "工作權益促進會"]
issues    ["救災", "倒塌", "消防", "到院前", "防災", "一氧化碳中毒", "天坑"]

issueBehavior   ["急救", "心肺復甦術", "CPR", "電擊", "灌救"]
issueGoods      ["AED", "住警器", "消防栓"]
issueSuicide    ["燒炭", "上吊", "割腕", "割喉", "自戕", "跳樓", "自殺"]
issueFire       ["火災", "失火", "起火", "大火", "火光", "火燒車",
                 "水線", "滅火器", "火海", "打火", "灌救",
                 "火調", "燒毀", "火警", "燒起來", "雲梯車"]
issueAccident   ["車禍", "地震深度", "最大震度", "芮氏規模", "有感地震",
                 "墜橋", "輾斃", "墜樓", "山難", "瓦斯外洩", "土石流"]
issueStatus     ["喪命", "喪生", "失蹤", "傷者", "遺體", "無生命跡象",
                 "殉職", "失聯", "嗆暈", "意識模糊", "無意識", "罹難",
                 "命危", "OHCA", "不治", "昏迷", "受困", "無呼吸心跳", "亡"]

deleteTagsLTN       {"ent":"娛樂", "istyle":"時尚", "sports":"體育", "ec":"財經", 
                     "def":"軍武", "3c":"3C", "art.ltn":"藝文", "playing":"玩咖",
                     "food":"食譜", "estate":"地產", "yes123":"求職", "auto":"汽車"}
deleteTagsUDN       ["娛樂", "股市", "產經", "運動", "科技", "文教", "健康"]
deleteTagsCNA       ["娛樂", "產經", "證券", "科技", "文化", "運動"]
deleteTagsETtoday   ["旅遊", "房產雲", "影劇", "時尚", "財經", "寵物動物", "ET車雲"]
deleteTagsApple     ["體育", "娛樂時尚", "財經地產", "購物"]
deleteTagsSET       ["娛樂", "財經", "運動", "兩岸", "音樂", "新奇"]
deleteTagsMIRROR    {"fin":"財經", "ind":"財經", "bus":"財經", "money":"財經", "ent":"娛樂"}
deleteTagsTVBS      ["娛樂", "食尚", "體育"]
deleteTagsCTWANT    ["娛樂", "財經", "漂亮"]
deleteTagsEBC       ["娛樂", "健康", "體育", "財經"]
deleteTagsCTS       ["財經", "氣象", "娛樂", "運動", "藝文"]
#############################################################
#   以下內容不要修改
#############################################################
doShortURL   True

import re
import sys
import time
import requests
from lxml import etree
from queue import Queue
from selenium import webdriver
from bs4 import BeautifulSoup, Tag
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from urllib3.exceptions import InsecureRequestWarning
from selenium.common.exceptions import NoSuchElementException
#############################################################
"""
1. 在1/19或11/9可能會發生內文有加上時間標記，因此每篇新聞都會被抓出來，需要人工review

Long-term feature:
1. 舉例來說，「殺人罪」會因為「殺人」的關鍵字被抓到，但有罪行的新聞應該都不是事件發生當天的新聞，應該要想辦法避開。
2. 天氣預報的新聞高機率會出現竹市，看有沒有general rule可以排除？ (暴力的用reg去除 11YMMDD 的數字串？)

pip install beautifulsoup4
pip install selenium
pip install webdriver_manager
pip install pip-system-certs      # 後來中央社不做SSL認證，cert相關應該可裝可不裝
pip install python-certifi-win32
pip install lxml

"""

newsInfoQueue   Queue()
issues   issues + issueFire + issueAccident + issueBehavior + issueGoods + issueSuicide + issueStatus

driverPath   ""
userAgent   ""
if sys.platform    "darwin":
    # macos
    userAgent   "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    driverPath   r"/usr/local/bin/chromedriver"
if sys.platform    "win32":
    # windows
    userAgent   "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    driverPath   r"C:\\Users\\Administrator\\Desktop\\news\\chromedriver.exe"

headers   {'User-Agent' : userAgent}
opt   webdriver.ChromeOptions()
opt.add_argument(f"--user-agent {userAgent}")
opt.add_argument("--disable-notifications")
opt.add_experimental_option('excludeSwitches', ['enable-logging'])

service_   Service(executable_path driverPath)
driver   webdriver.Chrome(service service_, options opt)

requests.packages.urllib3.disable_warnings(category InsecureRequestWarning)

programStartTime   datetime.now()
resultFilename   programStartTime.strftime("%Y%m%d_%H%M%S") + ".txt"
logFilename   "log_" + resultFilename

class Logger(object):
    def __init__(self):
        self.terminal   sys.stdout
   
    def write(self, message):
        self.terminal.write(message)
        self.log   open(logFilename, "a", encoding "utf-8")
        self.log.write(message)  
        self.log.close()

    def flush(self):
        # this flush method is needed for python 3 compatibility.
        # this handles the flush command by doing nothing.
        # you might want to specify some extra behavior here.
        pass    

sys.stdout   Logger()
sys.stderr   sys.stdout

#################################################################################
def getKeywordInNews(content):
    flagPlace   False
    flagPerson   False
    flagIssue   False

    keywords   []

    for place in places:
        if place in content:
            flagPlace   True
            keywords.append(place)
    for person in persons:
        if person in content:
            flagPerson   True
            keywords.append(person)
    for issue in issues:
        if issue in content:
            flagIssue   True
            keywords.append(issue)

    if flagPlace or flagIssue or (flagPlace and flagPerson):
        return keywords
    else:
        return []

def isInTimeRange(newsTime, dateFormat, earlier):
    newsTimeObj   datetime.strptime(newsTime, dateFormat)
    if newsTimeObj < earlier:
        return False
    return True

def getSoupFromURL(url, scrollPages, scrollDelay):
    driver.get(url)
    for x in range(0, scrollPages):
        time.sleep(scrollDelay)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(scrollDelay)
    soup   BeautifulSoup(driver.page_source,"html.parser")
    return soup

def printResult(newsTitle, source, newsLink, keywords):
    print(str(newsTitle), source)
    print(newsLink)
    print(keywords)

    if "竹市" in keywords:
        newsTitle   "(本市)" + str(newsTitle) 

    newsInfoQueue.put((newsTitle+ source, newsLink, keywords))

def getLinksFromURL(url, pressName):
    soup   getSoupFromURL(url, scrollPages, scrollDelay)

    if pressName    "LTN":
        return soup.find_all("a", class_ "tit")
    if pressName    "UDN":
        return soup.find_all('div', class_ "story-list__text")
    if pressName    "ETtoday":
        return soup.find_all('div', class_ "part_list_2")[0].findAll("h3")
    if pressName    "Apple":
        return soup.find_all('article', class_ "post-style3 infScroll postCount")
    if pressName    "SET":
        return soup.find_all("div", class_ "col-sm-12 newsItems")
    if pressName    "Mirror":
        return soup.find_all("a", target "_blank")
    if pressName    "TVBS":
        return soup.find_all("li")
    if pressName    "EBC":
        links   soup.find_all("div", class_ "news-list-box")
        return links[0].find_all("div", class_ "style1 white-box")
    if pressName    "CTS":
        links   soup.find_all("div", class_ "newslist-container flexbox one_row_style")
        return links[0].find_all("a")

def getSubsoupFromURL(newsLink):
    subResult   requests.get(newsLink)
    subResult.encoding 'utf-8'              # For CTS zh
    subSoup   BeautifulSoup(subResult.text, features "html.parser")

    for s in subSoup.select("script"):
        s.extract()
    for s in subSoup.select("style"):
        s.extract()
    
    return subSoup

def getCTSNewsTagFromLink(link):
    if "money" in link:
        return "財經"
    if "weather" in link:
        return "氣象"
    if "entertain" in link:
        return "娛樂"
    if "sports" in link:
        return "運動" 
    if "arts" in link:
        return "藝文"
    return None
#################################################################################

# 自由時報 即時新聞總覽
if SwitchLTN:
    print("vvvvvvvvv  開始: 自由時報")
    earlier   datetime.now() - timedelta(hours timeSlot)
    links   getLinksFromURL("https://news.ltn.com.tw/list/breakingnews", "LTN")

    counter   1
    for link in links:
        time.sleep(0.2)
        newsLink   str(link['href'])
        subSoup   getSubsoupFromURL(newsLink)

        newsTimes   subSoup.find_all("span", class_ "time")
        if len(newsTimes)    0:
            newsTimes   subSoup.find_all("time", class_ "time")
        newsTimeString   ""
        for sting_ in newsTimes:
            newsTimeString +  str(sting_.contents)
        times   re.findall(r"\d{4}\/\d{2}\/\d{2} \d{2}:\d{2}", newsTimeString)
        newsTime   str(times[0])

        if not isInTimeRange(newsTime, "%Y/%m/%d %H:%M", earlier):
            break

        print(str(counter) + "  " + newsTime)
        counter +  1

        flagIgnore   False
        for tags in deleteTagsLTN:
            if tags in newsLink:
                flagIgnore   True
                break

        if flagIgnore:
            continue

        newsContent   subSoup.find_all('p')
        newsContent2   []
        for content in newsContent:
            if "不用抽" not in str(content):
                newsContent2.append(content)
            else:
                break
        
        keywords   getKeywordInNews(str(newsContent2))

        if len(keywords) !  0:
            newsTitle   str(link.find("h3", class_ "title").contents[0])
            printResult(newsTitle, "（自由）", newsLink, keywords)
    print("^^^^^^^^^  結束: 自由時報\n")

#################################################################################

# 聯合新聞網 即時新聞
if SwitchUDN:
    print("vvvvvvvvv  開始: 聯合新聞網")
    earlier   datetime.now() - timedelta(hours timeSlot)
    links   getLinksFromURL("https://udn.com/news/breaknews", "UDN")

    counter   1
    for link in links:
        time.sleep(0.2)
        newsTitle   None
        newsTime   None
        newsLink   None
        
        if "猜你喜歡" in str(link):
            print("                                            ")
            print("跳過「猜你喜歡」部分的新聞，離開聯合新聞網。")
            print("                                            ")
            break

        tagAs   link.findAll("a")
        for tag in tagAs:
            if tag.has_attr("title"):
                newsTitle   str(tag["title"])
                newsLink   "https://udn.com" + str(tag["href"])
                newsLink   newsLink.replace("?from udn-ch1_breaknews-1-0-news", "")

        newsTime   link.find("div", class_ "story-list__info")
        if (newsTime is None) or (newsTitle is None) or (newsLink is None):
            print("continue")
            continue
        newsTime   newsTime.find("time", class_ "story-list__time").contents
        if len(newsTime)    1:
            newsTime   str(newsTime[0])
        else:
            newsTime   str(newsTime[1]) # Skip comment in html
        if not isInTimeRange(newsTime, "%Y-%m-%d %H:%M", earlier):
            break

        print(str(counter) + " " + str(newsTime))
        counter +  1

        subSoup   getSubsoupFromURL(newsLink)
        contents   subSoup.find_all('section', class_ "article-content__wrapper")

        newsTag   subSoup.find("nav", class_ "article-content__breadcrumb")
        if newsTag is not None:
            newsTag   newsTag.contents[3].contents[0]
            if newsTag in deleteTagsUDN:
                continue

        newsContent   ""
        for content in contents[0]:     ## bug here, may not appear every time
            if isinstance(content, Tag):
                div   content.find("div", class_   "article-content__paragraph")
                if div is not None:
                    for i in div.select("script"):
                        i.extract()
                    
                    pos   str(div).find("end of articles")
                    newsContent   str(div)[:pos-1]
                    break

        keywords   getKeywordInNews(newsContent)

        if len(keywords) !  0:
            printResult(newsTitle, "（聯合）", newsLink, keywords)
    print("^^^^^^^^^  結束: 聯合新聞網\n")

#################################################################################

# 中央社 即時新聞列表
if SwitchCNA:
    print("vvvvvvvvv  開始: 中央社")

    """
    enterCNARealtimeNews   False
    while not enterCNARealtimeNews:
        enterCNA   False
        while not enterCNA or "cna.com.tw" not in driver.current_url:
            driver.get("https://www.google.com/search?q %E4%B8%AD%E5%A4%AE%E7%A4%BE")

            time.sleep(1)
            try:
                # driver.find_element(By.XPATH, "/html/body/div[4]/div/div[11]/div[1]/div[2]/div[2]/div/div/div[1]/div/div/div/div/div/div/div/div[1]/div/span/a").click()
                driver.find_element(By.XPATH, "//*[contains(text(), '中央社CNA')]").click()
                enterCNA   True
            except NoSuchElementException:
                time.sleep(0.5)
                try:
                    driver.find_element(By.XPATH, "/html/body/div[5]/div/div[11]/div[1]/div[2]/div[2]/div/div/div[1]/div/div/div/div/div/div/div/div[1]/div/span/a").click()
                    enterCNA   True
                except NoSuchElementException:
                    time.sleep(0.5)
                    try:
                        driver.find_element(By.XPATH, "/html/body/div[6]/div/div[11]/div[1]/div[2]/div[2]/div/div/div[1]/div/div/div/div/div/div/div/div[1]/div/span/a").click()
                        enterCNA   True
                    except NoSuchElementException:
                        print("無法進入中央社即時新聞列表，若失敗太多次，請重新執行。")
                        time.sleep(0.5)
        time.sleep(0.5)
        try:
            driver.find_element(By.XPATH, '//*[@id "pnProductNavContents"]/ul/li[1]/a').click()
            enterCNARealtimeNews   True
        except NoSuchElementException:
            print("無法進入中央社即時新聞列表，若失敗太多次，請重新執行。")
    """

    driver.get("https://www.google.com/search?q %E4%B8%AD%E5%A4%AE%E7%A4%BE")
    time.sleep(0.5)
    driver.find_element(By.XPATH, "//*[contains(text(), '中央社CNA')]").click()
    time.sleep(0.5)
    driver.find_element(By.XPATH, '//*[@id "pnProductNavContents"]/ul/li[1]/a').click()
    time.sleep(0.5)
    earlier   datetime.now() - timedelta(hours timeSlot)
    soup   BeautifulSoup(driver.page_source,"html.parser")
    links   soup.find_all('ul', class_ "mainList imgModule")

    xpathCounter   1
    counter   1
    for link in links[0]:
        time.sleep(0.5)
        if link.has_attr("style"):
            continue

        newsTitle   str(link.find("span").contents[0])
        newsTime   link.find("div", class_ "date").contents[0]
        if not isInTimeRange(newsTime, "%Y/%m/%d %H:%M", earlier):
            break
        print(str(counter) + " " + newsTime)
        counter +  1

        xpath   '//*[@id "jsMainList"]/li[' + str(xpathCounter) + ']/a'
        button   driver.find_element(By.XPATH, xpath)
        xpathCounter +  1
        driver.execute_script("arguments[0].click();", button)
        time.sleep(0.5)

        newsLink   "https://www.cna.com.tw" + link.find("a")["href"]
        subSoup   BeautifulSoup(driver.page_source,"html.parser")

        newsTag   subSoup.find("div", class_ "breadcrumb").findAll("a")[1].contents[0]
        if newsTag in deleteTagsCNA:
            driver.execute_script("window.history.go(-1)")
            continue

        for s in subSoup.select("script"):
            s.extract()

        newsContent   str(subSoup.find_all('p'))
        toRemove   re.search(r"\d{7}.*<\/p>, <p>本網站之文字、圖片及影音，非經授權，不得轉載、公開播送或公開傳輸及利用。<\/p>", newsContent).group(0)
        newsContent   newsContent.replace(toRemove, "")

        if len(str(newsContent))    0:
            print("[ERROR] 中央社 新聞內文沒有抓到")

        keywords   getKeywordInNews(str(newsContent))
        if len(keywords) !  0:
            printResult(newsTitle, "（中央社）", newsLink, keywords)
        
        time.sleep(0.5)
        driver.execute_script("window.history.go(-1)")
    print("^^^^^^^^^  結束: 中央社\n")

#################################################################################

# ETtoday 新聞總覽
if SwitchET:
    print("vvvvvvvvv  開始: ETtoday")
    earlier   datetime.now() - timedelta(hours timeSlot)
    links   getLinksFromURL("https://ettoday.net/news/news-list.htm", "ETtoday")

    counter   1
    for link in links:
        time.sleep(0.2)

        newsTime   str(link.find("span", class_ "date").contents[0])
        if not isInTimeRange(newsTime, "%Y/%m/%d %H:%M", earlier):
            break

        newsTitle   link.find("a")
        if len(newsTitle)    2:
            newsTitle   newsTitle.contents[1]
        else:
            newsTitle   newsTitle.contents[0]

        print(str(counter) + " " + newsTime)
        counter +  1

        newsTag   str(link.find("em").contents[0])
        if newsTag in deleteTagsETtoday:
            continue

        newsLink   str(link.find("a")["href"])
        subSoup   getSubsoupFromURL(newsLink)
        newsContent   subSoup.find_all("div", class_ "story")
        pos   str(newsContent).find("其他新聞")
        newsContent   str(newsContent)[:pos-1]

        keywords   getKeywordInNews(str(newsContent))
        if len(keywords) !  0:
            printResult(newsTitle, "(ETtoday)", newsLink, keywords)
    print("^^^^^^^^^  結束: ETtoday\n")

#################################################################################

# 壹蘋新聞網 最新新聞列表
if SwitchApple:
    print("vvvvvvvvv  開始: 壹蘋新聞網")
    earlier   datetime.now() - timedelta(hours timeSlot)
    links   getLinksFromURL("https://tw.nextapple.com/realtime/latest", "Apple")

    counter   1
    for link in links:
        time.sleep(0.2)

        newsTime    link.find("time").contents[0]
        if not isInTimeRange(newsTime, "%Y/%m/%d %H:%M", earlier):
            break

        print(str(counter) + " " + newsTime)
        counter +  1

        newsTag     link.find("div", class_ "category").contents[0]
        if newsTag in deleteTagsApple:
            continue

        newsLink    link.find("h3").contents[1]["href"]
        subSoup   getSubsoupFromURL(newsLink)

        for s in subSoup.select("a"):
            s.extract()

        newsContents   subSoup.find_all("div", class_ "post-content")
        newsContent   subSoup.find_all("blockquote")
        newsContent +  newsContents[0].findAll("p")
        newsContent +  newsContents[0].findAll("figcaption")

        keywords   getKeywordInNews(str(newsContent))

        if len(keywords) !  0:
            newsTitle   link.find("h3").contents[1].contents[0]
            printResult(newsTitle, "(壹蘋新聞網)", newsLink, keywords)
    print("^^^^^^^^^  結束: 壹蘋新聞網\n")

#################################################################################

# 三立新聞 新聞總覽
if SwitchSET:
    print("vvvvvvvvv  開始: 三立新聞")
    earlier   datetime.now() - timedelta(hours timeSlot)
    links   getLinksFromURL("https://setn.com/viewall.aspx", "SET")

    counter   1
    for link in links:
        time.sleep(0.2)
        linkAndTitle   link.find("a", class_ "gt")
        newsLink   str(linkAndTitle["href"])
        if "https" not in str(linkAndTitle["href"]):
            newsLink   "https://setn.com" + str(linkAndTitle["href"])
        
        newsLink   newsLink.replace("&utm_campaign viewallnews", "")
        newsLink   newsLink.replace("?utm_campaign viewallnews", "")
        subSoup   getSubsoupFromURL(newsLink)

        newsTime   subSoup.find("time", class_ "page_date")

        if newsTime is None:
            newsTime   subSoup.find("time")

            """
            BUG:
            https://travel.setn.com/News/1420260
            這個頁面內的時間不是<time>而是<div>，所以兩個找不同的tag都找不到。
            而且只有年月日沒有時間，時間要從外面的列表看。
            Walkaround: just skip
            """
            if newsTime is None:
                continue

            newsTimeStr   str(newsTime.contents[0])
        else:
            newsTimeStr   str(newsTime.contents[0])[:-3]

        if not isInTimeRange(newsTimeStr, "%Y/%m/%d %H:%M", earlier):
            break

        print(str(counter) + "  " + newsTimeStr)
        counter +  1

        newsTag   link.find("div", class_ "newslabel-tab").contents[0].contents[0]
        if newsTag in deleteTagsSET:
            continue

        newsContent   subSoup.find_all("div", id "Content1")
        if newsContent is None or len(newsContent)    0:
            newsContent   subSoup.find_all("article", class_ "printdiv")
        if newsContent is None or len(newsContent)    0:
            newsContent   subSoup.find_all("div", class_ "page-text")

        pos   str(newsContent).find("延伸閱讀")
        if pos !  -1:
            newsContent   str(newsContent)[:pos]

        keywords   getKeywordInNews(newsContent)

        if len(keywords) !  0:
            newsTitle   str(linkAndTitle.contents[0])
            printResult(newsTitle, "（三立）", newsLink, keywords)
    print("^^^^^^^^^  結束: 三立新聞\n")

#################################################################################

# 鏡週刊 焦點新聞列表  
if SwitchMIRROR:
    print("vvvvvvvvv  開始: 鏡週刊")
    earlier   datetime.now() - timedelta(hours timeSlot)
    links   getLinksFromURL("https://mirrormedia.mg/category/news", "Mirror")

    counter   1
    for link in links:
        time.sleep(0.2)
        newsLink   None
        newsTitle   None
        newsTime   None

        divs   link.find_all("div")
        for div in divs:
            if div.has_attr("class"):
                if "article-list-item__ItemTitle-sc" in str(div["class"]):
                    newsTitle   str(div.contents[0])
                    newsLink   "https://mirrormedia.mg" + str(link["href"])
        if newsLink is None:
            continue

        subResult   None
        if sys.platform    "darwin":
            # macos
            subResult   requests.get(newsLink)
        if sys.platform    "win32":
            # windows
            subResult   requests.get(newsLink, verify False)

        subSoup   BeautifulSoup(subResult.text, features "html.parser")
        divs   subSoup.find_all("div")
        for div in divs:
            if div.has_attr("class"):
                if "normal__SectionAndDate-sc" in str(div["class"]):
                    newsTime   str(div.contents[1].contents[0])

        if newsTime is None:
            newsTimes   subSoup.find_all("p")
            for p in newsTimes:
                if p.has_attr("class"):
                    if "date__DateText-sc" in str(p["class"]):
                        newsTime   str(p.contents[2])
                        break

        if not isInTimeRange(newsTime, "%Y.%m.%d %H:%M", earlier):
            break

        print(str(counter) + "  " + newsTime)
        counter +  1

        flagIgnore   False
        for tags in deleteTagsMIRROR:
            if tags in newsLink:
                flagIgnore   True
                break
        
        if flagIgnore:
            continue

        newsContents   subSoup.find_all("span", {"data-text":"true"})
        newsContent   ""
        for content in newsContents:
            newsContent +  str(content.contents[0])

        keywords   getKeywordInNews(newsContent)

        if len(keywords) !  0:
            printResult(newsTitle, "（鏡週刊）", newsLink, keywords)
    print("^^^^^^^^^  結束: 鏡週刊\n")

#################################################################################

# TVBS 即時新聞列表  
if SwitchTVBS:
    print("vvvvvvvvv  開始: TVBS")
    earlier   datetime.now() - timedelta(hours timeSlot)
    links   getLinksFromURL("https://news.tvbs.com.tw/realtime", "TVBS")

    counter   1
    for link in links:
        time.sleep(0.2)
        if link.find("a") is None or link.find("div", class_ "time") is None:
            continue

        newsLink   "https://news.tvbs.com.tw" + str(link.find("a")["href"])
        subSoup   getSubsoupFromURL(newsLink)

        authorAndTime   subSoup.find_all("div", class_ "author")
        authorAndTime   str(authorAndTime[0])
        times   re.findall(r"\d{4}\/\d{2}\/\d{2} \d{2}:\d{2}", authorAndTime)
        newsTime   str(times[0])
        if not isInTimeRange(newsTime, "%Y/%m/%d %H:%M", earlier):
            break
        
        print(str(counter) + "  " + newsTime)
        counter +  1

        newsTag   link.find("div", class_ "type").contents[0]
        if newsTag in deleteTagsTVBS:
            continue

        newsContents   subSoup.find_all("div", class_ "article_content", id "news_detail_div")
        newsContents   str(newsContents)
        try:
            moreNews   re.search("更多新聞.*<\/a>", newsContents)
        except:
            aaaaaa   1

        if moreNews is not None:
            toRemove   str(moreNews.group(0))
            newsContents   newsContents.replace(toRemove, "")

        keywords   getKeywordInNews(newsContents)

        if len(keywords) !  0:
            newsTitle   str(link.find("h2").contents[0])
            printResult(newsTitle, "（TVBS）", newsLink, keywords)
    print("^^^^^^^^^  結束: TVBS\n")

#################################################################################

# NOWNEWS 即時新聞
if SwitchNOWNEWS:
    print("vvvvvvvvv  開始: NOWNEWS")
    earlier   datetime.now() - timedelta(hours timeSlot)

    url   "https://nownews.com/cat/breaking"
    driver.get(url)
    nextPageButton   driver.find_element(By.ID, "moreNews")
    for x in range(0, scrollPages-3):
        time.sleep(scrollDelay)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scrollDelay)
        nextPageButton.click()
    time.sleep(scrollDelay)
    soup   BeautifulSoup(driver.page_source,"html.parser")
    links   soup.find_all("ul", id "ulNewsList")

    counter   1
    for link in links[0]:
        time.sleep(0.2)
        if not isinstance(link, Tag):
            continue
        
        newsTime   str(link.find("p", class_ "time").contents[-1])
        if not isInTimeRange(newsTime, "%Y-%m-%d %H:%M", earlier):
            break

        print(str(counter) + "  " + newsTime)
        counter +  1

        newsLink   str(link.find("a")["href"])
        subSoup   getSubsoupFromURL(newsLink)
        newsBody   subSoup.find_all("article")  
        if newsBody is None or len(newsBody)    0:
            # 類似地震速報可能會被導到「頁面不存在」，直接跳過不處理
            continue

        newsContents   newsBody[0] # tag, should only have 1 result

        contentStr   ""
        for content in newsContents:
            if content.name    "div":
                if content.has_attr("class"):
                    if str(content["class"][0])    "related-item":
                        break

            contentStr +  str(content)

        keywords   getKeywordInNews(contentStr)

        if len(keywords) !  0:
            newsTitle   str(link.find("h3").contents[0])
            printResult(newsTitle, "（NOWNEWS）", newsLink, keywords)
    print("^^^^^^^^^  結束: NOWNEWS\n")

#################################################################################

# CTWANT 最新新聞列表
if SwitchCTWANT:
    print("vvvvvvvvv  開始: CTWANT")
    earlier   datetime.now() - timedelta(hours timeSlot)

    counter   1
    for page in range(1, scrollPages-2):
        url   "https://ctwant.com/category/最新?page " + str(page)
        soup   getSoupFromURL(url, 0, scrollDelay)
        links   soup.find_all("div", class_ "p-realtime__item")

        for link in links:
            time.sleep(0.2)

            newsTime   str(link.find("time")["datetime"])
            if not isInTimeRange(newsTime, "%Y-%m-%d %H:%M", earlier):
                break

            print(str(counter) + " " + newsTime)
            counter +  1
            
            newsLink   "https://ctwant.com" + str(link.find("a")["href"])
            subSoup   getSubsoupFromURL(newsLink)

            newsTag   subSoup.find("div", class_ "e-category__main").contents[0]
            newsTag   newsTag.replace(" ", "").replace("\n", "")
            if newsTag in deleteTagsCTWANT:
                continue

            newsContent   subSoup.find("div", class_ "p-article__content")
            buttons   newsContent.findAll("button")
            for button in buttons:
                button.extract()

            pos   str(newsContent).find("相關文章")
            if pos !  -1:
                newsContent   str(newsContent)[:pos]

            keywords   getKeywordInNews(newsContent)

            if len(keywords) !  0:
                newsTitle   str(link.find("h2").contents[0]).replace("\n", "").replace("  ", "")
                printResult(newsTitle, "（CTWANT）", newsLink, keywords)
    print("^^^^^^^^^  結束: CTWANT\n")

#################################################################################

# 東森新聞 即時新聞列表
# 看起來新聞內文的網頁有擋爬蟲
if SwitchEBC:
    print("vvvvvvvvv  開始: 東森新聞")
    earlier   datetime.now() - timedelta(hours timeSlot)

    counter   1
    for page in range(1, scrollPages-2):
        urlEBC   "https://news.ebc.net.tw/realtime?page " + str(page)
        links   getLinksFromURL(urlEBC, "EBC")

        time.sleep(1)
        for link in links:
            time.sleep(0.2)
            if not isinstance(link, Tag):
                continue

            newsLink   "https://news.ebc.net.tw" + str(link.find("a")["href"])
            subResult   requests.get(newsLink, headers headers)
            subSoup   BeautifulSoup(subResult.text, features "html.parser")

            newsInfo   str(subSoup.find("div", class_ "info"))
            newsTime   re.findall(r"\d{4}\/\d{2}\/\d{2} \d{2}:\d{2}", newsInfo)[0]
            if not isInTimeRange(newsTime, "%Y/%m/%d %H:%M", earlier):
                break

            print(str(counter) + " " + newsTime)
            counter +  1

            newsTag   link.find("div", class_ "news-category").contents[0]
            if newsTag in deleteTagsEBC:
                continue

            newsContent   str(subSoup.find("div", class_ "raw-style"))

            stopWords   ["更多鏡週刊報導", "往下看更多", "今日最熱門", "延伸閱讀"]
            for stopWord in stopWords:
                pos   newsContent.find(stopWord)
                if pos !  -1:
                    newsContent   newsContent[:pos]

            keywords   getKeywordInNews(newsContent)

            if len(keywords) !  0:
                newsTitle   str(link.find("span", class_ "title").contents[0])
                printResult(newsTitle, "（東森）", newsLink, keywords)
    print("^^^^^^^^^  結束: 東森新聞\n")

#################################################################################

# 華視新聞 即時新聞列表
if SwitchCTS:
    print("vvvvvvvvv  開始: 華視新聞")
    earlier   datetime.now() - timedelta(hours timeSlot)
    links   getLinksFromURL("https://news.cts.com.tw/real/index.html", "CTS")

    counter   1
    for link in links:
        time.sleep(0.2)

        newsTime   str(link.find("div", class_ "newstime").contents[0])
        if not isInTimeRange(newsTime, "%Y/%m/%d %H:%M", earlier):
            break

        print(str(counter) + "  " + newsTime)
        counter +  1

        newsTagLink   link.find("div", class_ "tag").find("img")["src"]
        newsTag   getCTSNewsTagFromLink(newsTagLink)

        if newsTag in deleteTagsCTS:
            continue

        newsLink   link["href"]
        subSoup   getSubsoupFromURL(newsLink)
        for div in subSoup.find_all("div", class_ "flexbox cts-tbfs"): 
            div.extract()
        for div in subSoup.find_all("div", class_ "yt_container_placeholder"): 
            div.extract()

        newsContent   subSoup.find_all("div", class_ "artical-content")
        keywords   getKeywordInNews(str(newsContent))

        if len(keywords) !  0:
            newsTitle   link["title"]
            printResult(newsTitle, "（華視）", newsLink, keywords)
    print("^^^^^^^^^  結束: 華視新聞\n")

#################################################################################

if not doShortURL:
    driver.close()
    exit()

# tinyurl縮網址
print("#####################################")
print("    網頁爬蟲部分正常結束，開始縮網址。")
print("#####################################")
newsInfoQueue.put(None) # To indicate termination

tinyurl   "https://tinyurl.com/app"
driver.get(tinyurl)
soup   BeautifulSoup(driver.page_source,"html.parser")

counter   0
getNextNews   True
with open(resultFilename, 'w', encoding 'UTF-8') as f:
    while True:
        driver.get(tinyurl)

        time.sleep(1.5)

        if getNextNews:
            newsInfo   newsInfoQueue.get()
            counter +  1

        if newsInfo    None:
            f.write("                                         \n")
            f.write("開始執行時間：" + str(programStartTime) + "\n")
            f.write("執行結束時間：" + str(datetime.now()) + "\n")
            f.write("抓取 " + str(timeSlot) + " 個小時內的新聞\n")
            f.write("總共有 " + str(counter - 1) + " 則相關新聞\n")
            break
        
        longUrl   str(newsInfo[1])

        # paste long url
        try:
            driver.find_element(By.ID,'long-url').send_keys(longUrl)
        except NoSuchElementException:
            print("[ERROR] 找不到長網址input")
            getNextNews   False
            continue
        time.sleep(1.5)

        # generate short url
        try:
            driver.find_element(By.XPATH, "//button[@data-test-id 'home_shortener_btn_create']").click()
        except NoSuchElementException:
            print("[ERROR] 找不到縮網址按鈕")
            getNextNews   False
            continue
        time.sleep(1.5)

        # copy short url
        try:
            shortURL   driver.find_element(By.ID,"homepage_create_tinyurl_form_created_input").get_attribute("value")
        except NoSuchElementException:
            print("[ERROR] 找不到短網址內容")
            getNextNews   False
            continue 
        time.sleep(1.5)

        getNextNews   True
        print(". " + newsInfo[0])
        print(str(shortURL))
        print(newsInfo[2])
        f.write(". " + newsInfo[0] + "\n")
        f.write(str(shortURL) + "\n")

print("#####################################")
print("   網頁爬蟲與縮網址部分正常結束，請開啟 " + resultFilename + " 檢視新聞")
print("#####################################")

driver.close()