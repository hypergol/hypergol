from pathlib import Path
import fire

from hypergol.name_string import NameString
from hypergol.hypergol_project import HypergolProject


VALID_TASK_TYPES = {'Task', 'Source'}


def get_task_type(taskType, source):
    if taskType is None or taskType in VALID_TASK_TYPES:
        return NameString('Source' if source else (taskType or 'Task'))
    raise ValueError(f'Unkown task type: {taskType}')


def create_task(className, *args, projectDirectory='.', dryrun=None, force=None, source=False, taskType=None):
    project = HypergolProject(projectDirectory=projectDirectory, dryrun=dryrun, force=force)
    className = NameString(className)
    taskType = get_task_type(taskType, source)

    dependencies = [NameString(value) for value in args]
    project.check_dependencies(dependencies)

    content = project.render(
        templateName=f'{taskType.asFileName}.j2',
        templateData={'className': className, 'dependencies': dependencies},
        filePath=Path(projectDirectory, 'tasks', className.asFileName)
    )

    print('')
    print(f'{taskType} {className} was created.{project.modeMessage}')
    print('')
    if project.isDryRun:
        return content
    return None


if __name__ == "__main__":
    fire.Fire(create_task)
