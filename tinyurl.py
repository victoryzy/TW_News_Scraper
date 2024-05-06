import time
import pyperclip as pc
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

driverPath = r"/usr/local/bin/chromedriver"
service_ = Service(executable_path=driverPath)
opt = webdriver.ChromeOptions()
opt.add_argument("user-agent\":\"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36")
opt.add_argument("--disable-notifications")
opt.add_argument("--no-sandbox")
driver = webdriver.Chrome(service=service_, options=opt)

url = "https://tinyurl.com/app"
driver.get(url)
soup = BeautifulSoup(driver.page_source,"html.parser")

for i in range(0, 5):
    longUrl = "https://youtube.com" + str(i)    # example

    # paste long url
    driver.find_element(By.ID,'long-url').send_keys(longUrl)
    time.sleep(1)

    # generate short url
    driver.find_element(By.XPATH, "//button[@data-test-id='home_shortener_btn_create']").click()
    time.sleep(1)

    # copy short url
    driver.find_element(By.XPATH, "//button[@id='form_tinyurl_copy_btn']").click()
    time.sleep(1)
    print(pc.paste())

    # return to original page for another iteration
    driver.find_element(By.XPATH, "//button[@id='homepage_create_tinyurl_form_shorten_another_btn']").click()


driver.close()