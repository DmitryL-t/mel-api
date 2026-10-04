import mel_api as mel

# mel.main_page() doesn't return all articles of the main page.
# the site mel.fm has button for loading more articles on the main page
# This method only shows articles that are in the source code of the main page.

# Fetching articles from a blog's page
# it's the main blog of the site
print('Main page articles:')
articles = mel.main_page()
for i in articles[:5]:
	print(i['title'])
	print(i['comment_count'], 'comments')
	print()


# mel.get_blog() and mel.get_author() don't return all articles of some blog or author.
# the site mel.fm has infinite scrolling at the blog pages
# So, these methods only show articles that are in the source code of a blog or author page.

# Fetching articles from an author's page
# it's an official Mel author
blog = mel.get_author('gramotnost-na-mele')
print('Author title:', blog['title'])
print('Author subtitle:', blog['title1'])
print()
articles = blog['articles'][:5]
for i in articles:
	print(i['title'])
	print(i['title1'])
	print(i['comment_count'], 'comments')
	print()

# Fetching articles from a blog's page
# it's the main blog of the site
blog = mel.get_blog('myel-myel')
print('Blog title:', blog['title'])
print('Blog subtitle:', blog['title1'])
print()
articles = blog['articles']
for i in articles[:5]:
	print(i['title'])
	print(i['title1'])
	print(i['comment_count'], 'comments')
	print()


# mel.get_blog('no-blog')) # None
# mel.get_author('no-author')) # None

# Fetching an article

# article = mel.get_article('/ucheba/yege/6893721-kakogo-cherta-bally-detey-...')
article = mel.get_article('ucheba', 'yege', 6893721)
print('Article')
print('Article title:', article['title'])
print('Article subtitle:', article['title1'])
# The content is stored at articles['content']

# Printing comments
print('\nArticle comments')
for i in article['comments']:
	print(i['author_name'])
	print(i['text'])
	for j in i['replies']:
		print('//', j['author_name'])
		print('--', j['text'])
	print()
	# The site has only 1-level replies


# Classes for fetching articles, that are only available by clicking "More articles" button or by scrolling
main_page = mel.MainPage()

print('Main page articles:')
for article in main_page.source_code:
	print(article['title'])

for i in range(2):
	articles = main_page.load()
	if len(articles) == 0:
		break
	for article in articles:
		print('>', article['title'])
	
author = mel.Author('gramotnost-na-mele')
print('Author title:', author.title)
print('Author subtitle:', author.title1)

print('Author articles:')
for article in author.source_code:
	print(article['title'])

for i in range(2):
	articles = author.load()
	if len(articles) == 0:
		break
	for article in articles:
		print('>', article['title'])

blog = mel.Blog('myel-myel')
print('Blog title:', blog.title)
print('Blog subtitle:', blog.title1)

print('Blog articles:')
for article in blog.source_code:
	print(article['title'])

for i in range(2):
	articles = blog.load()
	if len(articles) == 0:
		break
	for article in articles:
		print('>', article['title'])

print()

# Search
search_results = mel.search('огэ', sort='publicationTime')
print('Search results:')
for article in search_results:
	print(article['title'])
print()

print('Search results:')
search = mel.Search('огэ', sort='publicationTime')
for article in search.source_code:
	print(article['title'])

for i in range(2):
	articles = search.load()
	if len(articles) == 0:
		break
	for article in articles:
		print('>', article['title'])
