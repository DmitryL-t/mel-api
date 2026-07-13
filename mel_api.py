import requests
from bs4 import BeautifulSoup as bs
import json as json_
# Returns articles (posts) from the main page of the site mel.fm. Doesn't return articles that is only avaible by clicking "More articles" button.
def main_page():
	'''Returns articles from the main page of site

	Arguments: none
	Return value:
	list of dictionaries (articles) with keys:
		- title : string
		- title1 : string (subtitle)
		- publication time  : string
			date like 'DD.MM.YYYY'
		- comment count : int
			(with comment replies)
	'''
	s = requests.get('https://mel.fm').text
	soup = bs(s, features='html.parser')
	blocks = soup.find(class_='main-page__list')
	articles = []
	for i in blocks.find_all(class_='tile-card'):
		title = i.find(class_=['card-double__title', 'card-blog-double__title', 'card-half__title', 'card-blog-half__title', 'card-without-image__title']).text
		#print(title)
		url = i.find(class_='tile-card__url')['href']
		#print(url)
		publication_time = i.find(class_='tile-card__date').text
		#print(publication_time)
		comment_span = i.find('span')
		if comment_span:
			comment_count = int(comment_span.text)
		else:
			comment_count = 0
		#print(comment_count)
		articles.append({
			'title': title,
			'url': url,
			'publication_time': publication_time,
			'comment_count': comment_count
		})
	return articles


# This method gets title, subtitle, author's name, content, and comments of an article.
def get_article(*path):
	"""Returns data (title, subtitle, author's name and url, content and comments)
	
	Arguments: path (*array of strings or int)
	path can be an url (https://mel.fm/..., mel.fm/..., /.../... or .../...)
	or list of strings or ints (for example, '/ucheba/yege/123' = 'ucheba', 'yege', 123)

	Return value: article or None
	article : dict
		title : string
		title1: string or None - subtitle
		url : article url
		author_name : string - author's name or None
		author_url : string - author's url
		comment count : int (with comment replies)
		content : article content
		comments : dict
			author_name : string - author's name
			text : comment text
			replies : list of comment replies : dict
				author_name
				text

	content:
		list of elements:
		tuple ('bold_style', text)
		tuple ('text', text)
		...
	"""
	_path = '/'.join([str(i) for i in path])
	for _ in ('https://mel.fm', 'http://mel.fm', '/'):
		if _path.startswith(_):
			_path = _path[len(_):]

	last_part = _path.split('/')[-1]
	if sum([1 if '0' <= i <= '9' else 0 for i in last_part]) == len(last_part) > 0:
		_path += '-a'
	_path = '/' + _path

	s = requests.get('https://mel.fm' + _path).text
	soup = bs(s, features='html.parser')
	if soup.find(class_='article i-control') == None:
		return None

	title = soup.find(class_='publication-header__title').text
	# title1 = soup.find(class_='publication-header__subtitle').text
	title1_ = soup.find(class_='publication-header__subtitle')
	if title1_ != None:
		title1 = title1_.text
	else:
		title1 = None
	#print(title)
	#print(title1)
	s_info = soup.find(class_='article__meta-data')
	author_name_ = s_info.find(class_='article__author')
	if author_name_:
		author_name = author_name_.text
	else:
		author_name = None
	#print(author_name)
	comment_count_span = s_info.find('span')
	if comment_count_span:
		comment_count = int(comment_count_span.text)
	else:
		comment_count = 0
	#print(comment_count)
	main_content = soup.find(class_='publication-body')
	content_objects = []
	for i in main_content:
		if i.name == 'p':
			classes = i.get('class', [])
			if 'b-pb-publication-body__lead' in classes:
				content_objects.append(('bold_style', i.text)) 
			elif 'b-pb-publication-body__signature' not in classes:
				content_objects.append(('text', i.text))
		if i.name == 'div':
			classes = i.get('class', [])
			if 'b-pb-publication-body__background' in classes:
				colored_block = []
				for j in i:
					if j != str(j):
						if j.name != 'ul':
							colored_block.append(('text', j.text))
						else:
							ul_list = []
							for k in j:
								if k != str(k):
									ul_list.append(k.text)
							colored_block.append(('ul', ul_list))
				content_objects.append(('colored_block', colored_block))
		if i.name == 'h3':
			content_objects.append(('h3', i.text))
		if i.name == 'ul':
			ul_list = []
			for j in i.children:
				if j != str(j):
					ul_list.append(j.text)
			content_objects.append(('ul', ul_list))

	tag = soup.find(class_='article__under-content-block')
	if tag:
		author_url = tag.find(class_='author-bottom__link')['href']
	else:
		# Unknown error
		author_url = None
		#print(author_url)
	comments_ = soup.find(id='comments').find(class_='comments')
	comments = []
	for i in comments_.find_all(class_='comments__comment comment'):
		comment = i.find(class_='simple-comment__body')
		comment_author_name = comment.find(class_='comment-author-name__author-name').find('a').text
		#print(comment_author_name)
		comment_elem = i.find(class_='comment__text')
		comment_text_ = []
		for j in comment_elem.children:
			if repr(type(j)) == "<class 'bs4.element.NavigableString'>" and j.text != ' ':
				comment_text_.append(j.text)
		comment_text = ' '.join(comment_text_)
		#print(comment_text)
		comment_replies = []
		replies = i.find(class_='comment__answers')
		if replies != None:
			for j in replies.children:
				comment_reply = j.find(class_='simple-comment__body')
				reply_author_name = comment_reply.find(class_='comment-author-name__author-name').text
				#print(reply_author_name)
				comment_reply_elem = j.find(class_='comment__text')
				comment_reply_text_ = []
				for _j in comment_reply_elem:
					if repr(type(_j)) == "<class 'bs4.element.NavigableString'>" and _j.text != ' ':
						comment_reply_text_.append(_j.text)
				comment_reply_text = ' '.join(comment_reply_text_)
				#print(comment_reply_text)
				comment_replies.append({
					'author_name': reply_author_name,
					'text': comment_reply_text
				})

		comments.append({
			'author_name': comment_author_name,
			'text': comment_text,
			'replies': comment_replies
		})
	article_ = {
		'url': _path,
		'title': title,
		'title1': title1,
		'author_name': author_name,
		'author_url': author_url,
		'comment_count': int(comment_count),
		'content': content_objects,
		'comments': comments
	}
	return article_

