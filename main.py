# 0 = 不爬文 ;  1 = 爬文
SWITCH_LTN     = 1   # 自由時報 
SWITCH_UDN     = 1   # 聯合新聞網
SWITCH_CNA     = 1   # 中央社
SWITCH_ET      = 1   # ETtoday
SWITCH_APPLE   = 1   # 壹蘋新聞網
SWITCH_SET     = 1   # 三立新聞網
SWITCH_MIRROR  = 1   # 鏡週刊 
SWITCH_TVBS    = 1   # TVBS
SWITCH_NOWNEWS = 1   # NOWNEWS
SWITCH_CTWANT  = 1   # CTWANT
SWITCH_EBC     = 1   # 東森新聞
SWITCH_CTS     = 1   # 華視新聞

# 有些新聞網頁在滑鼠滾輪往下滾的時候會載入新的新聞，
# 假如下滑這些頁數以後還是沒有爬完 "TIMESLOT" 個小時內的新聞，
# 可以把下面這個數字加大，但爬文所需時間會慢一些
SCROLL_PAGES  = 4    # >= 4 ，自由和聯合新聞數量較多   
TIMESLOT      = 1.0  # 收集幾個小時內的新聞
SCROLL_DELAY  = 4.0  # 模擬滑鼠滾輪往下滾的間隔時間
TINYURL_DELAY = 1.5  # 縮網址時點擊的間隔時間

places  = ["竹市", "消防局", "消防署", "竹塹"]
persons = ["高虹安", "高市長", "特搜", "搜救人員", "消防役", "EMT",
           "義消", "義警消", "救護技術員", "消促會", "工作權益促進會"]
issues  = ["救災", "倒塌", "消防", "到院前", "防災", "位移", "坍方",
        "一氧化碳中毒", "天坑", "電線桿倒塌", "路樹倒塌", "崩塌", "走山", 
        ]

issue_behavior = ["急救", "心肺復甦術", "CPR", "電擊", "灌救"]
issue_goods    = ["AED", "住警器", "消防栓"]
issue_suicide  = ["燒炭", "上吊", "割腕", "割喉", "自戕",
                "跳樓", "自殺", 
                ]
issue_fire     = ["火災", "失火", "起火", "大火", "火光",
                "火燒車", "灌救", "水線", "火海", "打火",
                "火調", "燒毀", "火警", "雲梯車",
                ]
issue_accident = ["車禍", "地震深度", "最大震度", "芮氏規模",
                "有感地震", "墜橋", "輾斃", "墜樓", "山難",
                "瓦斯外洩", "土石流",
                ]
issue_status   = ["喪命", "喪生", "失蹤", "傷者", "遺體",
                "殉職", "失聯", "嗆暈", "命危", "不治",
                "昏迷", "罹難", "受困", "無意識", "OHCA",
                "意識模糊", "無呼吸心跳","無生命跡象",
                ]

delete_tags_LTN     = {"ent":"娛樂", "istyle":"時尚", "sports":"體育",
                    "ec":"財經", "def":"軍武", "3c":"3C", "art.ltn":"藝文",
                    "playing":"玩咖", "food":"食譜", "estate":"地產",
                    "yes123":"求職", "auto":"汽車"}
delete_tags_UDN     = ["娛樂", "股市", "產經", "運動", "科技", "文教", "健康"]
delete_tags_CNA     = ["娛樂", "產經", "證券", "科技", "文化", "運動"]
delete_tags_ETtoday = ["旅遊", "房產雲", "影劇", "時尚", "財經", "寵物動物", "ET車雲"]
delete_tags_Apple   = ["體育", "娛樂時尚", "財經地產", "購物"]
delete_tags_SET     = ["娛樂", "財經", "運動", "兩岸", "音樂", "新奇"]
delete_tags_MIRROR  = {"fin":"財經", "ind":"財經", "bus":"財經",
                    "money":"財經", "ent":"娛樂"}
delete_tags_TVBS    = ["娛樂", "食尚", "體育"]
delete_tags_CTWANT  = ["娛樂", "財經", "漂亮"]
delete_tags_EBC     = ["娛樂", "健康", "體育", "財經"]
delete_tags_CTS     = ["財經", "氣象", "娛樂", "運動", "藝文"]
#############################################################
#   以下內容不要修改
#############################################################
DO_SHORT_URL = False
HEADLESS = True

import re
import sys
import time
import requests
from queue import Queue
from selenium import webdriver
from bs4 import BeautifulSoup, Tag
from datetime import datetime, timedelta
from timeit import default_timer as timer
from urllib3.exceptions import InsecureRequestWarning
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import ElementClickInterceptedException
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

news_info_queue = Queue()
issues = issues + issue_fire + issue_accident + issue_behavior + issue_goods + issue_suicide + issue_status

driver_path = ""
user_agent = ""
if sys.platform == "darwin":
    # macos
    user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    driver_path = r"/usr/local/bin/chromedriver"
if sys.platform == "win32":
    # windows
    user_agent = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    driver_path = r"C:\\Users\\owner\\Desktop\\news\\chromedriver.exe"

headers = {'User-Agent' : user_agent}
opt = webdriver.ChromeOptions()
opt.add_argument(f"--user-agent={user_agent}")
opt.add_argument("--disable-notifications")
opt.add_experimental_option('excludeSwitches', ['enable-logging'])

if HEADLESS:
    opt.add_argument("--headless=new")

