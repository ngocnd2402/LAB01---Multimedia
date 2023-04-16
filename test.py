from facebook_scraper import get_posts

postIDs = []
for post in get_posts('nintendo', pages=5):
    postIDs.append(post['post_id'])
    print(postIDs)