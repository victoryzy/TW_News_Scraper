import re
import time
import requests
from bs4 import BeautifulSoup, Tag
from selenium import webdriver
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By

#############################################################
"""
1. 有些網站新聞的時間沒有日期資訊，假如跨日的話可能會算錯時間，再想想要修改還是當作限制。
2. (Done)判斷是否要抓的條件可以寫成function，input是字串，output是bool 
3. 在1/19或11/9可能會發生內文有加上時間標記，因此每篇新聞都會被抓出來，需要人工review
4. 三立的時間只有日期和時間，沒有年份資訊。
"""
#############################################################
# 0   不爬文 ;  1   爬文
SwitchLTN       0   # 自由時報 (沒有日期資訊)
SwitchUDN       0   # 聯合新聞網
SwitchCNA       0   # 中央社
SwitchET        0   # ETtoday
SwitchApple     0   # 壹蘋新聞網
SwitchSET       0   # 三立新聞網 
SwitchMIRROR    0   # 鏡週刊
SwitchTVBS      0   # TVBS 
SwitchNOWNEWS   0   # NOWNEWS

SwitchEBC       0   # 東森新聞   https://news.ebc.net.tw/realtime     可爬，需換頁加載，不確定會不會被擋
SwitchCTWANT    0   # CTWANT    https://ctwant.com/category/最新     可爬，需換頁加載，不確定會不會被擋


# 有些新聞網頁在滑鼠滾輪往下滾的時候會載入新的新聞，
# 假如下滑這些頁數以後還是沒有爬完 "timeSlot" 個小時內的新聞，
# 可以把下面這個數字加大，但爬文所需時間會慢一些
scrollPages   3   
timeSlot      2   # 收集幾個小時內的新聞

scrollDelay   1   # 模擬滑鼠滾輪往下滾的間隔時間

places   ["竹市", "消防局", "消防署", "訓練中心", "竹塹"]
persons   ["立委", "市長", "議員", "高虹安", "高市長", 
           "署長", "科長", "局長", "消防員", "替代役",
           "義消", "義警消", "分隊長", "小隊長", "大隊長", 
           "救護技術員", "EMT", "消促會", "工作權益促進會"]
issues   ["災情",  "救災", "救護", "屍", "倒塌", "消防", 
          "到院前", "特搜", "防災", "傷亡", "化學", 
         "救援", "撫卹", "119", "一氧化碳"]

issueFire   ["火災", "失火", "防火", "起火", "大火", "火光", "火燒車",
             "水線", "滅火器", "火海", "打火", "白煙", "黑煙", "灌救",
             "火調", "燒毀", "烈焰", "爆炸", "釀災", "冒煙", "濃煙",
             "延燒", "火警", "燒起來", "雲梯車", "火燒"]
issueAccident   ["車禍", "地震", "墜橋", "輾斃", "跌落", "墜落", "山難", "瓦斯外洩", "強震", "土石流"]
issueBehavior   ["急救", "心肺復甦術", "CPR", "電擊", "演練", "宣導", "搜救", "灌救", "安檢"]
issueGoods   ["AED", "住警器", "消防栓"]
issueSuicide   ["燒炭", "上吊", "割腕", "割喉", "自戕", "跳樓", "自殺", "珍惜生命"]
issueStatus   ["死亡", "喪命", "喪生", "離世", "失蹤", "傷者",
               "死者", "殉職", "失聯", "嗆暈", "意識模糊", "遺體", 
               "亡", "命危", "OHCA", "無生命跡象", "中毒", "不治",
               "任務結束", "無呼吸心跳", "受困", "罹難", "受傷", 
               "昏迷", "無意識"]
#############################################################

issues   issues + issueFire + issueAccident + issueBehavior + issueGoods + issueSuicide + issueStatus

opt   webdriver.ChromeOptions()

# [TODO] 要判斷作業系統加不同的argument
opt.add_argument("user-agent\":\"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36")
opt.add_argument("--disable-notifications")
driver   webdriver.Chrome(options opt)

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

