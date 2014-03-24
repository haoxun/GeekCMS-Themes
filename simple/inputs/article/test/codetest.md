Title: codetest
Date: 10/12/2013

# test

```python
class ArticlePageGenerator(BasePlugin, _TemplateRender):

    """
    1. Generate rel_path of outputs directory. (simple.article + title)
    2. Deal with url confilcts.
    3. Register page to article mappings.
    """

    plugin = 'gen_article_page'

    def __init__(self):
        self._unique_rel_paths = []

    def _adjust_conflict_rel_path(self, rel_path):
        while rel_path in self._unique_rel_paths:
            rel_path = re.sub(r'.html$', '', rel_path) + 'remove_conflict.html'
        self._unique_rel_paths.append(rel_path)
        return rel_path

    def _generate_article_rel_path(self, rel_path_to_inputs):
        _, filename = os.path.split(rel_path_to_inputs)
        # generate url base on rel_path of inputs.
        rel_path = os.path.join(
            ShareData.get('simple.article'),
            filename,
        )
        # change extension to .html.
        head, _ = os.path.splitext(rel_path)
        rel_path = head + '.html'
        # adjust conflits url.
        rel_path = self._adjust_conflict_rel_path(rel_path)
        return rel_path

    def _render_html(self, article_file):
        template_render = self._get_particle_template_render('article.html')
        html = template_render(
            title=article_file.meta_data['title'],
            article_html=article_file.html,
        )
        return html
```
