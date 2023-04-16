from requests_html import HTMLSession,AsyncHTMLSession
import time
import re

async def get_comments(link):
    all_comments = []
    try:
        session = AsyncHTMLSession()
        r = await session.get(link)
        await r.html.arender(sleep=1, timeout=30)
        comments = r.html.find('.full_content')
        usernames = r.html.find('.txt-name')
        for comment, username in zip(comments, usernames):
            comment_text = comment.text.split('\n')[-1].strip()
            username_text = username.text.strip()
            if username_text in comment_text:
                comment_text = comment_text.replace(username_text, '')
            all_comments.append((username_text, comment_text))
    except:
        pass
    return all_comments


async def crawl_articles(category, nums, startPage=1):
    url = 'https://vnexpress.net/'
    search_url = url + category.replace(' ', '-') + '-p' + str(startPage)
    session = AsyncHTMLSession()
    r = await session.get(search_url)
    await r.html.arender(sleep=1, timeout=30)
    article_titles = r.html.find('.title-news')
    articles = []
    for item in article_titles:
        title = item.find("a")[0].text
        link = item.find("a")[0].attrs['href']
        comments = await get_comments(link)
        articles.append({'title': title, 'link': link, 'comments': comments})
        if len(articles) >= nums:
            return articles
    if len(articles) >= nums:
        return articles
    else:
        return articles + await crawl_articles(category, nums - len(articles), startPage+1)

article = crawl_articles('kinh doanh', 2)
print(article)