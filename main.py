# 0   不爬文 ;  1   爬文
SwitchLTN       1   # 自由時報 
SwitchUDN       1   # 聯合新聞網
SwitchCNA       1   # 中央社
SwitchET        1   # ETtoday    (列表有tag，可以考慮刪掉某些分類像是「旅遊、房產雲、影劇、時尚、財經、寵物動物、ET車雲」）
SwitchApple     1   # 壹蘋新聞網 (列表有tag，可以考慮刪掉某些分類像是「體育、娛樂時尚、財經地產、購物」）
SwitchSET       1   # 三立新聞網 (列表有tag，可以考慮刪掉某些分類像是「娛樂、財經、運動、兩岸、音樂、新奇」)
SwitchMIRROR    1   # 鏡週刊 
SwitchTVBS      1   # TVBS       (列表有tag，可以考慮刪掉某些分類像是「娛樂、食尚、體育」）
SwitchNOWNEWS   1   # NOWNEWS
SwitchCTWANT    1   # CTWANT    （新聞內頁有tag)

SwitchEBC       0   # 東森新聞   https://news.ebc.net.tw/realtime     可爬，需換頁加載，不確定會不會被擋

# 有些新聞網頁在滑鼠滾輪往下滾的時候會載入新的新聞，
# 假如下滑這些頁數以後還是沒有爬完 "timeSlot" 個小時內的新聞，
# 可以把下面這個數字加大，但爬文所需時間會慢一些
scrollPages   1   
timeSlot      1.0   # 收集幾個小時內的新聞

scrollDelay   2.0   # 模擬滑鼠滾輪往下滾的間隔時間

places   ["竹市", "消防局", "消防署", "竹塹"]
persons   ["高虹安", "高市長", "消防員", "消防替代役", "消防役", "EMT",
           "義消", "義警消", "搜救人員", "救護技術員",  "消促會", "工作權益促進會"]
issues   ["災情",  "救災", "倒塌", "消防", "到院前", "防災", "一氧化碳中毒"]

issueFire   ["火災", "失火", "起火", "大火", "火光", "火燒車",
             "水線", "滅火器", "火海", "打火", "灌救",
             "火調", "燒毀", "火警", "燒起來", "雲梯車"]
issueAccident   ["車禍", "地震", "墜橋", "輾斃", "墜落", "山難", "瓦斯外洩", "強震", "土石流"]
issueBehavior   ["急救", "心肺復甦術", "CPR", "電擊", "灌救"]
issueGoods   ["AED", "住警器", "消防栓"]
issueSuicide   ["燒炭", "上吊", "割腕", "割喉", "自戕", "跳樓", "自殺"]
issueStatus   ["死亡", "喪命", "喪生", "失蹤", "傷者", "遺體", 
               "死者", "殉職", "失聯", "嗆暈", "意識模糊", 
               "命危", "OHCA", "無生命跡象", "不治", "昏迷",
               "無呼吸心跳", "受困", "罹難", "無意識"]

#############################################################
#   以下內容不要修改
#############################################################

import re
import os
import sys
import time
import requests
import pyperclip as pc
from queue import Queue
from selenium import webdriver
from bs4 import BeautifulSoup, Tag
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from urllib3.exceptions import InsecureRequestWarning

#############################################################
"""
1. 在1/19或11/9可能會發生內文有加上時間標記，因此每篇新聞都會被抓出來，需要人工review

Long-term feature:
1. 舉例來說，「殺人罪」會因為「殺人」的關鍵字被抓到，但有罪行的新聞應該都不是事件發生當天的新聞，應該要想辦法避開。
2. 某些媒體會針對新聞分類，例如：社會、娛樂、政治，可以考慮排除某些分類標籤的新聞。

"""

# 是否要印出新聞的編號與時間？ 要 True 不要 False
printCounterTime   True 


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

#################################################################################
def isRelatedNews(content):
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
    newsInfoQueue.put((str(newsTitle) + source, newsLink))

#################################################################################

