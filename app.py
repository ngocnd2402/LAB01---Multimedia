from Paper_Crawler.Paper_Crawler import crawl_acm
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI,Request
from fastapi.responses import HTMLResponse
import uvicorn
import csv 
import io
from fastapi.responses import StreamingResponse,FileResponse
import zipfile 
import os
import time
import requests
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from Google_Image_Crawler.Image_Crawler import get_images_from_google
import urllib.request
import tempfile

app = FastAPI()
app.mount("/static", StaticFiles(directory=r"D:\UIT\Năm 2\Kỳ 4\Tính toán đa phương tiện\Lab\Lab01_Crawler\static"), name="static")
# Định nghĩa API endpoint tới trang chủ
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
        with open('./static/index.html') as f:
            content = f.read()
        return content


# PAPER CRAWLER
@app.get("/paperCrawler", response_class=HTMLResponse)
async def paper_index():
    with open('./static/paper_crawler/paper_main.html') as f:
        content = f.read()
    return content
@app.get("/papercrawl")
async def crawl(author_name: str, num_papers: int):
    papers = crawl_acm(author_name, num_papers=num_papers, startPage=0, count_recursion=0)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Title', 'Author', 'Public Date', 'DOI'])
    for paper in papers:
        writer.writerow([paper['title'], ', '.join(paper['author']), paper['Public Date'], paper['DOI']])
    response = StreamingResponse(iter([output.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=papers.csv"
    return response
# END PAPER CRAWLER

# GOOGLE IMAGE CRAWLER
@app.get("/googleImageCrawler", response_class=HTMLResponse)
async def paper_index():
    with open('./static/GG_Image/google_main.html') as f:
        content = f.read()
    return content

@app.get("/googlecrawl")
async def crawl_images(query:str, total:int):
    PATH = r"./GG_Image_Crawler/chromedriver/chromedriver.exe"
    wd = webdriver.Chrome(executable_path=PATH)

    google_urls = ['https://www.google.com/search?q={}&tbm=isch'.format(query)]
    image_urls = set()
    for url in google_urls:
        urls = get_images_from_google(wd, 0.05, total, url)
        image_urls |= urls
    wd.quit()

    # Create a temporary directory to store the images
    with tempfile.TemporaryDirectory() as temp_dir:
        for i, url in enumerate(image_urls):
            file_name = str(i + 1) + '.jpg'
            file_path = os.path.join(temp_dir, file_name)
            # Download the image and save it to the temporary directory
            with urllib.request.urlopen(url) as response:
                img_content = response.read()
                with open(file_path, 'wb') as f:
                    f.write(img_content)

        # Create a zip file from the temporary directory
        zip_path = os.path.join(tempfile.gettempdir(), 'images.zip')
        with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zip_file:
            for root, dirs, files in os.walk(temp_dir):
                # Sort the list of files
                files = sorted(files, key=lambda x: int(x.split('.')[0]))
                for file in files:
                    file_path = os.path.join(root, file)
                    zip_file.write(file_path, file)

        # Prepare the response and return it
        response = FileResponse(zip_path, media_type='application/octet-stream', filename='images.zip')
        return response

if __name__ == "__main__":
    uvicorn.run('app:app', host="127.0.0.1", port=8000, reload = True)