my_service = Service(executable_path=driver_path)
driver = webdriver.Chrome(service=my_service, options=opt)

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

program_start_t = datetime.now()
result_filename = program_start_t.strftime("%Y%m%d_%H%M%S") + ".txt"
log_filename = "log_" + result_filename

class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout
   
    def write(self, message):
        self.terminal.write(message)
        self.log = open(log_filename, "a", encoding="utf-8")
        self.log.write(message)  
        self.log.close()

    def flush(self):
        # this flush method is needed for python 3 compatibility.
        # this handles the flush command by doing nothing.
        # you might want to specify some extra behavior here.
        pass    

sys.stdout = Logger()
sys.stderr = sys.stdout

#################################################################################
def get_keyword_in_news(content):
    flag_place = False
    flag_person = False
    flag_issue = False

    keywords = []

    for place in places:
        if place in content:
            flag_place = True
            keywords.append(place)
    for person in persons:
        if person in content:
            flag_person = True
            keywords.append(person)
    for issue in issues:
        if issue in content:
            flag_issue = True
            keywords.append(issue)

    if flag_place or flag_issue or (flag_place and flag_person):
        return keywords
    else:
        return []

def is_in_time_range(news_time, date_format, earlier):
    news_time_object = datetime.strptime(news_time, date_format)
    if news_time_object < earlier:
        return False
    return True

def get_soup_from_url(url, scroll_pages, scroll_delay):
    driver.get(url)
    for x in range(0, scroll_pages):
        if "udn" in url:
            time.sleep(10)
        else:
            time.sleep(scroll_delay)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(scroll_delay)
    soup = BeautifulSoup(driver.page_source,"html.parser")
    return soup

def print_result(news_title, source, news_link, keywords):
    print(str(news_title), source)
    print(news_link)
    print(keywords)

    if "竹市" in keywords:
        news_title = "(本市)" + str(news_title) 

    news_info_queue.put((news_title+ source, news_link, keywords))

def get_links_from_url(url, press_name):
    soup = get_soup_from_url(url, SCROLL_PAGES, SCROLL_DELAY)

    if press_name == "LTN":
        return soup.find_all("a", class_="tit")
    if press_name == "UDN":
        return soup.find_all('div', class_="story-list__text")
    if press_name == "ETtoday":
        return soup.find_all('div', class_="part_list_2")[0].findAll("h3")
    if press_name == "Apple":
        return soup.find_all('article', class_="post-style3 infScroll postCount")
    if press_name == "SET":
        return soup.find_all("div", class_="col-sm-12 newsItems")
    if press_name == "Mirror":
        return soup.find_all("a", target="_blank")
    if press_name == "TVBS":
        return soup.find_all("li")
    if press_name == "EBC":
        return soup.find_all("a", class_="item row_box")
    if press_name == "CTS":
        links = soup.find_all("div", class_="newslist-container flexbox one_row_style")
        return links[0].find_all("a")
    return None

def get_subsoup_from_url(news_link):
    sub_result = requests.get(news_link)
    sub_result.encoding='utf-8'              # For CTS zh
    sub_soup = BeautifulSoup(sub_result.text, features="html.parser")

    for s in sub_soup.select("script"):
        s.extract()
    for s in sub_soup.select("style"):
        s.extract()
    
    return sub_soup

def get_CTS_news_tag(link):
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
if SWITCH_LTN:
    print("vvvvvvvvv  開始: 自由時報")
    flag_exceed_time_range = False
    start_LTN = timer()
    earlier = datetime.now() - timedelta(hours=TIMESLOT)
    links = get_links_from_url("https://news.ltn.com.tw/list/breakingnews", "LTN")

    counter = 1
    for link in links:
        time.sleep(0.5)
        news_link = str(link['href'])
        sub_soup = get_subsoup_from_url(news_link)

        news_times = sub_soup.find_all("span", class_="time")
        if len(news_times) == 0:
            news_times = sub_soup.find_all("time", class_="time")
        news_time_string = ""
        for sting_ in news_times:
            news_time_string += str(sting_.contents)
        times = re.findall(r"\d{4}\/\d{2}\/\d{2} \d{2}:\d{2}", news_time_string)

        time_is_valid = True
        try:
            news_time = str(times[0])
        except IndexError:
            print("[ERROR] 時間的格式不同，不判斷時間是否在範圍內")
            time_is_valid = False
            news_time = news_time_string

        if time_is_valid and not is_in_time_range(news_time, "%Y/%m/%d %H:%M", earlier):
            print("下一則新聞已超過時間範圍，停止查看自由時報")
            flag_exceed_time_range = True
            break

        print(str(counter) + "  " + news_time)
        counter += 1

        flag_ignore = False
        for tags in delete_tags_LTN:
            if tags in news_link:
                flag_ignore = True
                break
        
        news_title = str(link.find("h3", class_="title").contents[0])
        if "健康網" in news_title:
            flag_ignore = True

        if flag_ignore:
            continue

        news_content = sub_soup.find_all('p')
        news_content2 = []
        for content in news_content:
            if "不用抽" not in str(content):
                news_content2.append(content)
            else:
                break
        
        keywords = get_keyword_in_news(str(news_content2))

        if len(keywords) != 0:
            print_result(news_title, "（自由）", news_link, keywords)
    end_LTN = timer()
    print("^^^^^^^^^  結束: 自由時報")
    print("用時 " + str(timedelta(seconds = end_LTN - start_LTN)) + "\n")
    if not flag_exceed_time_range:
        print("[WARNING - 自由時報] 已看完目前列表所抓的新聞，尚未確認時間範圍內的所有新聞，可能要增加捲動次數")