# 自由時報 即時新聞總覽
if SwitchLTN:
    print("         自由時報  開始              ")
    earlier   datetime.now() - timedelta(hours timeSlot)

    url   "https://news.ltn.com.tw/list/breakingnews"
    soup   getSoupFromURL(url, scrollPages, scrollDelay)
    links   soup.find_all('a', class_ "tit")

    counter   1
    for link in links:
        newsTitle   str(link.find("h3", class_ "title").contents[0])
        newsLink   str(link['href'])

        subResult   requests.get(newsLink)
        subSoup   BeautifulSoup(subResult.text, features "html.parser")

        newsContent   subSoup.find_all('p')

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

        if printCounterTime:
            print(str(counter) + "  " + newsTime)
            counter +  1

        newsContent2   []
        for content in newsContent:
            if "不用抽" not in str(content):
                newsContent2.append(content)
            else:
                break
        
        keywords   isRelatedNews(str(newsContent2))

        if len(keywords) !  0:
            printResult(newsTitle, "（自由）", newsLink, keywords)
    print("         自由時報  結束              ")

#################################################################################

# 聯合新聞網 即時新聞
if SwitchUDN:
    print("         聯合新聞網  開始              ")
    earlier   datetime.now() - timedelta(hours timeSlot)

    url   "https://udn.com/news/breaknews"
    soup   getSoupFromURL(url, scrollPages, scrollDelay)
    links   soup.find_all('div', class_ "story-list__text")

    counter   1
    for link in links:
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

        subResult   requests.get(newsLink)
        subSoup   BeautifulSoup(subResult.text, features "html.parser")
        for s in subSoup.select("style"):
            s.extract()
        for s in subSoup.select("script"):
            s.extract()

        contents   subSoup.find_all('section', class_ "article-content__wrapper")

        if not isInTimeRange(newsTime, "%Y-%m-%d %H:%M", earlier):
            break

        if printCounterTime:
            print(str(counter) + " " + str(newsTime))
            counter +  1
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

        keywords   isRelatedNews(newsContent)

        if len(keywords) !  0:
            printResult(newsTitle, "（聯合）", newsLink, keywords)
    print("         聯合新聞網  結束              ")

#################################################################################

# 中央社 即時新聞列表
if SwitchCNA:
    print("         中央社  開始              ")
    earlier   datetime.now() - timedelta(hours timeSlot)

    url   "https://cna.com.tw/list/aall.aspx"
    soup   getSoupFromURL(url, 0, 4)
    links   soup.find_all('ul', class_ "mainList imgModule")

    counter   1
    for link in links[0]:
        newsTime   link.find("div", class_ "date").contents[0]
        newsLink   "https://cna.com.tw" + link.find("a")["href"]
        newsTitle   str(link.find("span").contents[0])

        if not isInTimeRange(newsTime, "%Y/%m/%d %H:%M", earlier):
            break

        if printCounterTime:
            print(str(counter) + " " + newsTime)
            counter +  1

        time.sleep(3)
        subResult   requests.get(newsLink, headers headers)
        subSoup   BeautifulSoup(subResult.text, features "html.parser")

        for s in subSoup.select("script"):
            s.extract()


        newsContent   subSoup.find_all('p')
        newsContent   str(newsContent)

        toRemove   re.search(r"\d{7}.*<\/p>, <p>本網站之文字、圖片及影音，非經授權，不得轉載、公開播送或公開傳輸及利用。<\/p>", newsContent).group(0)
        newsContent   newsContent.replace(toRemove, "")

        keywords   isRelatedNews(str(newsContent))

        if len(keywords) !  0:
            printResult(newsTitle, "（中央社）", newsLink, keywords)
    print("         中央社  結束              ")

#################################################################################

# ETtoday 新聞總覽
if SwitchET:
    print("         ETtoday  開始              ")
    earlier   datetime.now() - timedelta(hours timeSlot)

    url   "https://ettoday.net/news/news-list.htm"
    soup   getSoupFromURL(url, 0, scrollDelay)
    links   soup.find_all('div', class_ "part_list_2")[0].findAll("h3")

    counter   1
    for link in links:
        newsTime   str(link.find("span", class_ "date").contents[0])

        newsTitle   link.find("a")
        if len(newsTitle)    2:
            newsTitle   newsTitle.contents[1]
        else:
            newsTitle   newsTitle.contents[0]

        newsLink   str(link.find("a")["href"])

        if not isInTimeRange(newsTime, "%Y/%m/%d %H:%M", earlier):
            break

        if printCounterTime:
            print(str(counter) + " " + newsTime)
            counter +  1

        subResult   requests.get(newsLink)
        subSoup   BeautifulSoup(subResult.text, features "html.parser")
        newsContent   subSoup.find_all('p')

        flagPlace   False
        flagPerson   False
        flagIssue   False
        keywords   set()
        for paragraph in newsContent:
            if "分享給朋友" in str(paragraph):
                break

            for place in places:
                if place in str(paragraph):
                    flagPlace   True
                    keywords.add(place)
            for person in persons:
                if person in str(paragraph):
                    flagPerson   True
                    keywords.add(person)
            for issue in issues:
                if issue in str(paragraph):
                    flagIssue   True
                    keywords.add(issue)

        if flagPlace or flagIssue or (flagPlace and flagPerson):
            printResult(newsTitle, "(ETtoday)", newsLink, keywords)
    print("         ETtoday  結束              ")

