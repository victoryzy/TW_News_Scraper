import re
import time
import requests
from bs4 import BeautifulSoup, Tag
from selenium import webdriver
from datetime import datetime, timedelta

#############################################################
# 0   不爬文 ;  1   爬文
SwitchLTN     0   # 自由時報 OK
SwitchUDN     0   # 聯合新聞網
SwitchCNA     0   # 中央社
SwitchET      0   # ETtoday
SwitchApple   0   # 壹蘋新聞網 OK

timeSlot      1.5   # 收集幾個小時內的新聞

# 有些新聞網頁在滑鼠滾輪往下滾的時候會載入新的新聞，
# 假如下滑這些頁數以後還是沒有爬完 "timeSlot" 個小時內的新聞，
# 可以把下面這個數字加大
scrollPages   3   

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
issueAccident   ["車禍", "地震", "墜橋", "輾斃", "跌落", "墜落", "山難", "瓦斯外洩", "強震"]
issueBehavior   ["急救", "心肺復甦術", "CPR", "電擊", "演練", "宣導", "搜救", "灌救", "安檢"]
issueGoods   ["AED", "住警器", "消防栓"]
issueSuicide   ["燒炭", "上吊", "割腕", "割喉", "自戕", "跳樓", "自殺", "珍惜生命"]
issueStatus   ["死亡", "喪命", "喪生", "離世", "失蹤", "傷者",
               "死者", "殉職", "失聯", "嗆暈", "意識模糊", "遺體", 
               "亡", "命危", "OHCA", "無生命跡象", "中毒", "不治",
               "任務結束", "無呼吸心跳", "受困", "罹難", "受傷", 
               "昏迷", "無意識"]
#############################################################

issues   issues + issueAccident + issueBehavior + issueGoods + issueSuicide + issueStatus

opt   webdriver.ChromeOptions()

# [TODO] 要判斷作業系統加不同的argument
opt.add_argument("user-agent\":\"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36")

driver   webdriver.Chrome(options opt)

#################################################################################

# 自由時報 即時新聞總覽
if SwitchLTN:
    url   "https://news.ltn.com.tw/list/breakingnews"
    now   datetime.now()
    earlier   now - timedelta(hours timeSlot)

    driver.get(url)
    for x in range(0, scrollPages):
        time.sleep(5)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(5)
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

        flagPlace   False
        flagPerson   False
        flagIssue   False
        keywords   []

        newsContent2   []
        for content in newsContent:
            if "不用抽" not in str(content):
                newsContent2.append(content)
            else:
                break
        
        newsContent2   str(newsContent2)

        for place in places:
            if place in newsContent2:
                flagPlace   True
                keywords.append(place)
        for person in persons:
            if person in newsContent2:
                flagPerson   True
                keywords.append(person)
        for issue in issues:
            if issue in newsContent2:
                flagIssue   True
                keywords.append(issue)

        if flagPlace or flagIssue or (flagPlace and flagPerson):
            print(link['title'], "（自由）")
            print(link['href'])
            print(keywords)

#################################################################################

