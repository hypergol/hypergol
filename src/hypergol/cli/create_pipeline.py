from pathlib import Path
import fire

from hypergol.name_string import NameString
from hypergol import utils
from hypergol.utils import Mode
from hypergol.utils import to_snake
from hypergol.cli.jinja_renderer import JinjaRenderer


def create_pipeline(pipeLineName, *args, projectDirectory='.', mode=Mode.NORMAL, dryrun=None, force=None):
    pipeLineName = NameString(pipeLineName)
    mode = utils.get_mode(mode=mode, dryrun=dryrun, force=force)
    dependencies = args
    taskDependencies = []
    dataModelDependencies = []
    dataModelTypes = utils.get_data_model_types(projectDirectory)
    taskTypes = utils.get_task_types(projectDirectory)
    for dependency in dependencies:
        if dependency in taskTypes:
            taskDependencies.append(dependency)
        elif dependency in dataModelTypes:
            dataModelDependencies.append(dependency)
        else:
            raise ValueError(f'Unknown dependency: {dependency}')

    templateData = {
        'snakeName': pipeLineName.asSnake,
        'taskDependencies': [{
            'importName': to_snake(name),
            'name': name,
            'lowerName': name[0].lower() + name[1:]
        } for name in taskDependencies],
        'dataModelDependencies': [{
            'importName': to_snake(name),
            'name': name,
            'pluralName': f'{name[0].lower() + name[1:]}s',
            'pluralSnakeName': f'{to_snake(name)}s'
        } for name in dataModelDependencies]
    }
    filePath = Path(projectDirectory, 'pipelines', pipeLineName.asFileName)
    content = JinjaRenderer().render(
        templateName='pipeline.py.j2',
        templateData=templateData,
        filePath=Path(projectDirectory, 'pipelines', pipeLineName.asFileName),
        mode=mode
    )

    scriptFilePath = Path(projectDirectory, f'{pipeLineName.asSnake}.sh')
    scriptContent = JinjaRenderer().render(
        templateName='pipeline.sh.j2',
        templateData={'snakeName': pipeLineName.asSnake},
        filePath=Path(projectDirectory, f'{pipeLineName.asSnake}.sh'),
        mode=mode
    )
    utils.make_file_executable(filePath=scriptFilePath, mode=mode)

    print('')
    print(f'PipeLine {pipeLineName.asSnake} was created in directory {filePath}.{utils.mode_message(mode)}')
    print('')
    if mode == Mode.DRY_RUN:
        return content, scriptContent
    return None


if __name__ == "__main__":
    fire.Fire(create_pipeline)
