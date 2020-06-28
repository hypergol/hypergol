from pathlib import Path
import fire

from hypergol import utils
from hypergol.utils import Mode
from hypergol.cli.jinja_renderer import JinjaRenderer
from hypergol.name_string import NameString
from hypergol.hypergol_project import HypergolProject


def create_pipeline(pipeLineName, *args, projectDirectory='.', mode=Mode.NORMAL, dryrun=None, force=None):
    project = HypergolProject(projectDirectory)
    pipeLineName = NameString(pipeLineName)
    mode = utils.get_mode(mode=mode, dryrun=dryrun, force=force)
    dependencies = [NameString(value) for value in args]
    if not all(project.is_project_class(dependency) for dependency in dependencies):
        print(project)
        raise ValueError(f'Unknown dependency {[d.asClass for d in dependencies if not project.is_project_class(d)]}')

    filePath = Path(projectDirectory, 'pipelines', pipeLineName.asFileName)
    content = JinjaRenderer().render(
        templateName='pipeline.py.j2',
        templateData={
            'snakeName': pipeLineName.asSnake,
            'taskDependencies': [name for name in dependencies if project.is_task_class(name)],
            'dataModelDependencies': [name for name in dependencies if project.is_data_model_class(name)]
        },
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
