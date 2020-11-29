from pathlib import Path

import fire

from hypergol.name_string import NameString
from hypergol.hypergol_project import HypergolProject


def create_pipeline(pipeLineName, *args, projectDirectory='.', dryrun=None, force=None, project=None):
    """Generates a pipeline script from the parameters

    Fails if the target file already exists unless ``force=True`` or ``--force`` in CLI is set.

    Generates pipe_line_name.py in pipelines, imports all the classes listed in ``*args`` and creates stubs for them to be filled. Also creates the executable ``pipe_line_name.sh`` in the project directory with examples how to pass parameters from the shell.

    Parameters
    ----------
    pipeLineName : string (CamelCase)
        Name of the pipeline to be created
    projectDirectory : string (default='.')
        Location of the project directory, the code will be created in ``projectDirectory/data_models/class_name.py``.
    dryrun : bool (default=None)
        If set to ``True`` it returns the generated code as a string
    force : bool (default=None)
        If set to ``True`` it overwrites the target file
    *args : List of strings (CamelCase)
        Classes to be imported into the generated code from the data model, fails if class not found in either ``data_models`` or ``tasks``

    Returns
    -------

    content : string
        The generated code if ``dryrun`` is specified
    scriptContent : string
        The generated shell script to run the pipeline if ``dryrun`` is specified

    """
    if project is None:
        project = HypergolProject(projectDirectory=projectDirectory, dryrun=dryrun, force=force)
    pipeLineName = NameString(pipeLineName)
    dependencies = [NameString(value) for value in args]
    project.check_dependencies(dependencies)

    content = project.render(
        templateName='pipeline.py.j2',
        templateData={
            'snakeName': pipeLineName.asSnake,
            'taskDependencies': [name for name in dependencies if project.is_task_class(name)],
            'dataModelDependencies': [name for name in dependencies if project.is_data_model_class(name)]
        },
        filePath=Path(projectDirectory, 'pipelines', pipeLineName.asFileName)
    )

    scriptContent = project.render_executable(
        templateName='pipeline.sh.j2',
        templateData={'snakeName': pipeLineName.asSnake},
        filePath=Path(projectDirectory, f'{pipeLineName.asSnake}.sh')
    )

    return project.cli_final_message(creationType='PipeLine', name=pipeLineName, content=(content, scriptContent))


if __name__ == "__main__":
    fire.Fire(create_pipeline)
