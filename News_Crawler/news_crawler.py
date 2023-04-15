from requests_html import HTMLSession,AsyncHTMLSession
import time
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
    categories =['thoi su', 'goc nhin', 'the gioi', 'kinh doanh', 'khoa hoc', 'giai tri', 'the thao', 'phap luat',
             'giao duc', 'suc khoe', 'doi song', 'du lich']
    max_ratio = max([jaccard_similarity(item, category) for item in categories])
    for item in categories:
        ratio = jaccard_similarity(item, category)
        if ratio == max_ratio:
            category = item
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
