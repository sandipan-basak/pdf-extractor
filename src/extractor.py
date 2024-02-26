import os
import requests
from selenium import webdriver
from dotenv import load_dotenv
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

load_dotenv()

def extract_pdf():
    chromedriver_path = os.getenv("CHROMEDRIVER_PATH")

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--enable-logging")
    chrome_options.add_argument("--v=1")

    service = Service(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get("https://rbi.org.in/Scripts/NotificationUser.aspx#mainsection")

        # Example of clicking an accordion for the year 2024
        wait = WebDriverWait(driver, 10)
        year_2024_button = wait.until(EC.element_to_be_clickable((By.ID, "btn2024")))
        year_2024_button.click()

        # Wait for the page content to load after clicking
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div[id="2024"] ul')))

        # html = driver.page_source
        # soup = BeautifulSoup(html, 'html.parser')

        year_range = 1

        for year in range(2024, 2024 - year_range, -1):
            all_months_link = driver.find_elements(By.CSS_SELECTOR, 'div[id="2024"] ul > li > a')

            if isinstance(all_months_link, list) and len(all_months_link) > 0:
                all_months_link[0].click()  # Click the first month link
                fetch_and_download_pdfs(driver, year)

    finally:
        driver.quit()


def fetch_and_download_pdfs(driver, year):
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '#doublescroll > table.tablebg > tbody'))
    )

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    tbody = soup.select_one('#doublescroll > table.tablebg > tbody')
    
    # Ensure the directory for the year exists
    year_dir = f"/usr/src/app/data/{year}"
    os.makedirs(year_dir, exist_ok=True)
    
    for tr in tbody.find_all('tr'):
        tds = tr.find_all('td')
        if len(tds) == 2:
            a_tag = tds[1].find('a')
            if a_tag and 'href' in a_tag.attrs:
                pdf_url = a_tag['href']
                download_pdf(pdf_url, year_dir)


def download_pdf(pdf_url, year_dir):
    if not pdf_url.startswith('http'):
        pdf_url = 'https://rbidocs.rbi.org.in' + pdf_url
    
    response = requests.get(pdf_url)
    filename = pdf_url.split('/')[-1] if '/' in pdf_url else 'downloaded_file.pdf'
    
    # Adjust the path to include the year directory
    file_path = os.path.join(year_dir, filename)
    
    # Check if the file already exists before downloading
    if not os.path.exists(file_path):
        with open(file_path, 'wb') as file:
            file.write(response.content)
        print(f"Downloaded: {file_path}")
    else:
        print(f"File already exists: {file_path}")
