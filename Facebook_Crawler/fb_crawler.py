from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from time import sleep
from bs4 import BeautifulSoup
from facebook_scraper import get_posts
from urllib.parse import urlparse, urlunparse

def init_driver():
    options = Options()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(executable_path='./chromedriver.exe', options=options)
    return driver


def login_facebook(driver, username, password):
    driver.get("https://mbasic.facebook.com/")
    text_user_name = driver.find_element(By.ID, "m_login_email")
    text_user_name.send_keys(username)
    text_password = driver.find_element(By.NAME, "pass")
    text_password.send_keys(password)
    text_password.submit()


def get_content_comment(driver):
    try:
        links = driver.find_elements(By.XPATH, '//a[contains(@href, "comment/replies")]')
        ids = []
        comments = []
        for link in links:
            take_link = link.get_attribute('href').split('ctoken=')[1].split('&')[0]
            if take_link not in ids:
                text_comment_element = driver.find_element(By.XPATH, f'//*[@id="{take_link.split("_")[1]}"]/div/div[1]')
                comments.append(text_comment_element.text)
                ids.append(take_link)
        return comments
    except Exception as e:
        print(f"Error while getting comments: {e}")

def get_amount_of_comments(driver, post_id, list_comments):
    try:
        driver.get(f"https://mbasic.facebook.com/{post_id}")
        comments = get_content_comment(driver)
        list_comments.append(comments)      
        try:
            next_btn = driver.find_elements(By.XPATH, '//*[contains(@id,"see_next")]/a')
            if len(next_btn) > 0:
                next_btn[0].click()
                new_comments = get_content_comment(driver)
                list_comments.append(new_comments)
                comments.extend(new_comments)
        except:
            print('Error while crawling comment content.')
        return list_comments
    except:
        print(f"Error while getting comments for post ID {post_id}")

def crawl_fb(url, num_posts):
    browser = init_driver()
    #login facebook
    login_facebook(browser,'thanhmvnt@gmail.com','123123qwerR')
    browser.get(url)
    soup = BeautifulSoup(browser.page_source, "html.parser")
    postIDs = []
    for post in get_posts(url, pages=5):
        postIDs.append(post['post_id'])
        if len(postIDs) == num_posts:
            break
    post = []
    #extract comments in each post
    for post_id in postIDs:
        comments = get_amount_of_comments(browser, post_id, [])
        post.append({'post_id': post_id, 'comment': comments})
    if (len(post) == num_posts):
        return post[:num_posts]
