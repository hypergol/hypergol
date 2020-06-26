from pathlib import Path

from hypergol import utils
from hypergol.utils import Mode
from hypergol.utils import to_snake
from hypergol.cli.jinja_renderer import JinjaRenderer


class TaskCreator:

    def __init__(self, taskType, mode):
        self.taskType = taskType
        self.mode = mode

    def create(self, className, *args, projectDirectory='.'):
        dependencies = list(args)
        dataModelTypes = utils.get_data_model_types(projectDirectory)
        unknownTypes = set(dependencies)-set(dataModelTypes)
        if len(unknownTypes) > 0:
            raise ValueError(f'Unknown dependencies: {unknownTypes}')

        templateData = {
            'className': className,
            'dependencies': [
                {'importName': to_snake(value), 'name': value}
                for value in dependencies
            ]
        }

        filePath = Path(projectDirectory, 'tasks', f'{to_snake(className)}.py')
        content = JinjaRenderer().render(
            templateName=f'{to_snake(self.taskType.lower)}.py.j2',
            templateData=templateData,
            filePath=filePath,
            mode=self.mode
        )

        print('')
        print(f'{self.taskType} {className} was created in directory {filePath}.{utils.mode_message(self.mode)}')
        print('')
        if self.mode == Mode.DRY_RUN:
            return content
        return None
