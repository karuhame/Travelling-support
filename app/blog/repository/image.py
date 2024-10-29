from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from blog.hashing import Hash
import crawlData


import base64
import os
import urllib.parse
import time
import requests
from io import BytesIO
from PIL import Image
from azure.storage.blob import BlobServiceClient
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup



import os
from dotenv import load_dotenv

# Tải các biến môi trường từ tệp .env
load_dotenv()
AZURE_CONNECTION_STRING = os.getenv('AZURE_CONNECTION_STRING')



class ImageHandler:
    def __init__(self, root_dir= 'travel-image', container_name = 'travel-image'):
        self.connection_string = AZURE_CONNECTION_STRING
        self.container_name = container_name
        self.root_dir = root_dir
        if not os.path.exists(self.root_dir):
            os.makedirs(self.root_dir)
        self.chrome_options = Options()
        self.chrome_options.add_argument("--incognito")
        self.driver = webdriver.Chrome(options=self.chrome_options)

    def crawl(self, keyword, max_num=5):
        """Thu thập hình ảnh từ Google dựa trên từ khóa."""
        search_url = f"https://www.google.com/search?hl=vi&q={urllib.parse.quote(keyword)}&tbm=isch"
        
        self.driver.get(search_url)
        time.sleep(3)  # Đợi trang tải
        page = BeautifulSoup(self.driver.page_source, features="html.parser")

        deals = page.find_all("div", {"data-attrid": "images universal"})
        img_urls = []
        for i in range(min(max_num, len(deals))):
            img_url = deals[i].find_all("img")[0]["src"]
            img_urls.append(img_url)

        # print("Collected image URLs:", img_urls)
        return img_urls

    def download_url(self, img_url, file_name=None):
        try:
            save_dir = self.root_dir  # Sử dụng self.root_dir
            
            if file_name:
                dir_name = os.path.dirname(file_name)
                full_dir_path = os.path.join(save_dir, dir_name)
                
                # Tạo thư mục nếu chưa tồn tại
                if not os.path.exists(full_dir_path):
                    os.makedirs(full_dir_path)
            
            if img_url.startswith('data:image'):
                # Xử lý hình ảnh mã hóa base64
                header, base64_data = img_url.split(',', 1)
                img_data = base64.b64decode(base64_data)
            else:
                # Xử lý URL hình ảnh bình thường
                img_data = requests.get(img_url).content

            img_file_name = os.path.join(save_dir, file_name)
            with open(img_file_name, 'wb') as img_file:
                img_file.write(img_data)
                print(f"Downloaded {img_file_name}")
            return img_file_name
        except Exception as e:
            print(f"Could not download image {img_url}: {e}")
    def download(self, img_urls, dir=None):
        """Tải xuống hình ảnh từ danh sách URL."""
        downloaded_images = []
        
        # Sử dụng dir nếu được cung cấp, nếu không sử dụng root_dir
        save_dir = dir if dir else self.root_dir
        
        # Tạo thư mục nếu chưa tồn tại
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        for idx, img_url in enumerate(img_urls):
            try:
                if img_url.startswith('data:image'):
                    # Xử lý hình ảnh mã hóa base64
                    header, base64_data = img_url.split(',', 1)
                    img_data = base64.b64decode(base64_data)
                else:
                    # Xử lý URL hình ảnh bình thường
                    img_data = requests.get(img_url).content

                img_name = os.path.join(save_dir, f'image_{idx + 1}.png')
                with open(img_name, 'wb') as img_file:
                    img_file.write(img_data)
                    print(f"Downloaded {img_name}")
                    downloaded_images.append(img_name)

            except Exception as e:
                print(f"Could not download image {img_url}: {e}")

        print(downloaded_images)
        return downloaded_images
    
    def upload_to_azure(self, img_file_name, blob_name_prefix):
        """Tải lên hình ảnh lên Azure Blob Storage."""
        connection_string = self.connection_string
        container_name = self.container_name

        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_client = blob_service_client.get_container_client(container_name)
        blob_client = container_client.get_blob_client(blob_name_prefix)
        with open(img_file_name, "rb") as data:
            blob_client.upload_blob(data, overwrite=True, content_type='image/png')
            print(f"Uploaded {img_file_name} to Azure as {blob_name_prefix}")

    def get_image_url(self, blob_name_prefix, img_file_name):
        """Lấy URL của hình ảnh từ Azure Blob Storage."""
        account_name = self.connection_string.split(';')[1].split('=')[1]  # Lấy tên tài khoản từ chuỗi kết nối
        container_name = self.container_name

        # Xây dựng và trả về URL của blob
        url = f"https://{account_name}.blob.core.windows.net/{container_name}/{blob_name_prefix}/{img_file_name}"
        return url

    def download_and_upload(self, id, img_urls, blob_name_prefix, target_size=(600, 400)):
        """Tải xuống hình ảnh và tải lên Azure Blob Storage."""
        downloaded_images = self.download(img_urls)

        for idx, img_name in enumerate(downloaded_images):
            try:
                # Resize and save the image
                # self.resize_and_save_image(img_name, target_size)

                # Tải lên Azure với tên blob chỉ định
                blob_name = f"{blob_name_prefix}/id_{idx + 1}.png"
                self.upload_to_azure(img_name, blob_name)

            except Exception as e:
                print(f"Could not upload image {img_name}: {e}")

    def resize_and_save_image(self, img_name, target_size):
        """Thay đổi kích thước và lưu hình ảnh."""
        with Image.open(img_name) as img:
            img.thumbnail(target_size, Image.LANCZOS)
            new_image = Image.new("RGB", target_size, (255, 255, 255))
            x = (target_size[0] - img.size[0]) // 2
            y = (target_size[1] - img.size[1]) // 2
            new_image.paste(img, (x, y))
            new_image.save(img_name)

        print(f"Resized and saved {img_name}")



    def close(self):
        """Đóng trình duyệt Selenium."""
        self.driver.quit()

    @staticmethod
    def crawl_image(db: Session, city = None, destination = None):
            
        from blog import models, schemas
            
        if city:
            obj = city
            google_crawler = crawlData.GoogleImageCrawler()
            
            download_links = google_crawler.crawl(keyword=f'Du lịch {obj.name}', max_num=3)
            google_crawler.close()
            
            for img_link in download_links:
                img = models.Image(
                    city_id = obj.id
                )
                db.add(img)
                db.commit()
                db.refresh(img)
                # import pdb; pdb.set_trace()
                img_file_name = google_crawler.download_url(img_url=img_link, file_name=f"cities/{obj.id}/{img.id}.png")
                google_crawler.upload_to_azure(img_file_name, blob_name_prefix=f"cities/{obj.id}/{img.id}.png" )
                url = google_crawler.get_image_url(blob_name_prefix=f"cities/{obj.id}", img_file_name=f"{img.id}.png")
                
                img.url = url
                db.add(img)
                db.commit()
                db.refresh(img)
        else:
            obj = destination
            google_crawler = crawlData.GoogleImageCrawler()
            
            download_imgs = google_crawler.crawl(keyword=f'Du lịch {obj.name}', max_num=3)
            google_crawler.close()
            
            for img_link in download_imgs:
                img = models.Image(
                    destination_id = obj.id
                )
                db.add(img)
                db.commit()
                db.refresh(img)
                
                img_file_name = google_crawler.download_url(img_url=img_link, file_name=f"destinations/{obj.id}/{img.id}.png")
                google_crawler.upload_to_azure(img_file_name, blob_name_prefix=f"destinations/{obj.id}/{img.id}.png" )
                url = google_crawler.get_image_url(blob_name_prefix=f"destinations/{obj.id}", img_file_name=f"{img.id}.png")
                
                img.url = url
                db.add(img)
                db.commit()
                db.refresh(img)
        
    
    def fake_db_destination(self, db: Session, destination=None, fake_dir ="travel-image/destinations/fake/"):
        from blog import models
        import glob

        # Lấy tất cả các file hình ảnh trong fake_dir
        image_files = glob.glob(os.path.join(fake_dir, '*'))  # Lấy tất cả file trong thư mục

        for img_file_path in image_files:
            try:
                # Tạo đối tượng Image mới
                img = models.Image(
                    destination_id=destination.id
                )
                db.add(img)  # Thêm vào session
                db.commit()  # Lưu lại để lấy id của image                        
                db.refresh(img)  # Làm mới đối tượng để lấy id

                # Tải lên hình ảnh lên Azure
                img_file_name = img_file_path  # Đường dẫn file hình ảnh
                blob_name = f"destinations/{destination.id}/{img.id}.png"  # Tên blob
                self.upload_to_azure(img_file_name, blob_name)  # Tải lên Azure

                # Lấy URL hình ảnh từ Azure
                url = self.get_image_url(blob_name_prefix=f"destinations/{destination.id}", img_file_name=f"{img.id}.png")
                
                # Gán URL cho đối tượng hình ảnh
                img.url = url
                db.add(img)  # Thêm lại vào session
                db.commit()  # Lưu lại
                db.refresh(img)  # Làm mới đối tượng
            except Exception as e:
                print(f"Could not process image {img_file_path}: {e}")
    def fake_db_review(self, db: Session, review=None, fake_dir ="travel-image/destinations/fake/"):
        from blog import models
        import glob

        # Lấy tất cả các file hình ảnh trong fake_dir
        image_files = glob.glob(os.path.join(fake_dir, '*'))  # Lấy tất cả file trong thư mục

        for img_file_path in image_files:
            try:
                # Tạo đối tượng Image mới
                img = models.Image(
                    review_id=review.id
                )
                db.add(img)  # Thêm vào session
                db.commit()  # Lưu lại để lấy id của image
                db.refresh(img)  # Làm mới đối tượng để lấy id

                # Tải lên hình ảnh lên Azure
                img_file_name = img_file_path  # Đường dẫn file hình ảnh
                blob_name = f"reviews/{review.id}/{img.id}.png"  # Tên blob
                self.upload_to_azure(img_file_name, blob_name)  # Tải lên Azure

                # Lấy URL hình ảnh từ Azure
                url = self.get_image_url(blob_name_prefix=f"reviews/{review.id}", img_file_name=f"{img.id}.png")
                
                # Gán URL cho đối tượng hình ảnh
                img.url = url
                db.add(img)  # Thêm lại vào session
                db.commit()  # Lưu lại
                db.refresh(img)  # Làm mới đối tượng
            except Exception as e:
                print(f"Could not process image {img_file_path}: {e}")

    

    