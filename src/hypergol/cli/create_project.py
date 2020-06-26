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


def locate(fname):
    return Path(hypergol.__path__[0], 'cli', 'templates', fname)


def setup_project_directory(projectPath, mode):
    create_directory(projectPath, mode)
    copy_file(locate('make_venv.sh'), Path(projectPath, 'make_venv.sh'), mode)
    make_file_executable(Path(projectPath, 'make_venv.sh'), mode)
    copy_file(locate('requirements.txt'), Path(projectPath, 'requirements.txt'), mode)
    copy_file(locate('requirements.txt'), Path(projectPath, 'requirements2.txt'), mode)


def create_project(projectName, mode=Mode.NORMAL, dryrun=None, force=None):
    mode = get_mode(mode=mode, dryrun=dryrun, force=force)
    projectPath = Path(to_snake(projectName))
    setup_project_directory(projectPath, mode)
    create_directory(Path(projectPath, 'data_models'), mode)
    create_directory(Path(projectPath, 'tasks'), mode)
    create_directory(Path(projectPath, 'pipelines'), mode)
    print('')
    print(f'Project {projectName} created in directory {projectPath}.{mode_message(mode)}')
    print('')


if __name__ == "__main__":
    fire.Fire(create_project)