# Returns articles from an author page. Doesn't return all articles.
def get_author(name):
	"""Returns information about some author

	Arguments: author nickname
	Return value:
		None OR
		dict
			title: blog title
			title1: blog subtitle
			articles: list of articles
				dict:
					publication_time : str "YYYY-MM-DDThh:mm:00+00:00"
					url : article url
					title : article title
					title1 : article subtitle
					comment_count : int
	"""
	# /author/gramotnost-na-mele
	# /author/anastasiya-shirokova
	# /author/sofya-shchudrina
	# /author/uznay-u-mela
	# /author/lyudmila-chirkova
	path = '/author/' + name
	full_path = 'https://mel.fm' + path
	s = requests.get(full_path).text
	soup = bs(s, features='html.parser')
	if soup.find(class_='b-author') == None:
		return None
	blog_title = soup.find(class_='b-pb-author__name').text
	#print(blog_title)
	blog_title1 = soup.find(class_='b-pb-author__quote').text
	#print(blog_title1)
	articles = []
	for i in soup.find_all(class_='b-article-feed__article-preview'):
		json = json_.loads(i.find(class_='i-control')['data-params'])
		publication_time = json['data']['publicationTime']
		#print(publication_time)

		# date_ = i.find(class_='b-article-preview__publication-date').text
		# time_ = i.find(class_='b-article-preview__publication-time').text
		# Doesn't work!
		url_ = i.find(class_='b-article-preview__read-next')
		url = url_['href']
		#print(url)
		title = i.find(class_='b-article-preview__title').text
		#print(title)
		title1 = i.find(class_='b-article-preview__subtitle').text
		#print(title1)
		comment_count_ = i.find(class_='b-article-preview__comments-count')
		if comment_count_:
			comment_count = int(comment_count_.text)
		else:
			comment_count = 0
		#print(comment_count)
		articles.append({
			'publication_time': publication_time,
			'url': url,
			'title': title,
			'title1': title1,
			'comment_count': comment_count
		})
	return {
		'title': blog_title,
		'title1': blog_title1,
		'articles': articles
	}

def get_blog(name):
	"""Returns information about some blog

	Arguments: blog name
	Return value:
		None OR
		dict
			title: blog title
			title1: blog subtitle
			articles: list of articles
				dict:
					publication_time : str "YYYY-MM-DDThh:mm:00+00:00"
					url : article url
					title : article title
					title1 : article subtitle
					comment_count : int
	"""
	# /blog/myel-myel
	path = '/blog/' + name
	full_path = 'https://mel.fm' + path
	s = requests.get(full_path).text
	soup = bs(s, features='html.parser')
	if soup.find(class_='b-blog') == None:
		return None
	blog_title = soup.find(class_='b-pb-author__name').text
	blog_title1_ = soup.find(class_='b-pb-author__quote')
	if blog_title1_:
		blog_title1 = blog_title1_.text
	else:
		blog_title1 = None # /blog/myel-myel
	articles = []
	for i in soup.find_all(class_='b-article-feed__article-preview'):
		json = json_.loads(i.find(class_='i-control')['data-params'])
		publication_time = json['data']['publicationTime']
		#print(publication_time)

		# date_ = i.find(class_='b-article-preview__publication-date').text
		# time_ = i.find(class_='b-article-preview__publication-time').text
		# Doesn't work!
		url_ = i.find(class_='b-article-preview__read-next')
		url = url_['href']
		#print(url)
		title = i.find(class_='b-article-preview__title').text
		#print(title)
		title1 = i.find(class_='b-article-preview__subtitle').text
		#print(title1)
		comment_count_ = i.find(class_='b-article-preview__comments-count')
		if comment_count_:
			comment_count = int(comment_count_.text)
		else:
			comment_count = 0
		#print(comment_count)
		articles.append({
			'publication_time': publication_time,
			'url': url,
			'title': title,
			'title1': title1,
			'comment_count': comment_count
		})
	return {
		'title': blog_title,
		'title1': blog_title1,
		'articles': articles
	}