#################################################################################

# 聯合新聞網 即時新聞
if SWITCH_UDN:
    print("vvvvvvvvv  開始: 聯合新聞網")
    flag_exceed_time_range = False
    start_UDN = timer()
    earlier = datetime.now() - timedelta(hours=TIMESLOT)
    links = get_links_from_url("https://udn.com/news/breaknews", "UDN")

    counter = 1
    for link in links:
        time.sleep(0.5)
        news_title = None
        news_time = None
        news_link = None
        
        if "猜你喜歡" in str(link):
            print("============================================")
            print("跳過「猜你喜歡」部分的新聞，離開聯合新聞網。")
            print("============================================")
            break

        tagAs = link.findAll("a")
        for tag in tagAs:
            if tag.has_attr("title"):
                news_title = str(tag["title"])
                news_link = "https://udn.com" + str(tag["href"])
                news_link = news_link.replace("?from=udn-ch1_breaknews-1-0-news", "")

        news_time = link.find("div", class_="story-list__info")
        if (news_time is None) or (news_title is None) or (news_link is None):
            # 這部分為機率性出現，相同的新聞連結可能不會每次都會因此被跳過
            print("continue")
            continue
        news_time = news_time.find("time", class_="story-list__time").contents
        if len(news_time) == 1:
            news_time = str(news_time[0])
        else:
            news_time = str(news_time[1]) # Skip comment in html
        if not is_in_time_range(news_time, "%Y-%m-%d %H:%M", earlier):
            print("下一則新聞已超過時間範圍，停止查看聯合新聞網")
            flag_exceed_time_range = True
            break

        print(str(counter) + " " + str(news_time))
        counter += 1

        sub_soup = get_subsoup_from_url(news_link)
        contents = sub_soup.find_all('section', class_="article-content__wrapper")

        news_tag = sub_soup.find("nav", class_="article-content__breadcrumb")
        if news_tag is not None:
            news_tag = news_tag.contents[3].contents[0]
            if news_tag in delete_tags_UDN:
                continue

        news_content = ""
        for content in contents[0]:     ## bug here, may not appear every time
            if isinstance(content, Tag):
                div = content.find("div", class_ = "article-content__paragraph")
                if div is not None:
                    for i in div.select("script"):
                        i.extract()
                    
                    pos = str(div).find("end of articles")
                    news_content = str(div)[:pos-1]
                    break

        keywords = get_keyword_in_news(news_content)

        if len(keywords) != 0:
            print_result(news_title, "（聯合）", news_link, keywords)
    end_UDN = timer()
    print("^^^^^^^^^  結束: 聯合新聞網")
    print("用時 " + str(timedelta(seconds = end_UDN - start_UDN)) + "\n")
    if not flag_exceed_time_range:
        print("[WARNING - 聯合新聞網] 已看完目前列表所抓的新聞，尚未確認時間範圍內的所有新聞，可能要增加捲動次數")

#################################################################################

# 中央社 即時新聞列表
if SWITCH_CNA:
    print("vvvvvvvvv  開始: 中央社")
    flag_exceed_time_range = False
    start_CNA = timer()
    
    # 中央社需要先由google搜尋的結果點進去，直接get中央社網站會被偵測到
    driver.get("https://www.google.com/search?q=%E4%B8%AD%E5%A4%AE%E7%A4%BE")
    time.sleep(0.5)
    # driver.find_element(By.XPATH, "//*[contains(text(), '中央社CNA')]").click() # 找中央社CNA的字串進入新聞網站
    # driver.find_element(By.XPATH, '//*[@id="pnProductNavContents"]/ul/li[1]/a').click() # 點擊「即時」
    driver.find_element(By.LINK_TEXT, "即時").click() # 直接從搜尋結果點擊「即時」，進到中央社的即時新聞列表

    time.sleep(0.5)
    earlier = datetime.now() - timedelta(hours=TIMESLOT)
    soup = BeautifulSoup(driver.page_source,"html.parser")
    links = soup.find_all('ul', class_="mainList imgModule")

    xpath_counter = 1
    counter = 1
    for link in links[0]:
        time.sleep(0.5)
        if link.has_attr("style"):
            continue

        news_title = str(link.find("span").contents[0])
        news_time = link.find("div", class_="date").contents[0]
        if not is_in_time_range(news_time, "%Y/%m/%d %H:%M", earlier):
            print("下一則新聞已超過時間範圍，停止查看中央社")
            flag_exceed_time_range = True
            break
        print(str(counter) + " " + news_time)
        counter += 1

        xpath = '//*[@id="jsMainList"]/li[' + str(xpath_counter) + ']/a'
        button = driver.find_element(By.XPATH, xpath)
        xpath_counter += 1
        driver.execute_script("arguments[0].click();", button)
        time.sleep(0.5)

        news_link = "https://www.cna.com.tw" + link.find("a")["href"]
        sub_soup = BeautifulSoup(driver.page_source,"html.parser")

        try:
            news_tag = sub_soup.find("div", class_="breadcrumb").findAll("a")[1].contents[0]
        except AttributeError:
            # 中央社會有新聞點進去內容不是一般的新聞，而是集結多個有關於ＯＯＯ的資訊，因此沒有新聞標題和類別
            continue

        if news_tag in delete_tags_CNA:
            driver.execute_script("window.history.go(-1)")
            continue

        for s in sub_soup.select("script"):
            s.extract()

        news_content = str(sub_soup.find_all('p'))

        try:
            toRemove = re.search(r"\d{7}.*<\/p>, <p>本網站之文字、圖片及影音，非經授權，不得轉載、公開播送或公開傳輸及利用。<\/p>", news_content).group(0)
            news_content = news_content.replace(toRemove, "")
        except AttributeError:
            print("[WARNING] 此新聞沒有文末的警語")

        if len(str(news_content)) == 0:
            print("[ERROR] 中央社 新聞內文沒有抓到")

        keywords = get_keyword_in_news(str(news_content))
        if len(keywords) != 0:
            print_result(news_title, "（中央社）", news_link, keywords)
        
        time.sleep(0.5)
        driver.execute_script("window.history.go(-1)")
    end_CNA = timer()
    print("^^^^^^^^^  結束: 中央社")
    print("用時 " + str(timedelta(seconds = end_CNA - start_CNA)) + "\n")
    if not flag_exceed_time_range:
        print("[WARNING - 中央社] 已看完目前列表所抓的新聞，尚未確認時間範圍內的所有新聞，可能要增加捲動次數")

