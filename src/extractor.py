import os
import requests
import shutil
from selenium import webdriver
from dotenv import load_dotenv
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
from urllib.parse import unquote


load_dotenv()

def extract_pdf():
    chromedriver_path = os.getenv("CHROMEDRIVER_PATH")

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920x1080")

    service = Service(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    base_url = "https://rbi.org.in/Scripts/NotificationUser.aspx#mainsection"
    base_data_dir = "/usr/src/app/data/"

    start_year = int(os.getenv('START_YEAR', 2024))
    year_range = int(os.getenv('YEAR_RANGE', 1))

    try:
        driver.get(base_url)

        wait = WebDriverWait(driver, 10)
        for year in range(start_year, start_year - year_range, -1):
            data_dir = os.path.join(base_data_dir, str(year))
            
            if os.path.exists(data_dir):
                print(f"Directory for year {year} already exists. Skipping...")
                continue

            os.makedirs(data_dir, exist_ok=True)

            try:
                year_button = wait.until(EC.element_to_be_clickable((By.ID, f"btn{year}")))
                year_button.click()
                wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, f'div[id="{year}"] ul')))

            except TimeoutException:
                print(f"Could not find the button for year {year} or the content took too long to load.")
                shutil.rmtree(data_dir)
                print(f"Deleted directory for year {year} due to timeout.")
                continue

            all_months_link = driver.find_elements(By.CSS_SELECTOR, f'div[id="{year}"] ul > li > a')
            if isinstance(all_months_link, list) and len(all_months_link) > 0:
                all_months_link[0].click()  
                fetch_and_download_pdfs(driver, year, data_dir)

    finally:
        driver.quit()


def fetch_and_download_pdfs(driver, year, year_dir):
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '#doublescroll > table.tablebg > tbody'))
    )

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    tbody = soup.select_one('#doublescroll > table.tablebg > tbody')
    
    for tr in tbody.find_all('tr'):
        tds = tr.find_all('td')
        if len(tds) == 2:
            announcement_name = tds[0].text.strip()
            a_tag = tds[1].find('a')
            if a_tag and 'href' in a_tag.attrs:
                pdf_url = a_tag['href']
                download_pdf(pdf_url, year_dir, announcement_name)

def download_pdf(pdf_url, year_dir, pdf_name):
    if not pdf_url.startswith('http'):
        pdf_url = 'https://rbidocs.rbi.org.in' + pdf_url
    
    # Use the provided PDF name as the filename, replacing invalid characters
    filename = f"{pdf_name}.pdf"
    filename = unquote(filename)  # Decode URL-encoded strings, if any
    # Replace any characters not allowed in file names
    for char in ['/', '\\', ':', '*', '?', '"', '<', '>', '|']:
        filename = filename.replace(char, '_')
    
    file_path = os.path.join(year_dir, filename)
    
    if not os.path.exists(file_path):
        response = requests.get(pdf_url)
        with open(file_path, 'wb') as file:
            file.write(response.content)
        print(f"Downloaded: {file_path}")
    else:
        print(f"File already exists: {file_path}")
