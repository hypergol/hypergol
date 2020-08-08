from pathlib import Path
import fire

from hypergol.name_string import NameString
from hypergol.hypergol_project import HypergolProject


def create_model(modelName, inputClass, outputClass, *args, projectDirectory='.', dryrun=None, force=None):
    project = HypergolProject(projectDirectory=projectDirectory, dryrun=dryrun, force=force)
    modelName = NameString(modelName)
    inputClass = NameString(inputClass)
    outputClass = NameString(outputClass)
    blocks = [NameString(value) for value in args]
    project.check_dependencies([inputClass, outputClass] + blocks)

    content = project.render(
        templateName='model.py.j2',
        templateData={
            'name': modelName,
        },
        filePath=Path(projectDirectory, 'models', modelName.asFileName)
    )

    content = project.render(
        templateName='data_processor.py.j2',
        templateData={
            'name': modelName,
            'outputClass': outputClass
        },
        filePath=Path(projectDirectory, 'models', f'{modelName.asSnake}_data_processor.py')
    )

    content = project.render(
        templateName='train_model.py.j2',
        templateData={
            'modelName': modelName,
            'inputClass': inputClass,
            'outputClass': outputClass,
            'blockDependencies': [name for name in blocks if project.is_model_block_class(name)],
        },
        filePath=Path(projectDirectory, 'models', f'train_{modelName.asFileName}')
    )

    scriptContent = project.render_executable(
        templateName='train_model.sh.j2',
        templateData={'snakeName': modelName.asSnake},
        filePath=Path(projectDirectory, f'train_{modelName.asSnake}.sh')
    )
    return project.cli_final_message(creationType='Model', name=modelName, content=(content, scriptContent))


if __name__ == "__main__":
    fire.Fire(create_model)
