#Scraping
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd
#Email
import smtplib
import email
from email.mime.text import MIMEText
from detect_captcha import detect_captcha
from yad2 import scrape
import tkinter as tk

def price_update(driver, link, csv_path, TRANSLATED_CITY):
    # Read the existing CSV file
    df_existing = pd.read_csv(f'{csv_path}/Listings_Data_{TRANSLATED_CITY}.csv')

    # Open the link and get the new price
    driver.get(link)
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')

    try:
        price_element = soup.find('span', {'class': 'price_price__xQt90', 'data-testid': 'price'})
        new_price = price_element.text.strip().replace(',', '').replace('₪', '').strip()
    except:
        new_price = None

    # Find the row in the DataFrame with the matching link
    row = df_existing.loc[df_existing['links'] == link]

    if not row.empty:
        # Check if the price has changed
        old_price = row['price'].values[0]
        if new_price != old_price:
            # Update the price in the DataFrame
            df_existing.loc[df_existing['links'] == link, 'price'] = new_price

            # Save the updated DataFrame to the CSV file
            df_existing.to_csv(f'{csv_path}/Listings_Data_{TRANSLATED_CITY}.csv', index=False)
            print(f"Price updated for link: {link}")
            return True
        else:
            print(f"Price has not changed for link: {link}")
            return False
    else:
        print(f"Link not found in CSV file: {link}")
        return False

def send_email(updated_links):
    # Email credentials
    sender_email = "your_email@example.com"
    receiver_email = "recipient_email@example.com"
    password = "your_email_password"

    # Create the email message
    msg = MIMEText(r"The following links have updated prices:\n\n{'\n'.join(updated_links)}")
    msg['Subject'] = "Price Updates for Yad2 Listings"
    msg['From'] = sender_email
    msg['To'] = receiver_email

    # Send the email
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.starttls()
        smtp.login(sender_email, password)
        smtp.send_message(msg)
        print("Email sent successfully!")