# 自由時報 即時新聞總覽
if SwitchLTN:
    url   "https://news.ltn.com.tw/list/breakingnews"
    now   datetime.now()
    earlier   now - timedelta(hours timeSlot)

    driver.get(url)
    for x in range(0, scrollPages):
        time.sleep(scrollDelay)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(scrollDelay)
    soup   BeautifulSoup(driver.page_source,"html.parser")
    links   soup.find_all('a', class_ "tit")

    counter   1
    for link in links:
        newsTime   str(link.find("span", class_ "time").contents[0])
        newsTitle   str(link.find("h3", class_ "title").contents[0])
        newsLink   str(link['href'])

        print(str(counter) + "  " + newsTime)
        counter +  1
        
        subResult   requests.get(newsLink)
        subSoup   BeautifulSoup(subResult.text, features "html.parser")

        newsContent   subSoup.find_all('p')

        newsContent2   []
        for content in newsContent:
            if "不用抽" not in str(content):
                newsContent2.append(content)
            else:
                break
        
        newsContent2   str(newsContent2)
        keywords   isRelatedNews(newsContent2)

        if len(keywords) !  0:
            print(newsTitle, "（自由）")
            print(newsLink)
            print(keywords)

#################################################################################

# 聯合新聞網 即時新聞
if SwitchUDN:
    url   "https://udn.com/news/breaknews"
    now   datetime.now()
    earlier   now - timedelta(hours timeSlot)

    driver.get(url)
    for x in range(0, scrollPages):
        time.sleep(scrollDelay)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(scrollDelay)
    soup   BeautifulSoup(driver.page_source,"html.parser")
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
        newsTime   newsTime.find("time", class_ "story-list__time").contents
        if len(newsTime)    1:
            newsTime   str(newsTime[0])
        else:
            newsTime   str(newsTime[1]) # Skip comment in html

        subResult   requests.get(newsLink)
        subSoup   BeautifulSoup(subResult.text, features "html.parser")
        contents   subSoup.find_all('section', class_ "article-content__wrapper")

        if not isInTimeRange(newsTime, "%Y-%m-%d %H:%M", earlier):
            break

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
            print(newsTitle, "（聯合）")
            print(newsLink)
            print(keywords)

#################################################################################

# 中央社 即時新聞列表
if SwitchCNA:
    url   "https://cna.com.tw/list/aall.aspx"
    now   datetime.now()
    earlier   now - timedelta(hours timeSlot)

    driver.get(url)
    soup   BeautifulSoup(driver.page_source,"html.parser")
    links   soup.find_all('ul', class_ "mainList imgModule")
    time.sleep(scrollDelay)

    counter   1
    for link in links[0]:
        newsTime   link.find("div", class_ "date").contents[0]
        newsLink   "https://cna.com.tw" + link.find("a")["href"]
        newsTitle   str(link.find("span").contents[0])

        if not isInTimeRange(newsTime, "%Y/%m/%d %H:%M", earlier):
            break

        print(str(counter) + " " + newsTime)
        counter +  1

        subResult   requests.get(newsLink)
        subSoup   BeautifulSoup(subResult.text, features "html.parser")
        contents   subSoup.find_all('p')
        newsContent   str(contents)

        keywords   isRelatedNews(newsContent)

        if len(keywords) !  0:
            print(newsTitle, "（中央社）")
            print(newsLink)
            print(keywords)

#################################################################################

# ETtoday 新聞總覽
if SwitchET:
    url   "https://ettoday.net/news/news-list.htm"
    now   datetime.now()
    earlier   now - timedelta(hours timeSlot)

    driver.get(url)
    soup   BeautifulSoup(driver.page_source,"html.parser")
    links   soup.find_all('div', class_ "part_list_2")[0].findAll("h3")
    time.sleep(scrollDelay)

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
            print(newsTitle, "(ETtoday)")
            print(newsLink)
            print(keywords)

        if counter > 70:
            break

#################################################################################

