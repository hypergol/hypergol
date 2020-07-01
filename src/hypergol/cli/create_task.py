from pathlib import Path
import fire

from hypergol.name_string import NameString
from hypergol.hypergol_project import HypergolProject


def create_task(className, *args, projectDirectory='.', dryrun=None, force=None, source=False, simple=True):
    if source and simple:
        raise ValueError('Task type cannot be determined, --source and --simple used together')
    if source:
        taskType = NameString('Source')
    elif simple:
        taskType = NameString('SimpleTask')
    else:
        taskType = NameString('Task')

    project = HypergolProject(projectDirectory=projectDirectory, dryrun=dryrun, force=force)
    className = NameString(className)

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
