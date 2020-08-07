from pathlib import Path
import fire

from hypergol.name_string import NameString
from hypergol.hypergol_project import HypergolProject


def create_model(modelName, *args, projectDirectory='.', dryrun=None, force=None):
    project = HypergolProject(projectDirectory=projectDirectory, dryrun=dryrun, force=force)
    modelName = NameString(modelName)
    dependencies = [NameString(value) for value in args]
    project.check_dependencies(dependencies)

    content = project.render(
        templateName='model.py.j2',
        templateData={
            'snakeName': modelName.asSnake,
            'modelBlockDependencies': [name for name in dependencies if project.is_model_block_class(name)],
        },
        filePath=Path(projectDirectory, 'models', modelName.asFileName)
    )

    content = project.render(
        templateName='data_processor.py.j2',
        templateData={
            'snakeName': modelName.asSnake,
            'dataModelDependencies': [name for name in dependencies if project.is_data_model_class(name)]
        },
        filePath=Path(projectDirectory, 'models', f'{modelName.asSnake}_data_processor.py')
    )

    content = project.render(
        templateName='train_model.py.j2',
        templateData={
            'snakeName': modelName.asSnake,
            'className': modelName.asClass,
            'modelBlockDependencies': [name for name in dependencies if project.is_model_block_class(name)],
        },
        filePath=Path(projectDirectory, 'models', f'train_{modelName.asFileName}')
    )

    scriptContent = project.render_executable(
        templateName='train_model.sh.j2',
        templateData={'snakeName': modelName.asSnake},
        filePath=Path(projectDirectory, f'train_{modelName.asSnake}.sh')
    )

    print('')
    print(f'Model {modelName.asSnake} was created in directory {project.modelsPath}.{project.modeMessage}')
    print('')
    if project.isDryRun:
        return content, scriptContent
    return None


if __name__ == "__main__":
    fire.Fire(create_model)