#################################################################################

# ETtoday 新聞總覽
if SWITCH_ET:
    print("vvvvvvvvv  開始: ETtoday")
    flag_exceed_time_range = False
    start_ET = timer()
    earlier = datetime.now() - timedelta(hours=TIMESLOT)
    # links = get_links_from_url("https://ettoday.net/news/news-list.htm", "ETtoday")

    result = requests.get("https://ettoday.net/news/news-list.htm")
    links = BeautifulSoup(result.text, features="html.parser").find_all('div', class_="part_list_2")[0].findAll("h3")

    counter = 1
    for link in links:
        time.sleep(0.5)

        news_time = str(link.find("span", class_="date").contents[0])
        if not is_in_time_range(news_time, "%Y/%m/%d %H:%M", earlier):
            print("下一則新聞已超過時間範圍，停止查看ETtoday")
            flag_exceed_time_range = True
            break

        news_title = link.find("a")
        if len(news_title) == 2:
            news_title = news_title.contents[1]
        else:
            news_title = news_title.contents[0]

        print(str(counter) + " " + news_time)
        counter += 1

        news_tag = str(link.find("em").contents[0])
        if news_tag in delete_tags_ETtoday:
            continue

        news_link = str(link.find("a")["href"])
        sub_soup = get_subsoup_from_url(news_link)
        news_content = sub_soup.find_all("div", class_="story")
        pos = str(news_content).find("其他新聞")
        news_content = str(news_content)[:pos-1]
        pos = str(news_content).find("延伸閱讀")
        news_content = str(news_content)[:pos-1]

        keywords = get_keyword_in_news(str(news_content))
        if len(keywords) != 0:
            print_result(news_title, "(ETtoday)", news_link, keywords)
    end_ET = timer()
    print("^^^^^^^^^  結束: ETtoday")
    print("用時 " + str(timedelta(seconds = end_ET - start_ET)) + "\n")
    if not flag_exceed_time_range:
        print("[WARNING - ETtoday] 已看完目前列表所抓的新聞，尚未確認時間範圍內的所有新聞，可能要增加捲動次數")

#################################################################################

# 壹蘋新聞網 最新新聞列表
if SWITCH_APPLE:
    print("vvvvvvvvv  開始: 壹蘋新聞網")
    flag_exceed_time_range = False
    start_Apple = timer()
    earlier = datetime.now() - timedelta(hours=TIMESLOT)
    links = get_links_from_url("https://tw.nextapple.com/realtime/latest", "Apple")

    # # 一次request html只會有20則新聞
    # result = requests.get(link)
    # links = BeautifulSoup(result.text, features="html.parser").find_all('article', class_="post-style3 infScroll postCount")

    counter = 1
    for link in links:
        time.sleep(0.5)

        news_time  = link.find("time").contents[0]
        if not is_in_time_range(news_time, "%Y/%m/%d %H:%M", earlier):
            print("下一則新聞已超過時間範圍，停止查看壹蘋新聞網")
            flag_exceed_time_range = True
            break

        print(str(counter) + " " + news_time)
        counter += 1

        news_tag = link.find("div", class_="category").contents[0]
        if news_tag in delete_tags_Apple:
            continue

        news_link  = link.find("h3").contents[1]["href"]
        sub_soup = get_subsoup_from_url(news_link)

        for s in sub_soup.select("a"):
            s.extract()
        
        news_contents = sub_soup.find_all("div", class_="post-content")
        news_content = sub_soup.find_all("blockquote")
        news_content += news_contents[0].findAll("p")
        news_content += news_contents[0].findAll("figcaption")

        keywords = get_keyword_in_news(str(news_content))

        if len(keywords) != 0:
            news_title = link.find("h3").contents[1].contents[0]
            print_result(news_title, "(壹蘋新聞網)", news_link, keywords)
    end_Apple = timer()
    print("^^^^^^^^^  結束: 壹蘋新聞網")
    print("用時 " + str(timedelta(seconds = end_Apple - start_Apple)) + "\n")
    if not flag_exceed_time_range:
        print("[WARNING - 壹蘋新聞網] 已看完目前列表所抓的新聞，尚未確認時間範圍內的所有新聞，可能要增加捲動次數")

