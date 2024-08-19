#Scraping
# pip install selenium
from selenium import webdriver
# If the above import fails, you may need to install selenium:
# pip install seleniumfrom selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# pip install BeautifuSoup
from bs4 import BeautifulSoup
#Data Frame
import pandas as pd
#Updates
from updates import *
#GUI
import tkinter as tk
from tkinter import messagebox
#Other
from detect_captcha import detect_captcha
import time
from translate import translate_city
#""""""""""""""""""""""""""""""""""""""SCRAPING CODE"""""""""""""""""""""""""""""""""""""""""""""""""
CITIES = ["תל אביב יפו", "ראשון לציון", "ירושלים", "חיפה", "פתח תקווה", "באר שבע"]
WEBSITE = "https://www.yad2.co.il/realestate/rent"
#Download ChromeDriver
DRIVER_PATH = "#" #Enter the path here
CSV_PATH = "#" #Enter the path here
DRIVER = webdriver.Chrome()

#Base lists
ids = []
links = []


#Lists that go into dataframe
new_links = []
new_ids = []
rooms = []
prices = []

#Links that the price was updated
updated_links = []

def check_prices_(driver,new_links,csv_path,translated_city,updated_links):
            for link in new_links:
                price_update(driver, link, csv_path, translated_city)
            for link in new_links:
                updated = price_update(driver, link, csv_path, translated_city)
                if updated:
                    updated_links.append(link)
            if updated_links:
                send_email(updated_links)

def captcha_warning(driver):
    if detect_captcha(driver):
            captcha_window = tk.Tk()
            captcha_window.title("Captcha Detected, Please Solve")
            captcha_button = tk.Button(captcha_window, text="Captcha Solved", command=main_(driver))
            captcha_button.pack(pady=10)

            captcha_window.mainloop()

def get_listings(driver, existing_ids,ids,links):
            boxes = driver.find_elements(By.XPATH, '//div[@class = "card_cardBox__KLi9I card-8_card8__HMpUa"]')
        #Get all listings in the page
            for box in boxes:
                try:
                    link = box.find_element(By.TAG_NAME, 'a').get_attribute('href')
                    start = link.find('item/') + len('item/')
                    end = link.find('?')
                    id = link[start:end]
                    if id not in existing_ids:
                        ids.append(id)
                        links.append(link)    
                except Exception as e:
                    print(f"Error occurred: {e}")   

def get_info(driver, existing_ids,links,rooms,new_ids,new_links,prices,city):
            #Open each link and extarct data
            for i in links[:-3]:
                try:
                    driver.get(i) #Open the link
                    start = i.find('item/') + len('item/')
                    end = i.find('?')
                    id = i[start:end]
                    if id not in existing_ids:
                        new_ids.append(id) 
                        new_links.append(i)
                        html = driver.page_source
                        soup = BeautifulSoup(html, 'lxml')

                        #Get price
                        try:
                            price_element = soup.find('span', {'class': 'price_price__xQt90', 'data-testid': 'price'})
                            price_text = price_element.text.strip()
                            price_text = price_text.replace(',', '').replace('₪', '').strip()
                            prices.append(price_text)
                        except:
                            pass

                        #Get number of rooms
                        try:
                            room_element = soup.find('span', {'data-testid': 'building-text'})
                            room_text = room_element.text.strip()
                            rooms.append(room_text)
                        except:
                            pass

                    #Detect captcha ---> start_
                    if detect_captcha(driver):
                        captcha_window = tk.Tk()
                        captcha_window.title("Captcha Detected, Please Solve")
                        captcha_button = tk.Button(captcha_window, text="Captcha Solved", command=scrape(driver,existing_ids,city))
                        captcha_button.pack(pady=10)

                        captcha_window.mainloop()
                except Exception as e:
                    print(f"Error occurred: {e}")                               

def main_(driver):
    for city in CITIES:
        driver.get(WEBSITE)

        #Detect captcha ---> main
        captcha_warning(driver)

        translated_city = translate_city(city)
        
        try:
            df_existing = pd.read_csv(f'{CSV_PATH}/Listings_Data_{translated_city}.csv')
            existing_ids = df_existing['ids'].values
        except FileNotFoundError:
            df_existing = pd.DataFrame(columns=['links', 'ids', 'rooms', 'price'])
            existing_ids = df_existing['ids'].values

        scrape(driver,existing_ids,city)
        driver.quit()
        
def scrape(driver, existing_ids, city):
            city_copy = city
            translated_city = translate_city(city_copy)
            existing_ids_copy = existing_ids.copy()
            #Select Textbox
            try:
                textbox = driver.find_element(By.XPATH, '//input[@aria-autocomplete = "list"]')
            except:
                print("Error: Could not find textbox")
                driver.quit() 
            #Write to Textbox        
            textbox.clear()
            textbox.send_keys(city_copy)
            time.sleep(1)

            #Select city option
            try:
                option = driver.find_element(By.XPATH, '//ul[@id = "עיר"]/li[@role = "option"]')
            except:
                print("Error: Could not find city option")
                driver.quit()
            option.click()

            #Click search button
            try:
                search_button = driver.find_element(By.XPATH, '//button[@type = "submit"]')
            except:
                print("Error: Could not find search button")
                driver.quit()

            search_button.click()
            time.sleep(2)

            #Detect captcha ---> scrape
            captcha_warning(driver)

            time.sleep(1)
            get_listings(driver, existing_ids_copy, ids, links)

            time.sleep(1)
            get_info(driver, existing_ids_copy, links, rooms, new_ids, new_links, prices, city_copy)

            df_new = pd.DataFrame({'links': new_links,'ids': new_ids, 'rooms': rooms, 'price': prices})
            df_new.to_csv(f'Listings_Data_{translated_city}.csv', mode='a', header=False, index=False)

#"""""""""""""""""""""""""""""""""""""""""GUI CODE""""""""""""""""""""""""""""""""""""""""""""""""""
    
def run_scraper():
    try:
        main_(DRIVER)
    except Exception as e:
         print(f"Error occurred: {e}")

# Create the main window
window = tk.Tk()
window.title("Yad2 Scraper")

# Create a button
run_button = tk.Button(window, text="Run Scraper", command=run_scraper)
run_button.pack(pady=10)

# Start the main event loop
window.mainloop()




