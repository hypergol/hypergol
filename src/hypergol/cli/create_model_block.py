from pathlib import Path
import fire

from hypergol.name_string import NameString
from hypergol.hypergol_project import HypergolProject


def create_model_block(className, projectDirectory='.', dryrun=None, force=None,):
    project = HypergolProject(projectDirectory=projectDirectory, dryrun=dryrun, force=force)
    className = NameString(className)

    content = project.render(
        templateName='model_block.py.j2',
        templateData={'className': className},
        filePath=Path(projectDirectory, 'models', className.asFileName)
    )

    print('')
    print(f'ModelBlock {className} was created.{project.modeMessage}')
    print('')
    if project.isDryRun:
        return content
    return None


if __name__ == "__main__":
    fire.Fire(create_model_block)
