from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from blog.hashing import Hash
import crawlData


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
                destinat_id = obj.id
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
    
    
    
    
    

    