#################################################################################

# 三立新聞 新聞總覽
if SWITCH_SET:
    print("vvvvvvvvv  開始: 三立新聞")
    flag_exceed_time_range = False
    start_SET = timer()
    earlier = datetime.now() - timedelta(hours=TIMESLOT)
    links = get_links_from_url("https://setn.com/viewall.aspx", "SET")

    # result = requests.get("https://setn.com/viewall.aspx")
    # links = BeautifulSoup(result.text, features="html.parser").find_all("div", class_="col-sm-12 newsItems")

    counter = 1
    for link in links:
        time.sleep(0.5)
        link_and_title = link.find("a", class_="gt")
        news_link = str(link_and_title["href"])
        if "https" not in str(link_and_title["href"]):
            news_link = "https://setn.com" + str(link_and_title["href"])
        
        news_link = news_link.replace("&utm_campaign=viewallnews", "")
        news_link = news_link.replace("?utm_campaign=viewallnews", "")
        sub_soup = get_subsoup_from_url(news_link)

        news_time = sub_soup.find("time", class_="page_date")

        if news_time is None:
            news_time = sub_soup.find("time")

            """
            BUG:
            https://travel.setn.com/News/1420260
            這個頁面內的時間不是<time>而是<div>，所以兩個找不同的tag都找不到。
            而且只有年月日沒有時間，時間要從外面的列表看。
            Walkaround: just skip
            """
            if news_time is None:
                continue

            news_time_str = str(news_time.contents[0])
        else:
            news_time_str = str(news_time.contents[0])[:-3]

        if not is_in_time_range(news_time_str, "%Y/%m/%d %H:%M", earlier):
            print("下一則新聞已超過時間範圍，停止查看三立新聞")
            flag_exceed_time_range = True
            break

        print(str(counter) + "  " + news_time_str)
        counter += 1

        news_tag = link.find("div", class_="newslabel-tab").contents[0].contents[0]
        if news_tag in delete_tags_SET:
            continue

        news_content = sub_soup.find_all("div", id="Content1")
        if news_content is None or len(news_content) == 0:
            news_content = sub_soup.find_all("article", class_="printdiv")
        if news_content is None or len(news_content) == 0:
            news_content = sub_soup.find_all("div", class_="page-text")

        pos = str(news_content).find("延伸閱讀")
        if pos != -1:
            news_content = str(news_content)[:pos]

        keywords = get_keyword_in_news(news_content)

        if len(keywords) != 0:
            news_title = str(link_and_title.contents[0])
            print_result(news_title, "（三立）", news_link, keywords)
    end_SET = timer()
    print("^^^^^^^^^  結束: 三立新聞")
    print("用時 " + str(timedelta(seconds = end_SET - start_SET)) + "\n")
    if not flag_exceed_time_range:
        print("[WARNING - 三立新聞] 已看完目前列表所抓的新聞，尚未確認時間範圍內的所有新聞，可能要增加捲動次數")

#################################################################################

# 鏡週刊 焦點新聞列表  
if SWITCH_MIRROR:
    print("vvvvvvvvv  開始: 鏡週刊")
    flag_exceed_time_range = False
    start_Mirror = timer()
    earlier = datetime.now() - timedelta(hours=TIMESLOT)
    links = get_links_from_url("https://mirrormedia.mg/category/news", "Mirror")

    counter = 1
    for link in links:
        time.sleep(0.5)
        news_link = None
        news_title = None
        news_time = None

        divs = link.find_all("div")
        for div in divs:
            if div.has_attr("class"):
                if "article-list-item__ItemTitle-sc" in str(div["class"]):
                    news_title = str(div.contents[0])
                    news_link = "https://mirrormedia.mg" + str(link["href"])
        if news_link is None:
            continue
        
        # 整篇新聞都是圖，沒有文字，新聞時間格式不同，直接略過不看
        if "圖輯" in news_title:
            print("略過 " + news_title)
            continue

        sub_result = None
        if sys.platform == "darwin":
            # macos
            sub_result = requests.get(news_link)
        if sys.platform == "win32":
            # windows
            sub_result = requests.get(news_link, verify=False)

        sub_soup = BeautifulSoup(sub_result.text, features="html.parser")
        divs = sub_soup.find_all("div")
        for div in divs:
            if div.has_attr("class"):
                if "normal__SectionAndDate-sc" in str(div["class"]):
                    news_time = str(div.contents[1].contents[0])

        if news_time is None:
            news_times = sub_soup.find_all("p")
            for p in news_times:
                if p.has_attr("class"):
                    if "date__DateText-sc" in str(p["class"]):
                        news_time = str(p.contents[2])
                        break

        if not is_in_time_range(news_time, "%Y.%m.%d %H:%M", earlier):
            print("下一則新聞已超過時間範圍，停止查看鏡週刊")
            flag_exceed_time_range = True
            break

        print(str(counter) + "  " + news_time)
        counter += 1

        flag_ignore = False
        for tags in delete_tags_MIRROR:
            if tags in news_link:
                flag_ignore = True
                break
        
        if flag_ignore:
            continue

        news_contents = sub_soup.find_all("span", {"data-text":"true"})
        news_content = ""
        for content in news_contents:
            news_content += str(content.contents[0])

        keywords = get_keyword_in_news(news_content)

        if len(keywords) != 0:
            print_result(news_title, "（鏡週刊）", news_link, keywords)
    end_Mirror = timer()
    print("^^^^^^^^^  結束: 鏡週刊")
    print("用時 " + str(timedelta(seconds = end_Mirror - start_Mirror)) + "\n")
    if not flag_exceed_time_range:
        print("[WARNING - 鏡週刊] 已看完目前列表所抓的新聞，尚未確認時間範圍內的所有新聞，可能要增加捲動次數")

