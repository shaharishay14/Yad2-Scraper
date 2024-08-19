from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


def detect_captcha(driver):
    try:
        # Check for reCAPTCHA v2
        if driver.find_element(By.CSS_SELECTOR, "div.g-recaptcha"):
            print("reCAPTCHA detected")
            return True
    except NoSuchElementException:
        pass

    try:
        # Check for invisible reCAPTCHA (v3)
        if driver.find_element(By.CSS_SELECTOR, "div.recaptcha-checkbox"):
            print("Invisible reCAPTCHA detected")
            return True
    except NoSuchElementException:
        pass

    try:
        # Check for hCaptcha
        if driver.find_element(By.CSS_SELECTOR, "div.h-captcha"):
            print("hCaptcha detected")
            return True
    except NoSuchElementException:
        pass

    try:
        # Generic check for captcha images
        if driver.find_element(By.XPATH, "//img[contains(@src, 'captcha')]"):
            print("CAPTCHA image detected")
            return True
    except NoSuchElementException:
        pass

    return False
