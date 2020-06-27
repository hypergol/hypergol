from pathlib import Path
import fire

from hypergol import utils
from hypergol.utils import Mode
from hypergol.cli.jinja_renderer import JinjaRenderer


VALID_TASK_TYPES = {'Task', 'Source'}


def get_task_type(taskType, source):
    if taskType is None or taskType in VALID_TASK_TYPES:
        return 'Source' if source else (taskType or 'Task')
    raise ValueError(f'Unkown task type: {taskType}')


def create_task(className, *args, projectDirectory='.', mode=Mode.NORMAL, dryrun=None, force=None, source=False, taskType=None):
    mode = utils.get_mode(mode, dryrun, force)
    taskType = get_task_type(taskType, source)

    dependencies = sorted(list(set(args)))
    dataModelTypes = utils.get_data_model_types(projectDirectory)
    for dependency in dependencies:
        if dependency not in dataModelTypes:
            raise ValueError(f'Unknown dependency: {dependency}')

    templateData = {
        'className': className,
        'dependencies': [
            {'importName': utils.to_snake(value), 'name': value}
            for value in dependencies
        ]
    }

    filePath = Path(projectDirectory, 'tasks', f'{utils.to_snake(className)}.py')
    content = JinjaRenderer().render(
        templateName=f'{utils.to_snake(taskType.lower())}.py.j2',
        templateData=templateData,
        filePath=filePath,
        mode=mode
    )

    print('')
    print(f'{taskType} {className} was created in directory {filePath}.{utils.mode_message(mode)}')
    print('')
    if mode == Mode.DRY_RUN:
        return content
    return None


if __name__ == "__main__":
    fire.Fire(create_task)