#################################################################################

# 壹蘋新聞網 最新新聞列表
if SwitchApple:
    print("         壹蘋新聞網  開始              ")
    earlier   datetime.now() - timedelta(hours timeSlot)

    url   "https://tw.nextapple.com/realtime/latest"
    soup   getSoupFromURL(url, scrollPages, scrollDelay)
    links   soup.find_all('article', class_ "post-style3 infScroll postCount")

    counter   1
    for link in links:
        newsTitle   None
        newsTime   None
        newsLink   None

        for l in link:
            if isinstance(l, Tag):
                title_   l.find("a", {"class":["post-title"]})
                time_   l.find("time")
                link_   l.find("a", href True)

                if title_ is not None:
                    newsTitle   str(title_.contents[0])
                if time_ is not None:
                    newsTime   str(time_.contents[0])
                if link_ is not None:
                    newsLink   str(link_["href"])

        if not isInTimeRange(newsTime, "%Y/%m/%d %H:%M", earlier):
            break

        if printCounterTime:
            print(str(counter) + " " + newsTime)
            counter +  1

        subResult   requests.get(newsLink)
        subSoup   BeautifulSoup(subResult.text, features "html.parser")

        for s in subSoup.select("script"):
            s.extract()
        for s in subSoup.select("a"):
            s.extract()

        newsContents   subSoup.find_all("div", class_ "post-content")
        newsContent   subSoup.find_all("blockquote")
        newsContent +  newsContents[0].findAll("p")
        newsContent +  newsContents[0].findAll("figcaption")

        keywords   isRelatedNews(str(newsContent))

        if len(keywords) !  0:
            printResult(newsTitle, "(壹蘋新聞網)", newsLink, keywords)
    print("         壹蘋新聞網  結束              ")

#################################################################################

# 三立新聞 新聞總覽
if SwitchSET:
    print("         三立新聞  開始              ")
    earlier   datetime.now() - timedelta(hours timeSlot)

    url   "https://setn.com/viewall.aspx"
    soup   getSoupFromURL(url, scrollPages, scrollDelay)
    links   soup.find_all("div", class_ "col-sm-12 newsItems")

    counter   1
    for link in links:
        linkAndTitle   link.find("a", class_ "gt")
        newsLink   str(linkAndTitle["href"])
        if "https" not in str(linkAndTitle["href"]):
            newsLink   "https://setn.com" + str(linkAndTitle["href"])
        
        newsLink   newsLink.replace("&utm_campaign viewallnews", "")
        newsLink   newsLink.replace("?utm_campaign viewallnews", "")
        newsTitle   str(linkAndTitle.contents[0])
        subResult   requests.get(newsLink)
        subSoup   BeautifulSoup(subResult.text, features "html.parser")

        for s in subSoup.select("script"):
            s.extract()

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

        if printCounterTime:
            print(str(counter) + "  " + newsTimeStr)
            counter +  1

        newsContent   subSoup.find_all("div", class_ "Content1")
        if newsContent is None or len(newsContent)    0:
            newsContent   subSoup.find_all("article", class_ "printdiv")
        if newsContent is None or len(newsContent)    0:
            newsContent   subSoup.find_all("div", class_ "page-text")

        keywords   isRelatedNews(str(newsContent))

        if len(keywords) !  0:
            printResult(newsTitle, "（三立）", newsLink, keywords)
    print("         三立新聞  結束              ")

#################################################################################

