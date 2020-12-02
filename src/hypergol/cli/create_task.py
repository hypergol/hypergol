from pathlib import Path

import fire

from hypergol.name_string import NameString
from hypergol.hypergol_project import HypergolProject


def create_task(className, *args, projectDirectory='.', dryrun=None, force=None, source=False):
    """Generates task class from the parameters derived from :class:`.Task`

    Fails if the target file already exists unless ``force=True`` or ``--force`` in the CLI is set.

    Setting the ``--source`` will generate a different template that have stubs with the functions that need to be overwritten.

    Parameters
    ----------
    className : string (CamelCase)
        Name of the class to be created
    projectDirectory : string (default='.')
        Location of the project directory, the code will be created in ``projectDirectory/data_models/class_name.py``.
    dryrun : bool (default=None)
        If set to ``True`` it returns the generated code as a string
    force : bool (default=None)
        If set to ``True`` it overwrites the target file
    source : bool (default=False)
        If set to ``True`` the class will generate stubs for functions to be overwritten
    *args : List of strings (CamelCase)
        Classes to be imported into the generated code from the datamodel, fails if class not found

    Returns
    -------

    content : string
        The generated code if ``dryrun`` is specified
    """

    if source:
        taskType = NameString('Source')
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

    return project.cli_final_message(creationType=taskType, name=className, content=(content, ))


if __name__ == "__main__":
    fire.Fire(create_task)
