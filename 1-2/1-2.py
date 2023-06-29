import random
import re
import time

import pandas as pd
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome import service as fs
import socket
import ssl
import OpenSSL
from urllib.parse import urlparse
from selenium.common.exceptions import NoSuchElementException






#ドライバーの設定
driver_path = r"C:\Users\Owner\Desktop\scraping_practice\1-2\chromedriver.exe"
chrome_service = fs.Service(executable_path=driver_path)

options = Options()
options.add_argument('--headless')

#user-agent設定
user_agent = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'
                ]

options.add_argument('--user-agent=' + user_agent[random.randrange(0, len(user_agent), 1)])


driver = webdriver.Chrome(service=chrome_service, options=options)


#ぐるなびのページに遷移
driver.get("https://www.gnavi.co.jp/")


#検索条件「イタリアン」で検索
driver.find_element(By.NAME, "suggest-number").send_keys("イタリアン")
driver.find_element(By.CLASS_NAME, "c-button").click()

driver.implicitly_wait(3)


page_num = 1

data = []

shop_urls = []


#店舗ごとのURL取得
while len(shop_urls) < 50:
    shops = driver.find_elements(By.CLASS_NAME, "style_wrap___kTYa")
    
    for shop in shops:
        shop_a_tag = shop.find_element(By.TAG_NAME, "a")
        shop_urls.append(shop_a_tag.get_attribute("href"))
        if len(shop_urls) == 50:
            break
    
    page_footer = driver.find_element(By.CLASS_NAME, "style_pages__Y9bbR")
    if page_num == 1:
        page_footer.find_elements(By.TAG_NAME, "li")[9].click()
    else:
        page_footer.find_elements(By.TAG_NAME, "li")[11].click()
    page_num += 1
    time.sleep(3)


#店舗ごとの情報取得  
for shop_url in shop_urls:
    driver.get(shop_url)
    
    driver.implicitly_wait(3)


    #店名
    shop_name = driver.find_element(By.ID, "info-name").text

    #電話番号
    phone_number = driver.find_element(By.CLASS_NAME, "number").text

    #メールアドレス
    mail = ""

    #住所
    address = driver.find_element(By.CLASS_NAME, "region").text
    try:
        building = driver.find_element(By.CLASS_NAME, "locality").text
    except NoSuchElementException:
        building = ""



    pattern = '''(...??[都道府県])((?:旭川|伊達|石狩|盛岡|奥州|田村|南相馬|那須塩原|東村山|武蔵村山|羽村|十日町|上越|
                富山|野々市|大町|蒲郡|四日市|姫路|大和郡山|廿日市|下松|岩国|田川|大村|宮古|富良野|別府|佐伯|黒部|小諸|塩尻|玉野|
                周南)市|(?:余市|高市|[^市]{2,3}?)郡(?:玉村|大町|.{1,5}?)[町村]|(?:.{1,4}市)?[^町]{1,4}?区|.{1,7}?[市町村])(.+)'''

    result = re.match(pattern, address)
    if result:
        address_1 = result.group(1)
        address_2 = result.group(2)
        address_3 = result.group(3)

    #URL, SSL
    try:
        official_url = driver.find_element(By.CLASS_NAME, "sv-of").get_attribute("href")

        #SSL証明書の有無
        if "https" in official_url:
            valid = True
        else:
            valid = False
            
    except Exception:
        official_url = ""
        valid = ""


    data.append([shop_name, phone_number, mail, address_1, address_2, address_3, building, official_url, valid])


    driver.implicitly_wait(3)

driver.quit()


#二次元リストをデータフレーム化
df = pd.DataFrame(data, columns=["店舗名", "電話番号", "メールアドレス", "都道府県", "市区町村", "番地", "建物名", "URL", "SSL"])
df.set_index("店舗名", inplace=True)


#CSVファイルとして保存
df.to_csv("1-2.csv", encoding="cp932")