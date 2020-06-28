from pathlib import Path
import fire

from hypergol.name_string import NameString
from hypergol import utils
from hypergol.utils import Mode
from hypergol.cli.jinja_renderer import JinjaRenderer
from hypergol.hypergol_project import HypergolProject


VALID_TASK_TYPES = {'Task', 'Source'}


def get_task_type(taskType, source):
    if taskType is None or taskType in VALID_TASK_TYPES:
        return NameString('Source' if source else (taskType or 'Task'))
    raise ValueError(f'Unkown task type: {taskType}')


def create_task(className, *args, projectDirectory='.', mode=Mode.NORMAL, dryrun=None, force=None, source=False, taskType=None):
    project = HypergolProject(projectDirectory)
    className = NameString(className)
    mode = utils.get_mode(mode, dryrun, force)
    taskType = get_task_type(taskType, source)

    dependencies = [NameString(value) for value in args]
    project.check_dependencies(dependencies)

    content = JinjaRenderer().render(
        templateName=f'{taskType.asFileName}.j2',
        templateData={
            'className': className.asClass,
            'dependencies': dependencies
        },
        filePath=Path(projectDirectory, 'tasks', className.asFileName),
        mode=mode
    )

    print('')
    print(f'{taskType.asClass} {className.asClass} was created.{utils.mode_message(mode)}')
    print('')
    if mode == Mode.DRY_RUN:
        return content
    return None


if __name__ == "__main__":
    fire.Fire(create_task)
