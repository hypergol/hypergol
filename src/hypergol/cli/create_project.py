from pathlib import Path
import fire
import hypergol
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


def setup_project_directory(projectName, projectPath, mode):
    create_directory(projectPath, mode)
    copy_file(locate('make_venv.sh'), Path(projectPath, 'make_venv.sh'), mode)
    make_file_executable(Path(projectPath, 'make_venv.sh'), mode)
    copy_file(locate('requirements.txt'), Path(projectPath, 'requirements.txt'), mode)
    copy_file(locate('.gitignore'), Path(projectPath, '.gitignore'), mode)

    JinjaRenderer().render(
        templateName='README.md.j2',
        templateData={'name': projectName},
        filePath=Path(projectPath, 'README.md'),
        mode=mode
    )


def create_project(projectName, mode=Mode.NORMAL, dryrun=None, force=None):
    mode = get_mode(mode=mode, dryrun=dryrun, force=force)
    projectPath = Path(to_snake(projectName))
    setup_project_directory(projectName, projectPath, mode)
    for directoryName in ['data_models', 'tasks', 'pipelines', 'tests']:
        create_directory(Path(projectPath, directoryName), mode)
        copy_file(locate('__init__.py'), Path(projectPath, directoryName, '__init__.py'), mode)
    print('')
    print(f'Project {projectName} was created in directory {projectPath}.{mode_message(mode)}')
    print('')


if __name__ == "__main__":
    fire.Fire(create_project)
