import os
import fire
from pathlib import Path
from hypergol.utils import Mode
from hypergol.utils import make_file_executable
from hypergol.utils import to_snake
from hypergol.utils import create_directory
from hypergol.utils import copy_file
import hypergol


def locate(fname):
    return Path(hypergol.__path__[0], 'cli', 'templates', fname)


def setup_project_directory(projectName, projectPath, mode):
    create_directory(projectPath, mode)
    copy_file(locate('make_venv.sh'), projectPath, mode)
    make_file_executable(Path(projectPath, 'make_venv.sh'))
    copy_file(locate('requirements.txt'), projectPath, mode)


def setup_data_models_directory(projectName, projectPath, mode):
    create_directory(Path(projectPath, 'data_models'), mode)


def create_project(projectName, mode=Mode.NORMAL, dryrun=None, force=None):
    if force:
        mode = Mode.FORCE
    if dryrun:
        mode = Mode.DRY_RUN
    if mode not in Mode.ALL:
        raise ValueError(f'mode must be one of {Mode.ALL}')
    projectPath = Path(to_snake(projectName))
    setup_project_directory(projectName, projectPath, mode)
    setup_data_models_directory(projectName, projectPath, mode)
    print('')
    print(f'Project {projectName} created in directory {projectPath}.')
    print('')


if __name__ == "__main__":
    fire.Fire(create_project)
