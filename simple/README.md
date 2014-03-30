
A simple template which generating html from markdown.

Settings:

* Each markdown file in *inputs* should place meta data at the top of file,
and seperate meta data with a blank line. Meta data with *Title* and *Date*
as its keys are necessary. *Title* should be a string without any line breaking
and *Date* should be a string with the format of "dd/mm/yyyy".
* Place a markdown file in /inputs/about for rendering *about* page.
* Place a markdown file in /inputs/index for rendering *index* page.
* Place a tree-like structure(file tree) contains multiple markdown files in /inputs/article
for rendering *article* pages.
* Place all image and other static resources in /inputs/static/, and with links them with the 
format of '/static/\*' for reference.
* Change the project settings *domain* to your domain.
* Change the project settings *disqus_shortname* to Disqus shortname.


Features:

* Markdown support with *mistune*.
* Code block with Github code style.
* Article tree is detected and genereated. The ordering of articles in the tree is stored in /states/simple/archive\_xml, which could be adjusted for reordering.
* Sitemap support.
* Disqus support.

Third-part packages Jinja2 and mistune is required.

	pip install Jinja2
	pin install mistune
