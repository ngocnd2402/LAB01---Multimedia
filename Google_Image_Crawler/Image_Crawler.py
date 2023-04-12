import os
import io
import time
import requests
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By

def get_images_from_google(wd, delay, max_images, url):
    def scroll_down(wd):
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(delay)

    wd.get(url)
    image_urls = set()
    image_count = 0
    while image_count < max_images:
        scroll_down(wd)
        thumbnails = wd.find_elements(By.CLASS_NAME, "Q4LuWd")

        for thumbnail in thumbnails[len(image_urls):]:
            try:
                thumbnail.click()
                time.sleep(delay)
            except:
                continue

            images = wd.find_elements(By.CLASS_NAME, "r48jcc")
            for image in images:
                src = image.get_attribute('src')
                if src and 'http' in src and src not in image_urls:
                    image_urls.add(src)
                    image_count += 1
                    break

            if image_count >= max_images:
                break

    return image_urls

def download_image(down_path, url, file_name, image_type='JPEG', max_retries=5, verbose=True):
    retry_count = 0
    while retry_count < max_retries:
        try:
            img_content = requests.get(url).content
            img_file = io.BytesIO(img_content)
            image = Image.open(img_file)
            # Chuyển chế độ từ RGBA sang RGB
            image = image.convert('RGB')
            file_pth = os.path.join(down_path, file_name)

            with open(file_pth, 'wb') as file:
                image.save(file, image_type)

            if verbose:
                print(f'The image {file_name} downloaded successfully.')
            
            # Exit the loop if image was downloaded successfully
            break
        
        except Exception as e:
            print(f'Unable to download image {file_name} due to the following error:\n {str(e)}')
            retry_count += 1
            if retry_count == max_retries:
                print(f'Maximum number of retries reached. Skipping image {file_name}.')





if __name__ == '__main__':
    PATH = r"../GG_Image_Crawler/chromedriver/chromedriver.exe"
    wd = webdriver.Chrome(executable_path=PATH)

    queries = ['Kratos']
    google_urls = ['https://www.google.com/search?q={}&tbm=isch'.format(q) for q in queries]
    labels = ['Kratos']
    player_path = r'../Google Image Crawler/images'

    if len(google_urls) != len(labels):
        raise ValueError('The length of the url list does not match the labels list.')
    
    for lbl in labels:
        dir_path = os.path.join(player_path, lbl)
        if not os.path.exists(dir_path):
            print(f'Making directory: {str(lbl)}')
            os.makedirs(dir_path)

    TOTAL_NUMBER_OF_EXAMPLES = 10
    for url_current, lbl in zip(google_urls, labels):
        urls = get_images_from_google(wd, 0.05, TOTAL_NUMBER_OF_EXAMPLES, url_current)
        for i, url in enumerate(urls):
            download_image(down_path=f'../Google Image Crawler/images/{lbl}/', 
                        url=url, 
                        file_name=str(i+1)+ '.jpg',
                        verbose=True) 
    wd.quit()