import base64
from io import BytesIO
import os
import requests
from bs4 import BeautifulSoup
import urllib.parse
import os
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from loguru import logger
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from PIL import Image

class GoogleImageCrawler:
    def __init__(self, storage):
        self.storage = storage
        self.root_dir = storage['root_dir']
        if not os.path.exists(self.root_dir):
            os.makedirs(self.root_dir)
        self.chrome_options = Options()
        self.chrome_options.add_argument("--incognito")
        self.driver = webdriver.Chrome(options=self.chrome_options)

    def crawl(self, keyword, max_num=5):
        search_url = f"https://www.google.com/search?hl=vi&q={urllib.parse.quote(keyword)}&tbm=isch"
        
        self.driver.get(search_url)
        time.sleep(3)  # Đợi trang tải
        page = BeautifulSoup(self.driver.page_source, features="html.parser")

        deals = page.find_all("div", {"data-attrid":"images universal"})
        img_urls = []
        for i in range(max_num):
            img_url = deals[i].find_all("img")[0]["src"]
            print(img_url)
            img_urls.append(img_url)
        
        print(img_urls)
        self.download_images(img_urls)

    from PIL import Image

    def resize_and_save_image(self, img_data, img_name, target_size):
        """Resize the image and save it to the specified path."""
        with Image.open(BytesIO(img_data)) as img:
            # Resize the image while maintaining aspect ratio
            img.thumbnail(target_size, Image.LANCZOS)

            # Create a new blank image with the desired size
            new_image = Image.new("RGB", target_size, (255, 255, 255))  # White background

            # Calculate position to center the image
            x = (target_size[0] - img.size[0]) // 2
            y = (target_size[1] - img.size[1]) // 2

            # Paste the resized image onto the new image
            new_image.paste(img, (x, y))

            # Save the resized image
            new_image.save(img_name)

        print(f"Downloaded and resized {img_name}")

    def download_images(self, img_urls, target_size=(600, 400)):
        for idx, img_url in enumerate(img_urls):
            try:
                if img_url.startswith('data:image'):
                    # Handle base64 encoded image
                    header, base64_data = img_url.split(',', 1)
                    img_data = base64.b64decode(base64_data)
                    img_name = os.path.join(self.root_dir, f'image_{idx + 1}.png')
                    with open(img_name, 'wb') as img_file:
                        img_file.write(img_data)
                        print(f"Downloaded {img_name}")
                else:
                    # Handle normal image URL
                    img_data = requests.get(img_url).content
                    img_name = os.path.join(self.root_dir, f'image_{idx + 1}.png')
                    with open(img_name, 'wb') as img_file:
                        img_file.write(img_data)
                        print(f"Downloaded {img_name}")

                # Resize and save the image
                # self.resize_and_save_image(img_data, img_name, target_size)

            except Exception as e:
                print(f"Could not download image {img_url}: {e}")

# Example usage
# if __name__ == "__main__":
#     google_crawler = GoogleImageCrawler(storage={'root_dir': 'image-travel/hotels'})
#     google_crawler.crawl(keyword='hanoi', max_num=5)