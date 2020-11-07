from pathlib import Path

import fire

from hypergol.name_string import NameString
from hypergol.hypergol_project import HypergolProject


def create_project(projectName, dryrun=None, force=None):
    """Generates the project directories and files

    Fails if the target directory already exists unless ``force=True`` or ``--force`` in CLI is set.

    Directories:
        - ``data_models`` with ``__init__.py``
        - ``pipelines`` with ``__init__.py``
        - ``tasks`` with ``__init__.py``
        - ``models`` with ``__init__.py``
        - ``models\blocks`` with ``__init__.py``
        - ``tests``

    Executables:
        - ``make_venv.sh`` to create a virtual environment
        - ``run_tests.sh`` to run tests
        - ``run_pylint.sh`` to run linting

    Misc:
        - ``requirements.txt``
        - ``.gitignore``
        - ``README.md``
        - ``pylintrc``

    Parameters
    ----------
    projectName : string (CamelCase)
        Name of the project to be created
    dryrun : bool (default=None)
        If set to ``True`` it returns the generated code as a string
    force : bool (default=None)
        If set to ``True`` it overwrites the target file
    """

    projectName = NameString(projectName)
    project = HypergolProject(projectDirectory=projectName.asSnake, dryrun=dryrun, force=force)
    project.create_project_directory()
    project.create_data_models_directory()
    project.render_simple(templateName='__init__.py.j2', filePath=Path(project.dataModelsPath, '__init__.py'))
    project.create_tasks_directory()
    project.render_simple(templateName='__init__.py.j2', filePath=Path(project.tasksPath, '__init__.py'))
    project.create_pipelines_directory()
    project.render_simple(templateName='__init__.py.j2', filePath=Path(project.pipelinesPath, '__init__.py'))
    project.create_models_directory()
    project.render_simple(templateName='__init__.py.j2', filePath=Path(project.modelsPath, '__init__.py'))
    project.create_blocks_directory()
    project.render_simple(templateName='__init__.py.j2', filePath=Path(project.blocksPath, '__init__.py'))
    project.create_tests_directory()
    project.render_executable(templateName='make_venv.sh.j2', templateData={}, filePath=Path(project.projectDirectory, 'make_venv.sh'))
    project.render_executable(templateName='run_tests.sh.j2', templateData={}, filePath=Path(project.projectDirectory, 'run_tests.sh'))
    project.render_executable(templateName='run_pylint.sh.j2', templateData={}, filePath=Path(project.projectDirectory, 'run_pylint.sh'))
    project.render_simple(templateName='requirements.txt.j2', filePath=Path(project.projectDirectory, 'requirements.txt'))
    project.render_simple(templateName='.gitignore.j2', filePath=Path(project.projectDirectory, '.gitignore'))
    project.render_simple(templateName='README.md.j2', filePath=Path(project.projectDirectory, 'README.md'))
    project.render_simple(templateName='pylintrc.j2', filePath=Path(project.projectDirectory, 'pylintrc'))

    return project.cli_final_message(creationType='Project', name=projectName, content=('', ))


if __name__ == "__main__":
    fire.Fire(create_project)
