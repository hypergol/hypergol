from pathlib import Path
import fire
import jinja2

import hypergol
from hypergol.utils import Mode
from hypergol.utils import get_mode
from hypergol.utils import mode_message
from hypergol.utils import create_text_file
from hypergol.utils import to_snake
from hypergol.utils import get_data_model_types


def create_source(className, *args, projectDirectory='.', mode=Mode.NORMAL, dryrun=None, force=None):
    mode = get_mode(mode=mode, dryrun=dryrun, force=force)
    dependencies = list(args)
    dataModelTypes = get_data_model_types(projectDirectory)
    unknownTypes = set(dependencies)-set(dataModelTypes)
    if len(unknownTypes) > 0:
        raise ValueError(f'Unknown dependencies: {unknownTypes}')

    templateEnvironment = jinja2.Environment(
        loader=jinja2.FileSystemLoader(
            searchpath=Path(hypergol.__path__[0], 'cli', 'templates')
        )
    )
    templateData = {
        'className': className,
        'dependencies': [
            {'importName': to_snake(value), 'name': value}
            for value in dependencies
        ]
    }
    content = templateEnvironment.get_template('source.j2').render(data=templateData)
    filePath = Path(projectDirectory, 'tasks', f'{to_snake(className)}.py')
    create_text_file(filePath=filePath, content=content, mode=mode)
    print('')
    print(f'Source {className} was created in directory {filePath}.{mode_message(mode)}')
    print('')
    if mode == Mode.DRY_RUN:
        return content
    return None


if __name__ == "__main__":
    fire.Fire(create_source)
