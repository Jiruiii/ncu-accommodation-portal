import json
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
import time
import re

# 讀取 data.json 
with open("C:\\Users\\User\\Documents\\Self_Practice\\ncu-accommodation-portal\\src\\data.json", "r", encoding="utf-8") as file:
    data = json.load(file)

titles = [item["標題"] for item in data]
locations = [item["地址"] for item in data]
prices = [item["房租"] for item in data]
types = [item["出租房數"].keys() for item in data]
studioSizes = [item["出租房數"]["套房"]["坪數"] if "套房" in item["出租房數"] else "" for item in data]
shareSizes = [item["出租房數"]["雅房"]["坪數"] if "雅房" in item["出租房數"] else "" for item in data]
studioRooms = [item["出租房數"]["套房"]["空房"] if "套房" in item["出租房數"] else "" for item in data]
shareRooms = [item["出租房數"]["雅房"]["空房"] if "雅房" in item["出租房數"] else ""  for item in data]
images = [item["房屋照片"][0] if item["房屋照片"] else "" for item in data if "房屋照片" in item]

# 設定 Chrome Driver 路徑
chrome_driver_path = "C:\\Users\\User\\Documents\\Self_Practice\\Web_Crawler\\chromedriver.exe"
service = Service(chrome_driver_path)
options = Options()

driver = webdriver.Chrome(service=service, options=options)  # 打開 Chrome 

driver.get("https://www.google.com/maps/@24.9681606,121.1927239,17z?entry=ttu&g_ep=EgoyMDI1MDUxMi4wIKXMDSoASAFQAw%3D%3D") # 打開 google map

time.sleep(1)

dataList = []
id = 1

for location in locations :
    data = {}

    # 找到搜尋框並點擊
    search_bar = driver.find_element(By.TAG_NAME, "input")
    search_bar.click()

    search_input = driver.find_element(By.ID, "searchboxinput")
    search_input.clear() # 清除搜尋框的內容
    search_input.send_keys(location)

    search_input.send_keys(Keys.ENTER)

    time.sleep(3)

    # 找到 canvas
    canvas = driver.find_element(By.CSS_SELECTOR, 'canvas.widget-scene-canvas')

    # 設定起點座標（canvas 中心）
    rect = canvas.rect
    start_x = rect['x'] + rect['width'] / 2
    start_y = rect['y'] + rect['height'] / 2

    # JS 模擬滑動的 function
    drag_script = """
        const canvas = arguments[0];
        const startX = arguments[1];
        const startY = arguments[2];
        const endX = arguments[3];
        const endY = arguments[4];
        const steps = arguments[5];

        function sleep(ms) {
            return new Promise(resolve => setTimeout(resolve, ms));
        }

        (async function simulateDrag() {
            function dispatchMouseEvent(type, x, y) {
                const evt = new MouseEvent(type, {
                    bubbles: true,
                    cancelable: true,
                    view: window,
                    clientX: x,
                    clientY: y,
                    buttons: 1
                });
                canvas.dispatchEvent(evt);
            }

            dispatchMouseEvent('mousedown', startX, startY);

            for (let i = 0; i <= steps; i++) {
                const x = startX + (endX - startX) * (i / steps);
                const y = startY + (endY - startY) * (i / steps);
                dispatchMouseEvent('mousemove', x, y);
                await sleep(10);  // 模擬拖拉的延遲
            }

            dispatchMouseEvent('mouseup', endX, endY);
        })();
    """

    end_x = start_x - 244 # 目標往左拖動 244px
    end_y = start_y + 1 # 目標往上拖動 1px

    # 拖動前取得 URL
    before_url = driver.current_url

    # 執行 JS 拖動
    driver.execute_script(drag_script, canvas, start_x, start_y, end_x, end_y, 70)

    time.sleep(3)

    url = driver.current_url

    # 擷取網址中 @ 後面的經緯度
    match = re.search(r'@([0-9\.\-]+),([0-9\.\-]+)', url)

    if match:
        latitude = float(match.group(1))
        longitude = float(match.group(2))

    x = ((longitude - 121.18) / (121.22 - 121.18)) * 100
    y = ((24.96 - latitude) / (24.97 - 24.96)) * 100

    priceText = prices[id - 1]
    priceNumbers = list(map(int, re.findall(r"\d+", priceText)))  # 轉換為整數
    if len(priceNumbers) > 1 :
        priceNumber = sum(priceNumbers) / len(priceNumbers) 
        price = "NT$ " + str(priceNumbers[0]) + "~" + str(priceNumbers[1]) + "/月"
    else :
        priceNumber = int(priceNumbers[0])
        price = "NT$ " + str(priceNumber) + "/月"
        
    typeText = list(types[id - 1])
    if len(typeText) > 1 :
        type = typeText[0] + "/" + typeText[1]
    else :
        type = typeText[0]

    studioSizeText = studioSizes[id - 1]
    shareSizeText = shareSizes[id - 1]
    if studioSizeText != "" and shareSizeText != "" :
        size = studioSizeText + "/" + shareSizeText
    elif studioSizeText != "":
        size = studioSizeText
    else :
        size = shareSizeText

    studioRoomText = studioRooms[id - 1]
    shareRoomText = shareRooms[id - 1]
    if studioSizeText != "" and shareSizeText != "" :
        room = str(studioRoomText) + "/" + str(shareRoomText)
    elif studioSizeText != "":
        room = str(studioRoomText)
    else :
        room = str(shareRoomText)
    
    data["id"] = id
    data["title"] = titles[id - 1]
    data["price"] = price
    data["priceNumber"] = priceNumber
    data["location"] = location
    data["type"] = type
    data["size"] = size
    data["room"] = room

    if images[id - 1] :
        data["image"] = images[id - 1]

    data["lat"] = latitude
    data["lng"] = longitude
    data["x"] = x
    data["y"] = y
    
    dataList.append(data)
    id += 1

outputPath = "C:\\Users\\User\\Documents\\Self_Practice\\ncu-accommodation-portal\\src\\mapMarkers.json"

#匯出成 JSON 檔案
with open(outputPath, "w", encoding = "utf-8") as f:
    json.dump(dataList, f, ensure_ascii = False, indent = 4)