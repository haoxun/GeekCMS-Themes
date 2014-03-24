Title: TopLevel
Date: 10/12/2013

# test
test

```python
class AboutPageGenerator(BasePlugin):

    plugin = 'gen_about_page'

    @pcl.accept_parameters(
        (pcl.RESOURCES, AboutFile),
    )
    def run(self, about_files):
        # about_file = about_files[0]
        pass
```