# 聯合新聞網 即時新聞
if SwitchUDN:
    url   "https://udn.com/news/breaknews"
    now   datetime.now()
    earlier   now - timedelta(hours timeSlot)

    driver.get(url)
    for x in range(0, scrollPages):
        time.sleep(5)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(5)
    soup   BeautifulSoup(driver.page_source,"html.parser")
    links   soup.find_all('div', class_ "story-list__news")

    counter   1
    for link in links:
        if "猜你喜歡" in str(link):
            print("跳過「猜你喜歡」部分的新聞，離開聯合新聞網。")
            break

        time_   re.findall("<time class \"story-list__time\"[\w\W]*>[\w\W]*\d+-\d+-\d+ \d+:\d+[\w\W]*<\/time>", str(link))

        if len(time_)    0:
            print("ERROR!!!!!")
            print("           ")
            print(link)
            exit()

        time_   re.findall("\d+-\d+-\d+ \d+:\d+", str(time_[0]))
        newsTime   str(time_[0])

        title_   re.findall("<h2>\n<a data-content_level[\w\W]*<\/a>\n<\/h2>", str(link))
        href_   re.findall("href \"[\w\W]*\" title", str(title_[0]))
        href_   href_[0][6:]
        newsLink   "https://udn.com" + href_[:-7]

        title_   re.findall("title \"[\w\W]*\"", str(title_[0]))
        title_   title_[0][7:]
        newsTitle   title_[:-1]
        
        subResult   requests.get(newsLink)
        subSoup   BeautifulSoup(subResult.text, features "html.parser")
        contents   subSoup.find_all('section', class_ "article-content__wrapper")

        print(str(counter) + " " + str(newsTime))
        counter +  1

        newsContent   ""
        for content in contents[0]:
            if isinstance(content, Tag):
                div   content.find("div", class_   "article-content__paragraph")
                if div is not None:
                    for i in div.select("script"):
                        i.extract()
                    
                    pos   str(div).find("end of articles")
                    newsContent   str(div)[:pos-1]
                    break

        flagPlace   False
        flagPerson   False
        flagIssue   False
        keywords   []

        for place in places:
            if place in newsContent:
                flagPlace   True
                keywords.append(place)
        for person in persons:
            if person in newsContent:
                flagPerson   True
                keywords.append(person)
        for issue in issues:
            if issue in newsContent:
                flagIssue   True
                keywords.append(issue)

        if flagPlace or flagIssue or (flagPlace and flagPerson):
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
    time.sleep(1)

    counter   1
    for link in links[0]:
        newsTitle   None
        newsTime   None

        if "https" not in link.contents[0]['href']:
            newsLink   "https://cna.com.tw" + link.contents[0]['href']
        else:
            newsLink   link.contents[0]['href']

        if len(link.contents[0].contents)    1:
            newsTitle   link.contents[0].contents[0].contents[0].contents[0].contents[0]
            newsTime   link.contents[0].contents[0].contents[1].contents[0]
        else:
            newsTitle   link.contents[0].contents[1].contents[0].contents[0].contents[0]
            newsTime   link.contents[0].contents[1].contents[1].contents[0]

        date_format   '%Y/%m/%d %H:%M'
        newsTimeObj   datetime.strptime(newsTime, date_format)
        if newsTimeObj < earlier:
            break

        print(str(counter) + " " + newsTime)
        counter +  1

        subResult   requests.get(newsLink)
        subSoup   BeautifulSoup(subResult.text, features "html.parser")
        contents   subSoup.find_all('p')
        newsContent   str(contents)

        flagPlace   False
        flagPerson   False
        flagIssue   False
        keywords   []

        for place in places:
            if place in newsContent:
                flagPlace   True
                keywords.append(place)
        for person in persons:
            if person in newsContent:
                flagPerson   True
                keywords.append(person)
        for issue in issues:
            if issue in newsContent:
                flagIssue   True
                keywords.append(issue)

        if flagPlace or flagIssue or (flagPlace and flagPerson):
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
    links   soup.find_all('div', class_ "part_list_2")
    time.sleep(1)

    counter   1
    for link in links[0].contents:
        newsTitle   None
        newsTime   None

        if link    '\n':
            continue
        
        newsTime   str(link.contents[0].contents[0])
        newsTitle   str(link.contents[2].contents[0])
        newsLink   str(link.contents[2]['href'])

        date_format   '%Y/%m/%d %H:%M'
        newsTimeObj   datetime.strptime(newsTime, date_format)
        if newsTimeObj < earlier:
            break

        # print(str(counter) + " " + newsTime)
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

        if counter > 100:
            break


#################################################################################

# 壹蘋新聞網 最新新聞列表
if SwitchApple:
    url   "https://tw.nextapple.com/realtime/latest"
    now   datetime.now()
    earlier   now - timedelta(hours timeSlot)

    driver.get(url)
    for x in range(0, scrollPages):
        time.sleep(5)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    soup   BeautifulSoup(driver.page_source,"html.parser")
    links   soup.find_all('article', class_ "post-style3 infScroll postCount")
    time.sleep(1)

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

        date_format   '%Y/%m/%d %H:%M'
        newsTimeObj   datetime.strptime(newsTime, date_format)
        if newsTimeObj < earlier:
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

        flagPlace   False
        flagPerson   False
        flagIssue   False
        keywords   []

        for place in places:
            if place in str(newsContent):
                flagPlace   True
                keywords.append(place)
                break
        for person in persons:
            if person in str(newsContent):
                flagPerson   True
                keywords.append(person)
                break
        for issue in issues:
            if issue in str(newsContent):
                flagIssue   True
                keywords.append(issue)       
                break

        if flagPlace or flagIssue or (flagPlace and flagPerson):
            print(newsTitle, "(壹蘋新聞網)")
            print(newsLink)
            print(keywords)

        if counter > 50:
            break