# 鏡週刊 焦點新聞列表  
if SwitchMIRROR:
    print("         鏡週刊  開始              ")
    earlier   datetime.now() - timedelta(hours timeSlot)

    url   "https://mirrormedia.mg/category/news"
    soup   getSoupFromURL(url, scrollPages, scrollDelay)
    links   soup.find_all("a", target "_blank")

    counter   1
    for link in links:
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

        if printCounterTime:
            print(str(counter) + "  " + newsTime)
            counter +  1

        newsContents   subSoup.find_all("span", {"data-text":"true"})
        newsContent   ""
        for content in newsContents:
            newsContent +  str(content.contents[0])

        keywords   isRelatedNews(newsContent)

        if len(keywords) !  0:
            printResult(newsTitle, "（鏡週刊）", newsLink, keywords)
    print("         鏡週刊  結束              ")

#################################################################################

# TVBS 即時新聞列表  
if SwitchTVBS:
    print("         TVBS  開始              ")
    earlier   datetime.now() - timedelta(hours timeSlot)

    url   "https://news.tvbs.com.tw/realtime"
    soup   getSoupFromURL(url, scrollPages, scrollDelay)
    links   soup.find_all("li")

    counter   1
    for link in links:
        if link.find("a") is None or link.find("div", class_ "time") is None:
            continue

        newsLink   "https://news.tvbs.com.tw" + str(link.find("a")["href"])
        newsTitle   str(link.find("h2").contents[0])

        subResult   requests.get(newsLink)
        subSoup   BeautifulSoup(subResult.text, features "html.parser")

        authorAndTime   subSoup.find_all("div", class_ "author")
        authorAndTime   str(authorAndTime[0])
        times   re.findall(r"\d{4}\/\d{2}\/\d{2} \d{2}:\d{2}", authorAndTime)
        newsTime   str(times[0])

        if not isInTimeRange(newsTime, "%Y/%m/%d %H:%M", earlier):
            break
        
        if printCounterTime:
            print(str(counter) + "  " + newsTime)
            counter +  1

        for s in subSoup.select("script"):
            s.extract()

        newsContents   subSoup.find_all("div", class_ "article_content", id "news_detail_div")
        keywords   isRelatedNews(str(newsContents))

        if len(keywords) !  0:
            printResult(newsTitle, "（TVBS）", newsLink, keywords)
    print("         TVBS  結束              ")

#################################################################################

# NOWNEWS 即時新聞
if SwitchNOWNEWS:
    print("         NOWNEWS  開始              ")
    earlier   datetime.now() - timedelta(hours timeSlot)

    url   "https://nownews.com/cat/breaking"
    driver.get(url)
    nextPageButton   driver.find_element(By.ID, "moreNews")
    for x in range(0, scrollPages+1):
        time.sleep(scrollDelay)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scrollDelay)
        nextPageButton.click()
    time.sleep(scrollDelay)
    soup   BeautifulSoup(driver.page_source,"html.parser")
    links   soup.find_all("ul", id "ulNewsList")

    counter   1
    for link in links[0]:
        if not isinstance(link, Tag):
            continue
        
        newsTitle   str(link.find("h3").contents[0])
        newsLink   str(link.find("a")["href"])
        newsTime   str(link.find("p", class_ "time").contents[-1])

        subResult   requests.get(newsLink)
        subSoup   BeautifulSoup(subResult.text, features "html.parser")

        for s in subSoup.select("script"):
            s.extract()

        if not isInTimeRange(newsTime, "%Y-%m-%d %H:%M", earlier):
            break

        if printCounterTime:
            print(str(counter) + "  " + newsTime)
            counter +  1

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

        keywords   isRelatedNews(contentStr)

        if len(keywords) !  0:
            printResult(newsTitle, "（NOWNEWS）", newsLink, keywords)
    print("         NOWNEWS  結束              ")

#################################################################################

