from pathlib import Path
import fire

from hypergol.cli.data_model_renderer import DataModelRenderer
from hypergol.name_string import NameString
from hypergol.hypergol_project import HypergolProject


def create_model_block(modelBlockName, project):
    content = (
        DataModelRenderer()
            .add('import tensorflow as tf            ')
            .add('                                   ')
            .add('from hypergol import BaseModelBlock')
            .add('                                   ')
            .add('                                   ')
            .add('class {className}(BaseModelBlock):         ', className=modelBlockName.asClass)
            .add('                                      ')
            .add('    def __init__(self, *args, **kwargs):  ')
            .add('        super().__init__(*args, **kwargs) ')
            .add('                                          ')
            .add('    def build(self, **kwargs):')
            .add('        """Contains the layer specification of a given block, attached to instance of the block"""')
            .add('        raise NotImplementedError(f"Model block {{self.__class__}} should implement `build` function")')
            .add('                                               ')
            .add('    def call(self, blockInputs, **kwargs):')
            .add('        """Contains code for how inputs should be processed, use `training` parameter to switch between tensorflow modes (for dropout etc)"""')
            .add('        raise NotImplementedError(f"model {{self.__class__}} must implement `call`")')
            .add('                                               ')
    ).get()
    project.create_text_file(content=content, filePath=Path(project.tensorflowModelsPath, 'blocks', modelBlockName.asFileName))


def create_model(modelName, *args, projectDirectory='.', dryrun=None, force=None):
    """Generates model class

    Fails if the target file already exist unless ``force=True`` or ``--force`` in CLI is set.

    Parameters
    ----------
    modelName : string (CamelCase)
        Name of the model to be created
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
    blockNames = [NameString(block) for block in args]
    for blockName in blockNames:
        create_model_block(modelBlockName=blockName, project=project)

    # TODO(Mike): specify blocks before model, so can take into account dependencies like in DataModel
    content = (
        DataModelRenderer()
            .add('import tensorflow as tf               ')
            .add('                                      ')
            .add('from hypergol import BaseModel        ')
            .add('from hypergol import TensorflowMetrics')
            .add('                                      ')
            .add('                                      ')
            .add('class {className}(BaseModel):         ', className=modelName.asClass)
            .add('                                      ')
            .add('    def __init__(self, {blocks}, *args, **kwargs):  ', blocks=', '.join([blockName.asVariable for blockName in blockNames]))
            .add('        super().__init__(*args, **kwargs) ')
            .add('                                          ')
            .add('    def call(self, inputs, training, **kwargs):')
            .add('        """Model processing code in here"""    ')
            .add('        raise NotImplementedError(f"model {{self.__class__}} must implement `call`")')
            .add('                                               ')
            .add('    @tf.function(input_signature=[                    ')
            .add('        tf.TensorSpec(shape=[None], dtype=tf.float32, name="firstInput"),')
            .add('        tf.TensorSpec(shape=[None], dtype=tf.float32, name="secondInput")')
            .add('    ])                                                                   ')
            .add('    def get_outputs(self, first_input, second_input):                    ')
            .add('        """Signature definitions + processing for model serving come from here"""')
            .add('        raise NotImplementedError(f"model {{self.__class__}} must implement `get_outputs`")')
            .add('                                                              ')
            .add('    def get_loss(self, outputs, targets):             ')
            .add('        """Fill in the loss function here"""')
            .add('        raise NotImplementedError(f"model {{self.__class__}} must implement `get_loss`")')
            .add('                                                                ')
            .add('    def get_metrics(self, inputs, outputs, targets):             ')
            .add('        """Metric processing, returns TensorflowMetrics class"""')
            .add('        raise NotImplementedError(f"model {{self.__class__}} must implement `get_metrics`")')
    ).get()
    project.create_text_file(content=content, filePath=Path(project.tensorflowModelsPath, modelName.asFileName))

    # TODO(Mike): need tests
    print('')
    print(f'Class {modelName} was created.{project.modeMessage}')
    print('')

    if project.isDryRun:
        return content
    return None


if __name__ == "__main__":
    fire.Fire(create_model)
