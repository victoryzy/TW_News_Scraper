hoursBefore   2  # 限定整數。例如：2，代表要留下「2個小時內有發文的臉書」瀏覽器分頁

urlAndName   []  # 這行不要動
# 以下的可以按照格式新增，如果要暫時「不看」某個臉書，在那一行的開頭加上"#"即可。
# 每一行的順序即為自動看臉書時的順序
# 多餘的空白只是為了程式碼美觀，沒有其他功能
urlAndName.append(("https://facebook.com/savefirefighters                 ", "搶救消防員       "))
urlAndName.append(("https://facebook.com/profile.php?id 100087552498464   ", "靠北消防3.0      "))
urlAndName.append(("https://facebook.com/SanCheng624                      ", "桃園市長 張善政   "))
urlAndName.append(("https://facebook.com/DrAnnKao                         ", "新竹市長 高虹安   "))
urlAndName.append(("https://facebook.com/WKYang.HC                        ", "新竹縣長 楊文科   "))
urlAndName.append(("https://facebook.com/DongJinZhong                     ", "苗栗縣長 鍾東錦   "))
urlAndName.append(("https://facebook.com/hsinchunew                       ", "新竹市政府        "))
urlAndName.append(("https://facebook.com/CCCHsinchu                       ", "立委 鄭正鈐       "))
urlAndName.append(("https://facebook.com/LawyerHandyChiu                  ", "立委 邱顯智       "))
urlAndName.append(("https://facebook.com/kerchenming                      ", "立委 柯建銘       "))
urlAndName.append(("https://facebook.com/woolwooldog2018                  ", "東區 鄭美娟       "))
urlAndName.append(("https://facebook.com/captainGINAonduty                ", "東區 劉彥伶       "))
urlAndName.append(("https://facebook.com/ShuYing1012                      ", "東區 鍾淑英       "))
urlAndName.append(("https://facebook.com/pangyen122525                    ", "東區 余邦彥       "))
urlAndName.append(("https://facebook.com/WenZhengHuangGoGo                ", "東區 黃文政       "))
urlAndName.append(("https://facebook.com/NPPSunnyBird                     ", "東區 蔡惠婷       "))
urlAndName.append(("https://facebook.com/ChangTsuYen.KMT                  ", "東區 張祖琰       "))
urlAndName.append(("https://facebook.com/ChooseBetterHsinchu              ", "東區 李國璋       "))
urlAndName.append(("https://facebook.com/iHsinChu.Liu                     ", "東區 劉崇顯       "))
urlAndName.append(("https://facebook.com/profile.php?id 100063771856763   ", "東區 曾資程       "))
urlAndName.append(("https://facebook.com/profile.php?id 100078702253431   ", "東區 宋品瑩       "))
urlAndName.append(("https://facebook.com/profile.php?id 100053426403761   ", "東區 段孝芳       "))
urlAndName.append(("https://facebook.com/WuHsuFeng                        ", "北區 吳旭豐       "))
urlAndName.append(("https://facebook.com/whiteservice225                  ", "北區 劉康彥       "))
urlAndName.append(("https://facebook.com/Hsinchu.LingYi                   ", "北區 楊玲宜       "))
urlAndName.append(("https://facebook.com/0Yenfu                           ", "北區 林彥甫       "))
urlAndName.append(("https://facebook.com/meihui5336696                    ", "北區 黃美慧       "))
urlAndName.append(("https://facebook.com/profile.php?id 100006838005121   ", "北區 孫錫洲       "))
urlAndName.append(("https://facebook.com/yao0909                          ", "北區 彭昆耀       "))
urlAndName.append(("https://facebook.com/market.chingchin                 ", "北區 鄭慶欽       "))
urlAndName.append(("https://facebook.com/profile.php?id 100002200637947   ", "北區 蕭志潔       "))
urlAndName.append(("https://facebook.com/passionhsinchu                   ", "西區 陳建名       "))
urlAndName.append(("https://facebook.com/a0932937349                      ", "西區 陳治雄       "))
urlAndName.append(("https://facebook.com/Taiwanbigear                     ", "香山區 林盈徹     "))
urlAndName.append(("https://facebook.com/ChenChiYuanGoGoGo                ", "香山區 陳啓源     "))
urlAndName.append(("https://facebook.com/people/吳國寶/1734388582          ", "香山區 吳國寶     "))
urlAndName.append(("https://facebook.com/SiangshanForward                 ", "香山區 廖子齊     "))
urlAndName.append(("https://facebook.com/ChingLing0828                    ", "香山區 陳慶齡     "))
urlAndName.append(("https://facebook.com/profile.php?id 100006637456112   ", "香山區 鄭成光     "))
urlAndName.append(("https://facebook.com/ashiugo                          ", "南區和原住民 許修睿"))
urlAndName.append(("https://facebook.com/9.so.good                        ", "南區和原住民 施乃如"))
urlAndName.append(("https://facebook.com/TienYaFang                       ", "南區和原住民 田雅芳"))
urlAndName.append(("https://facebook.com/hsmeihui                         ", "南區和原住民 徐美惠"))
# urlAndName.append(("https://facebook.com/profile.php?id 100002205505005   ", "南區和原住民 林慈愛"))  # 不是公開的個人專頁，所以看不到內容

########################################################################################
#    以下內容不要改動！！！
########################################################################################

import re
import sys
import time
import requests
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from urllib3.exceptions import InsecureRequestWarning

scrollPages   1
scrollDelay   2.5

def getSoupFromURL(url, scrollPages, scrollDelay):
    driver.get(url)
    closeX   driver.find_element(By.XPATH, '//div[@aria-label "關閉"]')
    closeX.click()
    for x in range(0, scrollPages):
        time.sleep(scrollDelay)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(scrollDelay)
    soup   BeautifulSoup(driver.page_source,"html.parser")
    return soup

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

driver.get("https://www.google.com")
original_window   driver.current_window_handle
driver.switch_to.new_window('tab')

requests.packages.urllib3.disable_warnings(category InsecureRequestWarning)

flagNewTab   True

for url, name in urlAndName:
    if flagNewTab:
        driver.switch_to.new_window('tab')
    soup   getSoupFromURL(url, scrollPages, scrollDelay)

    time.sleep(scrollDelay)

    As   soup.find_all("a")
    flagFindTime   False

    for a in As:
        if a.has_attr("aria-label"):
            labelContent   a["aria-label"]
            if  "小時" in labelContent  or "分鐘" in labelContent or \
                "月"   in labelContent or "日"   in labelContent or \
                "天"   in labelContent:
                flagFindTime   True
                
                if "分鐘" in labelContent:
                    flagNewTab   True
                elif  "小時" in labelContent:
                    hours   re.findall("\\d*", labelContent)[0]

                    if int(hours) <  hoursBefore:
                        flagNewTab   True
                    else:
                        flagNewTab   False
                else:
                    flagNewTab   False

                if flagNewTab:
                    driver.execute_script("window.scrollTo(0, document.body.scrollTop);")
                    print("已檢查 %s 的臉書，最新貼文時間：%s ，請查看： %s" %(name, labelContent, url))
                else:
                    print("已檢查 %s 的臉書，最新貼文時間：%s " %(name, labelContent))

                break

    if not flagFindTime:
        flagNewTab   False

if not flagNewTab:
    driver.get("https://www.google.com")

print("已檢查完所有臉書專頁，可手動關閉瀏覽器和命令提示字元，瀏覽器將在15分鐘後自動關閉。")

time.sleep(900)