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
from News_Crawler.news_crawler import crawl_articles
import json
from fastapi.responses import JSONResponse
from urllib.parse import urlparse
import natsort
from Facebook_Crawler.fb_crawler import get_amount_of_comments, get_content_comment, login_facebook, init_driver
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from requests_html import HTMLSession,AsyncHTMLSession
from facebook_scraper import get_posts
from bs4 import BeautifulSoup

app = FastAPI()
app.mount("/static", StaticFiles(directory=r"C:\Users\dac\Crawler\Lab01_Crawler\static"), name="static")
# Định nghĩa API endpoint tới trang chủ
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
        with open('./static/index.html') as f:
            content = f.read()
        return content


# BEGIN PAPER CRAWLER
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

# BEGIN GOOGLE IMAGE CRAWLER
@app.get("/googleImageCrawler", response_class=HTMLResponse)
async def paper_index():
    with open('./static/GG_Image/google_main.html') as f:
        content = f.read()
    return content

@app.get("/googlecrawl")
async def crawl_images(query:str, total:int):
    wd = webdriver.Chrome()
    google_urls = ['https://www.google.com/search?q={}&tbm=isch'.format(query)]
    image_urls = set()
    for url in google_urls:
        urls = get_images_from_google(wd, 0.05, total, url)
        image_urls |= urls
    wd.quit()

    # Create a temporary directory to store the images
    with tempfile.TemporaryDirectory() as temp_dir:
        for i, url in enumerate(image_urls):
            file_name = f'{i + 1}.jpg'
            file_path = os.path.join(temp_dir, file_name)
            # Download the image and save it to the temporary directory
            with urllib.request.urlopen(url) as response:
                img_content = response.read()
                with open(file_path, 'wb') as f:
                    f.write(img_content)
            time.sleep(0.5)
            # Open the image with PIL and resize it to a desired size
            img = Image.open(file_path)
            img = img.resize((img.width * 3, img.height * 3))
            img.save(file_path)
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
# END GOOGLE IMAGE CRAWLER  

# BEGIN NEWS CRAWLER
# Định nghĩa API endpoint cho việc crawl thông tin bài báo
@app.get("/newsCrawler", response_class=HTMLResponse)
async def paper_index():
    with open('./static/news_crawler/news_main.html', 'r',  encoding='utf-8') as f:
        content = f.read()
    return content
from fastapi.responses import Response

@app.get("/newscrawl")
async def crawl(base_category: str, nums:int):
    articles = await crawl_articles(base_category, nums)  # await the coroutine object
    output = []
    for article in articles:
        output.append({'title': article['title'], 'link': article['link'], 'comments': article['comments']})
    json_output = json.dumps(output, indent=4, ensure_ascii=False)
    response = Response(content=json_output, media_type="application/json; charset=utf-8")
    response.headers["Content-Disposition"] = "attachment; filename=newspapers.json"
    return response
# END NEWS CRAWLER


# BEGIN FB CRAWLER
@app.get("/facebookCrawler", response_class=HTMLResponse)
async def paper_index():
    with open('./static/FB_crawler/fb_main.html', 'r',  encoding='utf-8') as f:
        content = f.read()
    return content


@app.get("/fbcrawl")
async def crawl_fb(url: str, num_posts: int):
    url = url.split('/')[-1]
    browser = init_driver()
    #login facebook
    login_facebook(browser,'','')
    browser.get(url)
    soup = BeautifulSoup(browser.page_source, "html.parser")
    #extract elements contain post_id
    items = soup.findAll('div', id='recent')
    #extract post_id
    postID = []
    for item in items:
        objects = item.findAll('article', class_="dj ft fu")
        for object in objects:
            object=object.attrs["data-ft"]
            post_id = object.split('"post_id":"')[1].split('","')[0]
            postID.append(post_id)
        if len(postID)>= num_posts:
            break
        else:
            continue
    post = []
    #extract comments in each post
    for post_id in postID:
        comments = get_amount_of_comments(browser, post_id, [])
        post.append({'post_id': post_id, 'comment': comments})
        if (len(post) >= num_posts):
            return post[:num_posts]
        
    if (len(post) >= num_posts):
        return post[:num_posts]
    else:
        next_url = soup.findAll('div', class_='i')
        url = ''
        for item in next_url:
            next= item.find('a')
            if next.text == 'Hiển thị thêm':
                url = next.attrs["href"]
                break
            else:
                continue             
        return post + crawl_fb( "https://mbasic.facebook.com"+ url,num_posts - len(post))
    
# END FBS CRAWLER


if __name__ == "__main__":
    uvicorn.run('app:app', host="127.0.0.1", port=5000, reload = True)