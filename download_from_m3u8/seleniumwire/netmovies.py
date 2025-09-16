import subprocess
import logging
import requests
import json
from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("download_video.log"),
        logging.StreamHandler()
    ]
)

def load_settings(file_path="settings.json"):
    with open(file_path, 'r') as file:
        settings = json.load(file)
    return settings

def get_m3u8_url(website_url, button_class_name):
    try:
        logging.info(f"Opening the website: {website_url}")

        # Set up Chrome options and start the browser
        chrome_options = webdriver.ChromeOptions()
        #chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")

        driver = webdriver.Chrome(seleniumwire_options={}, options=chrome_options)

        driver.get(website_url)

        # Save the initial page source to check if the page loaded correctly
        with open("page_source_initial.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)

        logging.info("button_class_name: " + button_class_name)

        # Wait for the play button to be clickable and then click it
        play_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, button_class_name))
        )

        # Save the page source just before clicking the play button
        with open("page_source_before_click.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)

        try:
            play_button.click()
            logging.info("Play button clicked successfully.")
        except Exception as e:
            logging.error(f"Error clicking the play button: {e}")

        logging.info("Play button clicked, waiting for m3u8 URL to load...")

        # Wait for a short period to allow network traffic to generate
        time.sleep(20)

        # Save the page source after the button click
        with open("page_source_after_click.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)

        # Retrieve the m3u8 URL from the network logs
        m3u8_url = None
        for request in driver.requests:
            if request.response and ".m3u8" in request.url:
                m3u8_url = request.url
                break

        driver.quit()

        if m3u8_url:
            logging.info(f"m3u8 URL found: {m3u8_url}")
        else:
            logging.error("m3u8 URL not found.")

        return m3u8_url

    except Exception as e:
        logging.error(f"An error occurred while fetching the m3u8 URL: {e}")
        return None
    
def fetch_headers(url):
    try:
        logging.info(f"Fetching headers from {url}")
        response = requests.get(url)
        headers = response.headers
        logging.info(f"Headers fetched successfully from {url}")
        return headers
    except requests.RequestException as e:
        logging.error(f"An error occurred while fetching headers: {e}")
        return None

def download_hls_stream(manifest_url, headers, output_filename):
    ffmpeg_command = [
        'ffmpeg',
        '-headers', '\r\n'.join([f'{key}: {value}' for key, value in headers.items()]),
        '-i', manifest_url,
        '-c', 'copy',
        output_filename
    ]
    
    try:
        logging.info(f"Starting download from {manifest_url}")
        subprocess.run(ffmpeg_command, check=True)
        logging.info(f"Video downloaded successfully and saved as {output_filename}")
    except subprocess.CalledProcessError as e:
        logging.error(f"An error occurred while downloading the video: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    settings = load_settings()

    website_url = settings.get("website_url")
    output_filename = settings.get("output_filename")
    button_class_name = settings.get("button_class_name")

    if not website_url:
        logging.error("The website URL cannot be empty.")
    elif not output_filename:
        logging.error("The output filename cannot be empty.")
    else:
        # Step 1: Get the m3u8 URL by automating the browser
        manifest_url = get_m3u8_url(website_url, button_class_name)
        
        if manifest_url:
            # Step 2: Fetch headers dynamically from the website
            headers = fetch_headers(website_url)
            if headers:
                # Step 3: Download the video stream using the m3u8 URL and headers
                download_hls_stream(manifest_url, headers, output_filename)
            else:
                logging.error("Failed to fetch headers, cannot proceed with the download.")
        else:
            logging.error("Failed to retrieve the m3u8 URL, cannot proceed with the download.")
