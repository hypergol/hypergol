from pathlib import Path

import fire

from hypergol.name_string import NameString
from hypergol.hypergol_project import HypergolProject


def create_model_block(className, projectDirectory='.', dryrun=None, force=None, torch=False):
    """Generates a Model Block class.

    The file will be located in ``project_name/models/blocks/block_name.py``

    Parameters
    ----------
    className : string (CamelCase)
        Name of the class to be created
    torch : bool = False
        Set to true to generate blocks for a Torch model
    """
    project = HypergolProject(projectDirectory=projectDirectory, dryrun=dryrun, force=force)
    className = NameString(className)

    content = project.render(
        templateName='model_block_torch.py.j2' if torch else 'model_block.py.j2',
        templateData={'className': className},
        filePath=Path(projectDirectory, 'models', 'blocks', className.asFileName)
    )

    return project.cli_final_message(creationType='ModelBlock', name=className, content=(content, ))


if __name__ == "__main__":
    fire.Fire(create_model_block)
