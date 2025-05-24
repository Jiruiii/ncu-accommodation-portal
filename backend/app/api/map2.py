import json
import re


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

dataList = []
id = 1

for location in locations :
    data = {}

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

    dataList.append(data)
    id += 1

print(dataList)