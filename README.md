# mel-api
API for mel.fm site
## Methods
### main_page()
Returns all articles from the source code of the main page.

Return object is a list of dictionaries with keys 'title', 'url', 'publication_time', and 'comment_count'.
### get_article(*path)
Returns information about an article with that path or None.

Path can be an url, a path (/...), or a *path list* (`get_article('blog', 'title', 123)` gets article with path '/blog/title/123')

Return object is a dictionary with keys 'url', 'title', 'title1' (subtitle), 'author_name', 'author_url', 'comment_count', 'content' and 'comments'.
### get_author(name), get_blog(name)
Return information and articles from the source code of author or blog page or None.

Return object is a dictionary with keys 'title', 'title1' (subtitle), and 'articles'. Articles value is a list of dictionaries with keys 'publication_time', 'url', 'title', 'title1', and 'comment_count'.