#################################################################################

# TVBS 即時新聞列表  
if SWITCH_TVBS:
    print("vvvvvvvvv  開始: TVBS")
    flag_exceed_time_range = False
    start_TVBS = timer()
    earlier = datetime.now() - timedelta(hours=TIMESLOT)
    # links = get_links_from_url("https://news.tvbs.com.tw/realtime", "TVBS")

    result = requests.get("https://news.tvbs.com.tw/realtime")
    links = BeautifulSoup(result.text, features="html.parser").find_all("li")

    counter = 1
    for link in links:
        time.sleep(0.5)
        if link.find("a") is None or link.find("div", class_="time") is None:
            continue

        news_link = "https://news.tvbs.com.tw" + str(link.find("a")["href"])
        sub_soup = get_subsoup_from_url(news_link)

        author_and_time = str(sub_soup.find_all("div", class_="author")[0])
        times = re.findall(r"\d{4}\/\d{2}\/\d{2} \d{2}:\d{2}", author_and_time)
        news_time = str(times[0])
        if not is_in_time_range(news_time, "%Y/%m/%d %H:%M", earlier):
            print("下一則新聞已超過時間範圍，停止查看TVBS")
            flag_exceed_time_range = True
            break
        
        print(str(counter) + "  " + news_time)
        counter += 1

        news_tag = link.find("div", class_="type").contents[0]
        if news_tag in delete_tags_TVBS:
            continue

        news_contents = sub_soup.find_all("div", class_="article_content", id="news_detail_div")
        news_contents = str(news_contents)
        try:
            more_news = re.search("更多新聞.*<\/a>", news_contents)
        except:
            aaaaaa = 1  # do nothing

        if more_news is not None:
            to_remove = str(more_news.group(0))
            news_contents = news_contents.replace(to_remove, "")

        keywords = get_keyword_in_news(news_contents)

        if len(keywords) != 0:
            news_title = str(link.find("h2").contents[0])
            print_result(news_title, "（TVBS）", news_link, keywords)
    end_TVBS = timer()
    print("^^^^^^^^^  結束: TVBS")
    print("用時 " + str(timedelta(seconds = end_TVBS - start_TVBS)) + "\n")
    if not flag_exceed_time_range:
        print("[WARNING - TVBS] 已看完目前列表所抓的新聞，尚未確認時間範圍內的所有新聞，可能要增加捲動次數")

#################################################################################

# NOWNEWS 即時新聞
if SWITCH_NOWNEWS:
    print("vvvvvvvvv  開始: NOWNEWS")
    flag_exceed_time_range = False
    start_NOWNEWS = timer()
    earlier = datetime.now() - timedelta(hours=TIMESLOT)

    url = "https://nownews.com/cat/breaking"
    driver.get(url)
    next_page_button = driver.find_element(By.ID, "moreNews")
    for x in range(0, SCROLL_PAGES - 3):
        time.sleep(SCROLL_DELAY)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_DELAY)
        next_page_button.click()
    time.sleep(SCROLL_DELAY)
    soup = BeautifulSoup(driver.page_source,"html.parser")
    links = soup.find_all("ul", id="ulNewsList")

    counter = 1
    for link in links[0]:
        time.sleep(0.5)
        if not isinstance(link, Tag):
            continue
        
        news_time = str(link.find("p", class_="time").contents[-1])
        if not is_in_time_range(news_time, "%Y-%m-%d %H:%M", earlier):
            print("下一則新聞已超過時間範圍，停止查看NOWNEWS")
            flag_exceed_time_range = True
            break

        print(str(counter) + "  " + news_time)
        counter += 1

        news_link = str(link.find("a")["href"])
        sub_soup = get_subsoup_from_url(news_link)
        news_body = sub_soup.find_all("article")  
        if news_body is None or len(news_body) == 0:
            # 類似地震速報可能會被導到「頁面不存在」，直接跳過不處理
            continue

        news_contents = news_body[0] # tag, should only have 1 result

        content_string = ""
        for content in news_contents:
            if content.name == "div":
                if content.has_attr("class"):
                    if str(content["class"][0]) == "related-item":
                        break

            content_string += str(content)

        keywords = get_keyword_in_news(content_string)

        if len(keywords) != 0:
            news_title = str(link.find("h3").contents[0])
            print_result(news_title, "（NOWNEWS）", news_link, keywords)
    end_NOWNEWS = timer()
    print("^^^^^^^^^  結束: NOWNEWS")
    print("用時 " + str(timedelta(seconds = end_NOWNEWS - start_NOWNEWS)) + "\n")
    if not flag_exceed_time_range:
        print("[WARNING - NOWNEWS] 已看完目前列表所抓的新聞，尚未確認時間範圍內的所有新聞，可能要增加捲動次數")

#################################################################################

