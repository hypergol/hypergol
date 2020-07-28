from pathlib import Path
import fire

from hypergol.name_string import NameString
from hypergol.hypergol_project import HypergolProject


def create_model_block(modelBlockName, project):
    content = project.render(
        templateName='tensorflow_model_block.py.j2',
        templateData={'blockName': modelBlockName.asClass},
        filePath=Path(project.tensorflowModelsPath, 'blocks', modelBlockName.asFileName)
    )
    return content


def create_model(modelName, batchReaderName, *args, projectDirectory='.', dryrun=None, force=None):
    """Generates model class

    Fails if the target file already exist unless ``force=True`` or ``--force`` in CLI is set.

    Parameters
    ----------
    modelName : string (CamelCase)
        Name of the model to be created
    batchReaderName: string (CamelCase)
        Name of the batchReader to be created for the model
    projectDirectory : string (default='.')
        Location of the project directory, the code will be created in ``projectDirectory/data_models/class_name.py``.
    dryrun : bool (default=None)
        If set to ``True`` it returns the generated code as a string
    force : bool (default=None)
        If set to ``True`` it overwrites the target file

    Returns
    -------
    content : string
        The generated code if ``dryrun`` is specified
    """

    project = HypergolProject(projectDirectory=projectDirectory, dryrun=dryrun, force=force)
    modelName = NameString(modelName)
    batchReaderName = NameString(batchReaderName)
    blockNames = [NameString(block) for block in args]
    for blockName in blockNames:
        create_model_block(modelBlockName=blockName, project=project)

    # TODO(Mike): specify blocks before model, so can take into account dependencies like in DataModel?
    modelContent = project.render(
        templateName='tensorflow_model.py.j2',
        templateData={
            'modelName': modelName.asClass,
            'concatBlockNames': ', '.join([blockName.asVariable for blockName in blockNames]),
            'blockNames': blockNames
        },
        filePath=Path(project.tensorflowModelsPath, modelName.asFileName)
    )

    batchReaderContent = project.render(
        templateName='tensorflow_batch_reader.py.j2',
        templateData={
            'batchReaderName': batchReaderName
        },
        filePath=Path(project.tensorflowModelsPath, batchReaderName.asFileName)
    )

    trainingScriptContent = project.render(
        templateName='tensorflow_model_training_script.py.j2',
        templateData={
            'modelName': modelName,
            'batchReaderName': batchReaderName,
            'blockNames': blockNames
        },
        filePath=Path(project.tensorflowModelsPath, f'{modelName.asSnake}_training_script.py')
    )

    print('')
    print(f'Class {modelName} was created.{project.modeMessage}')
    print('')

    if project.isDryRun:
        return modelContent, batchReaderContent
    return None


if __name__ == "__main__":
    fire.Fire(create_model)