# CTWANT 最新新聞列表
if SwitchCTWANT:
    print("         CTWANT  開始              ")
    earlier   datetime.now() - timedelta(hours timeSlot)

    counter   1
    for page in range(1, scrollPages+1):
        url   "https://ctwant.com/category/最新?page " + str(page)
        soup   getSoupFromURL(url, 0, scrollDelay)
        links   soup.find_all("div", class_ "p-realtime__item")

        for link in links:
            newsLink   "https://ctwant.com" + str(link.find("a")["href"])
            newsTime   str(link.find("time")["datetime"])

            newsTitle   str(link.find("h2").contents[0])
            newsTitle   newsTitle.replace("\n", "")
            newsTitle   newsTitle.replace("  ", "")

            if not isInTimeRange(newsTime, "%Y-%m-%d %H:%M", earlier):
                break

            if printCounterTime:
                print(str(counter) + " " + newsTime)
                counter +  1

            subResult   requests.get(newsLink)
            subSoup   BeautifulSoup(subResult.text, features "html.parser")
            newsContent   subSoup.find("div", class_ "p-article__content")

            buttons   newsContent.findAll("button")
            for button in buttons:
                button.extract()

            keywords   isRelatedNews(str(newsContent))

            if len(keywords) !  0:
                printResult(newsTitle, "（CTWANT）", newsLink, keywords)
    print("         CTWANT  結束              ")

#################################################################################

# 東森新聞 即時新聞列表
# 看起來新聞內文的網頁有擋爬蟲
if SwitchEBC:
    earlier   datetime.now() - timedelta(hours timeSlot)

    for page in range(1, scrollPages+1):
        url   "https://news.ebc.net.tw/realtime?page " + str(page)
        soup   getSoupFromURL(url, 0, scrollDelay)
        links   soup.find_all("div", class_ "news-list-box")
        links   links[0].find_all("div", class_ "style1 white-box")

        time.sleep(1)

        counter   1
        for link in links:
            if not isinstance(link, Tag):
                continue

            newsTitle   str(link.find("span", class_ "title").contents[0])
            print(newsTitle)
            newsLink   "https://news.ebc.net.tw" + str(link.find("a")["href"])
            print(newsLink)

            subResult   requests.get(newsLink)
            subSoup   BeautifulSoup(subResult.text, features "html.parser")
            print(subSoup)
            newsInfo   subSoup.find_all("div", class_ "info")
            print(newsInfo)
            # newsTime   newsInfo.find("span", class_ "small-gray-text")
            # print(newsTime)

            break

            newsTime   link.find("div", class_ "date").contents[0]
            newsLink   "https://cna.com.tw" + link.find("a")["href"]
            newsTitle   str(link.find("span").contents[0])

            if not isInTimeRange(newsTime, "%Y/%m/%d %H:%M", earlier):
                break

            print(str(counter) + " " + newsTime)
            counter +  1

            newsContent   subSoup.find_all('p')

            keywords   isRelatedNews(str(newsContent))

            if len(keywords) !  0:
                printResult(newsTitle, "（中央社）", newsLink, keywords)


        break

#################################################################################

# tinyurl縮網址

print("#####################################")
print("    網頁爬蟲部分正常結束，開始縮網址。")
print("#####################################")
exit()
# To indicate termination
newsInfoQueue.put(None)

url   "https://tinyurl.com/app"
driver.get(url)
soup   BeautifulSoup(driver.page_source,"html.parser")

programStartTime   datetime.now()

filename   programStartTime.strftime("%Y%m%d_%H%M%S") + ".txt"
counter   1
with open(filename, 'w', encoding 'UTF-8') as f:
    while True:
        newsInfo   newsInfoQueue.get()

        if newsInfo    None:
            f.write("                                         \n")
            f.write("開始執行時間：" + str(programStartTime) + "\n")
            f.write("執行結束時間：" + str(datetime.now()) + "\n")
            f.write("抓取 " + str(timeSlot) + " 個小時內的新聞\n")
            f.write("總共有 " + str(counter) + " 則相關新聞\n")
            break
        
        counter +  1

        f.write(". " + newsInfo[0] + "\n")
        longUrl   str(newsInfo[1])

        # paste long url
        driver.find_element(By.ID,'long-url').send_keys(longUrl)
        time.sleep(1.5)

        # generate short url
        driver.find_element(By.XPATH, "//button[@data-test-id 'home_shortener_btn_create']").click()
        time.sleep(1.5)

        # copy short url
        driver.find_element(By.XPATH, "//button[@id 'form_tinyurl_copy_btn']").click()
        time.sleep(1.5)
        f.write(pc.paste() + "\n")

        # return to original page for another iteration
        driver.find_element(By.XPATH, "//button[@id 'homepage_create_tinyurl_form_shorten_another_btn']").click()

print("#####################################")
print("    縮網址部分正常結束，請開啟 " + filename + " 檢視新聞")
print("#####################################")

driver.close()