# CTWANT 最新新聞列表
if SWITCH_CTWANT:
    print("vvvvvvvvv  開始: CTWANT")
    flag_exceed_time_range = False
    start_CTWANT = timer()
    earlier = datetime.now() - timedelta(hours=TIMESLOT)

    counter = 1
    exit_from_changing_page = False
    for page in range(1, SCROLL_PAGES-2):
        if exit_from_changing_page:
            break

        url = "https://ctwant.com/category/最新?page=" + str(page)
        # soup = get_soup_from_url(url, 0, SCROLL_DELAY)
        # links = soup.find_all("div", class_="p-realtime__item")

        result = requests.get(url)
        links = BeautifulSoup(result.text, features="html.parser").find_all("div", class_="p-realtime__item")

        for link in links:
            time.sleep(0.5)

            news_time = str(link.find("time")["datetime"])
            if not is_in_time_range(news_time, "%Y-%m-%d %H:%M", earlier):
                print("下一則新聞已超過時間範圍，停止查看CTWANT")
                flag_exceed_time_range = True
                exit_from_changing_page = True
                break

            print(str(counter) + " " + news_time)
            counter += 1
            
            news_link = "https://ctwant.com" + str(link.find("a")["href"])
            sub_soup = get_subsoup_from_url(news_link)

            news_tag = sub_soup.find("div", class_="e-category__main").contents[0]
            news_tag = news_tag.replace(" ", "").replace("\n", "")
            if news_tag in delete_tags_CTWANT:
                continue

            news_content = sub_soup.find("div", class_="p-article__content")
            buttons = news_content.findAll("button")
            for button in buttons:
                button.extract()

            pos = str(news_content).find("相關文章")
            if pos != -1:
                news_content = str(news_content)[:pos]

            keywords = get_keyword_in_news(news_content)

            if len(keywords) != 0:
                news_title = str(link.find("h2").contents[0]).replace("\n", "").replace("  ", "")
                print_result(news_title, "（CTWANT）", news_link, keywords)
    end_CTWANT = timer()
    print("^^^^^^^^^  結束: CTWANT")
    print("用時 " + str(timedelta(seconds = end_CTWANT - start_CTWANT)) + "\n")
    if not flag_exceed_time_range:
        print("[WARNING - CTWANT] 已看完目前列表所抓的新聞，尚未確認時間範圍內的所有新聞，可能要增加捲動次數")

#################################################################################

# 東森新聞 即時新聞列表
# 看起來新聞內文的網頁有擋爬蟲
if SWITCH_EBC:
    print("vvvvvvvvv  開始: 東森新聞")
    flag_exceed_time_range = False
    start_EBC = timer()
    earlier = datetime.now() - timedelta(hours=TIMESLOT)

    links = get_links_from_url("https://news.ebc.net.tw/realtime", "EBC")
    
    counter = 1
    for link in links:
        time.sleep(0.5)
        if not isinstance(link, Tag):
            continue

        news_link = "https://news.ebc.net.tw/" + link["href"]
        sub_result = requests.get(news_link, headers=headers)
        sub_soup = BeautifulSoup(sub_result.text, features="html.parser")

        for div in sub_soup.find_all("div", class_="inline_text has_marker"): 
            div.extract()

        news_datetime = str(sub_soup.find("div", class_="article_info_date"))
        news_date = re.findall(r"\d{4}-\d{2}-\d{2}", news_datetime)[0]
        news_time = re.findall(r"\d{2}:\d{2}", news_datetime)[0]
        full_news_time = news_date + " " + news_time
        if not is_in_time_range(full_news_time, "%Y-%m-%d %H:%M", earlier):
            print("下一則新聞已超過時間範圍，停止查看東森新聞")
            flag_exceed_time_range = True
            break

        print(str(counter) + " " + full_news_time)
        counter += 1

        news_tag = sub_soup.find("div", class_="breadcrumb").contents[3].contents[0]["title"]
        if news_tag in delete_tags_EBC:
            continue

        news_content = str(sub_soup.find("div", class_="article_content"))

        stop_words = ["更多鏡週刊報導", "以上言論不代表東森新聞立場", "東森新聞關心您", "往下看更多",  "延伸閱讀"]
        for stop_word in stop_words:
            pos = news_content.find(stop_word)
            if pos != -1:
                news_content = news_content[:pos]

        keywords = get_keyword_in_news(news_content)

        if len(keywords) != 0:
            news_title = link["title"]
            print_result(news_title, "（東森）", news_link, keywords)
    end_EBC = timer()
    print("^^^^^^^^^  結束: 東森新聞")
    print("用時 " + str(timedelta(seconds = end_EBC - start_EBC)) + "\n")
    if not flag_exceed_time_range:
        print("[WARNING - 東森新聞] 已看完目前列表所抓的新聞，尚未確認時間範圍內的所有新聞，可能要增加捲動次數")

#################################################################################

