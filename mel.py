import mel_api as mel

# mel.get_blog() and mel.get_author() don't return all the articles of some blog or author.
# the site mel.fm has infinite scrolling at the blog pages
# So, these methods only show articles that are in the source code of a blog or author page.

# Fetching articles from a blog's page
# it's the main blog of the site
blog = mel.get_blog('myel-myel')
print('Blog title:', blog['title'])
print('Blog subtitle:', blog['title1'])
print()
articles = blog['articles'][:3]
for i in articles:
	print(i['title'])
	print(i['title1'])
	print(i['publication_time'])
	print(i['comment_count'])
	print()

# Fetching articles from an author's page
# it's an official Mel author
blog = mel.get_author('nadezhda-tega')
print('Blog title:', blog['title'])
print('Blog subtitle:', blog['title1'])
print()
articles = blog['articles'][:3]
for i in articles:
	print(i['title'])
	print(i['title1'])
	print(i['publication_time'])
	print(i['comment_count'])
	print()

print(mel.get_blog('no-blog')) # None
print(mel.get_author('no-author')) # None
print()

# Fetching articles from the main page
articles = mel.main_page()
for i in articles:
	if i['comment_count'] >= 10:
		print(i['title'], '-', i['comment_count'], 'comments')

# Fetching a post

# article = mel.get_article('/ucheba/yege/6893721-kakogo-cherta-bally-detey-...')
# https://mel.fm/author/gramotnost-na-mele
article = mel.get_article('ucheba', 'yege', 6893721)
print('Article')
print(article['title'])
print(article['title1'])
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
	# The site has only 1-level answers
