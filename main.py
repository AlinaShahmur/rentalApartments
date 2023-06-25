from get_coordinates import *
from data_handler import *
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from bs4 import BeautifulSoup
from selenium.webdriver.support import expected_conditions as EC
import requests
from selenium.webdriver.chrome.options import Options


headers = {
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
    "Accept-Language":"he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7"
}

chrome_options = Options()
chrome_options.add_experimental_option("detach", True)

YAD2_URL = "https://www.yad2.co.il/realestate/rent?topArea=2&area=1&city=5000&propertyGroup=apartments,houses"
WIKI_URL = "https://en.wikipedia.org/wiki/List_of_Israeli_universities_and_colleges"


# get html from Israel colleges and universities wiki data
response = requests.get(WIKI_URL)
soup = BeautifulSoup(response.text, "html.parser")

container = soup.find("div", {"class": "mw-parser-output"})

universities = container.select("table.wikitable tbody tr td li")
colleges = container.select("table:nth-of-type(2) tbody tr td ul li")
print(len(colleges))

education_tlv = []

# find universities in tel aviv
for un in universities:
    un_title = un.text
    if "tel aviv" in un_title.lower():
        print(un_title)
        un_coordinates = get_coordinates_by_search_query(un_title)
        latitude = un_coordinates.get('lat')
        longitude = un_coordinates.get('lng')
        education_tlv.append({"name": un_title.split(",")[0], 'lat': latitude, 'lng': longitude})

# find colleges in tel aviv
for col in colleges:
    col_title = col.text
    if "tel aviv" in col.text.lower():
        print(col_title)
        col_coordinates = get_coordinates_by_search_query(col_title)
        latitude = col_coordinates.get('lat')
        longitude = col_coordinates.get('lng')
        education_tlv.append({"name": col_title.split(",")[0], 'latitude': latitude, 'longitude': longitude})

print(education_tlv)

write_csv("education_tel_aviv.csv", education_tlv)

# set selenium options

chrome_driver_path = "C:\Development\chromedriver.exe"
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)
driver.set_window_size(1640, 969)

driver.get(YAD2_URL)
current_page = 1
pages_to_scrap = 8

apartments = []

# scrapping apartments data from 8 pages

while current_page <= pages_to_scrap:
    try:
        # apartments list
        items = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".feeditem.table")))
        print(items)
        for item in items:

            # waiting when it will be loaded
            driver.implicitly_wait(6)
            item.click()

            # waiting when it will be loaded
            driver.implicitly_wait(10)

            # skipping advertisements from realtors
            feed_item_list = item.find_elements(By.CSS_SELECTOR, ".feed_item.accordion")
            if len(feed_item_list) < 1:
                continue
            feed_item = feed_item_list[0]
            children = feed_item.find_elements(By.XPATH, "./*")
            if len(children) < 2:
                continue

            # yellow container with common data
            yellow_container = children[0]

            # unfolding window
            opened_window = children[1]

            # apartments detailed info
            info_items = opened_window.find_element(By.CSS_SELECTOR, 'div.info_items').find_elements(By.XPATH, "./*")

            # additional information
            additional_items = opened_window.find_element(By.CSS_SELECTOR,
                                                          'div.items_container').find_elements(By.XPATH, "./*")

            # set parameters
            elevator = 'no' if "delete" in additional_items[5].get_attribute('class') else 'yes'
            protected_room = 'no' if "delete" in additional_items[8].get_attribute('class') else 'yes'
            animals = 'no' if "delete" in additional_items[10].get_attribute('class') else 'yes'
            furniture = 'no' if "delete" in additional_items[12].get_attribute('class') else 'yes'

            parking = ""
            property_tax = ""
            floors_total = ""
            for i in info_items:
                if "חניות" in i.text:
                    parking = i.text.split('\n')[1]
                    continue
                if "ארנונה" in i.text:
                    property_tax = i.text.split('\n')[1]
                    continue
                if "קומות בבנין" in i.text:
                    floors_total = i.text.split('\n')[1]
                    continue

            apartment_type = yellow_container.find_element(By.CSS_SELECTOR, '.subtitle').text.split(',')[0]
            neighborhood = yellow_container.find_element(By.CSS_SELECTOR, '.subtitle').text.split(',')[1]
            address = yellow_container.find_element(By.CSS_SELECTOR, 'span.title').text
            rent_sum = yellow_container.find_element(By.CSS_SELECTOR, '.left_col.with_new_tab div.price').text.split(' ')[0]
            floor = yellow_container.find_element(By.CSS_SELECTOR, '.floor-item span.val').text
            rooms = yellow_container.find_element(By.CSS_SELECTOR, '.middle_col span.val').text
            square = yellow_container.find_element(By.CSS_SELECTOR,
                                                   '.middle_col div.SquareMeter-item span.val').text
            # get geographical coordinates
            apt_coordinates = get_coordinates_by_search_query(address + ", תל אביב")
            latitude = apt_coordinates.get('lat')
            longitude = apt_coordinates.get('lng')
            apartment_dict = {'apartment_type': apartment_type, 'neighborhood': neighborhood, 'address': address,
                                    'latitude': latitude, 'longitude': longitude,
                                    'floor': floor, 'floors_total': floors_total, 'rooms': rooms, 'square': square,
                                    'rent_sum': rent_sum, 'property_tax': property_tax, 'elevator': elevator,
                                    'protected_room': protected_room,'animals': animals, 'furniture': furniture,
                                    'parking': parking}
            apartments.append(apartment_dict)
        current_page = current_page+1
        driver.get(YAD2_URL+"&page=" + str(current_page))

    except:
        write_csv('apartments.csv', apartments)

write_csv('apartments.csv', apartments)