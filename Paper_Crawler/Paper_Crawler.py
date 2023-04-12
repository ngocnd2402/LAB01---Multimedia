import csv
import requests
from bs4 import BeautifulSoup
import unicodedata
import re
import time
import random
from sklearn.metrics import jaccard_score

def jaccard_similarity(str1, str2):
    set1 = set(str1.split())
    set2 = set(str2.split())
    intersection = set1.intersection(set2)
    union = set1.union(set2)
    return len(intersection) / len(union)

def crawl_acm(author_name, num_papers, startPage=0, count_recursion = 0):
    # Tạo URL tìm kiếm theo tên tác giả trên ACM
    name = author_name.replace(' ', '+')
    search_url = f"https://dl.acm.org/action/doSearch?AllField={name}&startPage={startPage}&pageSize=20"

    # Tải trang và sử dụng BeautifulSoup để phân tích cú pháp HTML
    try:
        page = requests.get(search_url)
        page.raise_for_status()
        soup = BeautifulSoup(page.content, 'html.parser')
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error occurred: {e}")
        return []

    # Tìm các thẻ HTML chứa thông tin về bài báo
    paper_tags = soup.find_all('div', {'class': 'issue-item__content'})
    # Duyệt qua các thẻ và trích xuất thông tin về bài báo
    papers = []
    for tag in paper_tags:
        
        title_tag = tag.find('h5', {'class': 'issue-item__title'})
        title = title_tag.get_text().strip() if title_tag else ''
        
        author_ul = tag.find('ul', {'class': 'rlist--inline loa truncate-list'})
        if author_ul is not None:
            authors = []
            for li in author_ul.find_all('li'):
                author = li.find('span').text.strip()
                authors.append(author)
                
            # Tìm độ tương đồng giữa tên tác giả và danh sách tác giả của paper
            max_ratio = max([jaccard_similarity(author_name, author) for author in authors])    
            # Chỉ lấy các paper có tác giả gần đúng với tên tác giả đã cho
            if max_ratio >= 0.6:
                publication_dates = []
                pub_info = tag.find('span', {'class': 'dot-separator'})
                if pub_info:
                    pub_date = pub_info.find('span')
                    if pub_date:
                        pub_date = pub_date.text.strip().split(',')[0]
                        publication_dates.append(pub_date)

                doi_tag = tag.find('a', {'class': 'issue-item__doi dot-separator'})
                doi = doi_tag['href'] if doi_tag else ''

                papers.append({'title': title, 'author': authors, 'Public Date': publication_dates, 'DOI': doi})

    # Kiểm tra số lượng bài báo lấy được, nếu đã đủ thì return
    if len(papers) >= num_papers or count_recursion == 10:
        return papers[:num_papers]
    # Nếu chưa đủ, tiếp tục đệ quy tới trang tiếp theo
    else:
        return papers + crawl_acm(author_name, num_papers - len(papers), startPage + 1, count_recursion + 1)