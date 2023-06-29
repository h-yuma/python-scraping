from bs4 import BeautifulSoup
import datetime
import numpy as np
import pandas as pd
import re
import requests
import time
from fake_useragent import UserAgent

#Useragent設定
ua = UserAgent()
header = {"user-agent": ua.chrome}

#ぐるなびの検索条件
dt_now = datetime.datetime.now().strftime("%Y%m%d")
keyword = "イタリアン"
search_url = f"https://r.gnavi.co.jp/area/jp/rs/?date={dt_now}&fw={keyword}"


#3ページ分のURL  
url_list = []
for i in range(1, 4):
    url_list.append(f"https://r.gnavi.co.jp/area/jp/rs/?date={dt_now}&fw={keyword}&p={i}")



#店舗ごとのURL取得
shop_urls = []

for url in url_list:
    response = requests.get(url, headers=header)
    bs = BeautifulSoup(response.text, "html.parser")
    shops = bs.find_all("div", class_="style_wrap___kTYa")
    
    for shop in shops:
        shop_a_tag = shop.find("a")
        shop_urls.append(shop_a_tag.get("href"))
        if len(shop_urls) == 50:
            break



data = []

#店舗ごとの情報取得
for shop_url in shop_urls:
    response = requests.get(shop_url, headers=header)
    bs = BeautifulSoup(response.content, "html.parser")
    
    #店名
    shop_name = bs.find("p", id="info-name")
    clear_shop_name = shop_name.text.replace(u'\xa0', u' ')
    
    #電話番号
    phone_number = bs.find("span", class_="number")
    if phone_number:
        phone_number = phone_number.text
    
    #メールアドレス
    mail = ""

    #住所
    address = bs.find("span", class_="region")
    building = bs.find("span", class_="locality")
    if building:
        building = building.text
    else:
        building = ""

    
    pattern = '''(...??[都道府県])((?:旭川|伊達|石狩|盛岡|奥州|田村|南相馬|那須塩原|東村山|武蔵村山|羽村|十日町|上越|
            富山|野々市|大町|蒲郡|四日市|姫路|大和郡山|廿日市|下松|岩国|田川|大村|宮古|富良野|別府|佐伯|黒部|小諸|塩尻|玉野|
            周南)市|(?:余市|高市|[^市]{2,3}?)郡(?:玉村|大町|.{1,5}?)[町村]|(?:.{1,4}市)?[^町]{1,4}?区|.{1,7}?[市町村])(.+)'''
            
    result = re.match(pattern, address.text)
    if result:
        address_1 = result.group(1)
        address_2 = result.group(2)
        address_3 = result.group(3)
    
    #オフィシャルURL
    official_url = ""
    official_url_SSL = ""
    
    data.append([clear_shop_name, phone_number, mail, address_1, address_2, address_3, building, official_url, official_url_SSL])
    
    #アイドリングタイム
    time.sleep(3)
    
    
df = pd.DataFrame(data, columns=["店舗名", "電話番号", "メールアドレス", "都道府県", "市区町村", "番地", "建物名", "URL", "SSL"])
df.set_index("店舗名", inplace=True)

df.to_csv("1-1.csv", encoding="cp932")

