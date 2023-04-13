from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import csv


# Create a new instance of the Chrome driver


def crawl_articles(category, nums, startPage=1, count_recursion = 0):
    # Navigate to the category page
    driver = webdriver.Chrome()
    url = 'https://vnexpress.net/'
    driver.get(url + category.replace(' ', '-') + '-p' + str(startPage))
    # Wait for the page to load and display the news items
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "title-news")))
    except TimeoutException:
        print("Timed out waiting for page to load")
        driver.quit()

    # Get the list of news items
    news_items = driver.find_elements(By.TAG_NAME, "h3")

    # Loop through each news item and extract the titles, links, and comments
    articles = []
    links = []
    titles = []
    for item in news_items:
        # Get the link to the news article
        link = item.find_element(By.TAG_NAME, "a").get_attribute("href")
        links.append(link)
        # Get the title of the news article
        title = item.find_element(By.TAG_NAME, "a").text
        titles.append(title)
    if len(links)>=nums:
        links = links[:nums]
        titles = titles[:nums]
   
    # Open the news article and extract the comment
    comments = []
    for i in range(0,nums):
        driver.get(links[i])
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "content-comment")))
        except TimeoutException:
            print(f"Timed out waiting for page to load: {link}")
            continue
        comment_elements = driver.find_elements(By.CLASS_NAME, "full_content")
        for comment in comment_elements:
            cmt = comment.text
            comments.append(cmt)
        articles.append({'title': titles[i], 'link': links[i], 'comment': comments})
    # Append the article to the list
    if len(articles) >= nums or count_recursion == 15:
        return articles[:nums]
    # Nếu chưa đủ, tiếp tục đệ quy tới trang tiếp theo
    else:
        return articles + crawl_articles(category, nums - len(articles), startPage + 1, count_recursion + 1)    



