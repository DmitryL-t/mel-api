import requests
from bs4 import BeautifulSoup as bs
import json as json_
# Returns articles (articles) from the main page of the site mel.fm. Doesn't return articles that is only available by clicking "More articles" button.
def main_page():
	'''Return articles from the main page of site

	Arguments: none
	Return value:
	list of dictionaries (articles) with keys:
		- title : string
		- url : string
			(url of an article)
		- publication_time : string
			date like 'DD.MM.YYYY'
		- comment count : int
			(comment count with comment replies)
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

# Loads articles from main page (with additional articles)
class MainPage:
	'''
	__init__ arguments:
		none
	Properties:
		- source_code : list of articles
			articles at source code
		- articles : list of articles
			articles at source code and fetched articles
		- is_all : bool
			flag of end of articles
	articles : dictionaries with keys:
		- publication_time : str
			time
		- url : str
			article url
		- title : str
		- comment_count : int
			comment count (including comment replies)
	Methods:
		load():
		Arguments: None
		Return value : list of dictionaries with keys: 
			- publication_time : str
			- url : str
				article url
			- title : str
			- comment_count : int
				comment count (with replies)
	'''
	def __init__(self):
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
				'publication_time': publication_time,
				'url': url,
				'title': title,
				'comment_count': comment_count
			})
		self.articles = self.source_code = articles
		link = None
		script_list = soup.find_all('script')
		for script in script_list:
			s_ = script.text.strip()
			if 'window.__APOLLO_STATE__={"' in s_:
				text = s_[s_.find('window.__APOLLO_STATE__={"') + 24:]
				if text[-1] == ';':
					text = text[:-1]
				json = json_.loads(text)
				link = json['$ROOT_QUERY.frontpageClient({})']['link']
		self.link = link
	def load(self):
		# print('Fetching more articles with link', self.link)
		data = "{\"operationName\":\"FrontpageClientQuery\",\"variables\":{\"link\":\"" + self.link + "\"},\"query\":\"query FrontpageClientQuery($link: String) {\\n  frontpageClient(link: $link) {\\n    publications {\\n      id\\n      publicationTime\\n      commentsCount\\n      title\\n      subtitle\\n      url\\n      coverImageUrl\\n      socialImageUrl\\n      type\\n      isEnabled\\n      isExternalPublication\\n      mainSection {\\n        sectionId\\n        sectionName\\n        sectionAddress\\n        __typename\\n      }\\n      mainPageTiles {\\n        type\\n        imageUrl\\n        __typename\\n      }\\n      isCommercialPublication\\n      __typename\\n    }\\n    link\\n    __typename\\n  }\\n}\\n\"}"
		s = requests.post('https://mel.fm/graphql?op=FrontpageClientQuery', headers={'content-type': 'application/json'}, data=data).text
		json = json_.loads(s)		
		publications = json['data']['frontpageClient']['publications']
		articles = []
		for i in publications:
			article = {
				'publication_time': i['publicationTime'],
				'url': i['url'],
				'title': i['title'],
				'comment_count': i['commentsCount']
			}
			articles.append(article)
		link = json['data']['frontpageClient']['link']
		# print('New link is', link)
		self.link = link
		self.articles += articles
		return articles

# This method gets title, subtitle, author's name, content, and comments of an article.
def get_article(*path):
	"""Returns data (title, subtitle, author's name and url, content and comments)
	
	Arguments: path (*array of strings or int)
	path can be an url (https://mel.fm/..., mel.fm/..., /.../... or .../...)
	or list of strings or ints (for example, '/ucheba/yege/123' = 'ucheba', 'yege', 123)

	Return value: article or None
	article : dictionary with keys:
		- url : str
			article url
		- title : str
		- title1: str or None
			subtitle of article
		- author_name : str or None
			author's name
		- comment_count : int
			(comment count with comment replies)
		- content
			article content
		- comments : list of dictionaries with keys:
			- author_name : str
				author's name
			- text : str
				comment text
			- replies : list of dictionaries with keys:
				- author_name : str
					name of reply author
				- author_url : str
					url of author's page
				- text : str
					reply text

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
	if soup.select_one('.article.i-control') == None:
		return None

	title = soup.find(class_='publication-header__title').text
	#print(title)

	# title1 = soup.find(class_='publication-header__subtitle').text
	title1_ = soup.find(class_='publication-header__subtitle')
	if title1_ != None:
		title1 = title1_.text
	else:
		title1 = None
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

# Returns articles from an author page. Doesn't return articles that are only available by infinite scrolling.
def get_author(name):
	"""Return information about some author

	Arguments: author nickname : str
	Return value: None or dictionary with keys:
		- title : str
		- title1 : str
			subtitle of author page
		- articles : list of articles (dictionaries with keys):
			- publication_time : str
				time like "YYYY-MM-DDThh:mm:00+00:00"
			- url : str
				article url
			- title : str
			- title1 : str
				subtitle of article
			- comment_count : int
				comment count (including comment replies)
	"""
	# /author/gramotnost-na-mele
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

# Loads articles from an author page (with additional articles)
class Author:
	'''
	__init__ arguments:
		name : str
			author nickname
	Properties:
		- source_code : list of articles
			articles at source code
		- articles : list of articles
			articles at source code and fetched articles
		- is_all : bool
			flag of end of articles
	articles : dictionaries with keys:
		- publication_time : str
			time
		- url : str
			url of article
		- title : str
		- title1 : str
			subtitle of article
		- comment_count : int
			comment count (including comment replies)
	Methods:
		load():
		Arguments: None
		Return value : list of dictionaries with keys: 
			- publication_time : str
			- title : str
			- title1 : str
				subtitle of article
			- url : str
				article url
			- comment_count : int
				comment count (with replies)
	'''
	def __init__(self, name):
		self.name = name
		path = '/author/' + name
		full_path = 'https://mel.fm' + path
		s = requests.get(full_path).text
		soup = bs(s, features='html.parser')
		if soup.find(class_='b-author') == None:
			return None
		self.title = soup.find(class_='b-pb-author__name').text
		#print(self.title)
		self.title1 = soup.find(class_='b-pb-author__quote').text
		#print(self.title1)
		json = None
		link_elem = soup.select('.i-control.b-author')[0]
		json = json_.loads(link_elem['data-params'])
		link = json['link']
		self.link = link

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
		self.articles = self.source_code = articles
		self.is_all = False
	def load(self):
		if self.is_all:
			return []
		#print('Fetching articles with link', self.link)
		s = requests.get(f'https://mel.fm/api' + self.link).text
		json = json_.loads(s)
		publications = json['publications']
		articles = []
		for i in publications:
			article = {
				'publication_time': i['publicationTime'],
				'title': i['title'],
				'title1': i['subtitle'],
				'url': i['linkToArticle'],
				'comment_count': i['commentsCount']
			}
			articles.append(article)
		if 'link' in json:
			self.link = json['link']
		else:
			self.link = None
			self.is_all = True
		#print('New link is', self.link)
		return articles

# Returns articles from a blog page. Doesn't return articles that are only available by infinite scrolling.
def get_blog(name):
	"""Return information about some blog

	Arguments: blog name : str
	Return value: None or dictionary with keys:
		- title : str
		- title1 : str
			subtitle of the blog page
		- articles: list of articles : dictionaries with keys:
			- publication_time : str
				time like "YYYY-MM-DDThh:mm:00+00:00"
			- url : str
				article url
			- title : str
			- title1 : str
				subtitle of article
			- comment_count : int
				comment count (including comment replies)
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

# Loads articles from a blog page (with additional articles)
class Blog:
	'''
	__init__ arguments:
		name : str
			blog name
	Properties:
		- source_code : list of articles
			articles at source code
		- articles : list of articles
			articles at source code and fetched articles
		- is_all : bool
			flag of end of articles
	articles : dictionaries with keys:
		- publication_time : str
			time
		- url : str
			article url
		- title : str
		- title1 : str
			subtitle of article
		- comment_count : int
			comment count (including comment replies)
	Methods:
		load():
		Arguments: None
		Return value : list of dictionaries with keys: 
			- publication_time : str
			- url : str
				article url
			- title : str
			- title1 : str
				subtitle of article
			- comment_count : int
				comment count (with replies)
	'''
	def __init__(self, name):
		self.name = name
		path = '/blog/' + name
		full_path = 'https://mel.fm' + path
		s = requests.get(full_path).text
		soup = bs(s, features='html.parser')
		if soup.find(class_='b-blog') == None:
			return None
		self.title = soup.find(class_='b-pb-author__name').text
		#print(self.title)
		blog_title1_ = soup.find(class_='b-pb-author__quote')
		if blog_title1_:
			self.title1 = title1_.text
		else:
			self.title1 = None
		json = None
		link_elem = soup.select('.i-control.b-blog.b-blog_pablo_mel')[0]
		json = json_.loads(link_elem['data-params'])
		link = json['link']
		self.link = link
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
		self.articles = self.source_code = articles
		self.is_all = False
	def load(self):
		if self.is_all:
			return []
		#print('Fetching articles with link', self.link)
		s = requests.get(f'https://mel.fm/api' + self.link).text
		json = json_.loads(s)
		publications = json['publications']
		articles = []
		for i in publications:
			article = {
				'publication_time': i['publicationTime'],
				'url': i['linkToArticle'],
				'title': i['title'],
				'title1': i['subtitle'],
				'comment_count': i['commentsCount'],
			}
			articles.append(article)
		if 'link' in json:
			self.link = json['link']
		else:
			self.link = None
			self.is_all = True
		#print('New link is', self.link)
		return articles
