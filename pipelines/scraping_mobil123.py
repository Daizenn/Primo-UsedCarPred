import os
import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from bs4 import BeautifulSoup

# Selenium WebDriver configuration
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument('--disable-dev-shm-usage')
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

# Install ChromeDriver using webdriver-manager
chrome_driver_path = ChromeDriverManager().install()

# Correct the path to point to chromedriver.exe
# This assumes chromedriver.exe is in the same directory as the THIRD_PARTY_NOTICES.chromedriver
chrome_driver_executable_path = os.path.join(os.path.dirname(chrome_driver_path), 'chromedriver.exe')

# Debugging: Check ChromeDriver path
print(f"ChromeDriver executable path: {chrome_driver_executable_path}")

# Debugging: Ensure ChromeDriver exists and is executable
assert os.path.exists(chrome_driver_executable_path), "ChromeDriver not found"
assert os.access(chrome_driver_executable_path, os.X_OK), "ChromeDriver is not executable"

# Initialize ChromeService with the correct ChromeDriver path
s = ChromeService(chrome_driver_executable_path)
driver = webdriver.Chrome(service=s, options=options)

def scrape_key_details(soup):
    car_data = {
        'Kondisi': "N/A",
        'Tahun Kendaraan': "N/A",
        'Kilometer': "N/A",
        'Warna': "N/A",
        'Cakupan mesin': "N/A",
        'Transmisi': "N/A",
        'Penumpang': "N/A"
    }
    specs = soup.select(".c-key-details__item")
    for spec in specs:
        try:
            key = spec.select_one("span.u-text-7").text.strip()
            value = spec.select_one("span.u-text-bold").text.strip()
            if key in car_data:
                car_data[key] = value
        except Exception as e:
            print(f"Error parsing key detail: {e}")
            continue
    return car_data

def scrape_specifications(soup):
    additional_data = {
        'Pintu': "N/A",
        'Dirakit': "N/A",
        'Tipe Bahan Bakar': "N/A"
    }
    spec_tab = soup.select_one("#tab-specifications")
    if spec_tab:
        spec_items = spec_tab.select(".u-border-bottom.u-padding-ends-xs.u-flex.u-flex--justify-between")
        for item in spec_items:
            try:
                key = item.select("span")[0].text.strip()
                value = item.select("span")[1].text.strip()
                if key in additional_data:
                    additional_data[key] = value
            except Exception as e:
                print(f"Error parsing specification: {e}")
                continue
    return additional_data

def scrape_page(page_number, data_list):
    url = f'https://www.mobil123.com/mobil-dijual/indonesia?type=used&page_number={page_number}&page_size=25'
    driver.get(url)
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h2.listing__title a"))
        )
    except TimeoutException:
        print(f"TimeoutException at page {page_number}")
        return

    car_elements = driver.find_elements(By.CSS_SELECTOR, "h2.listing__title a")
    car_urls = [car.get_attribute('href') for car in car_elements]

    for car_url in car_urls:
        driver.get(car_url)
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "h1.u-text-bold"))
            )
        except TimeoutException:
            print(f"TimeoutException at car URL: {car_url}")
            continue

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        car_details = {}

        try:
            car_details['Title'] = soup.select_one("h1.u-text-bold").text.strip()
        except Exception as e:
            print(f"Error parsing title: {e}")
            car_details['Title'] = "N/A"

        try:
            car_details['Harga'] = soup.select_one("div.listing__price.u-text-4.u-text-bold").text.strip()
        except Exception as e:
            print(f"Error parsing price: {e}")
            car_details['Harga'] = "N/A"

        # Scraping key details
        key_details = scrape_key_details(soup)
        car_details.update(key_details)

        # Scraping additional specifications
        specifications = scrape_specifications(soup)
        car_details.update(specifications)

        data_list.append(car_details)
        time.sleep(1)

def scheduled_scraping_job():
    data_list = []  # Reset data list
    for page in range(1, 2):  # Adjust range as needed
        scrape_page(page, data_list)
        time.sleep(5)
    
    if data_list:
        # Ensure the 'data' folder exists
        if not os.path.exists('data'):
            os.makedirs('data')
        
        file_path = os.path.join('data', 'car_data.csv')
        file_exists = os.path.isfile(file_path)

        keys = data_list[0].keys()
        with open(file_path, 'a', newline='', encoding='utf-8') as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=keys)
            if not file_exists:
                dict_writer.writeheader()
            dict_writer.writerows(data_list)

# Close the driver when the program ends
def cleanup_driver():
    driver.quit()

import atexit
atexit.register(cleanup_driver)
