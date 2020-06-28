from pathlib import Path
import fire
import hypergol
from hypergol.name_string import NameString
from hypergol.utils import Mode
from hypergol.utils import make_file_executable
from hypergol.utils import to_snake
from hypergol.utils import create_directory
from hypergol.utils import copy_file
from hypergol.utils import get_mode
from hypergol.utils import mode_message
from hypergol.cli.jinja_renderer import JinjaRenderer


def locate(fname):
    return Path(hypergol.__path__[0], 'cli', 'templates', fname)


def setup_project_directory(projectName: NameString, mode):
    create_directory(projectName.asSnake, mode)
    copy_file(locate('make_venv.sh'), Path(projectName.asSnake, 'make_venv.sh'), mode)
    make_file_executable(Path(projectName.asSnake, 'make_venv.sh'), mode)
    copy_file(locate('requirements.txt'), Path(projectName.asSnake, 'requirements.txt'), mode)
    copy_file(locate('.gitignore'), Path(projectName.asSnake, '.gitignore'), mode)

    JinjaRenderer().render(
        templateName='README.md.j2',
        templateData={'name': projectName.asClass},
        filePath=Path(projectName.asSnake, 'README.md'),
        mode=mode
    )


def create_project(projectName, mode=Mode.NORMAL, dryrun=None, force=None):
    projectName = NameString(projectName)
    mode = get_mode(mode=mode, dryrun=dryrun, force=force)
    setup_project_directory(projectName, mode)
    for directoryName in ['data_models', 'tasks', 'pipelines', 'tests']:
        create_directory(Path(projectName.asSnake, directoryName), mode)
        copy_file(locate('__init__.py'), Path(projectName.asSnake, directoryName, '__init__.py'), mode)
    print('')
    print(f'Project {projectName.asClass} was created in directory {projectName.asSnake}.{mode_message(mode)}')
    print('')


if __name__ == "__main__":
    fire.Fire(create_project)
