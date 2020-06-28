from pathlib import Path
import fire

from hypergol import utils
from hypergol.utils import Mode
from hypergol.utils import to_snake
from hypergol.cli.jinja_renderer import JinjaRenderer


def create_pipeline(pipeLineName, *args, projectDirectory='.', mode=Mode.NORMAL, dryrun=None, force=None):
    mode = utils.get_mode(mode=mode, dryrun=dryrun, force=force)
    if pipeLineName != pipeLineName.lower():
        if '_' in pipeLineName:
            raise ValueError('Error: {pipeLineName}, pipeline name must be either snake case or camel case')
        pipeLineName = to_snake(pipeLineName)

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
        'snakeName': pipeLineName,
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
    filePath = Path(projectDirectory, 'pipelines', f'{to_snake(pipeLineName)}.py')
    content = JinjaRenderer().render(
        templateName='pipeline.py.j2',
        templateData=templateData,
        filePath=Path(projectDirectory, 'pipelines', f'{to_snake(pipeLineName)}.py'),
        mode=mode
    )

    scriptFilePath = Path(projectDirectory, f'{to_snake(pipeLineName)}.sh')
    scriptContent = JinjaRenderer().render(
        templateName='pipeline.sh.j2',
        templateData={'snakeName': to_snake(pipeLineName)},
        filePath=Path(projectDirectory, f'{to_snake(pipeLineName)}.sh'),
        mode=mode
    )
    utils.make_file_executable(filePath=scriptFilePath, mode=mode)

    print('')
    print(f'PipeLine {pipeLineName} was created in directory {filePath}.{utils.mode_message(mode)}')
    print('')
    if mode == Mode.DRY_RUN:
        return content, scriptContent
    return None


if __name__ == "__main__":
    fire.Fire(create_pipeline)
