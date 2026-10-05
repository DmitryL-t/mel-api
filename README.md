# mel-api
API for mel.fm site
## Objects
### main_page()
Returns articles from the source code of the main page.

Return object is a list of dictionaries with keys 'title', 'url', 'publication_time', and 'comment_count'.
### get_article(*path)
Returns information about an article with that path or None.

Path can be an url, a path (/...), or a *path list* (`get_article('blog', 'title', 123)` gets article with path '/blog/title/123')

Return object is a dictionary with keys 'url', 'title', 'title1' (subtitle), 'author_name', 'author_url', 'comment_count', 'content' and 'comments'.

Comments are dictionaries with keys 'author_name', 'text', and 'replies'. Replies are dictionaries with keys 'author_name' and 'text'.
### get_author(name), get_blog(name)
Return information and articles from the source code of author or blog page or None.

Return object is a dictionary with keys 'title', 'title1' (subtitle), and 'articles'. Articles value is a list of dictionaries with keys 'publication_time', 'url', 'title', 'title1', and 'comment_count'.

### Classes MainPage, Author, and Blog
These classes get articles from the main page or author's or blog's page. They can load articles, available by infinite scrolling or clicking the "More articles" button. Using:
1. Creating an object:
```
# main page
main_page = mel.MainPage()
# author
author = mel.Author('gramotnost-na-mele')
# blog
blog = mel.Blog('myel-myel')
```
2. Getting articles from 'source_code' property:
```
# main page
articles = main_page.source_code
# author
articles = author.source_code
# blog
articles = blog.source_code
```
3. To get more articles, use `load` method:
```
articles = main_page.load()
articles = author.load()
articles = blog.load()
```
'source_code' property is a list of articles that were in the source code

'articles' property is a list of all articles (from source code and fetched)

'is_all' property is a boolean, that shows, is it the end of articles

### search(query, sort='revelance', section=None)
This method returns search results from the search page. `sort` parameter can be 'revelance', 'publicationTimeAsc', and 'publicationTime'.
`section` parameter can be `None` or integer from 1 to 15. If it is None, the site searches articles with all categories, if it is integer, site searches only articles with one category.

Return value is a list of dictionaries with keys 'url', 'tag' (category), 'title', 'title1', and 'comment_count'.

### Search(query, sort='revelance', section=None)
This class has `source_code` property, that contains articles from the source code of page. Loading more articles is possible by using `load()` method. They will be added to `articles` property of object.

Articles have keys 'url', 'tag, 'title', 'title1', and 'comment_count'.