# 華視新聞 即時新聞列表
if SWITCH_CTS:
    print("vvvvvvvvv  開始: 華視新聞")
    flag_exceed_time_range = False
    start_CTS = timer()
    earlier = datetime.now() - timedelta(hours=TIMESLOT)
    links = get_links_from_url("https://news.cts.com.tw/real/index.html", "CTS")

    counter = 1
    for link in links:
        time.sleep(0.5)

        news_time = str(link.find("div", class_="newstime").contents[0])
        if not is_in_time_range(news_time, "%Y/%m/%d %H:%M", earlier):
            print("下一則新聞已超過時間範圍，停止查看華視新聞")
            flag_exceed_time_range = True
            break

        print(str(counter) + "  " + news_time)
        counter += 1

        newsTagLink = link.find("div", class_="tag").find("img")["src"]
        news_tag = get_CTS_news_tag(newsTagLink)

        if news_tag in delete_tags_CTS:
            continue

        news_link = link["href"]
        sub_soup = get_subsoup_from_url(news_link)
        for div in sub_soup.find_all("div", class_="flexbox cts-tbfs"): 
            div.extract()
        for div in sub_soup.find_all("div", class_="yt_container_placeholder"): 
            div.extract()

        news_content = sub_soup.find_all("div", class_="artical-content")
        keywords = get_keyword_in_news(str(news_content))

        if len(keywords) != 0:
            news_title = link["title"]
            print_result(news_title, "（華視）", news_link, keywords)
    end_CTS = timer()
    print("^^^^^^^^^  結束: 華視新聞")
    print("用時 " + str(timedelta(seconds = end_CTS - start_CTS)) + "\n")
    if not flag_exceed_time_range:
        print("[WARNING - 華視新聞] 已看完目前列表所抓的新聞，尚未確認時間範圍內的所有新聞，可能要增加捲動次數")

#################################################################################

if not DO_SHORT_URL:
    driver.close()
    
    with open(result_filename, 'w', encoding='UTF-8') as f:
        counter = 1
        news_info_queue.put(None) # To indicate termination
        while True:
            news_info = news_info_queue.get()

            if news_info == None:
                f.write("=========================================\n")
                f.write("開始執行時間：" + str(program_start_t) + "\n")
                f.write("執行結束時間：" + str(datetime.now()) + "\n")
                f.write("抓取 " + str(TIMESLOT) + " 個小時內的新聞\n")
                f.write("總共有 " + str(counter - 1) + " 則相關新聞\n")
                break
            else:
                print(". " + news_info[0])
                print(news_info[1])
                print(news_info[2])
                f.write(". " + news_info[0] + "\n")
                f.write(news_info[1] + "\n")
                counter += 1
    exit()

# tinyurl縮網址
print("#####################################")
print("    網頁爬蟲部分正常結束，開始縮網址。")
print("#####################################")

start_Tinyurl = timer()

news_info_queue.put(None) # To indicate termination

tinyurl = "https://tinyurl.com/app"
driver.get(tinyurl)
# Close pop-up sign-in ad
try:
    driver.find_element(By.XPATH, "//button[@aria-label='Close dialog']").click()
except NoSuchElementException:
    do_nothing = True
except ElementNotInteractableException:
    do_nothing = True

soup = BeautifulSoup(driver.page_source,"html.parser")

counter = 0
flag_get_next_news = True
with open(result_filename, 'w', encoding='UTF-8') as f:
    while True:
        driver.get(tinyurl)

        # Close pop-up sign-in ad
        try:
            driver.find_element(By.XPATH, "//button[@aria-label='Close dialog']").click()
        except (NoSuchElementException, ElementNotInteractableException):
            doNothing = True

        time.sleep(1)

        # Accept Cookie
        try:
            driver.find_element(By.XPATH, "//button[@data-test-id='cookies_section_got_it_btn']").click()
        except (NoSuchElementException, ElementClickInterceptedException, ElementNotInteractableException):
            doNothing = True

        time.sleep(1)

        if flag_get_next_news:
            news_info = news_info_queue.get()
            counter += 1

        if news_info == None:
            f.write("=========================================\n")
            f.write("開始執行時間：" + str(program_start_t) + "\n")
            f.write("執行結束時間：" + str(datetime.now()) + "\n")
            f.write("抓取 " + str(TIMESLOT) + " 個小時內的新聞\n")
            f.write("總共有 " + str(counter - 1) + " 則相關新聞\n")
            break
        
        longUrl = str(news_info[1])

        # paste long url
        try:
            driver.find_element(By.ID,'long-url').send_keys(longUrl)
        except (NoSuchElementException, ElementClickInterceptedException, ElementNotInteractableException) as err:
            print("[ERROR tinyurl_01] 長網址輸入區 " + str(type(err)))
            flag_get_next_news = False
            continue
        time.sleep(TINYURL_DELAY)

        # generate short url
        try:
            driver.find_element(By.XPATH, "//button[@data-test-id='home_shortener_btn_create']").click()
        except (NoSuchElementException, ElementClickInterceptedException, ElementNotInteractableException) as err:
            print("[ERROR tinyurl_02] 縮網址按鈕 " + str(type(err)))
            flag_get_next_news = False
            continue
        time.sleep(TINYURL_DELAY)

        # copy short url
        try:
            short_url = driver.find_element(By.XPATH,"//input[@data-test-id='homepage_create_tinyurl_form_created_input']").get_attribute("value")
        except (NoSuchElementException, ElementClickInterceptedException, ElementNotInteractableException) as err:
            print("[ERROR_tinyurl_03] 短網址內容 " + str(type(err)))
            flag_get_next_news = False
            continue    
        time.sleep(TINYURL_DELAY)

        flag_get_next_news = True
        print(". " + news_info[0])
        print(str(short_url))
        print(news_info[2])
        f.write(". " + news_info[0] + "\n")
        f.write(str(short_url) + "\n")

print("#####################################")
print("   網頁爬蟲與縮網址部分正常結束，請開啟 " + result_filename + " 檢視新聞")
print("#####################################")
end_Tinyurl = timer()
print("縮網址用時 " + str(timedelta(seconds = end_Tinyurl - start_Tinyurl)) + "\n")
driver.close()