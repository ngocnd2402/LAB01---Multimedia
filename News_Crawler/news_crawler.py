from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import requests
from bs4 import BeautifulSoup
import csv
import re

def no_accent_vietnamese(s):
    s = re.sub(r'[àáạảãâầấậẩẫăằắặẳẵ]', 'a', s)
    s = re.sub(r'[ÀÁẠẢÃĂẰẮẶẲẴÂẦẤẬẨẪ]', 'A', s)
    s = re.sub(r'[èéẹẻẽêềếệểễ]', 'e', s)
    s = re.sub(r'[ÈÉẸẺẼÊỀẾỆỂỄ]', 'E', s)
    s = re.sub(r'[òóọỏõôồốộổỗơờớợởỡ]', 'o', s)
    s = re.sub(r'[ÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠ]', 'O', s)
    s = re.sub(r'[ìíịỉĩ]', 'i', s)
    s = re.sub(r'[ÌÍỊỈĨ]', 'I', s)
    s = re.sub(r'[ùúụủũưừứựửữ]', 'u', s)
    s = re.sub(r'[ƯỪỨỰỬỮÙÚỤỦŨ]', 'U', s)
    s = re.sub(r'[ỳýỵỷỹ]', 'y', s)
    s = re.sub(r'[ỲÝỴỶỸ]', 'Y', s)
    s = re.sub(r'[Đ]', 'D', s)
    s = re.sub(r'[đ]', 'd', s)
    return s

def jaccard_similarity(str1, str2):
    str1=str1.lower()
    str2=str2.lower()
    str1 = no_accent_vietnamese(str1)
    str2 = no_accent_vietnamese(str2)
    set1 = set(str1.split())
    set2 = set(str2.split())
    intersection = set1.intersection(set2)
    union = set1.union(set2)
    return len(intersection) / len(union)

def crawl_articles(category, nums, startPage=1, recursion=0):
    categories =['thoi su', 'goc nhin', 'the gioi', 'kinh doanh', 'khoa hoc', 'giai tri', 'the thao', 'phap luat',
             'giao duc', 'suc khoe', 'doi song', 'du lich']
    max_ratio = max([jaccard_similarity(item, category) for item in categories])
    for item in categories:
        ratio = jaccard_similarity(item, category)
        if ratio == max_ratio:
            category = item
    # Navigate to the category page
    url = 'https://vnexpress.net/'
    search_url = url + category.replace(' ', '-') + '-p' + str(startPage)
    # Tải trang và sử dụng BeautifulSoup để phân tích cú pháp HTML
    try:
        page = requests.get(search_url)
        page.raise_for_status()
        soup = BeautifulSoup(page.content, 'html.parser')
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error occurred: {e}")
        return []

    # Tìm các thẻ HTML chứa thông tin về bài báo
    article_titles = soup.find_all('h3', {'class': 'title-news'})
    # Duyệt qua các thẻ và trích xuất thông tin về bài báo
    articles = []
    for item in article_titles:
        title = item.find("a").get("title")
        link = item.find("a").get("href")
        driver = webdriver.Chrome() 
        driver.get(link)
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "content-comment")))
        except TimeoutException:
            print(f"Timed out waiting for page to load: {link}")
            continue
        comment_elements = driver.find_elements(By.CLASS_NAME, "full_content")
        comments = []
        for comment in comment_elements:
            cmt = comment.text
            comments.append(cmt)
        # Append the article to the list
        articles.append({'title': title, 'link': link, 'comment': comments})        
        if len(articles) >= nums or recursion >= 10 :
            return articles[:nums]
        
    # Nếu chưa đủ, tiếp tục đệ quy tới trang tiếp theo
    if len(articles) < nums and recursion < 10 :
        return articles + crawl_articles(category, nums - len(articles), startPage+1, recursion+1)
        

articles = crawl_articles('thời sự',2)
print(articles)