# 壹蘋新聞網 最新新聞列表
if SwitchApple:
    url   "https://tw.nextapple.com/realtime/latest"
    now   datetime.now()
    earlier   now - timedelta(hours timeSlot)

    driver.get(url)
    for x in range(0, scrollPages):
        time.sleep(scrollDelay)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    soup   BeautifulSoup(driver.page_source,"html.parser")
    links   soup.find_all('article', class_ "post-style3 infScroll postCount")
    time.sleep(scrollDelay)

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

        print(str(counter) + " " + newsTime)
        counter +  1

        subResult   requests.get(newsLink)
        subSoup   BeautifulSoup(subResult.text, features "html.parser")
        newsContents   subSoup.find_all("div", class_ "post-content")
        newsContent   subSoup.find_all("blockquote")
        newsContent +  newsContents[0].findAll("p")
        newsContent +  newsContents[0].findAll("figcaption")
        newsContent   str(newsContent)

        keywords   isRelatedNews(str(newsContent))

        if len(keywords) !  0:
            print(newsTitle, "(壹蘋新聞網)")
            print(newsLink)
            print(keywords)

        if counter > 50:
            break

#################################################################################

# 三立新聞 新聞總覽
if SwitchSET:
    url   "https://setn.com/viewall.aspx"
    now   datetime.now()
    earlier   now - timedelta(hours timeSlot)

    driver.get(url)
    for x in range(0, scrollPages):
        time.sleep(scrollDelay)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(scrollDelay)
    soup   BeautifulSoup(driver.page_source,"html.parser")

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
        newsTime   subSoup.find("time", class_ "page_date")

        if newsTime is None:
            newsTime   subSoup.find("time")
            newsTimeStr   str(newsTime.contents[0])
        else:
            newsTimeStr   str(newsTime.contents[0])[:-3]

        if not isInTimeRange(newsTimeStr, "%Y/%m/%d %H:%M", earlier):
            break

        print(str(counter) + "  " + newsTimeStr)
        counter +  1

        newsContent   subSoup.find_all('p')
        newsContent   str(newsContent)

        keywords   isRelatedNews(newsContent)

        if len(keywords) !  0:
            print(newsTitle, "（三立）")
            print(newsLink)
            print(keywords)

        if counter > 50:
            break

#################################################################################

# 鏡新聞 焦點新聞列表  
if SwitchMIRROR:
    url   "https://mirrormedia.mg/category/news"
    now   datetime.now()
    earlier   now - timedelta(hours timeSlot)

    driver.get(url)
    for x in range(0, scrollPages):
        time.sleep(scrollDelay)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(scrollDelay)
    soup   BeautifulSoup(driver.page_source,"html.parser")

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

        subResult   requests.get(newsLink)
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

        newsContents   subSoup.find_all("span", {"data-text":"true"})
        newsContent   ""
        for content in newsContents:
            newsContent +  str(content.contents[0])

        keywords   isRelatedNews(newsContent)

        if len(keywords) !  0:
            print(newsTitle, "（鏡新聞）")
            print(newsLink)
            print(keywords)

#################################################################################

# TVBS 即時新聞列表  
if SwitchTVBS:
    url   "https://news.tvbs.com.tw/realtime"
    now   datetime.now()
    earlier   now - timedelta(hours timeSlot)

    driver.get(url)
    for x in range(0, scrollPages):
        time.sleep(scrollDelay)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(scrollDelay)
    soup   BeautifulSoup(driver.page_source,"html.parser")

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
        times   re.findall("\d{4}\/\d{2}\/\d{2} \d{2}:\d{2}", authorAndTime)
        newsTime   str(times[0])

        if not isInTimeRange(newsTime, "%Y/%m/%d %H:%M", earlier):
            break

        print(str(counter) + "  " + newsTime)
        counter +  1

        newsContents   subSoup.find_all("div", class_ "article_content", id "news_detail_div")
        newsContents   str(newsContents)
        keywords   isRelatedNews(newsContents)

        if len(keywords) !  0:
            print(newsTitle, "（TVBS）")
            print(newsLink)
            print(keywords)

#################################################################################

# NOWNEWS 即時新聞
if SwitchNOWNEWS:
    url   "https://nownews.com/cat/breaking"
    now   datetime.now()
    earlier   now - timedelta(hours timeSlot)

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

        if not isInTimeRange(newsTime, "%Y-%m-%d %H:%M", earlier):
            break

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
            print(newsTitle, "（NOWNEWS）")
            print(newsLink)
            print(keywords)
