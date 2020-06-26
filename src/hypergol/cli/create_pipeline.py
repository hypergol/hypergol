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
from hypergol.utils import get_task_types


def create_pipeline(pipeLineName, *args, projectDirectory='.', mode=Mode.NORMAL, dryrun=None, force=None):
    mode = get_mode(mode=mode, dryrun=dryrun, force=force)
    if pipeLineName != pipeLineName.lower():
        if '_' in pipeLineName:
            raise ValueError('Error: {pipeLineName}, pipeline name must be either snake case or camel case')
        pipeLineName = to_snake(pipeLineName)
    dependencies = list(args)
    dataModelTypes = get_data_model_types(projectDirectory)
    taskTypes = get_task_types(projectDirectory)
    unknownTypes = set(dependencies)-set(dataModelTypes)-set(taskTypes)
    if len(unknownTypes) > 0:
        raise ValueError(f'Unknown dependencies: {unknownTypes}')

    templateEnvironment = jinja2.Environment(
        loader=jinja2.FileSystemLoader(
            searchpath=Path(hypergol.__path__[0], 'cli', 'templates')
        )
    )

    templateData = {
        'snakeName': pipeLineName,
        'taskDependencies': [{
            'importName': to_snake(name),
            'name': name,
            'lowerName': name[0].lower() + name[1:]
        } for name in dependencies & taskTypes],
        'dataModelDependencies': [{
            'importName': to_snake(name),
            'name': name,
            'pluralName': f'{name[0].lower() + name[1:]}s',
            'pluralSnakeName': f'{to_snake(name)}s'
        } for name in dependencies & dataModelTypes]
    }
    content = templateEnvironment.get_template('pipeline.j2').render(data=templateData)
    filePath = Path(projectDirectory, 'pipelines', f'{to_snake(pipeLineName)}.py')
    create_text_file(filePath=filePath, content=content, mode=mode)
    print('')
    print(f'PipeLine {pipeLineName} was created in directory {filePath}.{mode_message(mode)}')
    print('')
    if mode == Mode.DRY_RUN:
        return content
    return None


if __name__ == "__main__":
    fire.Fire(create_pipeline)
