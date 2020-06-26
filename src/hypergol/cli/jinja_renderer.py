from pathlib import Path
import jinja2
import hypergol
from hypergol.utils import create_text_file


class JinjaRenderer:

    def __init__(self):
        self.templateEnvironment = jinja2.Environment(
            loader=jinja2.FileSystemLoader(
                searchpath=Path(hypergol.__path__[0], 'cli', 'templates')
            )
        )

    def render(self, templateName, templateData, filePath, mode):
        content = self.templateEnvironment.get_template(templateName).render(templateData)
        create_text_file(filePath=filePath, content=content, mode=mode)
        return content
